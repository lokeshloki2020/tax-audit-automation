import os
import json
import re
import pandas as pd
import streamlit as st

from utils.common import load_clients


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def safe_float(value):
    try:
        return float(str(value).replace(",", "").strip())
    except:
        return 0.0


def format_indian_number(value):
    try:
        value = safe_float(value)

        if value == 0:
            return ""

        value = int(round(value, 0))
        s = str(value)

        if len(s) <= 3:
            return s

        last_three = s[-3:]
        remaining = s[:-3]

        parts = []

        while len(remaining) > 2:
            parts.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        if remaining:
            parts.insert(0, remaining)

        return ",".join(parts) + "," + last_three

    except:
        return ""


def format_indian_number_or_zero(value):
    formatted = format_indian_number(value)
    return formatted if formatted else "0"


def format_amount_session_state(key):
    if key in st.session_state:
        raw_value = st.session_state[key]

        if raw_value:
            numeric_value = safe_float(raw_value)
            st.session_state[key] = format_indian_number(numeric_value)


def amount_input(label, key, placeholder="Example: 2,50,00,000"):
    return st.text_input(
        label,
        key=key,
        placeholder=placeholder,
        on_change=format_amount_session_state,
        args=(key,)
    )


def safe_key(value):
    return re.sub(r"[^A-Za-z0-9_]", "_", str(value))


def get_index(options, value):
    if value in options:
        return options.index(value)
    return 0


def get_applicability_folder(client_name, ay):
    folder = f"clients/{client_name}/AY {ay}/Tax Audit Applicability"
    os.makedirs(folder, exist_ok=True)
    return folder


def get_draft_path(client_name, ay):
    return f"{get_applicability_folder(client_name, ay)}/tax_audit_applicability_draft.json"


def get_result_json_path(client_name, ay):
    return f"{get_applicability_folder(client_name, ay)}/tax_audit_applicability_result.json"


def get_result_excel_path(client_name, ay):
    return f"{get_applicability_folder(client_name, ay)}/tax_audit_applicability_result.xlsx"


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            return {}

    return {}


def save_draft(client_name, ay, draft_data):
    draft_path = get_draft_path(client_name, ay)
    save_json(draft_path, draft_data)
    return draft_path


def load_saved_applicability_data(client_name, ay):
    draft_data = load_json(get_draft_path(client_name, ay))

    if draft_data:
        return draft_data

    result_data = load_json(get_result_json_path(client_name, ay))

    if result_data:
        return result_data

    return {}


def save_applicability_outputs(client_name, ay, output_data):
    excel_path = get_result_excel_path(client_name, ay)
    json_path = get_result_json_path(client_name, ay)

    output_df = pd.DataFrame([output_data])
    output_df.to_excel(excel_path, index=False)

    save_json(json_path, output_data)

    return excel_path, json_path


def get_active_client_from_global_selection():
    selected_client = st.session_state.get("global_selected_client")
    selected_ay = st.session_state.get("global_selected_ay")

    if selected_client and selected_ay:
        return selected_client, selected_ay

    return None, None

# ---------------------------------------------------------
# DISPLAY LABELS
# ---------------------------------------------------------

PRESUMPTIVE_SECTION_OPTIONS = [
    "Not Applicable - Normal Business / Profession",
    "44AD - Presumptive Taxation for Eligible Business",
    "44ADA - Presumptive Taxation for Specified Profession",
    "44AE - Presumptive Taxation for Goods Carriage Business"
]


SECTION_44AD_4_OPTIONS = [
    "No - Section 44AD(4) not applicable",
    "Yes - Section 44AD(4) applicable: opted out after earlier presumptive taxation"
]


def get_presumptive_code(display_value):
    if str(display_value).startswith("44AD -"):
        return "44AD"

    if str(display_value).startswith("44ADA -"):
        return "44ADA"

    if str(display_value).startswith("44AE -"):
        return "44AE"

    return "Not Applicable"


def get_presumptive_display(code_or_display):
    value = str(code_or_display)

    for option in PRESUMPTIVE_SECTION_OPTIONS:
        if value == option:
            return option

    if value == "44AD":
        return "44AD - Presumptive Taxation for Eligible Business"

    if value == "44ADA":
        return "44ADA - Presumptive Taxation for Specified Profession"

    if value == "44AE":
        return "44AE - Presumptive Taxation for Goods Carriage Business"

    return "Not Applicable - Normal Business / Profession"


def get_44ad_4_code(display_value):
    if str(display_value).startswith("Yes"):
        return "Yes"
    return "No"


def get_44ad_4_display(value):
    if str(value) == "Yes":
        return "Yes - Section 44AD(4) applicable: opted out after earlier presumptive taxation"

    if str(value) == "No":
        return "No - Section 44AD(4) not applicable"

    if str(value).startswith("Yes"):
        return "Yes - Section 44AD(4) applicable: opted out after earlier presumptive taxation"

    return "No - Section 44AD(4) not applicable"


def load_saved_data_into_session(saved_data, keys):
    st.session_state[keys["entity_type"]] = saved_data.get("Entity Type", "Individual")
    st.session_state[keys["activity_type"]] = saved_data.get("Activity Type", "Business")

    saved_presumptive = saved_data.get("Presumptive Section", "Not Applicable")
    st.session_state[keys["presumptive_section"]] = get_presumptive_display(saved_presumptive)

    st.session_state[keys["business_nature"]] = saved_data.get("Business Nature", "Eligible Business")
    st.session_state[keys["is_resident"]] = saved_data.get("Is Resident", "Yes")

    saved_44ad_4 = saved_data.get("Section 44AD(4) Applicable", "No")
    st.session_state[keys["section_44ad_4_applicable"]] = get_44ad_4_display(saved_44ad_4)

    st.session_state[keys["turnover"]] = saved_data.get("Turnover / Gross Receipts Formatted", "")
    st.session_state[keys["cash_receipts"]] = saved_data.get("Cash Receipts Amount Formatted", "")
    st.session_state[keys["cash_payments"]] = saved_data.get("Cash Payments Amount Formatted", "")
    st.session_state[keys["profit_amount"]] = saved_data.get("Declared Profit Amount Formatted", "")

    st.session_state[keys["presumptive_profit_44ae"]] = saved_data.get("Presumptive Profit 44AE Formatted", "")

    st.session_state[keys["total_income"]] = saved_data.get("Total Income Above Basic Exemption", "Yes")
    st.session_state[keys["other_law_audit"]] = saved_data.get("Accounts Audited Under Other Law", "No")


def initialise_blank_session(keys):
    defaults = {
        keys["entity_type"]: "Individual",
        keys["activity_type"]: "Business",
        keys["presumptive_section"]: "Not Applicable - Normal Business / Profession",

        keys["business_nature"]: "Eligible Business",
        keys["is_resident"]: "Yes",
        keys["section_44ad_4_applicable"]: "No - Section 44AD(4) not applicable",

        keys["turnover"]: "",
        keys["cash_receipts"]: "",
        keys["cash_payments"]: "",
        keys["profit_amount"]: "",
        keys["presumptive_profit_44ae"]: "",

        keys["total_income"]: "Yes",
        keys["other_law_audit"]: "No",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------
# MAIN UI
# ---------------------------------------------------------

def show_tax_audit_applicability():
    st.subheader("🧭 Tax Audit Applicability & Filing Basis")

    selected_client, selected_ay = get_active_client_from_global_selection()

    if not selected_client or not selected_ay:
        st.info("Please add/select a client first.")
        return

    saved_data = load_saved_applicability_data(selected_client, selected_ay)

    context_key = f"{safe_key(selected_client)}_{safe_key(selected_ay)}"

    keys = {
        "entity_type": f"taa_entity_type_{context_key}",
        "activity_type": f"taa_activity_type_{context_key}",
        "presumptive_section": f"taa_presumptive_section_{context_key}",

        "business_nature": f"taa_business_nature_{context_key}",
        "is_resident": f"taa_is_resident_{context_key}",
        "section_44ad_4_applicable": f"taa_section_44ad_4_{context_key}",

        "turnover": f"taa_turnover_input_{context_key}",
        "cash_receipts": f"taa_cash_receipts_input_{context_key}",
        "cash_payments": f"taa_cash_payments_input_{context_key}",
        "profit_amount": f"taa_profit_amount_input_{context_key}",
        "presumptive_profit_44ae": f"taa_presumptive_profit_44ae_{context_key}",

        "total_income": f"taa_total_income_{context_key}",
        "other_law_audit": f"taa_other_law_audit_{context_key}",
        "loaded_marker": f"taa_loaded_marker_{context_key}",
    }

    initialise_blank_session(keys)

    # Auto-load saved data silently. No message shown.
    if saved_data and not st.session_state.get(keys["loaded_marker"], False):
        load_saved_data_into_session(saved_data, keys)
        st.session_state[keys["loaded_marker"]] = True

    st.divider()

    # ---------------------------------------------------------
    # BASIC DETAILS
    # ---------------------------------------------------------

    entity_options = [
        "Individual",
        "HUF",
        "Partnership Firm",
        "LLP",
        "Company",
        "AOP/BOI",
        "Other"
    ]

    activity_options = [
        "Business",
        "Profession",
        "Both Business and Profession"
    ]

    business_nature_options = [
        "Eligible Business",
        "Commission / Brokerage",
        "Agency Business",
        "Goods Carriage Business",
        "Specified Profession",
        "Other Ineligible Business"
    ]

    yes_no_options = ["Yes", "No"]

    c1, c2, c3 = st.columns(3)

    with c1:
        entity_type = st.selectbox(
            "Type / Status of Assessee",
            entity_options,
            index=get_index(entity_options, st.session_state.get(keys["entity_type"], "Individual")),
            key=keys["entity_type"]
        )

    with c2:
        activity_type = st.selectbox(
            "Nature of Activity",
            activity_options,
            index=get_index(activity_options, st.session_state.get(keys["activity_type"], "Business")),
            key=keys["activity_type"]
        )

    with c3:
        presumptive_section_display = st.selectbox(
            "Presumptive Taxation Section",
            PRESUMPTIVE_SECTION_OPTIONS,
            index=get_index(
                PRESUMPTIVE_SECTION_OPTIONS,
                st.session_state.get(
                    keys["presumptive_section"],
                    "Not Applicable - Normal Business / Profession"
                )
            ),
            key=keys["presumptive_section"]
        )

    presumptive_section = get_presumptive_code(presumptive_section_display)

    c4, c5, c6 = st.columns(3)

    with c4:
        is_resident = st.selectbox(
            "Is the assessee Resident?",
            yes_no_options,
            index=get_index(yes_no_options, st.session_state.get(keys["is_resident"], "Yes")),
            key=keys["is_resident"]
        )

    with c5:
        business_nature = st.selectbox(
            "Business / Income Nature",
            business_nature_options,
            index=get_index(business_nature_options, st.session_state.get(keys["business_nature"], "Eligible Business")),
            key=keys["business_nature"]
        )

    with c6:
        section_44ad_4_display = st.selectbox(
            "Section 44AD(4) - Opting out of presumptive taxation after earlier opting in",
            SECTION_44AD_4_OPTIONS,
            index=get_index(
                SECTION_44AD_4_OPTIONS,
                st.session_state.get(
                    keys["section_44ad_4_applicable"],
                    "No - Section 44AD(4) not applicable"
                )
            ),
            key=keys["section_44ad_4_applicable"],
            help="Select Yes where the assessee opted out of Section 44AD after earlier opting in and the lock-in condition is triggered."
        )

    section_44ad_4_applicable = get_44ad_4_code(section_44ad_4_display)

    st.divider()

    # ---------------------------------------------------------
    # AMOUNT DETAILS
    # ---------------------------------------------------------

    turnover_input = amount_input(
        "Total Turnover / Gross Receipts",
        key=keys["turnover"],
        placeholder="Example: 2,50,00,000"
    )

    turnover = safe_float(turnover_input)

    col1, col2 = st.columns(2)

    with col1:
        cash_receipts_input = amount_input(
            "Cash Receipts / Cash Turnover Amount",
            key=keys["cash_receipts"],
            placeholder="Example: 5,00,000"
        )

    cash_receipts = safe_float(cash_receipts_input)
    cash_receipts_percent = round((cash_receipts / turnover) * 100, 2) if turnover > 0 else 0

    digital_turnover = max(turnover - cash_receipts, 0)

    with col2:
        st.metric("Cash Receipts Percentage", f"{cash_receipts_percent}%")

        if presumptive_section == "44AD":
            st.caption(f"Digital / Banking Turnover auto-calculated: ₹{format_indian_number_or_zero(digital_turnover)}")
        else:
            st.caption("Digital turnover calculation is used only for Section 44AD.")

    col3, col4 = st.columns(2)

    with col3:
        cash_payments_input = amount_input(
            "Cash Payments Amount",
            key=keys["cash_payments"],
            placeholder="Example: 3,00,000"
        )

    cash_payments = safe_float(cash_payments_input)
    cash_payments_percent = round((cash_payments / turnover) * 100, 2) if turnover > 0 else 0

    with col4:
        st.metric("Cash Payments Percentage", f"{cash_payments_percent}%")

    col5, col6 = st.columns(2)

    with col5:
        profit_amount_input = amount_input(
            "Declared Profit Amount",
            key=keys["profit_amount"],
            placeholder="Example: 20,00,000"
        )

    declared_profit = safe_float(profit_amount_input)
    declared_profit_percent = round((declared_profit / turnover) * 100, 2) if turnover > 0 else 0

    with col6:
        st.metric("Declared Profit Percentage", f"{declared_profit_percent}%")

    presumptive_profit_44ae = 0.0

    if presumptive_section == "44AE":
        presumptive_profit_44ae_input = amount_input(
            "Presumptive Profit as per Section 44AE",
            key=keys["presumptive_profit_44ae"],
            placeholder="Example: 9,00,000"
        )
        presumptive_profit_44ae = safe_float(presumptive_profit_44ae_input)

    st.divider()

    # ---------------------------------------------------------
    # ADDITIONAL CONDITIONS
    # ---------------------------------------------------------

    total_income_above_basic_exemption = st.selectbox(
        "Is Total Income above Basic Exemption Limit?",
        yes_no_options,
        index=get_index(yes_no_options, st.session_state.get(keys["total_income"], "Yes")),
        key=keys["total_income"]
    )

    accounts_audited_under_other_law = st.selectbox(
        "Are accounts required to be audited under any other law? Example: Companies Act",
        yes_no_options,
        index=get_index(yes_no_options, st.session_state.get(keys["other_law_audit"], "No")),
        key=keys["other_law_audit"]
    )

    st.divider()

    # ---------------------------------------------------------
    # AUTO-CALCULATIONS DISPLAY
    # ---------------------------------------------------------

    presumptive_44ad_profit = round((cash_receipts * 0.08) + (digital_turnover * 0.06), 2)
    presumptive_44ada_profit = round(turnover * 0.50, 2)

    auto1, auto2, auto3 = st.columns(3)

    with auto1:
        if presumptive_section == "44AD":
            st.metric(
                "44AD Presumptive Profit",
                f"₹{format_indian_number_or_zero(presumptive_44ad_profit)}"
            )
            st.caption("8% on cash turnover + 6% on digital/banking turnover")
        else:
            st.metric("44AD Presumptive Profit", "Not Applicable")
            st.caption("Applicable only when Section 44AD is selected")

    with auto2:
        if presumptive_section == "44ADA":
            st.metric(
                "44ADA Presumptive Profit",
                f"₹{format_indian_number_or_zero(presumptive_44ada_profit)}"
            )
            st.caption("50% of professional gross receipts")
        else:
            st.metric("44ADA Presumptive Profit", "Not Applicable")
            st.caption("Applicable only when Section 44ADA is selected")

    with auto3:
        if presumptive_section == "44AD":
            st.metric(
                "Digital / Banking Turnover",
                f"₹{format_indian_number_or_zero(digital_turnover)}"
            )
            st.caption("Total turnover minus cash receipts")
        else:
            st.metric("Digital / Banking Turnover", "Not Applicable")
            st.caption("Used only for Section 44AD 6% / 8% calculation")

    # ---------------------------------------------------------
    # COMMON DATA FOR DRAFT / FINAL RESULT
    # ---------------------------------------------------------

    draft_output_data = {
        "Client Name": selected_client,
        "AY": selected_ay,

        "Entity Type": entity_type,
        "Activity Type": activity_type,
        "Presumptive Section": presumptive_section,
        "Presumptive Section Display": presumptive_section_display,
        "Business Nature": business_nature,
        "Is Resident": is_resident,
        "Section 44AD(4) Applicable": section_44ad_4_applicable,
        "Section 44AD(4) Display": section_44ad_4_display,

        "Turnover / Gross Receipts": turnover,
        "Turnover / Gross Receipts Formatted": format_indian_number(turnover),

        "Cash Receipts Amount": cash_receipts,
        "Cash Receipts Amount Formatted": format_indian_number(cash_receipts),
        "Cash Receipts %": cash_receipts_percent,

        "Cash Payments Amount": cash_payments,
        "Cash Payments Amount Formatted": format_indian_number(cash_payments),
        "Cash Payments %": cash_payments_percent,

        "Digital / Banking Turnover": digital_turnover,
        "Digital / Banking Turnover Formatted": format_indian_number(digital_turnover),

        "Declared Profit Amount": declared_profit,
        "Declared Profit Amount Formatted": format_indian_number(declared_profit),
        "Declared Profit %": declared_profit_percent,

        "44AD Presumptive Profit": presumptive_44ad_profit,
        "44AD Presumptive Profit Formatted": format_indian_number(presumptive_44ad_profit),

        "44ADA Presumptive Profit": presumptive_44ada_profit,
        "44ADA Presumptive Profit Formatted": format_indian_number(presumptive_44ada_profit),

        "Presumptive Profit 44AE": presumptive_profit_44ae,
        "Presumptive Profit 44AE Formatted": format_indian_number(presumptive_profit_44ae),

        "Total Income Above Basic Exemption": total_income_above_basic_exemption,
        "Accounts Audited Under Other Law": accounts_audited_under_other_law,
    }

    st.divider()

    save_col, check_col = st.columns(2)

    with save_col:
        if st.button("💾 Save Draft", key=f"taa_save_draft_button_{context_key}", use_container_width=True):
            draft_path = save_draft(selected_client, selected_ay, draft_output_data)
            st.session_state[keys["loaded_marker"]] = True
            st.success(f"✅ Draft saved successfully: {draft_path}")

    with check_col:
        check_clicked = st.button(
            "🔍 Check Tax Audit Applicability",
            key=f"taa_check_button_{context_key}",
            use_container_width=True
        )

    if check_clicked:
        result = determine_applicability(
            entity_type=entity_type,
            activity_type=activity_type,
            presumptive_section=presumptive_section,
            business_nature=business_nature,
            is_resident=is_resident,
            turnover=turnover,
            cash_receipts=cash_receipts,
            cash_receipts_percent=cash_receipts_percent,
            cash_payments_percent=cash_payments_percent,
            declared_profit=declared_profit,
            presumptive_44ad_profit=presumptive_44ad_profit,
            presumptive_44ada_profit=presumptive_44ada_profit,
            presumptive_profit_44ae=presumptive_profit_44ae,
            total_income_above_basic_exemption=total_income_above_basic_exemption,
            section_44ad_4_applicable=section_44ad_4_applicable,
            accounts_audited_under_other_law=accounts_audited_under_other_law
        )

        st.subheader("📌 Applicability Result")

        r1, r2, r3 = st.columns(3)

        with r1:
            st.metric("Tax Audit Applicable", result["tax_audit_applicable"])

        with r2:
            st.metric("ITR Filing Basis", result["itr_basis"])

        with r3:
            st.metric("Audit Form", result["audit_form"])

        st.write("### Detailed Reasoning")

        for reason in result["reasons"]:
            st.write(reason)

        st.write("### Recommended ITR Form")
        st.info(result["itr_form"])

        st.write("### Applicable Section / Clause")
        st.success(result["section_reference"])

        final_output_data = {
            **draft_output_data,
            "Tax Audit Applicable": result["tax_audit_applicable"],
            "ITR Basis": result["itr_basis"],
            "Audit Form": result["audit_form"],
            "ITR Form": result["itr_form"],
            "Section Reference": result["section_reference"],
            "Reason": " | ".join(result["reasons"])
        }

        save_draft(selected_client, selected_ay, draft_output_data)

        excel_path, json_path = save_applicability_outputs(
            selected_client,
            selected_ay,
            final_output_data
        )

        st.success(f"✅ Applicability Excel report saved: {excel_path}")
        st.success(f"✅ Applicability JSON data saved: {json_path}")

        st.info(
            "This result will be automatically used in the Tax Report module "
            "to select Form 3CA-3CD or Form 3CB-3CD."
        )


# ---------------------------------------------------------
# TAX AUDIT APPLICABILITY LOGIC
# ---------------------------------------------------------

def determine_applicability(
    entity_type,
    activity_type,
    presumptive_section,
    business_nature,
    is_resident,
    turnover,
    cash_receipts,
    cash_receipts_percent,
    cash_payments_percent,
    declared_profit,
    presumptive_44ad_profit,
    presumptive_44ada_profit,
    presumptive_profit_44ae,
    total_income_above_basic_exemption,
    section_44ad_4_applicable,
    accounts_audited_under_other_law
):
    reasons = []
    tax_audit_applicable = "No"
    itr_basis = "Normal Basis"
    audit_form = "Not Applicable"
    section_reference = "Not Applicable"

    is_company = entity_type == "Company"
    is_llp = entity_type == "LLP"

    is_itr4_eligible_entity_44ad = entity_type in ["Individual", "HUF", "Partnership Firm"]
    is_44ada_eligible_entity = entity_type in ["Individual", "Partnership Firm"]

    total_income_exceeds_bel = total_income_above_basic_exemption == "Yes"

    possible_audit_form = (
        "Form 3CA-3CD"
        if accounts_audited_under_other_law == "Yes"
        else "Form 3CB-3CD"
    )

    if accounts_audited_under_other_law == "Yes":
        reasons.append(
            "Accounts are required to be audited under another law. If tax audit applies, Form 3CA-3CD will be applicable."
        )
    else:
        reasons.append(
            "Accounts are not required to be audited under another law. If tax audit applies, Form 3CB-3CD will be applicable."
        )

    # ---------------------------------------------------------
    # NORMAL BUSINESS - SECTION 44AB(a)
    # ---------------------------------------------------------

    if presumptive_section == "Not Applicable" and activity_type in ["Business", "Both Business and Profession"]:

        digital_condition = cash_receipts_percent <= 5 and cash_payments_percent <= 5

        business_audit_limit = 10_00_00_000 if digital_condition else 1_00_00_000

        if turnover > business_audit_limit:
            tax_audit_applicable = "Yes"
            section_reference = "Section 44AB(a)"
            reasons.append(
                f"Business turnover exceeds applicable audit limit of ₹{format_indian_number(business_audit_limit)}."
            )
        else:
            reasons.append(
                f"Business turnover is within applicable audit limit of ₹{format_indian_number(business_audit_limit)} under Section 44AB(a)."
            )

        itr_basis = "Normal Basis"

    # ---------------------------------------------------------
    # NORMAL PROFESSION - SECTION 44AB(b)
    # ---------------------------------------------------------

    if presumptive_section == "Not Applicable" and activity_type in ["Profession", "Both Business and Profession"]:

        profession_audit_limit = 50_00_000

        if turnover > profession_audit_limit:
            tax_audit_applicable = "Yes"
            section_reference = "Section 44AB(b)"
            reasons.append(
                "Professional gross receipts exceed ₹50,00,000. Tax audit is applicable under Section 44AB(b)."
            )
        else:
            reasons.append(
                "Professional gross receipts do not exceed ₹50,00,000. Normal profession audit is not triggered under Section 44AB(b)."
            )

        itr_basis = "Normal Basis"

    # ---------------------------------------------------------
    # PRESUMPTIVE BUSINESS - SECTION 44AD
    # ---------------------------------------------------------

    if presumptive_section == "44AD":

        itr_basis = "Presumptive Basis - Section 44AD"

        if activity_type not in ["Business", "Both Business and Profession"]:
            itr_basis = "Normal Basis"
            reasons.append("Section 44AD is not applicable because the selected activity is not business.")

        elif is_resident != "Yes":
            itr_basis = "Normal Basis"
            reasons.append("Section 44AD is available only to resident eligible assessees.")

        elif not is_itr4_eligible_entity_44ad or is_llp or is_company:
            itr_basis = "Normal Basis"
            reasons.append("Section 44AD is not available to Company, LLP, or ineligible entity types.")

        elif business_nature in [
            "Commission / Brokerage",
            "Agency Business",
            "Goods Carriage Business",
            "Specified Profession",
            "Other Ineligible Business"
        ]:
            itr_basis = "Normal Basis"
            reasons.append(
                f"Section 44AD is not applicable because business nature is '{business_nature}'."
            )

        else:
            reasons.append(
                f"Presumptive profit under Section 44AD is ₹{format_indian_number_or_zero(presumptive_44ad_profit)} "
                "computed as 8% of cash turnover and 6% of digital/banking turnover."
            )

            if declared_profit >= presumptive_44ad_profit:
                tax_audit_applicable = "No"
                section_reference = "Section 44AD"
                reasons.append(
                    "Declared profit is not lower than presumptive profit under Section 44AD. Tax audit is not triggered."
                )
            else:
                if section_44ad_4_applicable == "Yes" and total_income_exceeds_bel:
                    tax_audit_applicable = "Yes"
                    section_reference = "Section 44AB(e) read with Section 44AD(4)"
                    reasons.append(
                        "Declared profit is lower than presumptive profit, Section 44AD(4) applies, and total income exceeds basic exemption limit. Tax audit is applicable under Section 44AB(e)."
                    )
                else:
                    tax_audit_applicable = "No"
                    section_reference = "Section 44AD"
                    reasons.append(
                        "Declared profit is lower than presumptive profit, but Section 44AB(e) condition is not triggered because either Section 44AD(4) is not applicable or income does not exceed basic exemption limit."
                    )

    # ---------------------------------------------------------
    # PRESUMPTIVE PROFESSION - SECTION 44ADA
    # ---------------------------------------------------------

    if presumptive_section == "44ADA":

        itr_basis = "Presumptive Basis - Section 44ADA"

        ada_limit = 75_00_000 if cash_receipts_percent <= 5 else 50_00_000

        if activity_type not in ["Profession", "Both Business and Profession"]:
            itr_basis = "Normal Basis"
            reasons.append("Section 44ADA is not applicable because the selected activity is not profession.")

        elif is_resident != "Yes":
            itr_basis = "Normal Basis"
            reasons.append("Section 44ADA is available only to resident eligible assessees.")

        elif not is_44ada_eligible_entity or is_llp or is_company:
            itr_basis = "Normal Basis"
            reasons.append("Section 44ADA is not available to Company, LLP, HUF or other ineligible entity types.")

        elif turnover > ada_limit:
            tax_audit_applicable = "Yes"
            itr_basis = "Normal Basis"
            section_reference = "Section 44AB(b)"
            reasons.append(
                f"Professional gross receipts exceed the applicable Section 44ADA eligibility limit of ₹{format_indian_number(ada_limit)}. Normal profession audit rule under Section 44AB(b) applies."
            )

        elif declared_profit >= presumptive_44ada_profit:
            tax_audit_applicable = "No"
            section_reference = "Section 44ADA"
            reasons.append(
                f"Declared professional income is at least 50% of gross receipts. Minimum presumptive income is ₹{format_indian_number_or_zero(presumptive_44ada_profit)}."
            )

        else:
            if total_income_exceeds_bel:
                tax_audit_applicable = "Yes"
                section_reference = "Section 44AB(d) read with Section 44ADA(4)"
                reasons.append(
                    "Declared professional income is lower than 50% of gross receipts and total income exceeds basic exemption limit. Tax audit is applicable under Section 44AB(d)."
                )
            else:
                tax_audit_applicable = "No"
                section_reference = "Section 44ADA"
                reasons.append(
                    "Declared professional income is lower than 50%, but total income does not exceed basic exemption limit. Tax audit is not triggered."
                )

    # ---------------------------------------------------------
    # GOODS CARRIAGE PRESUMPTIVE TAXATION - SECTION 44AE
    # ---------------------------------------------------------

    if presumptive_section == "44AE":

        itr_basis = "Presumptive Basis - Section 44AE"

        if business_nature != "Goods Carriage Business":
            reasons.append(
                "Section 44AE is generally linked to goods carriage business. Please verify business nature."
            )

        if presumptive_profit_44ae <= 0:
            tax_audit_applicable = "No"
            section_reference = "Section 44AE"
            reasons.append(
                "Presumptive profit under Section 44AE was not entered. Enter the deemed income as per vehicle details for exact audit decision."
            )

        elif declared_profit < presumptive_profit_44ae:
            tax_audit_applicable = "Yes"
            section_reference = "Section 44AB(c) read with Section 44AE"
            reasons.append(
                "Declared profit is lower than deemed income under Section 44AE. Tax audit is applicable under Section 44AB(c)."
            )

        else:
            tax_audit_applicable = "No"
            section_reference = "Section 44AE"
            reasons.append(
                "Declared income is not lower than deemed income under Section 44AE. Tax audit is not triggered."
            )

    # ---------------------------------------------------------
    # AUDIT FORM DECISION
    # ---------------------------------------------------------

    if tax_audit_applicable == "Yes":
        audit_form = possible_audit_form
        reasons.append(f"Since tax audit is applicable, applicable audit report is {audit_form}.")
    else:
        audit_form = "Not Applicable"
        reasons.append("Since tax audit is not applicable, Form 3CA/3CB-3CD is not required.")

    itr_form = recommend_itr_form(entity_type, itr_basis)

    return {
        "tax_audit_applicable": tax_audit_applicable,
        "itr_basis": itr_basis,
        "audit_form": audit_form,
        "itr_form": itr_form,
        "section_reference": section_reference,
        "reasons": reasons
    }


# ---------------------------------------------------------
# ITR FORM RECOMMENDATION
# ---------------------------------------------------------

def recommend_itr_form(entity_type, itr_basis):

    if "Presumptive" in itr_basis:
        if entity_type in ["Individual", "HUF", "Partnership Firm"]:
            return "ITR-4, subject to other ITR-4 eligibility conditions"
        return "Presumptive basis not recommended for this entity type"

    if entity_type in ["Individual", "HUF"]:
        return "ITR-3 for normal business/professional income"

    if entity_type in ["Partnership Firm", "LLP"]:
        return "ITR-5"

    if entity_type == "Company":
        return "ITR-6"

    return "Check applicable ITR form based on entity status"