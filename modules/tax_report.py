
# modules/tax_report.py

import os
import re
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
# FINAL INCOME-TAX UTILITY COMPATIBLE JSON EXPORT
# ---------------------------------------------------------

STATE_CODE_MAP = {
    "andaman and nicobar islands": "01",
    "andhra pradesh": "02",
    "arunachal pradesh": "03",
    "assam": "04",
    "bihar": "05",
    "chandigarh": "06",
    "dadra and nagar haveli": "07",
    "daman and diu": "08",
    "delhi": "09",
    "goa": "10",
    "gujarat": "11",
    "haryana": "12",
    "himachal pradesh": "13",
    "jammu and kashmir": "14",
    "karnataka": "15",
    "kerala": "16",
    "lakshadweep": "17",
    "madhya pradesh": "18",
    "maharashtra": "19",
    "manipur": "20",
    "meghalaya": "21",
    "mizoram": "22",
    "nagaland": "23",
    "odisha": "24",
    "puducherry": "25",
    "punjab": "26",
    "rajasthan": "27",
    "sikkim": "28",
    "tamil nadu": "29",
    "tripura": "30",
    "uttar pradesh": "31",
    "west bengal": "32",
    "chhattisgarh": "33",
    "uttarakhand": "34",
    "jharkhand": "35",
    "telangana": "36",
    "ladakh": "37",
    "foreign": "99",
}

STATUS_CODE_MAP = {
    "individual": 1,
    "huf": 2,
    "hindu undivided family": 2,
    "firm": 3,
    "partnership firm": 3,
    "limited liability partnership": 4,
    "llp": 4,
    "company": 5,
    "trust": 6,
    "aop": 7,
    "association of person": 7,
    "local authority": 8,
    "artificial juridical person": 9,
    "co-operative society": 10,
    "cooperative society": 10,
    "co-operative bank": 11,
    "cooperative bank": 11,
    "body of individuals": 12,
    "boi": 12,
}

LAW_CODE_MAP_3CA = {
    "companies act, 2013": "14",
    "company": "14",
    "limited liability partnership act, 2008": "33",
    "llp": "33",
    "co-operative societies act": "52",
    "cooperative societies act": "52",
    "societies registration act": "58",
    "trust act": "27",
    "indian trusts act, 1882": "27",
    "income-tax act, 1961": "24",
    "other law": "99",
}


def export_internal_json(client_name, ay, report_data):
    """
    This exports the TAAS internal schema-based JSON.
    """
    folder = get_tax_report_folder(client_name, ay)
    audit_form = report_data.get("meta", {}).get("audit_form", "Not Applicable")
    form_code = get_tax_audit_form_code(audit_form)

    path = f"{folder}/taas_internal_{form_code}_3CD_schema_data.json"

    with open(path, "w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4, ensure_ascii=False)

    return path


def get_report_fields(report_data):
    return report_data.get("report_form", {}).get("fields", {}) or {}


def get_field(fields, *names, default=""):
    for name in names:
        value = fields.get(name, "")
        if str(value).strip() not in ["", "None", "nan", "NaT"]:
            return value
    return default


def normalize_text(value, max_length=None):
    value = "" if value is None else str(value).strip()

    if max_length and len(value) > max_length:
        value = value[:max_length]

    return value


def normalize_date_string(value, default=""):
    if value in ["", None, "None", "nan", "NaT"]:
        return default

    try:
        parsed = pd.to_datetime(value)
        return parsed.strftime("%Y-%m-%d")
    except Exception:
        return str(value)


def normalize_country_code(value):
    value = normalize_text(value)

    if not value:
        return "91"

    if "-" in value:
        return value.split("-")[0].strip()

    if value.lower() in ["india", "in"]:
        return "91"

    if value.isdigit():
        return value

    return "91"


def normalize_state_code(value):
    value = normalize_text(value)

    if not value:
        return ""

    if value.isdigit():
        return value.zfill(2)

    lowered = value.lower().strip()

    if "-" in lowered:
        possible_code = lowered.split("-")[0].strip()
        if possible_code.isdigit():
            return possible_code.zfill(2)

    return STATE_CODE_MAP.get(lowered, "")


def normalize_pan(value):
    return normalize_text(value).upper()


def normalize_aadhaar(value):
    value = normalize_text(value)
    digits = "".join(ch for ch in value if ch.isdigit())
    return digits


def normalize_membership(value):
    value = normalize_text(value)
    digits = "".join(ch for ch in value if ch.isdigit())

    if len(digits) >= 6:
        return digits[-6:]

    return digits


def normalize_yes_no(value, default="N"):
    value = normalize_text(value).upper()

    if value in ["Y", "YES", "TRUE", "1", "APPLICABLE"]:
        return "Y"

    if value in ["N", "NO", "FALSE", "0", "NOT APPLICABLE"]:
        return "N"

    return default


def ay_to_schema_year(ay):
    value = normalize_text(ay)

    match = re.search(r"(20\d{2})", value)

    if match:
        return match.group(1)

    current = date.today()
    return str(current.year)


def ay_to_full_string(ay):
    value = normalize_text(ay)

    if re.match(r"20\d{2}-\d{2}", value):
        return value

    year = ay_to_schema_year(value)

    try:
        return f"{int(year)}-{str(int(year) + 1)[-2:]}"
    except Exception:
        return value


def get_financial_year_start_end_from_ay(ay):
    ay_year = int(ay_to_schema_year(ay))
    py_start = date(ay_year - 1, 4, 1).strftime("%Y-%m-%d")
    py_end = date(ay_year, 3, 31).strftime("%Y-%m-%d")
    return py_start, py_end


def build_assessee_name(fields, client_name):
    last_name = get_field(fields, "Assessee Last Name", default="")

    if not last_name:
        last_name = client_name

    return {
        "FirstName": normalize_text(get_field(fields, "Assessee First Name"), 25),
        "MiddleName": normalize_text(get_field(fields, "Assessee Middle Name"), 25),
        "LastName": normalize_text(last_name, 75),
    }


def build_address_detail(fields, prefix="Assessee"):
    addr1 = get_field(fields, f"{prefix} Flat Door Building", default="")
    addr2 = get_field(fields, f"{prefix} Road Street Block Sector", default="")
    district = get_field(fields, f"{prefix} District", default="")
    area = get_field(fields, f"{prefix} Area Locality", default="")
    post_office = get_field(fields, f"{prefix} Post Office", default="")
    state = get_field(fields, f"{prefix} State", default="")
    country = get_field(fields, f"{prefix} Country Region", default="91-India")
    pincode = get_field(fields, f"{prefix} Pincode", f"{prefix} ZIP Code", default="")

    return {
        "AddrDetail1": normalize_text(addr1, 100),
        "AddrDetail2": normalize_text(addr2, 100),
        "CityOrTownOrDistrict": normalize_text(district, 50),
        "LocalityOrArea": normalize_text(area, 50),
        "LocalityOrAreaName": normalize_text(area, 50),
        "PostOffice": normalize_text(post_office, 50),
        "PostOfficeName": normalize_text(post_office, 50),
        "StateCode": normalize_state_code(state),
        "CountryCode": normalize_country_code(country),
        "PinCode": normalize_text(pincode),
    }


def build_accountant_other_info(fields):
    report_date = normalize_date_string(
        get_field(fields, "Report Date", "Date of signing Tax Audit Report"),
        default=date.today().strftime("%Y-%m-%d")
    )

    return {
        "FirstName": normalize_text(get_field(fields, "Accountant First Name"), 25),
        "MiddleName": normalize_text(get_field(fields, "Accountant Middle Name"), 25),
        "LastName": normalize_text(get_field(fields, "Accountant Last Name"), 75),
        "AddrDetail1": normalize_text(get_field(fields, "Accountant Flat Door Building"), 100),
        "AddrDetail2": normalize_text(get_field(fields, "Accountant Road Street Block Sector"), 100),
        "CityOrTownOrDistrict": normalize_text(get_field(fields, "Accountant District"), 50),
        "LocalityOrArea": normalize_text(get_field(fields, "Accountant Area Locality"), 50),
        "LocalityOrAreaName": normalize_text(get_field(fields, "Accountant Area Locality"), 50),
        "PostOffice": normalize_text(get_field(fields, "Accountant Post Office"), 50),
        "PostOfficeName": normalize_text(get_field(fields, "Accountant Post Office"), 50),
        "StateCode": normalize_state_code(get_field(fields, "Accountant State")),
        "CountryCode": normalize_country_code(get_field(fields, "Accountant Country Region", default="91-India")),
        "PinCode": normalize_text(get_field(fields, "Accountant ZIP Code")),
        "Place": normalize_text(get_field(fields, "Place"), 35),
        "IpAddress": "IpAddress",
        "Date": report_date,
        "MembershipNo": normalize_membership(get_field(fields, "Accountant Membership Number")),
        "FirmRegNum": normalize_text(get_field(fields, "Accountant FRN"), 8),
    }


def get_client_database_row(client_name):
    try:
        df = load_clients()
        if df.empty or "Client Name" not in df.columns:
            return {}

        rows = df[df["Client Name"].astype(str) == str(client_name)]

        if len(rows) == 0:
            return {}

        return rows.iloc[0].to_dict()
    except Exception:
        return {}


# ---------------------------------------------------------
# PHASE 1 AUTO-POPULATION
# 3CA / 3CB basic report details + Form 3CD Clause 1 to 8
# Source: Client Management + Tax Audit Applicability
# ---------------------------------------------------------

def client_row_value(client_row, column, default=""):
    if not isinstance(client_row, dict):
        return default

    value = client_row.get(column, default)

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return str(value).strip()


def client_row_first(client_row, columns, default=""):
    for column in columns:
        value = client_row_value(client_row, column, "")
        if value:
            return value
    return default


def value_is_blank(value):
    return str(value).strip() in ["", "None", "nan", "NaT"]


def set_field_if_blank(fields, key, value):
    if value_is_blank(value):
        return

    if key not in fields or value_is_blank(fields.get(key, "")):
        fields[key] = value


def force_set_field(fields, key, value):
    if not value_is_blank(value):
        fields[key] = value


def build_client_full_address(client_row):
    parts = [
        client_row_value(client_row, "Flat / Door / Building"),
        client_row_value(client_row, "Road / Street / Block / Sector"),
        client_row_value(client_row, "Area / Locality"),
        client_row_value(client_row, "Post Office"),
        client_row_value(client_row, "District / City"),
        client_row_value(client_row, "State Code"),
        client_row_value(client_row, "PIN Code"),
    ]

    return ", ".join([part for part in parts if part])


def build_client_country_region(client_row):
    country_code = client_row_value(client_row, "Country Code", "91")

    if country_code in ["", "91", "91-India", "India"]:
        return "91-India"

    return country_code


def get_client_py_dates(client_row, ay):
    py_start = client_row_value(client_row, "Previous Year Start Date")
    py_end = client_row_value(client_row, "Previous Year End Date")

    if py_start and py_end:
        return py_start, py_end

    try:
        return get_financial_year_start_end_from_ay(ay)
    except Exception:
        return "", ""


def get_balance_sheet_year_from_py_end(py_end, ay):
    py_end = normalize_date_string(py_end, default="")

    if py_end:
        try:
            return str(pd.to_datetime(py_end).year)
        except Exception:
            pass

    return ay_to_schema_year(ay)


def count_branches(branch_details):
    branch_details = normalize_text(branch_details)

    if not branch_details:
        return "0"

    # If user entered a number, keep it.
    try:
        return str(int(float(branch_details.replace(",", ""))))
    except Exception:
        pass

    # Otherwise count non-empty lines / comma separated branch names.
    lines = [item.strip() for item in re.split(r"[\n,;]+", branch_details) if item.strip()]
    return str(len(lines)) if lines else "0"


def build_report_defaults_from_client_master(audit_form, client_name, ay, client_row):
    py_start, py_end = get_client_py_dates(client_row, ay)

    legal_name = client_row_first(
        client_row,
        ["Client Legal Name", "Last Name / Entity Name", "Client Name"],
        client_name,
    )

    first_name = client_row_value(client_row, "First Name")
    middle_name = client_row_value(client_row, "Middle Name")
    last_name = client_row_first(
        client_row,
        ["Last Name / Entity Name", "Client Legal Name", "Client Name"],
        client_name,
    )

    address_full = build_client_full_address(client_row)
    books_address = client_row_first(
        client_row,
        ["Books Head Office Address"],
        address_full,
    )

    branch_details = client_row_value(client_row, "Branch Details")
    audited_under_other_law = client_row_value(client_row, "Audited Under Other Law", "No")
    law_under_which_audited = client_row_value(client_row, "Law Under Which Audited")
    statutory_auditor = client_row_value(client_row, "Statutory Auditor / Firm Name")
    statutory_audit_date = client_row_value(client_row, "Statutory Audit Report Date")

    common = {
        "Assessee First Name": first_name,
        "Assessee Middle Name": middle_name,
        "Assessee Last Name": last_name or legal_name,
        "Type / Status of Assessee": client_row_value(client_row, "Status of Assessee"),
        "Assessee Country Region": build_client_country_region(client_row),
        "Assessee Flat Door Building": client_row_value(client_row, "Flat / Door / Building"),
        "Assessee Road Street Block Sector": client_row_value(client_row, "Road / Street / Block / Sector"),
        "Assessee Pincode": client_row_value(client_row, "PIN Code"),
        "Assessee Post Office": client_row_value(client_row, "Post Office"),
        "Assessee Area Locality": client_row_value(client_row, "Area / Locality"),
        "Assessee District": client_row_value(client_row, "District / City"),
        "Assessee State": client_row_value(client_row, "State Code"),
        "Assessee PAN": client_row_value(client_row, "PAN").upper(),
        "Assessee Aadhaar": client_row_value(client_row, "Aadhaar"),
        "Period Beginning From": py_start,
        "Period Ending On": py_end,
    }

    if audit_form == "Form 3CA-3CD":
        defaults = {
            **common,
            "Declaration Type": "I",
            "Statutory Audit Conducted By": "me",
            "Statutory Auditor Name": statutory_auditor,
            "Other Law Name": law_under_which_audited or "Companies Act, 2013",
            "Other Law Declaration Type": "I",
            "Audit Report Possessive": "my",
            "Statutory Audit Report Date": statutory_audit_date,
            "Audited Statement Type": "Profit and loss account",
            "Audited Balance Sheet Date": py_end,
        }
    elif audit_form == "Form 3CB-3CD":
        defaults = {
            **common,
            "Declaration Type": "I",
            "Balance Sheet Date": get_balance_sheet_year_from_py_end(py_end, ay),
            "Statement Type": "Profit and loss account",
            "Books Head Office Address": books_address,
            "Books Branches": count_branches(branch_details),
            "Profit Or Loss": "Profit",
        }
    else:
        defaults = common

    return defaults


def apply_report_form_defaults_from_client_master(report_data, audit_form, client_name, ay, overwrite=False):
    client_row = get_client_database_row(client_name)

    if not client_row:
        return report_data, False

    report_data.setdefault("report_form", {})
    report_data["report_form"].setdefault("fields", {})

    fields = report_data["report_form"].get("fields", {})

    defaults = build_report_defaults_from_client_master(
        audit_form=audit_form,
        client_name=client_name,
        ay=ay,
        client_row=client_row,
    )

    changed = False

    for key, value in defaults.items():
        before = fields.get(key, "")

        if overwrite:
            if not value_is_blank(value) and str(before) != str(value):
                fields[key] = value
                changed = True
        else:
            if (key not in fields or value_is_blank(fields.get(key, ""))) and not value_is_blank(value):
                fields[key] = value
                changed = True

    report_data["report_form"]["fields"] = fields

    return report_data, changed


def build_phase1_clause_auto_data(client_name, ay, client_row, applicability_data):
    py_start, py_end = get_client_py_dates(client_row, ay)

    client_legal_name = client_row_first(
        client_row,
        ["Client Legal Name", "Last Name / Entity Name", "Client Name"],
        client_name,
    )

    address_full = build_client_full_address(client_row)

    gstin = client_row_value(client_row, "GSTIN")
    indirect_flag = client_row_value(client_row, "Indirect Tax Applicable", "Yes" if gstin else "No")
    state_code = client_row_value(client_row, "GST State Code") or client_row_value(client_row, "State Code")

    section_ref = normalize_section_44ab_clause_code(
        applicability_data.get("section_reference", "")
    ) or normalize_section_44ab_clause_code(
        applicability_data.get("reason", "")
    )

    return {
        "1": {
            "fields": {
                "Name of the assessee": client_legal_name,
            },
            "remarks": "Auto-populated from Client Management.",
        },
        "2": {
            "fields": {
                "Address Line 1": client_row_value(client_row, "Flat / Door / Building"),
                "Address Line 2": client_row_value(client_row, "Road / Street / Block / Sector"),
                "Area / Locality": client_row_value(client_row, "Area / Locality"),
                "Post Office": client_row_value(client_row, "Post Office"),
                "City / Town / District": client_row_value(client_row, "District / City"),
                "State Code": client_row_value(client_row, "State Code"),
                "Country Code": client_row_value(client_row, "Country Code", "91"),
                "Pincode": client_row_value(client_row, "PIN Code"),
                "Full Address": address_full,
            },
            "remarks": "Auto-populated from Client Management address details.",
        },
        "3": {
            "fields": {
                "PAN": client_row_value(client_row, "PAN").upper(),
                "Aadhaar Number, if available": client_row_value(client_row, "Aadhaar"),
            },
            "remarks": "Auto-populated from Client Management PAN/Aadhaar details.",
        },
        "4": {
            "fields": {
                "Whether liable to pay indirect tax": indirect_flag,
                "Type of indirect tax": "GST" if gstin else "",
                "State Code": state_code,
                "Registration number / GSTIN": gstin,
                "Remarks": "Auto-populated from Client Management GST details.",
            },
            "remarks": "Auto-populated from Client Management GST/indirect tax details.",
        },
        "5": {
            "fields": {
                "Status of assessee": client_row_value(client_row, "Status of Assessee"),
            },
            "remarks": "Auto-populated from Client Management status of assessee.",
        },
        "6": {
            "fields": {
                "Previous year from date": py_start,
                "Previous year to date": py_end,
            },
            "remarks": "Auto-populated from Assessment Year / previous year dates.",
        },
        "7": {
            "fields": {
                "Assessment year": ay_to_full_string(ay),
            },
            "remarks": "Auto-populated from Client Management assessment year.",
        },
        "8": {
            "fields": {
                "Relevant clause of section 44AB": section_ref,
                "Section reference as per applicability module": applicability_data.get("section_reference", ""),
                "Reason for applicability": applicability_data.get("reason", ""),
                "Whether auto-filled from Tax Audit Applicability module": "Yes",
            },
            "remarks": "Auto-populated from Tax Audit Applicability module.",
        },
    }


def apply_phase1_3cd_clause_auto_population(report_data, client_name, ay, applicability_data, overwrite=True):
    client_row = get_client_database_row(client_name)

    if not client_row:
        return report_data, False

    report_data.setdefault("form_3cd", {})

    clause_data_map = build_phase1_clause_auto_data(
        client_name=client_name,
        ay=ay,
        client_row=client_row,
        applicability_data=applicability_data,
    )

    changed = False

    for clause_no, auto_data in clause_data_map.items():
        existing = report_data["form_3cd"].get(clause_no, {})
        existing_fields = existing.get("fields", {})

        if not isinstance(existing_fields, dict):
            existing_fields = {}

        auto_fields = auto_data.get("fields", {})

        for key, value in auto_fields.items():
            before = existing_fields.get(key, "")

            if overwrite:
                if str(before) != str(value):
                    existing_fields[key] = value
                    changed = True
            else:
                if (key not in existing_fields or value_is_blank(existing_fields.get(key, ""))) and not value_is_blank(value):
                    existing_fields[key] = value
                    changed = True

        current_status = existing.get("status", "Not Filled")
        new_status = "Filled"

        # If all values are blank, do not mark as filled.
        if not any(str(v).strip() for v in existing_fields.values()):
            new_status = current_status

        report_data["form_3cd"][clause_no] = {
            "title": get_clause_title(clause_no),
            "utility_sheet": get_clause_sheet(clause_no),
            "status": new_status,
            "remarks": auto_data.get("remarks", existing.get("remarks", "")),
            "fields": existing_fields,
            "blocks": existing.get("blocks", {}),
            "schema_based": existing.get("schema_based", False),
            "auto_populated_phase": "Phase 1 - Basic Details",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    return report_data, changed


def apply_phase1_auto_population(report_data, audit_form, client_name, ay, applicability_data, overwrite_report=False):
    report_data, report_changed = apply_report_form_defaults_from_client_master(
        report_data=report_data,
        audit_form=audit_form,
        client_name=client_name,
        ay=ay,
        overwrite=overwrite_report,
    )

    report_data, clause_changed = apply_phase1_3cd_clause_auto_population(
        report_data=report_data,
        client_name=client_name,
        ay=ay,
        applicability_data=applicability_data,
        overwrite=True,
    )

    return report_data, report_changed or clause_changed



def build_creation_info(fields):
    return {
        "SWVersionNo": "R2",
        "SWCreatedBy": "TAAS",
        "JSONCreatedBy": "TAAS",
        "JSONCreationDate": date.today().strftime("%Y-%m-%d"),
        "IntermediaryCity": normalize_text(get_field(fields, "Place", default="Hyderabad"), 50),
    }


def build_form_details(audit_form, ay):
    form_name = "FORM3CA" if audit_form == "Form 3CA-3CD" else "FORM3CB"

    if audit_form == "Form 3CA-3CD":
        description = (
            "Audit report under section 44AB of the Income-tax Act, 1961, "
            "in a case where the accounts of the business or profession of a person have been audited under any other law"
        )
    else:
        description = (
            "Audit report under section 44AB of the Income-tax Act, 1961, "
            "in a case of a person referred to in clause (b) of sub-rule (1) of rule 6G"
        )

    return {
        "FormName": form_name,
        "Description": description,
        "AssessmentYear": ay_to_schema_year(ay),
        "SchemaVer": "Ver2.5",
        "FormVer": "1.0",
    }


def build_observations_array(text_value):
    text_value = normalize_text(text_value, 1000)

    if not text_value:
        return []

    return [
        {
            "ObservationsCode": "17",
            "ObservationsVal": text_value,
        }
    ]


def build_declaration_3ca(fields, client_name, ay):
    assessee_name = build_assessee_name(fields, client_name)
    address_detail = build_address_detail(fields, "Assessee")

    law_value = normalize_text(get_field(fields, "Other Law Name", default="Companies Act, 2013")).lower()
    law_code = LAW_CODE_MAP_3CA.get(law_value, "99")

    start_date, end_date = get_financial_year_start_end_from_ay(ay)

    audit_start_date = normalize_date_string(
        get_field(fields, "Period Beginning From"),
        default=start_date
    )
    audit_end_date = normalize_date_string(
        get_field(fields, "Period Ending On"),
        default=end_date
    )

    balance_sheet_date = normalize_date_string(
        get_field(fields, "Audited Balance Sheet Date"),
        default=end_date
    )

    audit_report_date = normalize_date_string(
        get_field(fields, "Statutory Audit Report Date"),
        default=date.today().strftime("%Y-%m-%d")
    )

    signing_date = normalize_date_string(
        get_field(fields, "Date of signing Tax Audit Report"),
        default=date.today().strftime("%Y-%m-%d")
    )

    point1 = {
        "I_We1": normalize_text(get_field(fields, "Declaration Type", default="I")),
        "AssesseeName": assessee_name,
        "AddressDetail": address_detail,
        "PAN": normalize_pan(get_field(fields, "Assessee PAN")),
        "AadhaarCardNo": normalize_aadhaar(get_field(fields, "Assessee Aadhaar")),
        "Me_Us_Ms": normalize_text(get_field(fields, "Statutory Audit Conducted By", default="me")).title(),
        "CA_FirmName": normalize_text(get_field(fields, "Statutory Auditor Name"), 125),
        "Act": law_code,
        "Other_Act": normalize_text(get_field(fields, "Other Law Name"), 125) if law_code == "99" else "",
        "I_We2": normalize_text(get_field(fields, "Other Law Declaration Type", default="I")),
        "My_Our_Their": normalize_text(get_field(fields, "Audit Report Possessive", default="my")).title(),
        "AuditDated": audit_report_date,
        "DateofsigningTaxAuditReport": signing_date,
        "PointA": {
            "TypeOfAccount": normalize_text(get_field(fields, "Audited Statement Type", default="Profit and loss account")),
            "AuditStartDate": audit_start_date,
            "AuditEndDate": audit_end_date,
        },
        "AuditYearDate": balance_sheet_date,
        "PointC": normalize_text(get_field(fields, "Audited Statement Type", default="Profit and loss account")),
    }

    obs_text = get_field(fields, "Form 3CD Observations Qualifications", default="")

    point3 = {
        "My_Our1": "My",
        "My_Our2": "My",
        "Me_Us": "Me",
        "Observations": build_observations_array(obs_text),
    }

    return {
        "Point1": point1,
        "Point3": point3,
    }


def build_declaration_3cb(fields, client_name, ay):
    assessee_name = build_assessee_name(fields, client_name)
    address_detail = build_address_detail(fields, "Assessee")

    start_date, end_date = get_financial_year_start_end_from_ay(ay)

    period_start = normalize_date_string(
        get_field(fields, "Period Beginning From"),
        default=start_date
    )
    period_end = normalize_date_string(
        get_field(fields, "Period Ending On"),
        default=end_date
    )

    signing_date = normalize_date_string(
        get_field(fields, "Date of signing Tax Audit Report"),
        default=date.today().strftime("%Y-%m-%d")
    )

    balance_year_value = get_field(fields, "Balance Sheet Date", default=ay_to_schema_year(ay))

    try:
        balance_year = int(str(balance_year_value).strip()[:4])
    except Exception:
        balance_year = int(ay_to_schema_year(ay))

    statement_type = normalize_text(get_field(fields, "Statement Type", default="Profit and loss account"))
    declaration_type = normalize_text(get_field(fields, "Declaration Type", default="I"))

    branches_value = get_field(fields, "Books Branches", default="0")

    try:
        number_of_branches = int(float(str(branches_value).replace(",", "").strip() or 0))
    except Exception:
        number_of_branches = 0

    observations_text = get_field(fields, "Observations Comments Discrepancies", default="")
    form3cd_obs_text = get_field(fields, "Form 3CD Observations Qualifications", default="")
    profit_loss = normalize_text(get_field(fields, "Profit Or Loss", default="Profit"))

    return {
        "Point1": {
            "I_We": declaration_type,
            "DateofsigningTaxAuditReport": signing_date,
            "Year": balance_year,
            "TypeOfAccount": statement_type,
            "StartDate": period_start,
            "EndDate": period_end,
            "AssesseeName": assessee_name,
            "AddressDetail": address_detail,
            "AadhaarCardNo": normalize_aadhaar(get_field(fields, "Assessee Aadhaar")),
            "PAN": normalize_pan(get_field(fields, "Assessee PAN")),
        },
        "Point2": {
            "I_We": declaration_type,
            "TypeOfAccount": statement_type,
            "HeadOfficeLocation": normalize_text(get_field(fields, "Books Head Office Address"), 150),
            "NumberOfBrances": number_of_branches,
        },
        "Point3": {
            "PointA": {
                "I_We": declaration_type,
                "OCDI": "Observations" if observations_text else "",
                "OCDI_Description": normalize_text(observations_text, 1000),
            },
            "PointB_A": {
                "I_We": declaration_type,
                "My_Our": "My" if declaration_type == "I" else "Our",
            },
            "PointB_B": {
                "My_Our1": "My" if declaration_type == "I" else "Our",
                "My_Our2": "My" if declaration_type == "I" else "Our",
            },
            "PointB_C": {
                "My_Our1": "My" if declaration_type == "I" else "Our",
                "My_Our2": "My" if declaration_type == "I" else "Our",
                "Me_Us": "Me" if declaration_type == "I" else "Us",
                "PointFirst": str(balance_year),
                "PointSecond": {
                    "typeOfAccount": statement_type,
                    "PLSD": profit_loss,
                },
            },
        },
        "Point5": {
            "My_Our1": "My" if declaration_type == "I" else "Our",
            "My_Our2": "My" if declaration_type == "I" else "Our",
            "Me_Us": "Me" if declaration_type == "I" else "Us",
            "Observations": build_observations_array(form3cd_obs_text),
        },
    }


def merge_non_empty(base, updates):
    for key, value in updates.items():
        if isinstance(value, dict):
            base.setdefault(key, {})
            if isinstance(base[key], dict):
                merge_non_empty(base[key], value)
            else:
                base[key] = value
        elif isinstance(value, list):
            if value:
                base[key] = value
        else:
            if str(value).strip() not in ["", "None", "nan", "NaT"]:
                base[key] = value
    return base


def set_by_schema_key(target, schema_key, data):
    if not schema_key or schema_key.startswith("TAAS_"):
        return

    if data in [None, {}, []]:
        return

    parts = schema_key.split(".")
    root_key = parts[0]

    if root_key == "PartA":
        current = target.setdefault("PartA", {})

        if len(parts) == 1:
            if isinstance(data, dict):
                merge_non_empty(current, data)
            return

        for part in parts[1:-1]:
            current = current.setdefault(part, {})

        last_key = parts[-1]
        current[last_key] = data
        return

    current = target

    for part in parts[:-1]:
        current = current.setdefault(part, {})

    current[parts[-1]] = data


def clean_utility_value(value):
    if value is None:
        return None

    if isinstance(value, dict):
        cleaned = {}

        for key, item in value.items():
            cleaned_item = clean_utility_value(item)

            if cleaned_item not in [None, "", [], {}]:
                cleaned[key] = cleaned_item

        return cleaned

    if isinstance(value, list):
        cleaned_list = []

        for item in value:
            cleaned_item = clean_utility_value(item)

            if cleaned_item not in [None, "", [], {}]:
                cleaned_list.append(cleaned_item)

        return cleaned_list

    if isinstance(value, float):
        if value.is_integer():
            return int(value)

        return value

    if isinstance(value, str):
        value = value.strip()

        if value in ["", "None", "nan", "NaT"]:
            return ""

        return value

    return value


def build_part_a_defaults(fields, client_name, ay, client_row):
    start_date, end_date = get_financial_year_start_end_from_ay(ay)

    assessee_pan = normalize_pan(
        get_field(fields, "Assessee PAN", default=client_row.get("PAN", ""))
    )

    aadhaar = normalize_aadhaar(get_field(fields, "Assessee Aadhaar"))

    status_value = get_field(fields, "Type / Status of Assessee", default="")
    status_code = STATUS_CODE_MAP.get(str(status_value).strip().lower(), "")

    part_a = {
        "AssesseeName": build_assessee_name(fields, client_name),
        "AddressDetail": build_address_detail(fields, "Assessee"),
        "PAN": assessee_pan,
        "IndirectTaxFlag": "Y" if str(client_row.get("GSTIN", "")).strip() else "N",
        "Status": status_code,
        "PartAStartDate": start_date,
        "PartAEndDate": end_date,
        "AssessmentYear": ay_to_full_string(ay),
    }

    if aadhaar:
        part_a["AadhaarCardNo"] = aadhaar

    if str(client_row.get("GSTIN", "")).strip():
        part_a["Form3cdIndirectTax"] = [
            {
                "IndirectTaxType": "GST",
                "RegNo": str(client_row.get("GSTIN", "")).strip(),
            }
        ]

    return part_a


def build_form3cd_flags(inner_data):
    flags = {
        "ChngMethodOfAcc": "N",
        "ChngShareSec79": "X",
        "IncomeCluaseixofsubsection2": "N",
        "IncomeCluasexofsubsection2": "N",
        "FurnishStatement": "N",
        "SubSec2Sec286": "D",
    }

    optional_flag_defaults = {
        "ChangeInPartner": "N",
        "ChangeNaturBuisnes": "N",
        "BookOfAcnt": "N",
        "PrftLoassAcnt": "N",
        "Sec145": "N",
        "Sec145A": "N",
        "Sec40A3": "N",
        "Sec40A3A": "N",
        "SalesTax": "N",
        "VATAcnt": "N",
        "VATPY": "N",
        "Section69D": "N",
        "SectionDed": "N",
        "ChapXVIIFlag": "N",
        "TaxPrescTime": "N",
        "Sec201_1A_206_C7": "X",
        "SharesOfMem": "N",
        "Form3cdSec562viiaFlag": "X",
        "Form3cdSec562viibFlag": "X",
        "TransferPriceSection92CE": "N",
        "IncurredExpenditure": "N",
        "ImpermissibleSec96": "N",
        "Section36BFlag": "N",
        "SubClauseeofClause22": "N",
    }

    flags.update(optional_flag_defaults)

    # Basic auto-detection from exported data.
    key_to_flag = {
        "Form3cdChangeInPartners": "ChangeInPartner",
        "F3cdFirmAopDtlChangeInNature": "ChangeNaturBuisnes",
        "Form3cdBooksOfAccLst": "BookOfAcnt",
        "Form3cdProfGainsPresum": "PrftLoassAcnt",
        "Form3cdChngMethAccVal": "ChngMethodOfAcc",
        "Form3cdChngMethAccValChange": "Sec145",
        "MethodValCS": "Sec145A",
        "Form3cdIncomeUnderSec40A_3": "Sec40A3",
        "ExpendSec40A_3": "Sec40A3A",
        "Form3cdSec69d": "Section69D",
        "Form3cdChapVIaChapIII": "SectionDed",
        "Form3cdChapXVII": "ChapXVIIFlag",
        "Form3cdTaxDedCollect": "TaxPrescTime",
        "Form3cdSec2011A206C7": "Sec201_1A_206_C7",
        "Form3cdSec562viia": "Form3cdSec562viiaFlag",
        "Form3cdSec562viib": "Form3cdSec562viibFlag",
        "Form3cdSec29IncOtherSourcesAb": "IncomeCluaseixofsubsection2",
        "Form3cdSec29IncOtherSourcesBb": "IncomeCluasexofsubsection2",
        "Form3cdSec92CE": "TransferPriceSection92CE",
        "Form3cdIncurredExpenditure": "IncurredExpenditure",
        "Form3cdImpermissibleSec96": "ImpermissibleSec96",
        "Form3cd36BRecievedAmt": "Section36BFlag",
        "Form3cdFurnishStatemnt": "FurnishStatement",
        "Form3cdFurnishAltReportSec286": "SubSec2Sec286",
    }

    for data_key, flag_key in key_to_flag.items():
        if data_key in inner_data and inner_data.get(data_key) not in [None, {}, []]:
            if flag_key in ["ChngShareSec79", "Sec201_1A_206_C7", "Form3cdSec562viiaFlag", "Form3cdSec562viibFlag"]:
                flags[flag_key] = "Y"
            elif flag_key == "SubSec2Sec286":
                flags[flag_key] = "Y"
            else:
                flags[flag_key] = "Y"

    if "Form3cdFlags" in inner_data and isinstance(inner_data.get("Form3cdFlags"), dict):
        merge_non_empty(flags, inner_data["Form3cdFlags"])

    return flags


def apply_saved_3cd_blocks_to_utility_json(inner_data, report_data):
    form_3cd = report_data.get("form_3cd", {}) or {}

    for clause_no, clause_data in form_3cd.items():
        blocks = clause_data.get("blocks", {}) or {}

        for block_name, block_data in blocks.items():
            schema_key = block_data.get("schema_key", "")
            block_type = block_data.get("type", "")
            data = block_data.get("data", [] if block_type == "table" else {})

            data = clean_utility_value(data)

            if data in [None, "", [], {}]:
                continue

            set_by_schema_key(inner_data, schema_key, data)

    # Legacy Clause 8 linkage support.
    clause_8 = form_3cd.get("8", {})
    legacy_fields = clause_8.get("fields", {})

    if legacy_fields and "PartA" in inner_data:
        clause_value = legacy_fields.get("Relevant clause of section 44AB", "")
        clause_value = normalize_section_44ab_clause_code(clause_value)

        if clause_value:
            inner_data["PartA"]["Clause"] = [{"ClauseNo": clause_value}]


def normalize_section_44ab_clause_code(value):
    value = normalize_text(value)

    value_upper = value.upper().replace(" ", "")

    mapping = {
        "44AB(A)": "44ABa",
        "44ABA": "44ABa",
        "44AB(A)-PROVISO": "44ABAA",
        "44ABAA": "44ABAA",
        "44AB(B)": "44ABb",
        "44ABB": "44ABb",
        "44AB(C)": "44ABci",
        "44ABC": "44ABci",
        "44AB(D)": "44ABd",
        "44ABD": "44ABd",
        "44AB(E)": "44ABe",
        "44ABE": "44ABe",
        "44AB3": "44AB3",
        "OTHERLAWAUDIT": "44AB3",
    }

    for key, mapped in mapping.items():
        if key in value_upper:
            return mapped

    allowed = ["44ABa", "44ABAA", "44ABb", "44ABci", "44ABcii", "44ABciii", "44ABd", "44ABe", "44AB3"]

    if value in allowed:
        return value

    return ""


def build_utility_json_payload(client_name, ay, report_data):
    audit_form = report_data.get("meta", {}).get("audit_form", "Not Applicable")

    if not is_valid_tax_audit_form(audit_form):
        raise ValueError("Invalid or missing audit form. Complete Tax Audit Applicability first.")

    fields = get_report_fields(report_data)
    client_row = get_client_database_row(client_name)

    root_key, inner_root_key = get_tax_audit_root_keys(audit_form)
    form_code = get_tax_audit_form_code(audit_form)

    inner_data = {
        "CreationInfo": build_creation_info(fields),
        "Form_Details": build_form_details(audit_form, ay),
        "PartA": build_part_a_defaults(fields, client_name, ay, client_row),
        "OtherInformation1": build_accountant_other_info(fields),
    }

    if audit_form == "Form 3CA-3CD":
        inner_data["Declaration"] = build_declaration_3ca(fields, client_name, ay)
    else:
        inner_data["Declaration"] = build_declaration_3cb(fields, client_name, ay)

    apply_saved_3cd_blocks_to_utility_json(inner_data, report_data)

    inner_data["Form3cdFlags"] = build_form3cd_flags(inner_data)

    inner_data = clean_utility_value(inner_data)

    payload = {
        "metadata": {
            "filingType": "O",
            "refYearType": "AY",
            "financialQtr": 0,
            "refYear": int(ay_to_schema_year(ay)),
            "formName": f"F{form_code}-3CD",
        },
        "data": {
            root_key: {
                inner_root_key: inner_data
            }
        }
    }

    return payload


def collect_missing_utility_fields(payload, audit_form):
    missing = []

    try:
        root_key, inner_root_key = get_tax_audit_root_keys(audit_form)
        inner = payload.get("data", {}).get(root_key, {}).get(inner_root_key, {})

        required_top = ["CreationInfo", "Form_Details", "Declaration", "PartA", "Form3cdFlags", "OtherInformation1"]

        for key in required_top:
            if key not in inner or inner.get(key) in [{}, [], "", None]:
                missing.append(key)

        part_a = inner.get("PartA", {}) or {}

        for key in ["AssesseeName", "AddressDetail", "PAN", "IndirectTaxFlag", "Status", "PartAStartDate", "PartAEndDate", "AssessmentYear"]:
            if part_a.get(key) in ["", None, {}, []]:
                missing.append(f"PartA.{key}")

        address = part_a.get("AddressDetail", {}) or {}

        for key in ["AddrDetail1", "CityOrTownOrDistrict", "StateCode", "CountryCode", "PinCode"]:
            if address.get(key) in ["", None, {}, []]:
                missing.append(f"PartA.AddressDetail.{key}")

        assessee = part_a.get("AssesseeName", {}) or {}

        if not assessee.get("LastName"):
            missing.append("PartA.AssesseeName.LastName")

        other = inner.get("OtherInformation1", {}) or {}

        for key in ["LastName", "AddrDetail1", "CityOrTownOrDistrict", "StateCode", "PinCode", "CountryCode", "Place", "Date", "MembershipNo"]:
            if other.get(key) in ["", None, {}, []]:
                missing.append(f"OtherInformation1.{key}")

        declaration = inner.get("Declaration", {}) or {}

        if audit_form == "Form 3CA-3CD":
            point1 = declaration.get("Point1", {}) or {}
            for key in ["I_We1", "AssesseeName", "AddressDetail", "Me_Us_Ms", "CA_FirmName", "Act", "I_We2", "My_Our_Their", "AuditDated", "DateofsigningTaxAuditReport", "PointA", "AuditYearDate", "PointC"]:
                if point1.get(key) in ["", None, {}, []]:
                    missing.append(f"Declaration.Point1.{key}")
        else:
            point1 = declaration.get("Point1", {}) or {}
            for key in ["I_We", "DateofsigningTaxAuditReport", "Year", "TypeOfAccount", "StartDate", "EndDate", "AssesseeName", "AddressDetail", "PAN"]:
                if point1.get(key) in ["", None, {}, []]:
                    missing.append(f"Declaration.Point1.{key}")

            point2 = declaration.get("Point2", {}) or {}
            for key in ["I_We", "TypeOfAccount", "HeadOfficeLocation", "NumberOfBrances"]:
                if point2.get(key) in ["", None, {}, []]:
                    missing.append(f"Declaration.Point2.{key}")

    except Exception as e:
        missing.append(f"Validation check failed: {e}")

    return sorted(set(missing))


def export_utility_compatible_json(client_name, ay, report_data):
    folder = get_tax_report_folder(client_name, ay)
    audit_form = report_data.get("meta", {}).get("audit_form", "Not Applicable")
    form_code = get_tax_audit_form_code(audit_form)

    payload = build_utility_json_payload(client_name, ay, report_data)

    json_path = f"{folder}/income_tax_utility_{form_code}_3CD.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=4, ensure_ascii=False)

    missing_fields = collect_missing_utility_fields(payload, audit_form)

    validation_path = f"{folder}/income_tax_utility_{form_code}_3CD_validation_summary.txt"

    with open(validation_path, "w", encoding="utf-8") as file:
        file.write("TAAS Income-tax Utility JSON Export Validation Summary\n")
        file.write("=" * 58 + "\n\n")
        file.write(f"Client Name: {client_name}\n")
        file.write(f"Assessment Year: {ay}\n")
        file.write(f"Audit Form: {audit_form}\n")
        file.write(f"JSON File: {json_path}\n\n")

        if missing_fields:
            file.write("Pending / Missing Required Values:\n")
            for item in missing_fields:
                file.write(f"- {item}\n")
        else:
            file.write("No major required-field gaps detected by TAAS basic validation.\n")

        file.write("\nImportant:\n")
        file.write("This is a schema-structured utility export generated from TAAS saved data.\n")
        file.write("Final acceptance should still be tested in the Income-tax offline/online utility.\n")

    return json_path, validation_path, missing_fields


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

    audit_form = report_data.get("meta", {}).get("audit_form", "Not Applicable")

    report_data, phase1_changed = apply_phase1_auto_population(
        report_data=report_data,
        audit_form=audit_form,
        client_name=selected_client,
        ay=selected_ay,
        applicability_data=applicability_data,
        overwrite_report=False,
    )

    save_tax_report(selected_client, selected_ay, report_data)

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

    refresh_col1, refresh_col2 = st.columns([2, 8])

    with refresh_col1:
        if st.button("🔄 Refresh from Client Master", use_container_width=True):
            report_data, _ = apply_phase1_auto_population(
                report_data=report_data,
                audit_form=audit_form,
                client_name=selected_client,
                ay=selected_ay,
                applicability_data=applicability_data,
                overwrite_report=True,
            )
            save_tax_report(selected_client, selected_ay, report_data)
            st.success("✅ 3CA/3CB basic details and 3CD Clause 1 to 8 refreshed from Client Management.")
            st.rerun()

    with refresh_col2:
        st.caption("Auto-fill source: Client Management master data + Tax Audit Applicability. Manual entries are preserved unless you click refresh.")

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

    export_col1, export_col2, export_col3 = st.columns(3)

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

    with export_col3:
        if st.button("🏛️ Export Income-tax Utility JSON", use_container_width=True):
            try:
                utility_json_path, validation_path, missing_fields = export_utility_compatible_json(
                    selected_client,
                    selected_ay,
                    latest_report_data
                )

                st.success(f"✅ Utility JSON exported successfully: {utility_json_path}")
                st.info(f"Validation summary saved: {validation_path}")

                if missing_fields:
                    with st.expander("View pending required values"):
                        for item in missing_fields:
                            st.write(f"- {item}")
                else:
                    st.success("No major required-field gaps detected by TAAS basic validation.")

            except Exception as e:
                st.error(f"Utility JSON export failed: {e}")

    st.caption(
        "This version supports schema-aware Form 3CD data entry and Income-tax utility-style JSON export. "
        "Final portal/offline-utility acceptance should be tested with completed mandatory fields."
    )
