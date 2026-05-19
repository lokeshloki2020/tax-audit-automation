import os
import json
import pandas as pd
import streamlit as st

from utils.common import load_clients


CLAUSES = [
    ("1", "Name of the Assessee"),
    ("2", "Address"),
    ("3", "PAN"),
    ("4", "Whether liable to pay indirect tax like GST, excise, customs etc."),
    ("5", "Status"),
    ("6", "Previous Year"),
    ("7", "Assessment Year"),
    ("8", "Relevant clause of section 44AB under which audit conducted"),
    ("9", "Firm/Association details and changes therein"),
    ("10", "Nature of business or profession and changes"),
    ("11", "Books of accounts maintained"),
    ("12", "Presumptive income under sections 44AD, 44ADA, 44AE etc."),
    ("13", "Method of accounting employed"),
    ("14", "Method of valuation of closing stock"),
    ("15", "Capital asset converted into stock-in-trade"),
    ("16", "Amounts not credited to P&L account"),
    ("17", "Transfer of land/building for lower consideration than stamp duty value"),
    ("18", "Depreciation allowable"),
    ("19", "Deductions under Chapter VI-A / sections like 32AC, 35 etc."),
    ("20", "Bonus, commission, PF, ESI and employee benefits"),
    ("21", "Amounts inadmissible under Income Tax Act"),
    ("22", "Payments to MSME outstanding beyond due date"),
    ("23", "Payments to persons specified under section 40A(2)(b)"),
    ("24", "Amounts deemed as profits under section 32AC/33AB/33ABA etc."),
    ("25", "Profits chargeable under section 41"),
    ("26", "Section 43B disallowances"),
    ("27", "CENVAT/GST input credit treatment"),
    ("28", "Speculation loss"),
    ("29", "Deemed income under sections 56(2)(ix), 56(2)(x) etc."),
    ("30", "Transfer pricing / domestic transfer pricing"),
    ("30A", "Primary adjustment to transfer price"),
    ("30B", "Limitation on interest deduction under section 94B"),
    ("30C", "Impermissible avoidance arrangement"),
    ("31", "Particulars of loans/deposits under sections 269SS, 269ST, 269T"),
    ("32", "Losses and depreciation"),
    ("33", "Deductions admissible under Chapter VI-A"),
    ("34", "TDS/TCS compliance"),
    ("35", "Quantitative details and stock records"),
    ("36", "Dividend Distribution Tax particulars"),
    ("37", "Cost audit"),
    ("38", "Excise audit / GST audit observations"),
    ("39", "Service tax particulars historical / where applicable"),
    ("40", "Ratios"),
    ("41", "Demand or refund under tax laws"),
    ("42", "Reporting of Form 61, 61A, 61B"),
    ("43", "Country-by-Country Reporting / Master File details"),
    ("44", "Break-up of total expenditure with GST registration details"),
]


def get_clause_fields(clause_no):
    base_fields = ["Details / Particulars", "Amount if applicable", "Auditor Remarks"]

    specific_fields = {
        "1": ["Name of Assessee"],
        "2": ["Registered Address"],
        "3": ["PAN"],
        "4": ["Indirect Tax Applicable", "GSTIN / Registration Number"],
        "5": ["Status of Assessee"],
        "6": ["Previous Year"],
        "7": ["Assessment Year"],
        "8": ["Relevant Clause of Section 44AB"],
        "11": ["Books Maintained", "Books Examined", "Place of Maintenance"],
        "13": ["Method of Accounting", "Change from Previous Year", "Impact if any"],
        "14": ["Stock Valuation Method", "Change from Previous Year", "Impact if any"],
        "18": ["Block of Asset", "Opening WDV", "Additions", "Deletions", "Depreciation Allowable"],
        "21": ["Nature of Inadmissible Amount", "Section", "Amount", "Remarks"],
        "22": ["MSME Vendor", "Amount Outstanding", "Due Date", "Payment Date", "Disallowance"],
        "26": ["Nature of Liability", "Amount", "Due Date", "Payment Date", "Allowable / Disallowable"],
        "31": ["Nature of Transaction", "Party Name", "Amount", "Mode", "Section"],
        "34": ["TDS/TCS Section", "Amount Paid", "TDS/TCS Deducted", "Deposit Status", "Remarks"],
        "35": ["Item Name", "Opening Qty", "Purchases", "Sales", "Closing Qty"],
        "40": ["Ratio Name", "Current Year", "Previous Year", "Variance"],
        "41": ["AY", "Demand / Refund", "Amount", "Status"],
        "42": ["Form Type", "Reporting Requirement", "Filed / Not Filed", "Acknowledgement Number", "Remarks"],
        "43": ["International Group Applicable", "Master File Requirement", "CbCR Requirement", "Filing Status", "Remarks"],
        "44": ["Nature of Expenditure", "Registered Dealer Amount", "Unregistered Dealer Amount", "Composition Dealer Amount", "Exempt Supply Amount", "Total Amount"],
    }

    return specific_fields.get(clause_no, base_fields)


def load_tax_report(client_name, ay):
    folder = f"clients/{client_name}/AY {ay}/Tax Report"
    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/form_3cd_tax_report.json"

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    return {}


def save_tax_report(client_name, ay, report_data):
    folder = f"clients/{client_name}/AY {ay}/Tax Report"
    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/form_3cd_tax_report.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4)


def export_tax_report_excel(client_name, ay, report_data):
    folder = f"clients/{client_name}/AY {ay}/Tax Report"
    os.makedirs(folder, exist_ok=True)

    rows = []

    for clause_no, title in CLAUSES:
        data = report_data.get(clause_no, {})
        rows.append({
            "Clause No": clause_no,
            "Title": title,
            "Status": data.get("status", "Not Filled"),
            "Remarks": data.get("remarks", ""),
            "Saved Data": json.dumps(data.get("fields", {}), ensure_ascii=False)
        })

    df = pd.DataFrame(rows)
    excel_path = f"{folder}/form_3cd_tax_report_summary.xlsx"
    df.to_excel(excel_path, index=False)

    return excel_path


def show_tax_report():
    st.subheader("📑 Tax Report - Form 3CD Clause-wise Reporting")

    df = load_clients()

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    selected_client = st.selectbox(
        "Search / Select Client",
        client_list,
        index=0 if len(client_list) > 0 else None,
        placeholder="Search client name..."
    )

    if len(df) == 0 or not selected_client:
        st.info("Please select a client.")
        return

    selected_row = df[df["Client Name"] == selected_client].iloc[0]
    selected_ay = selected_row["AY"]

    report_data = load_tax_report(selected_client, selected_ay)

    rows = []

    for clause_no, title in CLAUSES:
        clause_saved = report_data.get(clause_no, {})
        rows.append({
            "Clause No": clause_no,
            "Title / Particulars": title,
            "Remark": clause_saved.get("status", "Not Filled"),
            "Auditor Remarks": clause_saved.get("remarks", "")
        })

    clause_df = pd.DataFrame(rows)

    st.write(f"### Client: {selected_client} | AY: {selected_ay}")
    st.dataframe(clause_df, use_container_width=True)

    selected_clause_display = st.selectbox(
        "Select Clause to Fill / Edit",
        [f"{no} - {title}" for no, title in CLAUSES]
    )

    selected_clause_no = selected_clause_display.split(" - ")[0]
    selected_clause_title = dict(CLAUSES)[selected_clause_no]

    @st.dialog(f"Clause {selected_clause_no} - {selected_clause_title}")
    def clause_dialog():
        existing = report_data.get(selected_clause_no, {})
        existing_fields = existing.get("fields", {})

        st.write("### Enter Clause Data")

        fields = get_clause_fields(selected_clause_no)
        filled_fields = {}

        for field in fields:
            filled_fields[field] = st.text_area(
                field,
                value=existing_fields.get(field, ""),
                height=80
            )

        remarks = st.text_area(
            "Final Auditor Remark",
            value=existing.get("remarks", ""),
            height=100
        )

        status = st.selectbox(
            "Clause Status",
            ["Not Filled", "Filled"],
            index=1 if existing.get("status", "Not Filled") == "Filled" else 0
        )

        if st.button("💾 Save Clause"):
            report_data[selected_clause_no] = {
                "title": selected_clause_title,
                "status": status,
                "remarks": remarks,
                "fields": filled_fields
            }

            save_tax_report(selected_client, selected_ay, report_data)

            st.success("✅ Clause saved successfully.")
            st.rerun()

    if st.button("📝 Open Selected Clause"):
        clause_dialog()

    st.divider()

    filled_count = len([
        c for c in report_data.values()
        if c.get("status") == "Filled"
    ])

    total_clauses = len(CLAUSES)
    completion = round((filled_count / total_clauses) * 100, 2)

    st.subheader("📊 Tax Report Completion")
    st.progress(completion / 100)
    st.write(f"**{filled_count} / {total_clauses} clauses filled ({completion}%)**")

    if st.button("📤 Export Tax Report Summary to Excel"):
        excel_path = export_tax_report_excel(selected_client, selected_ay, report_data)
        st.success(f"✅ Exported successfully: {excel_path}")