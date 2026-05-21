
# modules/tax_report.py

import os
import json
from datetime import datetime, date

import pandas as pd
import streamlit as st

from utils.common import load_clients

from modules.tax_report_template import (
    get_all_clauses,
    get_clause_title,
    get_clause_sheet,
    get_clause_fields,
    get_clause_schema_blocks,
    get_tax_audit_form_fields,
    get_tax_audit_form_title,
    get_tax_audit_form_code,
    get_tax_audit_schema_file_name,
    get_tax_audit_root_keys,
    is_valid_tax_audit_form,
)

try:
    from modules.tax_report_template import get_tax_audit_form_field_schema
except ImportError:
    get_tax_audit_form_field_schema = None


# ---------------------------------------------------------
# GLOBAL CLIENT HELPER
# ---------------------------------------------------------

def get_active_client_from_global_selection():
    selected_client = st.session_state.get("global_selected_client")
    selected_ay = st.session_state.get("global_selected_ay")

    if selected_client and selected_ay:
        return selected_client, selected_ay

    return None, None


# ---------------------------------------------------------
# STYLE
# ---------------------------------------------------------

def apply_tax_report_style():
    st.markdown("""
    <style>
    .tax-report-hero {
        padding: 22px;
        border-radius: 22px;
        background: linear-gradient(135deg, #0f172a, #1d4ed8, #0f766e);
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.25);
    }
    .tax-report-hero h2 {
        margin: 0;
        font-size: 32px;
        font-weight: 900;
        color: white;
    }
    .tax-report-hero p {
        margin-top: 8px;
        font-size: 15px;
        opacity: 0.95;
        color: white;
    }
    .active-client-strip {
        padding: 14px 18px;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.75);
        border-left: 6px solid #10b981;
        color: #f8fafc;
        margin-bottom: 18px;
        font-weight: 800;
    }
    .report-section-box {
        padding: 15px 18px;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.78);
        border-left: 6px solid #2563eb;
        margin-top: 18px;
        margin-bottom: 14px;
        font-weight: 900;
        color: #f8fafc;
    }
    .readonly-statement {
        padding: 12px 14px;
        border-radius: 12px;
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.22);
        margin-bottom: 10px;
        color: #e5e7eb;
        font-size: 14px;
        line-height: 1.5;
    }
    .schema-chip {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        background: rgba(37, 99, 235, 0.20);
        border: 1px solid rgba(96, 165, 250, 0.35);
        color: #bfdbfe;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .clause-help-box {
        padding: 12px 14px;
        border-radius: 14px;
        background: rgba(2, 6, 23, 0.35);
        border: 1px solid rgba(148, 163, 184, 0.18);
        color: #cbd5e1;
        font-size: 13px;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# PATH HELPERS
# ---------------------------------------------------------

def get_tax_report_folder(client_name, ay):
    folder = f"clients/{client_name}/AY {ay}/Tax Report"
    os.makedirs(folder, exist_ok=True)
    return folder


def get_applicability_folder(client_name, ay):
    folder = f"clients/{client_name}/AY {ay}/Tax Audit Applicability"
    os.makedirs(folder, exist_ok=True)
    return folder


def get_tax_report_json_path(client_name, ay):
    return f"{get_tax_report_folder(client_name, ay)}/tax_audit_report.json"


def get_old_form_3cd_json_path(client_name, ay):
    return f"{get_tax_report_folder(client_name, ay)}/form_3cd_tax_report.json"


def get_applicability_excel_path(client_name, ay):
    return f"{get_applicability_folder(client_name, ay)}/tax_audit_applicability_result.xlsx"


def get_applicability_json_path(client_name, ay):
    return f"{get_applicability_folder(client_name, ay)}/tax_audit_applicability_result.json"


def get_schema_search_paths(schema_file_name):
    if not schema_file_name:
        return []

    return [
        os.path.join("schemas", schema_file_name),
        os.path.join("data", schema_file_name),
        schema_file_name,
    ]


# ---------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------

def safe_value(value, default=""):
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return value


def normalize_audit_form(value):
    value = str(value or "").strip()

    if "3CA" in value.upper():
        return "Form 3CA-3CD"

    if "3CB" in value.upper():
        return "Form 3CB-3CD"

    if value in ["Form 3CA-3CD", "Form 3CB-3CD"]:
        return value

    return "Not Applicable"


def default_report_structure(audit_form="Not Applicable"):
    return {
        "meta": {
            "audit_form": audit_form,
            "form_code": get_tax_audit_form_code(audit_form),
            "created_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "schema_source": "",
        },
        "applicability": {},
        "report_form": {},
        "form_3cd": {}
    }


def parse_date_value(value):
    if value in ["", None, "nan", "NaT"]:
        return None

    try:
        parsed = pd.to_datetime(value)
        return parsed.date()
    except Exception:
        return None


def date_to_string(value):
    if value in ["", None]:
        return ""

    try:
        return value.strftime("%Y-%m-%d")
    except Exception:
        return str(value)


def make_required_label(label, required=False):
    return f"{label} *" if required else label


def clean_label(label):
    label = str(label or "")
    label = label.replace("_", " ")
    label = label.replace("Form3cd", "")
    label = label.replace("F3cd", "")
    label = " ".join(label.split())
    return label if label else "Field"


def remove_empty_rows(records):
    cleaned = []

    for row in records:
        if not isinstance(row, dict):
            continue

        has_value = False

        for value in row.values():
            if str(value).strip() not in ["", "nan", "None", "NaT"]:
                has_value = True
                break

        if has_value:
            cleaned.append(row)

    return cleaned


# ---------------------------------------------------------
# SCHEMA LOADER / EXTRACTOR
# ---------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_tax_schema_cached(schema_file_name):
    for path in get_schema_search_paths(schema_file_name):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    schema = json.load(file)

                return {
                    "schema": schema,
                    "path": path,
                    "loaded": True,
                    "error": "",
                }
            except Exception as e:
                return {
                    "schema": {},
                    "path": path,
                    "loaded": False,
                    "error": str(e),
                }

    return {
        "schema": {},
        "path": "",
        "loaded": False,
        "error": "Schema file not found. Put schema_3CA.json and schema_3CB.json inside the schemas/ folder.",
    }


def dereference_schema_node(schema, node):
    if not isinstance(node, dict):
        return node

    if "$ref" not in node:
        return node

    ref = node.get("$ref", "")

    if not ref.startswith("#/definitions/"):
        return node

    definition_name = ref.replace("#/definitions/", "")
    return schema.get("definitions", {}).get(definition_name, node)


def resolve_schema_key(schema, schema_key):
    """
    Resolve keys like:
    - Form3cdDeprAllw
    - PartA
    - PartA.AssesseeName
    - PartA.Clause
    - Form3cdFirmAopDetailNew.Form3cdFirmAopDetailPK
    """

    if not schema or not schema_key:
        return None

    if schema_key.startswith("TAAS_"):
        return None

    definitions = schema.get("definitions", {})
    parts = schema_key.split(".")

    current = definitions.get(parts[0])

    if current is None:
        return None

    current = dereference_schema_node(schema, current)

    for part in parts[1:]:
        current = dereference_schema_node(schema, current)

        if not isinstance(current, dict):
            return None

        if current.get("type") == "array":
            current = dereference_schema_node(schema, current.get("items", {}))

        properties = current.get("properties", {})

        if part not in properties:
            return None

        current = properties.get(part)
        current = dereference_schema_node(schema, current)

    return current


def infer_widget_type(field_name, property_schema):
    field_name_lower = str(field_name).lower()

    if isinstance(property_schema, dict):
        if "enum" in property_schema:
            return "select"

        schema_type = property_schema.get("type")

        if schema_type in ["integer", "number"]:
            return "number"

        if "date" in field_name_lower:
            return "date"

        pattern = str(property_schema.get("pattern", ""))

        if "d{3}" in pattern and "0[1-9]" in pattern:
            return "date"

    if "date" in field_name_lower:
        return "date"

    if any(word in field_name_lower for word in ["amount", "value", "ratio", "rate", "percentage", "perc", "wdv", "profit", "loss", "tax"]):
        return "number"

    return "text"


def get_schema_fields(schema, schema_key, include_fields=None, fallback_fields=None):
    fallback_fields = fallback_fields or []
    include_fields = include_fields or []

    node = resolve_schema_key(schema, schema_key)

    if not node:
        return [
            {
                "name": field,
                "label": clean_label(field),
                "type": "text",
                "options": [],
                "required": False,
            }
            for field in (include_fields or fallback_fields)
        ]

    node = dereference_schema_node(schema, node)

    if isinstance(node, dict) and node.get("type") == "array":
        node = dereference_schema_node(schema, node.get("items", {}))

    if not isinstance(node, dict):
        return [
            {
                "name": field,
                "label": clean_label(field),
                "type": "text",
                "options": [],
                "required": False,
            }
            for field in (include_fields or fallback_fields)
        ]

    properties = node.get("properties", {})
    required_fields = set(node.get("required", []))

    if include_fields:
        field_names = include_fields
    else:
        field_names = list(properties.keys())

    if not field_names:
        field_names = fallback_fields

    fields = []

    for field_name in field_names:
        property_schema = properties.get(field_name, {})

        property_schema = dereference_schema_node(schema, property_schema)

        # Avoid rendering deep technical upload CSV helper fields unless specifically requested.
        if field_name in ["CsvDtls", "attachmentDocument"]:
            continue

        # For nested array/object properties, show as text unless it is the exact schema key target.
        field_type = infer_widget_type(field_name, property_schema)
        options = []

        if isinstance(property_schema, dict) and "enum" in property_schema:
            options = [str(item) for item in property_schema.get("enum", [])]

        fields.append({
            "name": field_name,
            "label": clean_label(field_name),
            "type": field_type,
            "options": options,
            "required": field_name in required_fields,
        })

    if not fields:
        fields = [
            {
                "name": field,
                "label": clean_label(field),
                "type": "text",
                "options": [],
                "required": False,
            }
            for field in fallback_fields
        ]

    return fields


# ---------------------------------------------------------
# APPLICABILITY READER
# ---------------------------------------------------------

def load_tax_audit_applicability_result(client_name, ay):
    result = {
        "tax_audit_applicable": "",
        "audit_form": "Not Applicable",
        "section_reference": "",
        "itr_basis": "",
        "itr_form": "",
        "reason": ""
    }

    json_path = get_applicability_json_path(client_name, ay)
    excel_path = get_applicability_excel_path(client_name, ay)

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            result["tax_audit_applicable"] = safe_value(data.get("Tax Audit Applicable", data.get("tax_audit_applicable", "")))
            result["audit_form"] = normalize_audit_form(data.get("Audit Form", data.get("audit_form", "Not Applicable")))
            result["section_reference"] = safe_value(data.get("Section Reference", data.get("section_reference", "")))
            result["itr_basis"] = safe_value(data.get("ITR Basis", data.get("itr_basis", "")))
            result["itr_form"] = safe_value(data.get("ITR Form", data.get("itr_form", "")))
            result["reason"] = safe_value(data.get("Reason", data.get("reason", "")))

            return result

        except Exception as e:
            st.warning(f"Could not read applicability JSON. Reason: {e}")

    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path)

            if len(df) > 0:
                row = df.iloc[0]

                result["tax_audit_applicable"] = safe_value(row.get("Tax Audit Applicable", ""))
                result["audit_form"] = normalize_audit_form(row.get("Audit Form", "Not Applicable"))
                result["section_reference"] = safe_value(row.get("Section Reference", ""))
                result["itr_basis"] = safe_value(row.get("ITR Basis", ""))
                result["itr_form"] = safe_value(row.get("ITR Form", ""))
                result["reason"] = safe_value(row.get("Reason", ""))

                return result

        except Exception as e:
            st.warning(f"Could not read applicability Excel. Reason: {e}")

    return result


# ---------------------------------------------------------
# LOAD / SAVE REPORT
# ---------------------------------------------------------

def load_tax_report(client_name, ay):
    file_path = get_tax_report_json_path(client_name, ay)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        data.setdefault("meta", {})
        data.setdefault("applicability", {})
        data.setdefault("report_form", {})
        data.setdefault("form_3cd", {})

        return data

    old_file_path = get_old_form_3cd_json_path(client_name, ay)

    if os.path.exists(old_file_path):
        with open(old_file_path, "r", encoding="utf-8") as file:
            old_3cd_data = json.load(file)

        migrated = default_report_structure()
        migrated["form_3cd"] = old_3cd_data

        save_tax_report(client_name, ay, migrated)
        return migrated

    return default_report_structure()


def save_tax_report(client_name, ay, report_data):
    report_data.setdefault("meta", {})
    report_data.setdefault("applicability", {})
    report_data.setdefault("report_form", {})
    report_data.setdefault("form_3cd", {})

    report_data["meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_path = get_tax_report_json_path(client_name, ay)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4, ensure_ascii=False)


# ---------------------------------------------------------
# APPLICABILITY LINKAGE
# ---------------------------------------------------------

def apply_applicability_to_report(report_data, applicability_data):
    audit_form = normalize_audit_form(applicability_data.get("audit_form", "Not Applicable"))

    report_data.setdefault("meta", {})
    report_data.setdefault("applicability", {})
    report_data.setdefault("form_3cd", {})
    report_data.setdefault("report_form", {})

    report_data["meta"]["audit_form"] = audit_form
    report_data["meta"]["form_code"] = get_tax_audit_form_code(audit_form)

    schema_file = get_tax_audit_schema_file_name(audit_form)
    schema_status = load_tax_schema_cached(schema_file)

    report_data["meta"]["schema_source"] = schema_status.get("path", "")

    root_key, inner_root_key = get_tax_audit_root_keys(audit_form)

    report_data["meta"]["schema_root"] = root_key
    report_data["meta"]["schema_inner_root"] = inner_root_key

    report_data["applicability"] = applicability_data

    clause_8_existing = report_data["form_3cd"].get("8", {})
    clause_8_fields = clause_8_existing.get("fields", {})

    if applicability_data.get("section_reference"):
        clause_8_fields.setdefault(
            "Relevant clause of section 44AB",
            applicability_data.get("section_reference", "")
        )

    if applicability_data.get("reason"):
        clause_8_fields.setdefault(
            "Reason for applicability",
            applicability_data.get("reason", "")
        )

    clause_8_fields.setdefault(
        "Whether auto-filled from Tax Audit Applicability module",
        "Yes"
    )

    report_data["form_3cd"]["8"] = {
        "title": get_clause_title("8"),
        "utility_sheet": get_clause_sheet("8"),
        "status": clause_8_existing.get("status", "In Progress"),
        "remarks": clause_8_existing.get("remarks", "Auto-filled from Tax Audit Applicability module."),
        "fields": clause_8_fields,
        "blocks": clause_8_existing.get("blocks", {}),
    }

    return report_data


# ---------------------------------------------------------
# REPORT FORM FIELD RENDERER - 3CA / 3CB
# ---------------------------------------------------------

def render_structured_report_fields(audit_form, existing_fields, selected_client, selected_ay, form_code):
    updated_fields = {}

    schema = None

    if get_tax_audit_form_field_schema:
        schema = get_tax_audit_form_field_schema(audit_form)

    if not schema:
        form_fields = get_tax_audit_form_fields(audit_form)

        for field in form_fields:
            updated_fields[field] = st.text_area(
                field,
                value=existing_fields.get(field, ""),
                height=70,
                key=f"report_form_{form_code}_{selected_client}_{selected_ay}_{field}"
            )

        return updated_fields

    for section in schema:
        section_title = section.get("section", "")

        st.markdown(f"""
        <div class="report-section-box">
            {section_title}
        </div>
        """, unsafe_allow_html=True)

        for field in section.get("fields", []):
            field_name = field.get("name", "")
            label = field.get("label", field_name)
            field_type = field.get("type", "text")
            required = bool(field.get("required", False))
            default_value = field.get("default", "")
            saved_value = existing_fields.get(field_name, default_value)

            widget_key = f"report_form_{form_code}_{selected_client}_{selected_ay}_{field_name}"
            display_label = make_required_label(label, required)

            if field_type == "readonly":
                st.markdown(f"""
                <div class="readonly-statement">
                    {label}
                </div>
                """, unsafe_allow_html=True)
                updated_fields[field_name] = field.get("default", "Agreed")

            elif field_type == "select":
                options = field.get("options", [])

                if saved_value not in options:
                    saved_value = default_value if default_value in options else options[0] if options else ""

                selected_value = st.selectbox(
                    display_label,
                    options,
                    index=options.index(saved_value) if saved_value in options else 0,
                    key=widget_key
                )

                updated_fields[field_name] = selected_value

            elif field_type == "date":
                existing_date = parse_date_value(saved_value)

                selected_date = st.date_input(
                    display_label,
                    value=existing_date,
                    key=widget_key
                )

                updated_fields[field_name] = date_to_string(selected_date)

            elif field_type == "textarea":
                updated_fields[field_name] = st.text_area(
                    display_label,
                    value=saved_value,
                    height=field.get("height", 100),
                    key=widget_key
                )

            else:
                updated_fields[field_name] = st.text_input(
                    display_label,
                    value=saved_value,
                    placeholder=field.get("placeholder", ""),
                    key=widget_key
                )

    return updated_fields


# ---------------------------------------------------------
# FORM 3CD CLAUSE RENDERER
# ---------------------------------------------------------

def make_empty_table_df(fields):
    columns = [field["name"] for field in fields]

    if not columns:
        return pd.DataFrame()

    return pd.DataFrame(columns=columns)


def object_value_to_widget(field, saved_value, widget_key):
    field_name = field.get("name", "")
    label = make_required_label(field.get("label", field_name), field.get("required", False))
    field_type = field.get("type", "text")
    options = field.get("options", [])

    if field_type == "select" and options:
        saved_value = str(saved_value or "")

        if saved_value not in options:
            options = [""] + options
            selected_index = 0
        else:
            selected_index = options.index(saved_value)

        return st.selectbox(
            label,
            options=options,
            index=selected_index,
            key=widget_key
        )

    if field_type == "date":
        selected_date = st.date_input(
            label,
            value=parse_date_value(saved_value),
            key=widget_key
        )
        return date_to_string(selected_date)

    if field_type == "number":
        try:
            number_value = float(str(saved_value).replace(",", "")) if str(saved_value).strip() else 0.0
        except Exception:
            number_value = 0.0

        return st.number_input(
            label,
            value=number_value,
            step=1.0,
            key=widget_key
        )

    if len(str(saved_value or "")) > 120:
        return st.text_area(
            label,
            value=str(saved_value or ""),
            height=80,
            key=widget_key
        )

    return st.text_input(
        label,
        value=str(saved_value or ""),
        key=widget_key
    )


def build_table_column_config(fields):
    config = {}

    for field in fields:
        name = field.get("name", "")
        label = field.get("label", name)
        field_type = field.get("type", "text")
        options = field.get("options", [])

        if field_type == "select" and options and len(options) <= 100:
            config[name] = st.column_config.SelectboxColumn(
                label,
                options=[""] + options,
                required=False
            )
        elif field_type == "number":
            config[name] = st.column_config.NumberColumn(label)
        elif field_type == "date":
            config[name] = st.column_config.TextColumn(label, help="Enter date in YYYY-MM-DD format")
        else:
            config[name] = st.column_config.TextColumn(label)

    return config


def render_clause_blocks(clause_no, existing_clause, audit_form, selected_client, selected_ay):
    schema_file = get_tax_audit_schema_file_name(audit_form)
    schema_status = load_tax_schema_cached(schema_file)
    schema = schema_status.get("schema", {}) if schema_status.get("loaded") else {}

    blocks = get_clause_schema_blocks(clause_no)

    existing_blocks = existing_clause.get("blocks", {})

    # Backward compatibility with old saved clause fields
    old_fields = existing_clause.get("fields", {})

    updated_blocks = {}
    flattened_fields = {}

    if not blocks:
        fallback_fields = get_clause_fields(clause_no)

        object_data = {}

        for field in fallback_fields:
            object_data[field] = st.text_area(
                field,
                value=old_fields.get(field, ""),
                height=80,
                key=f"clause_{selected_client}_{selected_ay}_{clause_no}_{field}"
            )
            flattened_fields[field] = object_data[field]

        updated_blocks["Fallback"] = {
            "type": "object",
            "schema_key": "",
            "data": object_data
        }

        return updated_blocks, flattened_fields

    if schema_status.get("loaded"):
        st.markdown(
            f'<span class="schema-chip">Schema loaded: {schema_status.get("path")}</span>',
            unsafe_allow_html=True
        )
    else:
        st.warning(schema_status.get("error", "Schema file not loaded. Fallback fields are being used."))

    for block_index, block in enumerate(blocks):
        block_name = block.get("name", f"Block {block_index + 1}")
        schema_key = block.get("schema_key", "")
        block_type = block.get("type", "object")
        include_fields = block.get("include_fields", [])
        fallback_fields = block.get("fallback_fields", [])

        st.markdown(f"""
        <div class="report-section-box">
            {block_name}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="clause-help-box">
            Utility schema key: <b>{schema_key}</b>
        </div>
        """, unsafe_allow_html=True)

        fields = get_schema_fields(
            schema=schema,
            schema_key=schema_key,
            include_fields=include_fields,
            fallback_fields=fallback_fields
        )

        block_saved = existing_blocks.get(block_name, {})

        if block_type == "table":
            saved_rows = block_saved.get("data", [])

            if not isinstance(saved_rows, list):
                saved_rows = []

            columns = [field["name"] for field in fields]

            if saved_rows:
                table_df = pd.DataFrame(saved_rows)

                for col in columns:
                    if col not in table_df.columns:
                        table_df[col] = ""

                table_df = table_df[columns]
            else:
                table_df = make_empty_table_df(fields)

            edited_df = st.data_editor(
                table_df,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                column_config=build_table_column_config(fields),
                key=f"clause_table_{selected_client}_{selected_ay}_{clause_no}_{block_index}_{schema_key}"
            )

            records = edited_df.fillna("").to_dict("records")
            records = remove_empty_rows(records)

            updated_blocks[block_name] = {
                "type": "table",
                "schema_key": schema_key,
                "data": records
            }

            for row_index, row in enumerate(records, start=1):
                for key, value in row.items():
                    flattened_fields[f"{block_name} - Row {row_index} - {key}"] = value

        else:
            saved_data = block_saved.get("data", {})

            if not isinstance(saved_data, dict):
                saved_data = {}

            # Backward compatibility: use old flat field if object data not saved.
            for field in fields:
                field_name = field.get("name", "")

                if field_name not in saved_data and field_name in old_fields:
                    saved_data[field_name] = old_fields.get(field_name, "")

            object_data = {}

            for field in fields:
                field_name = field.get("name", "")
                widget_key = f"clause_object_{selected_client}_{selected_ay}_{clause_no}_{block_index}_{schema_key}_{field_name}"
                saved_value = saved_data.get(field_name, "")

                object_data[field_name] = object_value_to_widget(
                    field=field,
                    saved_value=saved_value,
                    widget_key=widget_key
                )

            updated_blocks[block_name] = {
                "type": "object",
                "schema_key": schema_key,
                "data": object_data
            }

            for key, value in object_data.items():
                flattened_fields[f"{block_name} - {key}"] = value

    return updated_blocks, flattened_fields


# ---------------------------------------------------------
# EXPORT
# ---------------------------------------------------------

def flatten_report_form_rows(report_form, audit_form):
    rows = []

    for field_name, field_value in report_form.get("fields", {}).items():
        rows.append({
            "Audit Form": audit_form,
            "Field": field_name,
            "Value": field_value
        })

    return rows


def flatten_3cd_clause_rows(form_3cd):
    rows = []

    for clause_no, title in get_all_clauses():
        clause_data = form_3cd.get(str(clause_no), {})
        blocks = clause_data.get("blocks", {})

        if blocks:
            for block_name, block_data in blocks.items():
                block_type = block_data.get("type", "")
                schema_key = block_data.get("schema_key", "")
                data = block_data.get("data", {})

                if block_type == "table":
                    if isinstance(data, list) and data:
                        for row_index, row in enumerate(data, start=1):
                            for field_name, field_value in row.items():
                                rows.append({
                                    "Clause No": clause_no,
                                    "Title": title,
                                    "Utility Sheet": get_clause_sheet(clause_no),
                                    "Block": block_name,
                                    "Schema Key": schema_key,
                                    "Row No": row_index,
                                    "Field": field_name,
                                    "Value": field_value,
                                    "Status": clause_data.get("status", "Not Filled"),
                                    "Auditor Remark": clause_data.get("remarks", "")
                                })
                    else:
                        rows.append({
                            "Clause No": clause_no,
                            "Title": title,
                            "Utility Sheet": get_clause_sheet(clause_no),
                            "Block": block_name,
                            "Schema Key": schema_key,
                            "Row No": "",
                            "Field": "",
                            "Value": "",
                            "Status": clause_data.get("status", "Not Filled"),
                            "Auditor Remark": clause_data.get("remarks", "")
                        })

                else:
                    if isinstance(data, dict) and data:
                        for field_name, field_value in data.items():
                            rows.append({
                                "Clause No": clause_no,
                                "Title": title,
                                "Utility Sheet": get_clause_sheet(clause_no),
                                "Block": block_name,
                                "Schema Key": schema_key,
                                "Row No": "",
                                "Field": field_name,
                                "Value": field_value,
                                "Status": clause_data.get("status", "Not Filled"),
                                "Auditor Remark": clause_data.get("remarks", "")
                            })
                    else:
                        rows.append({
                            "Clause No": clause_no,
                            "Title": title,
                            "Utility Sheet": get_clause_sheet(clause_no),
                            "Block": block_name,
                            "Schema Key": schema_key,
                            "Row No": "",
                            "Field": "",
                            "Value": "",
                            "Status": clause_data.get("status", "Not Filled"),
                            "Auditor Remark": clause_data.get("remarks", "")
                        })
        else:
            fields = clause_data.get("fields", {})

            if fields:
                for field_name, field_value in fields.items():
                    rows.append({
                        "Clause No": clause_no,
                        "Title": title,
                        "Utility Sheet": get_clause_sheet(clause_no),
                        "Block": "Legacy Fields",
                        "Schema Key": "",
                        "Row No": "",
                        "Field": field_name,
                        "Value": field_value,
                        "Status": clause_data.get("status", "Not Filled"),
                        "Auditor Remark": clause_data.get("remarks", "")
                    })
            else:
                rows.append({
                    "Clause No": clause_no,
                    "Title": title,
                    "Utility Sheet": get_clause_sheet(clause_no),
                    "Block": "",
                    "Schema Key": "",
                    "Row No": "",
                    "Field": "",
                    "Value": "",
                    "Status": "Not Filled",
                    "Auditor Remark": ""
                })

    return rows


def export_tax_audit_report_excel(client_name, ay, report_data):
    folder = get_tax_report_folder(client_name, ay)

    audit_form = report_data.get("meta", {}).get("audit_form", "Not Applicable")
    form_code = report_data.get("meta", {}).get("form_code", "")
    applicability = report_data.get("applicability", {})
    report_form = report_data.get("report_form", {})
    form_3cd = report_data.get("form_3cd", {})

    report_info_df = pd.DataFrame([{
        "Client Name": client_name,
        "Assessment Year": ay,
        "Audit Form": audit_form,
        "Form Code": form_code,
        "Schema Source": report_data.get("meta", {}).get("schema_source", ""),
        "Schema Root": report_data.get("meta", {}).get("schema_root", ""),
        "Schema Inner Root": report_data.get("meta", {}).get("schema_inner_root", ""),
        "Tax Audit Applicable": applicability.get("tax_audit_applicable", ""),
        "Section Reference": applicability.get("section_reference", ""),
        "ITR Basis": applicability.get("itr_basis", ""),
        "ITR Form": applicability.get("itr_form", ""),
        "Generated On": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])

    report_form_df = pd.DataFrame(flatten_report_form_rows(report_form, audit_form))

    summary_rows = []

    for clause_no, title in get_all_clauses():
        data = form_3cd.get(str(clause_no), {})
        blocks = get_clause_schema_blocks(clause_no)

        summary_rows.append({
            "Clause No": clause_no,
            "Title": title,
            "Utility Sheet / Schema Area": get_clause_sheet(clause_no),
            "Schema Blocks Count": len(blocks),
            "Filling Status": data.get("status", "Not Filled"),
            "Final Auditor Remark": data.get("remarks", "")
        })

    form_3cd_summary_df = pd.DataFrame(summary_rows)
    form_3cd_details_df = pd.DataFrame(flatten_3cd_clause_rows(form_3cd))

    excel_path = f"{folder}/tax_audit_report_{form_code or 'NA'}_3CD_schema_based.xlsx"

    with pd.ExcelWriter(excel_path) as writer:
        report_info_df.to_excel(writer, sheet_name="Report_Info", index=False)
        report_form_df.to_excel(writer, sheet_name="3CA_3CB_Report", index=False)
        form_3cd_summary_df.to_excel(writer, sheet_name="Form_3CD_Summary", index=False)
        form_3cd_details_df.to_excel(writer, sheet_name="Form_3CD_Details", index=False)

    return excel_path


# ---------------------------------------------------------
# COMPLETION
# ---------------------------------------------------------

def calculate_completion(report_data):
    form_3cd = report_data.get("form_3cd", {})

    completed_count = 0
    total_count = len(get_all_clauses())

    for clause_no, title in get_all_clauses():
        status = form_3cd.get(str(clause_no), {}).get("status", "Not Filled")

        if status in ["Filled", "Not Applicable"]:
            completed_count += 1

    completion = round((completed_count / total_count) * 100, 2) if total_count > 0 else 0

    return completed_count, total_count, completion


# ---------------------------------------------------------
# BASIC JSON EXPORT PLACEHOLDER
# ---------------------------------------------------------

def export_internal_json(client_name, ay, report_data):
    """
    This exports the TAAS internal schema-based JSON.
    Final Income-tax portal utility JSON mapping can be added after field testing.
    """
    folder = get_tax_report_folder(client_name, ay)
    audit_form = report_data.get("meta", {}).get("audit_form", "Not Applicable")
    form_code = get_tax_audit_form_code(audit_form)

    path = f"{folder}/taas_internal_{form_code}_3CD_schema_data.json"

    with open(path, "w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4, ensure_ascii=False)

    return path


# ---------------------------------------------------------
# MAIN UI
# ---------------------------------------------------------

def show_tax_report():
    apply_tax_report_style()

    st.markdown("""
    <div class="tax-report-hero">
        <h2>📑 Tax Audit Report - Form 3CA / 3CB with Form 3CD</h2>
        <p>Prepare Form 3CA / 3CB report details and schema-based Form 3CD clause-wise reporting.</p>
    </div>
    """, unsafe_allow_html=True)

    selected_client, selected_ay = get_active_client_from_global_selection()

    if not selected_client or not selected_ay:
        st.info("Please select a client from the top-right Active Audit Client selector.")
        return

    st.markdown(f"""
    <div class="active-client-strip">
        Active Client: {selected_client} | AY: {selected_ay}
    </div>
    """, unsafe_allow_html=True)

    applicability_data = load_tax_audit_applicability_result(selected_client, selected_ay)

    report_data = load_tax_report(selected_client, selected_ay)
    report_data = apply_applicability_to_report(report_data, applicability_data)
    save_tax_report(selected_client, selected_ay, report_data)

    audit_form = report_data.get("meta", {}).get("audit_form", "Not Applicable")
    form_code = report_data.get("meta", {}).get("form_code", "")

    st.divider()

    st.write("## 🧭 Auto-linked Tax Audit Applicability")

    a1, a2, a3 = st.columns(3)

    with a1:
        st.metric("Tax Audit Applicable", applicability_data.get("tax_audit_applicable", ""))

    with a2:
        st.metric("Audit Form", audit_form)

    with a3:
        st.metric("Section Reference", applicability_data.get("section_reference", ""))

    if audit_form == "Not Applicable":
        st.warning(
            "Tax audit form is not available from the Tax Audit Applicability module. "
            "Please first complete the Tax Audit Applicability tab for this client."
        )
        return

    if not is_valid_tax_audit_form(audit_form):
        st.error("Invalid audit form detected. Please check Tax Audit Applicability result.")
        return

    schema_file = get_tax_audit_schema_file_name(audit_form)
    schema_status = load_tax_schema_cached(schema_file)

    st.success(f"Applicable report selected automatically: {audit_form}")
    st.caption(get_tax_audit_form_title(audit_form))

    if schema_status.get("loaded"):
        st.info(f"Schema file detected: {schema_status.get('path')}")
    else:
        st.warning(
            "Schema file not detected. Form 3CD will still work with fallback fields. "
            "For schema-based fields, place schema_3CA.json and schema_3CB.json inside the schemas/ folder."
        )

    if applicability_data.get("reason"):
        with st.expander("View Applicability Reason"):
            st.write(applicability_data.get("reason"))

    st.divider()

    # ---------------------------------------------------------
    # FORM 3CA / 3CB REPORT DETAILS
    # ---------------------------------------------------------

    st.write(f"## 🧾 {form_code} Report Details")

    report_data.setdefault("report_form", {})
    report_data["report_form"].setdefault("fields", {})

    existing_report_fields = report_data["report_form"].get("fields", {})

    with st.expander(f"Open {form_code} Report Data Entry", expanded=False):
        updated_report_fields = render_structured_report_fields(
            audit_form,
            existing_report_fields,
            selected_client,
            selected_ay,
            form_code
        )

        if st.button(f"💾 Save {form_code} Report Details", key=f"save_{form_code}_report_details"):
            report_data["report_form"] = {
                "audit_form": audit_form,
                "form_code": form_code,
                "title": get_tax_audit_form_title(audit_form),
                "fields": updated_report_fields
            }

            save_tax_report(selected_client, selected_ay, report_data)
            st.success(f"✅ {form_code} report details saved successfully.")
            st.rerun()

    st.divider()

    # ---------------------------------------------------------
    # FORM 3CD CLAUSE-WISE REPORTING
    # ---------------------------------------------------------

    st.write("## 📋 Form 3CD Clause-wise Reporting")

    latest_report_data = load_tax_report(selected_client, selected_ay)
    form_3cd_data = latest_report_data.get("form_3cd", {})

    clause_rows = []

    for clause_no, title in get_all_clauses():
        saved = form_3cd_data.get(str(clause_no), {})
        blocks = get_clause_schema_blocks(clause_no)

        clause_rows.append({
            "Clause No": clause_no,
            "Title / Particulars": title,
            "Utility Sheet / Schema Area": get_clause_sheet(clause_no),
            "Schema Blocks": len(blocks),
            "Filling Status": saved.get("status", "Not Filled")
        })

    clause_df = pd.DataFrame(clause_rows)

    st.info("Click once on any clause row to open the Form 3CD schema-based data entry dialog.")

    selected_event = st.dataframe(
        clause_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key=f"form_3cd_clause_table_{selected_client}_{selected_ay}"
    )

    @st.dialog("Form 3CD Clause Data Entry")
    def open_clause_dialog(clause_no):
        clause_no = str(clause_no)

        clause_title = get_clause_title(clause_no)
        utility_sheet = get_clause_sheet(clause_no)

        latest_data = load_tax_report(selected_client, selected_ay)
        latest_data.setdefault("form_3cd", {})

        existing = latest_data["form_3cd"].get(clause_no, {})

        st.write(f"### Clause {clause_no}")
        st.write(f"**{clause_title}**")
        st.caption(f"Utility Sheet / Schema Reference: {utility_sheet}")

        updated_blocks, flattened_fields = render_clause_blocks(
            clause_no=clause_no,
            existing_clause=existing,
            audit_form=audit_form,
            selected_client=selected_client,
            selected_ay=selected_ay
        )

        final_remark = st.text_area(
            "Final Auditor Remark",
            value=existing.get("remarks", ""),
            height=100,
            key=f"clause_{selected_client}_{selected_ay}_{clause_no}_final_remark"
        )

        status_options = [
            "Not Filled",
            "In Progress",
            "Filled",
            "Not Applicable"
        ]

        existing_status = existing.get("status", "Not Filled")

        status = st.selectbox(
            "Filling Status",
            status_options,
            index=status_options.index(existing_status) if existing_status in status_options else 0,
            key=f"clause_{selected_client}_{selected_ay}_{clause_no}_status"
        )

        save_col, close_col = st.columns(2)

        with save_col:
            if st.button("💾 Save Clause", key=f"save_clause_{selected_client}_{selected_ay}_{clause_no}", use_container_width=True):
                latest_data["form_3cd"][clause_no] = {
                    "title": clause_title,
                    "utility_sheet": utility_sheet,
                    "status": status,
                    "remarks": final_remark,
                    "fields": flattened_fields,
                    "blocks": updated_blocks,
                    "schema_based": True,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                save_tax_report(selected_client, selected_ay, latest_data)
                st.success("✅ Clause saved successfully.")
                st.rerun()

        with close_col:
            if st.button("Close", key=f"close_clause_{selected_client}_{selected_ay}_{clause_no}", use_container_width=True):
                st.rerun()

    selected_rows = selected_event.selection.rows

    if selected_rows:
        row_index = selected_rows[0]
        selected_clause_no = str(clause_df.iloc[row_index]["Clause No"])
        open_clause_dialog(selected_clause_no)

    st.divider()

    # ---------------------------------------------------------
    # COMPLETION
    # ---------------------------------------------------------

    latest_report_data = load_tax_report(selected_client, selected_ay)

    completed_count, total_clauses, completion = calculate_completion(latest_report_data)

    st.subheader("📊 Tax Audit Report Completion")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Completed Clauses", completed_count)

    with c2:
        st.metric("Total Clauses", total_clauses)

    with c3:
        st.metric("Completion", f"{completion}%")

    st.progress(completion / 100)

    st.divider()

    # ---------------------------------------------------------
    # EXPORTS
    # ---------------------------------------------------------

    st.subheader("📤 Export")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        if st.button("📤 Export Complete Tax Audit Report to Excel", use_container_width=True):
            excel_path = export_tax_audit_report_excel(
                selected_client,
                selected_ay,
                latest_report_data
            )
            st.success(f"✅ Exported successfully: {excel_path}")

    with export_col2:
        if st.button("🧾 Export TAAS Internal JSON", use_container_width=True):
            json_path = export_internal_json(
                selected_client,
                selected_ay,
                latest_report_data
            )
            st.success(f"✅ Internal JSON exported successfully: {json_path}")

    st.caption(
        "This version implements schema-aware Form 3CD data entry. "
        "The next enhancement can convert TAAS internal JSON into final Income-tax portal utility JSON."
    )
