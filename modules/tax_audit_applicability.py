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
    """
    Converts formatted Indian/normal number string into float.
    Example:
    2,50,00,000 -> 25000000
    """
    try:
        return float(str(value).replace(",", "").strip())
    except:
        return 0.0


def format_indian_number(value):
    """
    Formats number into Indian comma format.
    Example:
    25000000 -> 2,50,00,000
    """
    try:
        value = safe_float(value)

        if value == 0:
            return ""

        value = int(value)
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


def format_amount_session_state(key):
    """
    Formats amount fields into Indian comma format after entry.
    """
    if key in st.session_state:
        raw_value = st.session_state[key]

        if raw_value:
            numeric_value = safe_float(raw_value)
            st.session_state[key] = format_indian_number(numeric_value)


def amount_input(label, key, placeholder="Example: 2,50,00,000"):
    """
    Reusable amount input with Indian comma formatting.
    """
    return st.text_input(
        label,
        key=key,
        placeholder=placeholder,
        on_change=format_amount_session_state,
        args=(key,)
    )


def safe_key(value):
    """
    Creates safe session-state key names from client name and AY.
    """
    return re.sub(r"[^A-Za-z0-9_]", "_", str(value))


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


def save_draft(client_name, ay, draft_data):
    draft_path = get_draft_path(client_name, ay)

    with open(draft_path, "w", encoding="utf-8") as file:
        json.dump(draft_data, file, indent=4, ensure_ascii=False)

    return draft_path


def load_draft(client_name, ay):
    draft_path = get_draft_path(client_name, ay)

    if os.path.exists(draft_path):
        try:
            with open(draft_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            return {}

    return {}


def save_applicability_outputs(client_name, ay, output_data):
    """
    Saves final applicability result in both Excel and JSON.
    """
    excel_path = get_result_excel_path(client_name, ay)
    json_path = get_result_json_path(client_name, ay)

    output_df = pd.DataFrame([output_data])
    output_df.to_excel(excel_path, index=False)

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)

    return excel_path, json_path


def get_index(options, value):
    if value in options:
        return options.index(value)
    return 0


def load_draft_into_session(draft_data, keys):
    """
    Force-loads saved draft data into Streamlit session state.
    This is the important fix.
    """
    st.session_state[keys["entity_type"]] = draft_data.get("Entity Type", "Individual")
    st.session_state[keys["activity_type"]] = draft_data.get("Activity Type", "Business")
    st.session_state[keys["turnover"]] = draft_data.get("Turnover / Gross Receipts Formatted", "")
    st.session_state[keys["cash_receipts"]] = draft_data.get("Cash Receipts Amount Formatted", "")
    st.session_state[keys["cash_payments"]] = draft_data.get("Cash Payments Amount Formatted", "")
    st.session_state[keys["profit_amount"]] = draft_data.get("Profit Amount Formatted", "")
    st.session_state[keys["total_income"]] = draft_data.get("Total Income Above Basic Exemption", "Yes")
    st.session_state[keys["presumptive_last_year"]] = draft_data.get("Opted Presumptive Last Year", "Not Applicable / First Year")
    st.session_state[keys["wants_presumptive"]] = draft_data.get("Wants To Opt Presumptive", "Yes")
    st.session_state[keys["other_law_audit"]] = draft_data.get("Accounts Audited Under Other Law", "No")


def initialise_blank_session(keys):
    """
    Initialises blank/default values when no draft is available.
    """
    defaults = {
        keys["entity_type"]: "Individual",
        keys["activity_type"]: "Business",
        keys["turnover"]: "",
        keys["cash_receipts"]: "",
        keys["cash_payments"]: "",
        keys["profit_amount"]: "",
        keys["total_income"]: "Yes",
        keys["presumptive_last_year"]: "Not Applicable / First Year",
        keys["wants_presumptive"]: "Yes",
        keys["other_law_audit"]: "No",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------
# MAIN MODULE
# ---------------------------------------------------------

def show_tax_audit_applicability():
    st.subheader("🧭 Tax Audit Applicability & Filing Basis")

    df = load_clients()

    if df.empty or "Client Name" not in df.columns:
        st.info("Please add clients first.")
        return

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    if len(client_list) == 0:
        st.info("Please add clients first.")
        return

    selected_client = st.selectbox(
        "Search / Select Client",
        client_list,
        index=0,
        placeholder="Search client name...",
        key="taa_selected_client"
    )

    if not selected_client:
        st.info("Please select a client.")
        return

    selected_row = df[df["Client Name"] == selected_client].iloc[0]
    selected_ay = selected_row["AY"]

    st.write(f"### Client: {selected_client} | AY: {selected_ay}")

    draft_data = load_draft(selected_client, selected_ay)

    # ---------------------------------------------------------
    # UNIQUE SESSION KEYS CLIENT-WISE
    # ---------------------------------------------------------

    context_key = f"{safe_key(selected_client)}_{safe_key(selected_ay)}"

    keys = {
        "entity_type": f"taa_entity_type_{context_key}",
        "activity_type": f"taa_activity_type_{context_key}",
        "turnover": f"taa_turnover_input_{context_key}",
        "cash_receipts": f"taa_cash_receipts_input_{context_key}",
        "cash_payments": f"taa_cash_payments_input_{context_key}",
        "profit_amount": f"taa_profit_amount_input_{context_key}",
        "total_income": f"taa_total_income_{context_key}",
        "presumptive_last_year": f"taa_presumptive_last_year_{context_key}",
        "wants_presumptive": f"taa_wants_presumptive_{context_key}",
        "other_law_audit": f"taa_other_law_audit_{context_key}",
        "loaded_marker": f"taa_loaded_marker_{context_key}",
    }

    initialise_blank_session(keys)

    # ---------------------------------------------------------
    # FORCE AUTO-LOAD DRAFT
    # ---------------------------------------------------------

    should_force_load = False

    if draft_data and not st.session_state.get(keys["loaded_marker"], False):
        should_force_load = True

    if draft_data:
        current_amount_values_blank = (
            not st.session_state.get(keys["turnover"])
            and not st.session_state.get(keys["cash_receipts"])
            and not st.session_state.get(keys["cash_payments"])
            and not st.session_state.get(keys["profit_amount"])
        )

        draft_has_amount_values = (
            draft_data.get("Turnover / Gross Receipts Formatted")
            or draft_data.get("Cash Receipts Amount Formatted")
            or draft_data.get("Cash Payments Amount Formatted")
            or draft_data.get("Profit Amount Formatted")
        )

        if current_amount_values_blank and draft_has_amount_values:
            should_force_load = True

    if should_force_load:
        load_draft_into_session(draft_data, keys)
        st.session_state[keys["loaded_marker"]] = True

    if draft_data:
        st.success("✅ Saved draft loaded for this client.")

    if st.button("🔄 Reload Saved Draft", key=f"reload_draft_{context_key}"):
        if draft_data:
            load_draft_into_session(draft_data, keys)
            st.session_state[keys["loaded_marker"]] = True
            st.success("✅ Saved draft reloaded successfully.")
            st.rerun()
        else:
            st.warning("No saved draft available for this client.")

    st.divider()

    # ---------------------------------------------------------
    # OPTIONS
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

    yes_no_options = ["Yes", "No"]

    presumptive_last_year_options = [
        "Yes",
        "No",
        "Not Applicable / First Year"
    ]

    # ---------------------------------------------------------
    # BASIC DETAILS
    # ---------------------------------------------------------

    entity_type = st.selectbox(
        "Type / Status of Assessee",
        entity_options,
        index=get_index(entity_options, st.session_state.get(keys["entity_type"], "Individual")),
        key=keys["entity_type"]
    )

    activity_type = st.selectbox(
        "Nature of Activity",
        activity_options,
        index=get_index(activity_options, st.session_state.get(keys["activity_type"], "Business")),
        key=keys["activity_type"]
    )

    turnover_input = amount_input(
        "Total Turnover / Gross Receipts",
        key=keys["turnover"],
        placeholder="Example: 2,50,00,000"
    )

    turnover = safe_float(turnover_input)

    st.divider()

    # ---------------------------------------------------------
    # CASH RECEIPTS
    # ---------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        cash_receipts_input = amount_input(
            "Cash Receipts Amount",
            key=keys["cash_receipts"],
            placeholder="Example: 5,00,000"
        )

    cash_receipts = safe_float(cash_receipts_input)
    cash_receipts_percent = round((cash_receipts / turnover) * 100, 2) if turnover > 0 else 0

    with col2:
        st.metric("Cash Receipts Percentage", f"{cash_receipts_percent}%")

    # ---------------------------------------------------------
    # CASH PAYMENTS
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # PROFIT AMOUNT
    # ---------------------------------------------------------

    col5, col6 = st.columns(2)

    with col5:
        profit_amount_input = amount_input(
            "Profit Amount",
            key=keys["profit_amount"],
            placeholder="Example: 20,00,000"
        )

    profit_amount = safe_float(profit_amount_input)
    profit_percent = round((profit_amount / turnover) * 100, 2) if turnover > 0 else 0

    with col6:
        st.metric("Profit Percentage on Turnover / Receipts", f"{profit_percent}%")

    st.divider()

    # ---------------------------------------------------------
    # OTHER DETAILS
    # ---------------------------------------------------------

    total_income_above_basic_exemption = st.selectbox(
        "Is Total Income above Basic Exemption Limit?",
        yes_no_options,
        index=get_index(yes_no_options, st.session_state.get(keys["total_income"], "Yes")),
        key=keys["total_income"]
    )

    opted_presumptive_last_year = st.selectbox(
        "Was presumptive taxation opted in earlier year?",
        presumptive_last_year_options,
        index=get_index(
            presumptive_last_year_options,
            st.session_state.get(keys["presumptive_last_year"], "Not Applicable / First Year")
        ),
        key=keys["presumptive_last_year"]
    )

    wants_to_opt_presumptive = st.selectbox(
        "Does client want to file under presumptive taxation this year?",
        yes_no_options,
        index=get_index(yes_no_options, st.session_state.get(keys["wants_presumptive"], "Yes")),
        key=keys["wants_presumptive"]
    )

    accounts_audited_under_other_law = st.selectbox(
        "Are accounts required to be audited under any other law? Example: Companies Act",
        yes_no_options,
        index=get_index(yes_no_options, st.session_state.get(keys["other_law_audit"], "No")),
        key=keys["other_law_audit"]
    )

    # ---------------------------------------------------------
    # COMMON DRAFT DATA
    # ---------------------------------------------------------

    draft_output_data = {
        "Client Name": selected_client,
        "AY": selected_ay,
        "Entity Type": entity_type,
        "Activity Type": activity_type,
        "Turnover / Gross Receipts": turnover,
        "Turnover / Gross Receipts Formatted": format_indian_number(turnover),
        "Cash Receipts Amount": cash_receipts,
        "Cash Receipts Amount Formatted": format_indian_number(cash_receipts),
        "Cash Receipts %": cash_receipts_percent,
        "Cash Payments Amount": cash_payments,
        "Cash Payments Amount Formatted": format_indian_number(cash_payments),
        "Cash Payments %": cash_payments_percent,
        "Profit Amount": profit_amount,
        "Profit Amount Formatted": format_indian_number(profit_amount),
        "Profit %": profit_percent,
        "Total Income Above Basic Exemption": total_income_above_basic_exemption,
        "Opted Presumptive Last Year": opted_presumptive_last_year,
        "Wants To Opt Presumptive": wants_to_opt_presumptive,
        "Accounts Audited Under Other Law": accounts_audited_under_other_law,
    }

    st.divider()

    save_col, check_col = st.columns(2)

    with save_col:
        if st.button("💾 Save Draft", key=f"taa_save_draft_button_{context_key}"):
            draft_path = save_draft(
                selected_client,
                selected_ay,
                draft_output_data
            )

            st.session_state[keys["loaded_marker"]] = True

            st.success(f"✅ Draft saved successfully: {draft_path}")

    with check_col:
        check_clicked = st.button(
            "🔍 Check Tax Audit Applicability",
            key=f"taa_check_button_{context_key}"
        )

    # ---------------------------------------------------------
    # FINAL APPLICABILITY RESULT
    # ---------------------------------------------------------

    if check_clicked:

        result = determine_applicability(
            entity_type,
            activity_type,
            turnover,
            cash_receipts_percent,
            cash_payments_percent,
            profit_percent,
            total_income_above_basic_exemption,
            opted_presumptive_last_year,
            wants_to_opt_presumptive,
            accounts_audited_under_other_law
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

        # Save draft also when final result is generated
        save_draft(selected_client, selected_ay, draft_output_data)

        excel_path, json_path = save_applicability_outputs(
            selected_client,
            selected_ay,
            final_output_data
        )

        st.success(f"✅ Applicability Excel report saved: {excel_path}")
        st.success(f"✅ Applicability JSON data saved: {json_path}")

        st.info(
            "This result will now be automatically used in the Tax Report module "
            "to select Form 3CA-3CD or Form 3CB-3CD."
        )


# ---------------------------------------------------------
# TAX AUDIT APPLICABILITY LOGIC
# ---------------------------------------------------------

def determine_applicability(
    entity_type,
    activity_type,
    turnover,
    cash_receipts_percent,
    cash_payments_percent,
    profit_percent,
    total_income_above_basic_exemption,
    opted_presumptive_last_year,
    wants_to_opt_presumptive,
    accounts_audited_under_other_law
):
    reasons = []
    tax_audit_applicable = "No"
    itr_basis = "Normal Basis"
    audit_form = "Not Applicable"
    section_reference = "Not Applicable"

    digital_condition = cash_receipts_percent <= 5 and cash_payments_percent <= 5

    is_company = entity_type == "Company"
    is_llp = entity_type == "LLP"
    is_itr4_eligible_entity = entity_type in ["Individual", "HUF", "Partnership Firm"]

    possible_audit_form = "Form 3CA-3CD" if accounts_audited_under_other_law == "Yes" else "Form 3CB-3CD"

    if accounts_audited_under_other_law == "Yes":
        reasons.append(
            "Accounts are required to be audited under another law. Therefore, Form 3CA-3CD will apply if tax audit is applicable."
        )
    else:
        reasons.append(
            "Accounts are not required to be audited under another law. Therefore, Form 3CB-3CD will apply if tax audit is applicable."
        )

    # ---------------------------------------------------------
    # BUSINESS LOGIC
    # ---------------------------------------------------------

    if activity_type in ["Business", "Both Business and Profession"]:

        business_audit_limit = 10_00_00_000 if digital_condition else 1_00_00_000
        presumptive_44ad_limit = 3_00_00_000 if cash_receipts_percent <= 5 else 2_00_00_000

        if turnover > business_audit_limit:
            tax_audit_applicable = "Yes"
            section_reference = "Section 44AB(a)"
            reasons.append(
                f"Business turnover exceeds applicable audit limit of ₹{format_indian_number(business_audit_limit)}."
            )
        else:
            reasons.append(
                f"Business turnover is within applicable audit limit of ₹{format_indian_number(business_audit_limit)}."
            )

        if wants_to_opt_presumptive == "Yes":
            if (
                is_itr4_eligible_entity
                and not is_llp
                and not is_company
                and turnover <= presumptive_44ad_limit
            ):
                itr_basis = "Presumptive Basis - Section 44AD"
                reasons.append(
                    f"Client is eligible for presumptive taxation u/s 44AD within turnover limit of ₹{format_indian_number(presumptive_44ad_limit)}."
                )
            else:
                itr_basis = "Normal Basis"
                reasons.append(
                    "Presumptive taxation u/s 44AD is not suitable due to entity type or turnover limit."
                )
        else:
            itr_basis = "Normal Basis"
            reasons.append("Client does not want to opt presumptive taxation.")

        if (
            opted_presumptive_last_year == "Yes"
            and wants_to_opt_presumptive == "No"
            and total_income_above_basic_exemption == "Yes"
            and is_itr4_eligible_entity
        ):
            tax_audit_applicable = "Yes"
            section_reference = "Section 44AB(e) read with Section 44AD"
            reasons.append(
                "Client opted out of presumptive taxation after earlier opting in and income exceeds basic exemption limit."
            )

    # ---------------------------------------------------------
    # PROFESSION LOGIC
    # ---------------------------------------------------------

    if activity_type in ["Profession", "Both Business and Profession"]:

        profession_audit_limit = 75_00_000 if cash_receipts_percent <= 5 else 50_00_000
        presumptive_44ada_limit = 75_00_000 if cash_receipts_percent <= 5 else 50_00_000

        if turnover > profession_audit_limit:
            tax_audit_applicable = "Yes"
            section_reference = "Section 44AB(b)"
            reasons.append(
                f"Professional gross receipts exceed applicable audit limit of ₹{format_indian_number(profession_audit_limit)}."
            )
        else:
            reasons.append(
                f"Professional gross receipts are within applicable audit limit of ₹{format_indian_number(profession_audit_limit)}."
            )

        if wants_to_opt_presumptive == "Yes":
            if entity_type == "Individual" and turnover <= presumptive_44ada_limit:
                itr_basis = "Presumptive Basis - Section 44ADA"
                reasons.append(
                    f"Client may consider presumptive taxation u/s 44ADA within receipts limit of ₹{format_indian_number(presumptive_44ada_limit)}."
                )
            else:
                reasons.append(
                    "Section 44ADA presumptive basis may not apply due to entity type or receipt limit."
                )

        if (
            wants_to_opt_presumptive == "No"
            and profit_percent < 50
            and total_income_above_basic_exemption == "Yes"
            and entity_type == "Individual"
            and turnover <= presumptive_44ada_limit
        ):
            tax_audit_applicable = "Yes"
            section_reference = "Section 44AB(d) read with Section 44ADA"
            reasons.append(
                "Professional income is below 50% of receipts and total income exceeds basic exemption limit."
            )

    itr_form = recommend_itr_form(entity_type, itr_basis)

    if tax_audit_applicable == "Yes":
        audit_form = possible_audit_form
    else:
        audit_form = "Not Applicable"

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
            return "ITR-4, subject to other eligibility conditions"

        return "Presumptive basis not recommended for this entity type"

    if entity_type in ["Individual", "HUF"]:
        return "ITR-3 for normal business/professional income"

    if entity_type in ["Partnership Firm", "LLP"]:
        return "ITR-5"

    if entity_type == "Company":
        return "ITR-6"

    return "Check applicable ITR form based on entity status"