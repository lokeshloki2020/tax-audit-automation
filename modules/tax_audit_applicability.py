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
    except Exception:
        return 0.0


def safe_int(value):
    try:
        return int(float(str(value).replace(",", "").strip()))
    except Exception:
        return 0


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

    except Exception:
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


def amount_input(label, key, placeholder="Example: 2,50,00,000", help_text=None):
    return st.text_input(
        label,
        key=key,
        placeholder=placeholder,
        help=help_text,
        on_change=format_amount_session_state,
        args=(key,)
    )


def safe_key(value):
    return re.sub(r"[^A-Za-z0-9_]", "_", str(value))


def get_index(options, value):
    if value in options:
        return options.index(value)
    return 0


def percentage(numerator, denominator):
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def yes_no_bool(value):
    return str(value).strip().lower() == "yes"


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
        except Exception:
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
# DISPLAY OPTIONS
# ---------------------------------------------------------

ENTITY_OPTIONS = [
    "Individual",
    "HUF",
    "Partnership Firm",
    "LLP",
    "Company",
    "AOP/BOI",
    "Other"
]

ACTIVITY_OPTIONS = [
    "Business",
    "Profession",
    "Goods Carriage Business",
    "Both Business and Profession"
]

BUSINESS_NATURE_OPTIONS = [
    "Eligible Business",
    "Commission / Brokerage",
    "Agency Business",
    "Goods Carriage Business",
    "Specified Profession",
    "Other Ineligible Business"
]

YES_NO_OPTIONS = ["Yes", "No"]

EXERCISE_OPTIONS = [
    "Yes - Exercise presumptive taxation option",
    "No - Do not exercise presumptive taxation option"
]


def get_exercise_code(display_value):
    if str(display_value).startswith("Yes"):
        return "Yes"
    return "No"


def get_exercise_display(value):
    if str(value) == "Yes" or str(value).startswith("Yes"):
        return "Yes - Exercise presumptive taxation option"
    return "No - Do not exercise presumptive taxation option"


def get_44ad_previous_code(display_value):
    if str(display_value).startswith("Yes"):
        return "Yes"
    return "No"


def get_44ad_previous_display(value):
    if str(value) == "Yes" or str(value).startswith("Yes"):
        return "Yes - Earlier opted 44AD and now opting out within lock-in period"
    return "No - No earlier 44AD lock-in issue"


SECTION_44AD_PREVIOUS_OPTIONS = [
    "No - No earlier 44AD lock-in issue",
    "Yes - Earlier opted 44AD and now opting out within lock-in period"
]


# ---------------------------------------------------------
# SESSION HELPERS
# ---------------------------------------------------------

def load_saved_data_into_session(saved_data, keys):
    st.session_state[keys["entity_type"]] = saved_data.get("Entity Type", "Individual")
    st.session_state[keys["activity_type"]] = saved_data.get("Activity Type", "Business")
    st.session_state[keys["business_nature"]] = saved_data.get("Business Nature", "Eligible Business")
    st.session_state[keys["is_resident"]] = saved_data.get("Is Resident", "Yes")

    previous_44ad = (
        saved_data.get("Earlier 44AD Opted / Lock-in Applicable")
        or saved_data.get("Section 44AD(4) Applicable")
        or "No"
    )
    st.session_state[keys["earlier_44ad_opted"]] = get_44ad_previous_display(previous_44ad)

    exercise_option = saved_data.get("Exercise Presumptive Option", "Yes")
    st.session_state[keys["exercise_presumptive_option"]] = get_exercise_display(exercise_option)

    st.session_state[keys["turnover"]] = saved_data.get("Turnover / Gross Receipts Formatted", "")
    st.session_state[keys["cash_receipts"]] = saved_data.get("Cash Receipts Amount Formatted", "")
    st.session_state[keys["cash_payments"]] = saved_data.get("Cash Payments Amount Formatted", "")
    st.session_state[keys["profit_amount"]] = saved_data.get("Declared Profit Amount Formatted", "")
    st.session_state[keys["presumptive_profit_44ae"]] = saved_data.get("Presumptive Profit 44AE Formatted", "")
    st.session_state[keys["goods_carriages_count"]] = str(saved_data.get("Goods Carriages Owned", ""))

    st.session_state[keys["total_income"]] = saved_data.get("Total Income Above Basic Exemption", "Yes")
    st.session_state[keys["other_law_audit"]] = saved_data.get("Accounts Audited Under Other Law", "No")


def initialise_blank_session(keys):
    defaults = {
        keys["entity_type"]: "Individual",
        keys["activity_type"]: "Business",
        keys["business_nature"]: "Eligible Business",
        keys["is_resident"]: "Yes",
        keys["earlier_44ad_opted"]: "No - No earlier 44AD lock-in issue",
        keys["exercise_presumptive_option"]: "Yes - Exercise presumptive taxation option",

        keys["turnover"]: "",
        keys["cash_receipts"]: "",
        keys["cash_payments"]: "",
        keys["profit_amount"]: "",
        keys["presumptive_profit_44ae"]: "",
        keys["goods_carriages_count"]: "",

        keys["total_income"]: "Yes",
        keys["other_law_audit"]: "No",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------
# PRESUMPTIVE ELIGIBILITY LOGIC
# ---------------------------------------------------------

def infer_presumptive_section(activity_type, business_nature):
    if activity_type == "Goods Carriage Business" or business_nature == "Goods Carriage Business":
        return "44AE"

    if activity_type == "Profession" or business_nature == "Specified Profession":
        return "44ADA"

    if activity_type in ["Business", "Both Business and Profession"] and business_nature == "Eligible Business":
        return "44AD"

    return "Not Available"


def is_44ad_eligible_entity(entity_type):
    return entity_type in ["Individual", "HUF", "Partnership Firm"]


def is_44ada_eligible_entity(entity_type):
    return entity_type in ["Individual", "Partnership Firm"]


def evaluate_presumptive_availability(
    entity_type,
    activity_type,
    business_nature,
    is_resident,
    turnover,
    cash_receipts_percent,
    cash_receipts,
    digital_turnover,
    goods_carriages_count,
    presumptive_profit_44ae
):
    section = infer_presumptive_section(activity_type, business_nature)

    result = {
        "section": section,
        "available": "No",
        "limit": 0,
        "limit_display": "Not Applicable",
        "presumptive_profit": 0.0,
        "reason": "",
        "profit_caption": "",
    }

    if section == "Not Available":
        result["reason"] = "Presumptive taxation is not available for the selected activity / business nature."
        return result

    if is_resident != "Yes":
        result["reason"] = f"Section {section} is available only to resident eligible assessees."
        return result

    if section == "44AD":
        if activity_type not in ["Business", "Both Business and Profession"]:
            result["reason"] = "Section 44AD is applicable only to eligible business."
            return result

        if not is_44ad_eligible_entity(entity_type):
            result["reason"] = "Section 44AD is not available to Company, LLP, AOP/BOI or other ineligible entity types."
            return result

        if business_nature != "Eligible Business":
            result["reason"] = f"Section 44AD is not available because business nature is '{business_nature}'."
            return result

        limit = 3_00_00_000 if cash_receipts_percent <= 5 else 2_00_00_000
        result["limit"] = limit
        result["limit_display"] = "₹3 crore" if cash_receipts_percent <= 5 else "₹2 crore"

        if turnover <= 0:
            result["reason"] = "Enter turnover / gross receipts to check Section 44AD eligibility."
            return result

        if turnover > limit:
            result["reason"] = f"Turnover exceeds applicable Section 44AD limit of {result['limit_display']}."
            return result

        presumptive_profit = round((cash_receipts * 0.08) + (digital_turnover * 0.06), 2)

        result["available"] = "Yes"
        result["presumptive_profit"] = presumptive_profit
        result["reason"] = f"Section 44AD is available because turnover is within {result['limit_display']}."
        result["profit_caption"] = "8% on cash receipts + 6% on digital / banking receipts."
        return result

    if section == "44ADA":
        if activity_type not in ["Profession", "Both Business and Profession"] and business_nature != "Specified Profession":
            result["reason"] = "Section 44ADA is applicable only to specified profession."
            return result

        if not is_44ada_eligible_entity(entity_type):
            result["reason"] = "Section 44ADA is not available to Company, LLP, HUF, AOP/BOI or other ineligible entity types."
            return result

        limit = 75_00_000 if cash_receipts_percent <= 5 else 50_00_000
        result["limit"] = limit
        result["limit_display"] = "₹75 lakh" if cash_receipts_percent <= 5 else "₹50 lakh"

        if turnover <= 0:
            result["reason"] = "Enter gross receipts to check Section 44ADA eligibility."
            return result

        if turnover > limit:
            result["reason"] = f"Gross receipts exceed applicable Section 44ADA limit of {result['limit_display']}."
            return result

        presumptive_profit = round(turnover * 0.50, 2)

        result["available"] = "Yes"
        result["presumptive_profit"] = presumptive_profit
        result["reason"] = f"Section 44ADA is available because gross receipts are within {result['limit_display']}."
        result["profit_caption"] = "50% of professional gross receipts."
        return result

    if section == "44AE":
        result["limit"] = 10
        result["limit_display"] = "Not more than 10 goods carriages"

        if activity_type != "Goods Carriage Business" and business_nature != "Goods Carriage Business":
            result["reason"] = "Section 44AE is applicable only to goods carriage business."
            return result

        if goods_carriages_count <= 0:
            result["reason"] = "Enter number of goods carriages owned to check Section 44AE eligibility."
            return result

        if goods_carriages_count > 10:
            result["reason"] = "Section 44AE is not available because goods carriages owned exceed 10."
            return result

        result["available"] = "Yes"
        result["presumptive_profit"] = presumptive_profit_44ae
        result["reason"] = "Section 44AE is available because goods carriages owned are not more than 10."
        result["profit_caption"] = "Presumptive income is based on vehicle-wise prescribed amount."
        return result

    return result


# ---------------------------------------------------------
# TAX AUDIT APPLICABILITY LOGIC
# ---------------------------------------------------------

def normal_business_audit_result(turnover, cash_receipts_percent, cash_payments_percent):
    digital_audit_condition = cash_receipts_percent <= 5 and cash_payments_percent <= 5
    business_audit_limit = 10_00_00_000 if digital_audit_condition else 1_00_00_000

    if turnover > business_audit_limit:
        return {
            "applicable": True,
            "section": "Section 44AB(a)",
            "reason": f"Business turnover exceeds applicable audit limit of ₹{format_indian_number(business_audit_limit)}.",
            "limit": business_audit_limit,
        }

    return {
        "applicable": False,
        "section": "Section 44AB(a)",
        "reason": f"Business turnover is within applicable audit limit of ₹{format_indian_number(business_audit_limit)}.",
        "limit": business_audit_limit,
    }


def normal_profession_audit_result(turnover):
    profession_audit_limit = 50_00_000

    if turnover > profession_audit_limit:
        return {
            "applicable": True,
            "section": "Section 44AB(b)",
            "reason": "Professional gross receipts exceed ₹50,00,000.",
            "limit": profession_audit_limit,
        }

    return {
        "applicable": False,
        "section": "Section 44AB(b)",
        "reason": "Professional gross receipts do not exceed ₹50,00,000.",
        "limit": profession_audit_limit,
    }


def determine_applicability(
    entity_type,
    activity_type,
    business_nature,
    is_resident,
    turnover,
    cash_receipts,
    cash_receipts_percent,
    cash_payments_percent,
    digital_turnover,
    declared_profit,
    goods_carriages_count,
    presumptive_profit_44ae,
    exercise_presumptive_option,
    total_income_above_basic_exemption,
    earlier_44ad_opted,
    accounts_audited_under_other_law
):
    reasons = []
    notes = []

    tax_audit_applicable = "No"
    itr_basis = "Normal Basis"
    audit_form = "Not Applicable"
    section_reference = "Not Applicable"

    total_income_exceeds_bel = total_income_above_basic_exemption == "Yes"

    possible_audit_form = (
        "Form 3CA-3CD"
        if accounts_audited_under_other_law == "Yes"
        else "Form 3CB-3CD"
    )

    if accounts_audited_under_other_law == "Yes":
        reasons.append("Accounts are audited under another law. If tax audit applies, Form 3CA-3CD will be applicable.")
    else:
        reasons.append("Accounts are not audited under another law. If tax audit applies, Form 3CB-3CD will be applicable.")

    availability = evaluate_presumptive_availability(
        entity_type=entity_type,
        activity_type=activity_type,
        business_nature=business_nature,
        is_resident=is_resident,
        turnover=turnover,
        cash_receipts_percent=cash_receipts_percent,
        cash_receipts=cash_receipts,
        digital_turnover=digital_turnover,
        goods_carriages_count=goods_carriages_count,
        presumptive_profit_44ae=presumptive_profit_44ae,
    )

    presumptive_section = availability["section"]
    presumptive_available = availability["available"] == "Yes"
    presumptive_profit = availability["presumptive_profit"]

    reasons.append(f"Auto-detected presumptive section: {presumptive_section}.")
    reasons.append(availability["reason"])

    exercising = exercise_presumptive_option == "Yes" and presumptive_available

    # ---------------------------------------------------------
    # CASE 1: PRESUMPTIVE OPTION EXERCISED
    # ---------------------------------------------------------

    if exercising:
        itr_basis = f"Presumptive Basis - Section {presumptive_section}"
        section_reference = f"Section {presumptive_section}"

        if presumptive_section in ["44AD", "44ADA"]:
            if declared_profit > 0 and declared_profit < presumptive_profit:
                reasons.append(
                    f"Declared profit entered is lower than presumptive income of ₹{format_indian_number_or_zero(presumptive_profit)}. "
                    "For presumptive filing, income should be declared at least at the presumptive amount."
                )
            else:
                reasons.append(
                    f"Presumptive option is exercised. Minimum presumptive income is ₹{format_indian_number_or_zero(presumptive_profit)}."
                )

            tax_audit_applicable = "No"

        elif presumptive_section == "44AE":
            if presumptive_profit <= 0:
                reasons.append("Section 44AE is exercised, but vehicle-wise prescribed presumptive income was not entered.")
                tax_audit_applicable = "No"
            elif declared_profit > 0 and declared_profit < presumptive_profit:
                tax_audit_applicable = "Yes"
                section_reference = "Section 44AB(c) read with Section 44AE"
                reasons.append(
                    "Declared income is lower than prescribed income under Section 44AE. Tax audit is applicable."
                )
            else:
                tax_audit_applicable = "No"
                reasons.append("Declared income is not lower than prescribed income under Section 44AE.")

    # ---------------------------------------------------------
    # CASE 2: PRESUMPTIVE NOT EXERCISED OR NOT AVAILABLE
    # ---------------------------------------------------------

    else:
        itr_basis = "Normal Basis"

        if presumptive_available:
            reasons.append(f"Presumptive taxation is available under Section {presumptive_section}, but the option is not exercised.")
        else:
            reasons.append("Presumptive taxation is not available. Filing basis will be normal.")

        # Normal audit rule depending on activity / inferred section.
        normal_audit = {
            "applicable": False,
            "section": "Not Applicable",
            "reason": "No normal audit rule triggered.",
        }

        if presumptive_section == "44ADA" or activity_type == "Profession" or business_nature == "Specified Profession":
            normal_audit = normal_profession_audit_result(turnover)

        elif presumptive_section in ["44AD", "44AE"] or activity_type in ["Business", "Goods Carriage Business", "Both Business and Profession"]:
            normal_audit = normal_business_audit_result(
                turnover=turnover,
                cash_receipts_percent=cash_receipts_percent,
                cash_payments_percent=cash_payments_percent,
            )

        reasons.append(normal_audit["reason"])

        if normal_audit["applicable"]:
            tax_audit_applicable = "Yes"
            section_reference = normal_audit["section"]

        # Special lower-than-presumptive checks only if normal audit has not already triggered.
        if tax_audit_applicable == "No" and presumptive_available:

            if presumptive_section == "44AD":
                if earlier_44ad_opted == "Yes":
                    notes.append("Note: 44AD benefit may not be available for the next 5 subsequent assessment years.")

                    if declared_profit < presumptive_profit and total_income_exceeds_bel:
                        tax_audit_applicable = "Yes"
                        section_reference = "Section 44AB(e) read with Section 44AD(4) and 44AD(5)"
                        reasons.append(
                            "Earlier 44AD was opted, current year 44AD is not exercised, declared profit is lower than presumptive income, and total income exceeds basic exemption limit."
                        )
                    else:
                        reasons.append(
                            "44AD lock-in note applies, but audit is not triggered because lower-profit and basic exemption conditions are not both satisfied."
                        )
                else:
                    reasons.append("Earlier 44AD lock-in condition is not selected. Special 44AD opt-out audit rule is not triggered.")

            elif presumptive_section == "44ADA":
                if declared_profit < presumptive_profit and total_income_exceeds_bel:
                    tax_audit_applicable = "Yes"
                    section_reference = "Section 44AB(d) read with Section 44ADA(4)"
                    reasons.append(
                        "Professional income is declared below 50% of gross receipts and total income exceeds basic exemption limit."
                    )
                else:
                    reasons.append(
                        "44ADA lower-income audit condition is not triggered because declared income is not below 50% or total income does not exceed basic exemption limit."
                    )

            elif presumptive_section == "44AE":
                if presumptive_profit <= 0:
                    reasons.append("44AE prescribed vehicle-wise presumptive income was not entered. Exact lower-income audit check cannot be completed.")
                elif declared_profit < presumptive_profit:
                    tax_audit_applicable = "Yes"
                    section_reference = "Section 44AB(c) read with Section 44AE"
                    reasons.append("Declared income is lower than prescribed income under Section 44AE.")
                else:
                    reasons.append("Declared income is not lower than prescribed income under Section 44AE.")

    # ---------------------------------------------------------
    # FINAL AUDIT FORM DECISION
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
        "reasons": reasons,
        "notes": notes,
        "presumptive_section": presumptive_section,
        "presumptive_available": "Yes" if presumptive_available else "No",
        "presumptive_limit": availability["limit"],
        "presumptive_limit_display": availability["limit_display"],
        "presumptive_profit": presumptive_profit if presumptive_available else 0,
        "exercise_presumptive_option": exercise_presumptive_option if presumptive_available else "Not Applicable",
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
        "business_nature": f"taa_business_nature_{context_key}",
        "is_resident": f"taa_is_resident_{context_key}",
        "earlier_44ad_opted": f"taa_earlier_44ad_opted_{context_key}",
        "exercise_presumptive_option": f"taa_exercise_presumptive_option_{context_key}",

        "turnover": f"taa_turnover_input_{context_key}",
        "cash_receipts": f"taa_cash_receipts_input_{context_key}",
        "cash_payments": f"taa_cash_payments_input_{context_key}",
        "profit_amount": f"taa_profit_amount_input_{context_key}",
        "presumptive_profit_44ae": f"taa_presumptive_profit_44ae_{context_key}",
        "goods_carriages_count": f"taa_goods_carriages_count_{context_key}",

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

    st.write("### 1. Basic Classification")

    c1, c2, c3 = st.columns(3)

    with c1:
        entity_type = st.selectbox(
            "Type / Status of Assessee",
            ENTITY_OPTIONS,
            index=get_index(ENTITY_OPTIONS, st.session_state.get(keys["entity_type"], "Individual")),
            key=keys["entity_type"]
        )

    with c2:
        activity_type = st.selectbox(
            "Nature of Activity",
            ACTIVITY_OPTIONS,
            index=get_index(ACTIVITY_OPTIONS, st.session_state.get(keys["activity_type"], "Business")),
            key=keys["activity_type"]
        )

    with c3:
        business_nature = st.selectbox(
            "Business / Income Nature",
            BUSINESS_NATURE_OPTIONS,
            index=get_index(BUSINESS_NATURE_OPTIONS, st.session_state.get(keys["business_nature"], "Eligible Business")),
            key=keys["business_nature"]
        )

    c4, c5 = st.columns(2)

    with c4:
        is_resident = st.selectbox(
            "Is the assessee Resident?",
            YES_NO_OPTIONS,
            index=get_index(YES_NO_OPTIONS, st.session_state.get(keys["is_resident"], "Yes")),
            key=keys["is_resident"]
        )

    with c5:
        accounts_audited_under_other_law = st.selectbox(
            "Are accounts required to be audited under any other law? Example: Companies Act",
            YES_NO_OPTIONS,
            index=get_index(YES_NO_OPTIONS, st.session_state.get(keys["other_law_audit"], "No")),
            key=keys["other_law_audit"]
        )

    st.divider()

    # ---------------------------------------------------------
    # AMOUNT DETAILS
    # ---------------------------------------------------------

    st.write("### 2. Turnover, Cash and Profit Details")

    turnover_input = amount_input(
        "Total Turnover / Gross Receipts",
        key=keys["turnover"],
        placeholder="Example: 2,50,00,000",
        help_text="Total turnover includes both cash and digital/banking receipts."
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
    cash_receipts_percent = percentage(cash_receipts, turnover)
    digital_turnover = max(turnover - cash_receipts, 0)

    with col2:
        st.metric("Cash Receipts Percentage", f"{cash_receipts_percent}%")
        st.caption(f"Digital / Banking receipts auto-calculated: ₹{format_indian_number_or_zero(digital_turnover)}")

    col3, col4 = st.columns(2)

    with col3:
        cash_payments_input = amount_input(
            "Cash Payments Amount",
            key=keys["cash_payments"],
            placeholder="Example: 3,00,000",
            help_text="Used only for normal business tax audit ₹10 crore threshold."
        )

    cash_payments = safe_float(cash_payments_input)
    cash_payments_percent = percentage(cash_payments, turnover)

    with col4:
        st.metric("Cash Payments Percentage", f"{cash_payments_percent}%")

    col5, col6 = st.columns(2)

    with col5:
        profit_amount_input = amount_input(
            "Declared Profit / Income Amount",
            key=keys["profit_amount"],
            placeholder="Example: 20,00,000"
        )

    declared_profit = safe_float(profit_amount_input)
    declared_profit_percent = percentage(declared_profit, turnover)

    with col6:
        st.metric("Declared Profit Percentage", f"{declared_profit_percent}%")

    st.divider()

    # ---------------------------------------------------------
    # PRESUMPTIVE AUTO-DETECTION
    # ---------------------------------------------------------

    goods_carriages_count = 0
    presumptive_profit_44ae = 0.0

    inferred_section = infer_presumptive_section(activity_type, business_nature)

    if inferred_section == "44AE":
        st.write("### 3. Goods Carriage Details - Section 44AE")

        g1, g2 = st.columns(2)

        with g1:
            goods_carriages_count_input = st.text_input(
                "Number of Goods Carriages Owned",
                key=keys["goods_carriages_count"],
                placeholder="Example: 5"
            )

        goods_carriages_count = safe_int(goods_carriages_count_input)

        with g2:
            presumptive_profit_44ae_input = amount_input(
                "Prescribed Presumptive Income as per Section 44AE",
                key=keys["presumptive_profit_44ae"],
                placeholder="Example: 9,00,000",
                help_text="Enter vehicle-wise prescribed presumptive income total."
            )

        presumptive_profit_44ae = safe_float(presumptive_profit_44ae_input)

    availability = evaluate_presumptive_availability(
        entity_type=entity_type,
        activity_type=activity_type,
        business_nature=business_nature,
        is_resident=is_resident,
        turnover=turnover,
        cash_receipts_percent=cash_receipts_percent,
        cash_receipts=cash_receipts,
        digital_turnover=digital_turnover,
        goods_carriages_count=goods_carriages_count,
        presumptive_profit_44ae=presumptive_profit_44ae,
    )

    st.write("### 4. Auto-detected Presumptive Taxation Eligibility")

    e1, e2, e3 = st.columns(3)

    with e1:
        st.metric("Detected Section", availability["section"])

    with e2:
        st.metric("Presumptive Available", availability["available"])

    with e3:
        st.metric("Limit Applied", availability["limit_display"])

    st.caption(availability["reason"])

    exercise_presumptive_option = "Not Applicable"

    if availability["available"] == "Yes":
        p1, p2 = st.columns(2)

        with p1:
            st.metric(
                f"{availability['section']} Presumptive Income",
                f"₹{format_indian_number_or_zero(availability['presumptive_profit'])}"
            )
            st.caption(availability["profit_caption"])

        with p2:
            exercise_display = st.selectbox(
                "Do you want to exercise presumptive taxation option this year?",
                EXERCISE_OPTIONS,
                index=get_index(
                    EXERCISE_OPTIONS,
                    st.session_state.get(
                        keys["exercise_presumptive_option"],
                        "Yes - Exercise presumptive taxation option"
                    )
                ),
                key=keys["exercise_presumptive_option"]
            )
            exercise_presumptive_option = get_exercise_code(exercise_display)

    else:
        st.info("Presumptive income is not shown because presumptive taxation is not available for the current facts.")

    st.divider()

    # ---------------------------------------------------------
    # ADDITIONAL CONDITIONS
    # ---------------------------------------------------------

    st.write("### 5. Additional Conditions")

    a1, a2 = st.columns(2)

    with a1:
        total_income_above_basic_exemption = st.selectbox(
            "Is Total Income above Basic Exemption Limit?",
            YES_NO_OPTIONS,
            index=get_index(YES_NO_OPTIONS, st.session_state.get(keys["total_income"], "Yes")),
            key=keys["total_income"],
            help="Relevant for lower-than-presumptive income rule under 44AD / 44ADA."
        )

    earlier_44ad_opted = "No"

    with a2:
        if availability["section"] == "44AD" or inferred_section == "44AD":
            earlier_44ad_display = st.selectbox(
                "Earlier 44AD opted and now opting out within 5-year lock-in?",
                SECTION_44AD_PREVIOUS_OPTIONS,
                index=get_index(
                    SECTION_44AD_PREVIOUS_OPTIONS,
                    st.session_state.get(keys["earlier_44ad_opted"], "No - No earlier 44AD lock-in issue")
                ),
                key=keys["earlier_44ad_opted"]
            )
            earlier_44ad_opted = get_44ad_previous_code(earlier_44ad_display)
        else:
            st.caption("44AD lock-in field is not applicable for profession / 44ADA / 44AE.")

    # ---------------------------------------------------------
    # COMMON DATA FOR DRAFT / FINAL RESULT
    # ---------------------------------------------------------

    draft_output_data = {
        "Client Name": selected_client,
        "AY": selected_ay,

        "Entity Type": entity_type,
        "Activity Type": activity_type,
        "Business Nature": business_nature,
        "Is Resident": is_resident,

        "Detected Presumptive Section": availability["section"],
        "Presumptive Section": availability["section"],
        "Presumptive Available": availability["available"],
        "Presumptive Limit": availability["limit"],
        "Presumptive Limit Display": availability["limit_display"],
        "Exercise Presumptive Option": exercise_presumptive_option,

        "Earlier 44AD Opted / Lock-in Applicable": earlier_44ad_opted,
        "Section 44AD(4) Applicable": earlier_44ad_opted,

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

        "Presumptive Profit": availability["presumptive_profit"] if availability["available"] == "Yes" else 0,
        "Presumptive Profit Formatted": format_indian_number(availability["presumptive_profit"]) if availability["available"] == "Yes" else "",

        "44AD Presumptive Profit": availability["presumptive_profit"] if availability["section"] == "44AD" and availability["available"] == "Yes" else 0,
        "44AD Presumptive Profit Formatted": format_indian_number(availability["presumptive_profit"]) if availability["section"] == "44AD" and availability["available"] == "Yes" else "",

        "44ADA Presumptive Profit": availability["presumptive_profit"] if availability["section"] == "44ADA" and availability["available"] == "Yes" else 0,
        "44ADA Presumptive Profit Formatted": format_indian_number(availability["presumptive_profit"]) if availability["section"] == "44ADA" and availability["available"] == "Yes" else "",

        "Goods Carriages Owned": goods_carriages_count,
        "Presumptive Profit 44AE": presumptive_profit_44ae if availability["section"] == "44AE" and availability["available"] == "Yes" else 0,
        "Presumptive Profit 44AE Formatted": format_indian_number(presumptive_profit_44ae) if availability["section"] == "44AE" and availability["available"] == "Yes" else "",

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
            business_nature=business_nature,
            is_resident=is_resident,
            turnover=turnover,
            cash_receipts=cash_receipts,
            cash_receipts_percent=cash_receipts_percent,
            cash_payments_percent=cash_payments_percent,
            digital_turnover=digital_turnover,
            declared_profit=declared_profit,
            goods_carriages_count=goods_carriages_count,
            presumptive_profit_44ae=presumptive_profit_44ae,
            exercise_presumptive_option=exercise_presumptive_option,
            total_income_above_basic_exemption=total_income_above_basic_exemption,
            earlier_44ad_opted=earlier_44ad_opted,
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

        r4, r5, r6 = st.columns(3)

        with r4:
            st.metric("Presumptive Available", result["presumptive_available"])

        with r5:
            st.metric("Exercise Option", result["exercise_presumptive_option"])

        with r6:
            st.metric("Section", result["section_reference"])

        if result["notes"]:
            for note in result["notes"]:
                st.caption(note)

        st.write("### Detailed Reasoning")

        for reason in result["reasons"]:
            st.write(reason)

        st.write("### Recommended ITR Form")
        st.info(result["itr_form"])

        final_output_data = {
            **draft_output_data,
            "Tax Audit Applicable": result["tax_audit_applicable"],
            "ITR Basis": result["itr_basis"],
            "Audit Form": result["audit_form"],
            "ITR Form": result["itr_form"],
            "Section Reference": result["section_reference"],
            "Reason": " | ".join(result["reasons"]),
            "Notes": " | ".join(result["notes"]),
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
