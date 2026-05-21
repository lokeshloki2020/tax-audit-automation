import os
from datetime import date

import pandas as pd
import streamlit as st

from utils.common import load_clients, save_clients


# ---------------------------------------------------------
# MASTER COLUMNS REQUIRED FOR PHASE 1 AUTOMATION
# ---------------------------------------------------------

CLIENT_COLUMNS = [
    "Client Name",
    "Client Legal Name",
    "First Name",
    "Middle Name",
    "Last Name / Entity Name",
    "PAN",
    "Aadhaar",
    "GSTIN",
    "Indirect Tax Applicable",
    "GST State Code",
    "Status of Assessee",
    "Country Code",
    "Flat / Door / Building",
    "Road / Street / Block / Sector",
    "Area / Locality",
    "Post Office",
    "District / City",
    "State Code",
    "PIN Code",
    "AY",
    "Previous Year Start Date",
    "Previous Year End Date",
    "Audited Under Other Law",
    "Law Under Which Audited",
    "Statutory Auditor / Firm Name",
    "Statutory Audit Report Date",
    "Books Head Office Address",
    "Branch Details",
    "Document Status",
    "Audit Status",
    "3CD/3CA Filing Status",
    "ITR Filing Status",
    "Assigned Staff",
    "Checklist Completion %",
]


DEFAULT_VALUES = {
    "Client Name": "",
    "Client Legal Name": "",
    "First Name": "",
    "Middle Name": "",
    "Last Name / Entity Name": "",
    "PAN": "",
    "Aadhaar": "",
    "GSTIN": "",
    "Indirect Tax Applicable": "No",
    "GST State Code": "",
    "Status of Assessee": "Individual",
    "Country Code": "91",
    "Flat / Door / Building": "",
    "Road / Street / Block / Sector": "",
    "Area / Locality": "",
    "Post Office": "",
    "District / City": "",
    "State Code": "",
    "PIN Code": "",
    "AY": "",
    "Previous Year Start Date": "",
    "Previous Year End Date": "",
    "Audited Under Other Law": "No",
    "Law Under Which Audited": "",
    "Statutory Auditor / Firm Name": "",
    "Statutory Audit Report Date": "",
    "Books Head Office Address": "",
    "Branch Details": "",
    "Document Status": "Pending",
    "Audit Status": "Pending",
    "3CD/3CA Filing Status": "Not Filed",
    "ITR Filing Status": "Not Filed",
    "Assigned Staff": "",
    "Checklist Completion %": 0,
}


STATUS_OPTIONS = [
    "Individual",
    "HUF",
    "Firm",
    "LLP",
    "Company",
    "Trust",
    "AOP",
    "Local Authority",
    "Artificial Juridical Person",
    "Co-operative Society",
    "Co-operative Bank",
    "Body of Individuals",
]


STATE_CODE_OPTIONS = [
    "",
    "01-Andaman and Nicobar Islands",
    "02-Andhra Pradesh",
    "03-Arunachal Pradesh",
    "04-Assam",
    "05-Bihar",
    "06-Chandigarh",
    "07-Dadra and Nagar Haveli",
    "08-Daman and Diu",
    "09-Delhi",
    "10-Goa",
    "11-Gujarat",
    "12-Haryana",
    "13-Himachal Pradesh",
    "14-Jammu and Kashmir",
    "15-Karnataka",
    "16-Kerala",
    "17-Lakshadweep",
    "18-Madhya Pradesh",
    "19-Maharashtra",
    "20-Manipur",
    "21-Meghalaya",
    "22-Mizoram",
    "23-Nagaland",
    "24-Odisha",
    "25-Puducherry",
    "26-Punjab",
    "27-Rajasthan",
    "28-Sikkim",
    "29-Tamil Nadu",
    "30-Tripura",
    "31-Uttar Pradesh",
    "32-West Bengal",
    "33-Chhattisgarh",
    "34-Uttarakhand",
    "35-Jharkhand",
    "36-Telangana",
    "37-Ladakh",
    "99-Foreign",
]


AUDIT_LAW_OPTIONS = [
    "",
    "Companies Act, 2013",
    "Limited Liability Partnership Act, 2008",
    "Co-operative Societies Act",
    "Societies Registration Act",
    "Trust Act",
    "Other Law",
]


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def ensure_client_columns(df):
    if df is None or df.empty:
        df = pd.DataFrame(columns=CLIENT_COLUMNS)

    for col in CLIENT_COLUMNS:
        if col not in df.columns:
            df[col] = DEFAULT_VALUES.get(col, "")

    return df


def safe_str(value):
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value)


def get_state_code(value):
    value = safe_str(value)

    if "-" in value:
        return value.split("-")[0].strip()

    return value.strip()


def calculate_previous_year_dates(ay):
    """
    Converts AY 2026-27 to:
    Previous Year Start Date: 2025-04-01
    Previous Year End Date: 2026-03-31
    """

    ay = safe_str(ay).strip()

    if not ay:
        return "", ""

    try:
        if "-" in ay:
            start_year = int(ay.split("-")[0]) - 1
        else:
            start_year = int(ay) - 1

        return f"{start_year}-04-01", f"{start_year + 1}-03-31"

    except Exception:
        return "", ""


def get_client_folder_path(client_name, ay):
    return f"clients/{client_name}/AY {ay}"


def create_client_folders_and_trackers(client_name, ay):
    base_path = get_client_folder_path(client_name, ay)

    folders = [
        "Bank Statements",
        "GST Returns",
        "TDS",
        "Financial Statements",
        "Audit Working Papers",
        "Form 3CD",
        "Final Filing",
        "Tax Report",
        "Tax Audit Applicability",
    ]

    for folder in folders:
        os.makedirs(f"{base_path}/{folder}", exist_ok=True)

    checklist_path = f"{base_path}/document_checklist.xlsx"

    if not os.path.exists(checklist_path):
        checklist_items = [
            "PAN Card / PAN Verification",
            "Aadhaar, if applicable",
            "GST Registration Certificate",
            "Address Proof / Registered Office Proof",
            "Certificate of Incorporation / Partnership Deed / LLP Agreement / Trust Deed",
            "Previous Year ITR",
            "Previous Year Tax Audit Report",
            "Signed Financial Statements",
            "Statutory Audit Report, if Form 3CA",
            "Branch Details, if any",
            "Final Trial Balance",
            "Profit & Loss Account",
            "Balance Sheet",
            "Fixed Asset Register",
            "GST Returns - GSTR-1",
            "GST Returns - GSTR-3B",
            "GSTR-2B",
            "TDS Returns",
            "Form 26AS",
            "AIS/TIS",
            "Cash Book",
            "Bank Book",
            "Loan Statements",
            "Debtors List",
            "Creditors List",
            "Stock Details",
        ]

        checklist_df = pd.DataFrame({
            "Document Name": checklist_items,
            "Status": ["Pending"] * len(checklist_items),
            "Remarks": [""] * len(checklist_items),
        })

        checklist_df.to_excel(checklist_path, index=False)

    wp_path = f"{base_path}/working_papers_tracker.xlsx"

    if not os.path.exists(wp_path):
        working_papers = [
            ["Trial Balance Verification", "General"],
            ["Financial Statements Verification", "General"],
            ["Profit and Loss Verification", "General"],
            ["Balance Sheet Verification", "General"],
            ["Depreciation Schedule", "Clause 18"],
            ["TDS Reconciliation", "Clause 34"],
            ["GST Reconciliation", "Clause 44"],
            ["Clause 44 Working", "Clause 44"],
            ["Cash Payment Verification", "Clause 21"],
            ["Loan Verification", "Clause 31"],
            ["Related Party Transactions", "Clause 23"],
            ["Quantitative Details", "Clause 35"],
            ["Stock Verification", "Clause 35"],
            ["Form 26AS Reconciliation", "General"],
            ["AIS/TIS Verification", "General"],
            ["Section 43B Verification", "Clause 26"],
            ["MSME Verification", "Clause 22"],
            ["Accounting Ratios", "Clause 40"],
        ]

        wp_df = pd.DataFrame(
            working_papers,
            columns=["Working Paper", "Clause Reference"]
        )

        wp_df["Status"] = "Pending"
        wp_df["Prepared By"] = ""
        wp_df["Reviewed By"] = ""
        wp_df["Remarks"] = ""

        wp_df.to_excel(wp_path, index=False)


def get_row_value(row, column, default=""):
    if column not in row:
        return default

    value = row[column]

    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return value


# ---------------------------------------------------------
# MAIN MODULE
# ---------------------------------------------------------

def show_client_management():
    st.subheader("👥 Client Management")

    df = ensure_client_columns(load_clients())

    # ---------------------------------------------------------
    # ADD NEW CLIENT - SIDEBAR
    # ---------------------------------------------------------

    st.sidebar.header("➕ Add New Client")

    with st.sidebar.form("add_client_form", clear_on_submit=False):
        client_name = st.text_input("Client Display Name")
        client_legal_name = st.text_input("Client Legal Name / Entity Name")
        pan = st.text_input("PAN")
        ay = st.text_input("Assessment Year", placeholder="Example: 2026-27")
        assigned_staff = st.text_input("Assigned Staff")

        status_of_assessee = st.selectbox(
            "Status of Assessee",
            STATUS_OPTIONS,
            index=0,
        )

        gstin = st.text_input("GSTIN")
        indirect_tax_applicable = st.selectbox(
            "Indirect Tax Applicable",
            ["No", "Yes"],
            index=1 if gstin else 0,
        )

        audited_under_other_law = st.selectbox(
            "Audited Under Other Law?",
            ["No", "Yes"],
            index=0,
        )

        add_client_btn = st.form_submit_button("➕ Add Client")

    if add_client_btn:
        if client_name.strip() == "" or pan.strip() == "" or ay.strip() == "":
            st.sidebar.error("Client Name, PAN and Assessment Year are mandatory.")
        else:
            py_start, py_end = calculate_previous_year_dates(ay)

            existing_match = df[
                (df["Client Name"].astype(str).str.lower() == client_name.strip().lower()) &
                (df["AY"].astype(str) == ay.strip())
            ]

            if len(existing_match) > 0:
                st.sidebar.warning("Client already exists for this Assessment Year.")
            else:
                new_client = DEFAULT_VALUES.copy()

                new_client.update({
                    "Client Name": client_name.strip(),
                    "Client Legal Name": client_legal_name.strip() or client_name.strip(),
                    "Last Name / Entity Name": client_legal_name.strip() or client_name.strip(),
                    "PAN": pan.strip().upper(),
                    "GSTIN": gstin.strip().upper(),
                    "Indirect Tax Applicable": indirect_tax_applicable,
                    "Status of Assessee": status_of_assessee,
                    "AY": ay.strip(),
                    "Previous Year Start Date": py_start,
                    "Previous Year End Date": py_end,
                    "Audited Under Other Law": audited_under_other_law,
                    "Assigned Staff": assigned_staff.strip(),
                    "Document Status": "Pending",
                    "Audit Status": "Pending",
                    "3CD/3CA Filing Status": "Not Filed",
                    "ITR Filing Status": "Not Filed",
                    "Checklist Completion %": 0,
                })

                df = pd.concat([df, pd.DataFrame([new_client])], ignore_index=True)
                save_clients(df)

                create_client_folders_and_trackers(client_name.strip(), ay.strip())

                st.sidebar.success("✅ Client added successfully.")
                st.rerun()

    # ---------------------------------------------------------
    # CLIENT SELECTION
    # ---------------------------------------------------------

    df = ensure_client_columns(load_clients())

    if df.empty or "Client Name" not in df.columns:
        st.info("No clients added yet. Add a new client from the sidebar.")
        return

    client_list = sorted(df["Client Name"].dropna().astype(str).unique().tolist())
    client_options = ["Select Client"] + client_list

    selected_client = st.selectbox(
        "Search / Select Client",
        client_options,
        index=0,
        placeholder="Select client...",
        key="client_management_selected_client",
    )

    if selected_client == "Select Client":
        st.info("Showing all clients. Select a client to view or edit master details.")
        filtered_df = df.copy()
        download_file_name = "all_clients_data.csv"
    else:
        filtered_df = df[df["Client Name"].astype(str) == selected_client].copy()
        download_file_name = f"{selected_client}_client_data.csv"

    # ---------------------------------------------------------
    # SELECTED CLIENT MASTER EDIT
    # ---------------------------------------------------------

    if selected_client != "Select Client" and not filtered_df.empty:
        selected_index = filtered_df.index[0]
        row = df.loc[selected_index]

        st.markdown("## 🧾 Phase 1 Master Data for 3CA / 3CB / 3CD Clause 1 to 8")

        with st.form("client_master_edit_form"):
            st.write("### 1. Basic Details")

            b1, b2, b3 = st.columns(3)

            with b1:
                edit_client_name = st.text_input(
                    "Client Display Name",
                    value=safe_str(get_row_value(row, "Client Name")),
                )

                edit_client_legal_name = st.text_input(
                    "Client Legal Name",
                    value=safe_str(get_row_value(row, "Client Legal Name")),
                )

                edit_pan = st.text_input(
                    "PAN",
                    value=safe_str(get_row_value(row, "PAN")),
                )

            with b2:
                edit_first_name = st.text_input(
                    "First Name",
                    value=safe_str(get_row_value(row, "First Name")),
                )

                edit_middle_name = st.text_input(
                    "Middle Name",
                    value=safe_str(get_row_value(row, "Middle Name")),
                )

                edit_last_name = st.text_input(
                    "Last Name / Entity Name",
                    value=safe_str(get_row_value(row, "Last Name / Entity Name")),
                )

            with b3:
                edit_aadhaar = st.text_input(
                    "Aadhaar, if available",
                    value=safe_str(get_row_value(row, "Aadhaar")),
                )

                current_status = safe_str(get_row_value(row, "Status of Assessee", "Individual"))

                edit_status = st.selectbox(
                    "Status of Assessee",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 0,
                )

                edit_assigned_staff = st.text_input(
                    "Assigned Staff",
                    value=safe_str(get_row_value(row, "Assigned Staff")),
                )

            st.write("### 2. Address Details")

            a1, a2, a3 = st.columns(3)

            with a1:
                edit_country_code = st.text_input(
                    "Country Code",
                    value=safe_str(get_row_value(row, "Country Code", "91")),
                )

                edit_flat = st.text_input(
                    "Flat / Door / Building",
                    value=safe_str(get_row_value(row, "Flat / Door / Building")),
                )

                edit_road = st.text_input(
                    "Road / Street / Block / Sector",
                    value=safe_str(get_row_value(row, "Road / Street / Block / Sector")),
                )

            with a2:
                edit_area = st.text_input(
                    "Area / Locality",
                    value=safe_str(get_row_value(row, "Area / Locality")),
                )

                edit_post_office = st.text_input(
                    "Post Office",
                    value=safe_str(get_row_value(row, "Post Office")),
                )

                edit_district = st.text_input(
                    "District / City",
                    value=safe_str(get_row_value(row, "District / City")),
                )

            with a3:
                current_state_code = safe_str(get_row_value(row, "State Code"))

                edit_state_code_display = st.selectbox(
                    "State Code",
                    STATE_CODE_OPTIONS,
                    index=STATE_CODE_OPTIONS.index(current_state_code)
                    if current_state_code in STATE_CODE_OPTIONS else 0,
                )

                edit_pin = st.text_input(
                    "PIN Code",
                    value=safe_str(get_row_value(row, "PIN Code")),
                )

            st.write("### 3. GST / Indirect Tax Details")

            g1, g2, g3 = st.columns(3)

            with g1:
                edit_gstin = st.text_input(
                    "GSTIN",
                    value=safe_str(get_row_value(row, "GSTIN")),
                )

            with g2:
                current_indirect = safe_str(get_row_value(row, "Indirect Tax Applicable", "No"))

                edit_indirect = st.selectbox(
                    "Indirect Tax Applicable",
                    ["No", "Yes"],
                    index=["No", "Yes"].index(current_indirect) if current_indirect in ["No", "Yes"] else 0,
                )

            with g3:
                current_gst_state = safe_str(get_row_value(row, "GST State Code"))

                edit_gst_state_display = st.selectbox(
                    "GST State Code",
                    STATE_CODE_OPTIONS,
                    index=STATE_CODE_OPTIONS.index(current_gst_state)
                    if current_gst_state in STATE_CODE_OPTIONS else 0,
                )

            st.write("### 4. Assessment Year / Previous Year")

            y1, y2, y3 = st.columns(3)

            with y1:
                edit_ay = st.text_input(
                    "Assessment Year",
                    value=safe_str(get_row_value(row, "AY")),
                )

            auto_py_start, auto_py_end = calculate_previous_year_dates(edit_ay)

            with y2:
                edit_py_start = st.text_input(
                    "Previous Year Start Date",
                    value=safe_str(get_row_value(row, "Previous Year Start Date")) or auto_py_start,
                )

            with y3:
                edit_py_end = st.text_input(
                    "Previous Year End Date",
                    value=safe_str(get_row_value(row, "Previous Year End Date")) or auto_py_end,
                )

            st.write("### 5. 3CA / 3CB Report Master Details")

            r1, r2, r3 = st.columns(3)

            with r1:
                current_audited_other = safe_str(get_row_value(row, "Audited Under Other Law", "No"))

                edit_audited_other_law = st.selectbox(
                    "Audited Under Other Law?",
                    ["No", "Yes"],
                    index=["No", "Yes"].index(current_audited_other)
                    if current_audited_other in ["No", "Yes"] else 0,
                )

            with r2:
                current_law = safe_str(get_row_value(row, "Law Under Which Audited"))

                edit_law = st.selectbox(
                    "Law Under Which Audited",
                    AUDIT_LAW_OPTIONS,
                    index=AUDIT_LAW_OPTIONS.index(current_law) if current_law in AUDIT_LAW_OPTIONS else 0,
                )

            with r3:
                edit_stat_auditor = st.text_input(
                    "Statutory Auditor / Firm Name",
                    value=safe_str(get_row_value(row, "Statutory Auditor / Firm Name")),
                )

            r4, r5 = st.columns(2)

            with r4:
                edit_stat_audit_date = st.text_input(
                    "Statutory Audit Report Date",
                    value=safe_str(get_row_value(row, "Statutory Audit Report Date")),
                    placeholder="YYYY-MM-DD",
                )

            with r5:
                edit_books_head_office = st.text_input(
                    "Books Head Office Address",
                    value=safe_str(get_row_value(row, "Books Head Office Address")),
                )

            edit_branch_details = st.text_area(
                "Branch Details",
                value=safe_str(get_row_value(row, "Branch Details")),
                height=80,
            )

            st.write("### 6. Filing Status")

            s1, s2, s3, s4 = st.columns(4)

            with s1:
                edit_document_status = st.selectbox(
                    "Document Status",
                    ["Pending", "Partially Received", "Received"],
                    index=["Pending", "Partially Received", "Received"].index(
                        safe_str(get_row_value(row, "Document Status", "Pending"))
                    )
                    if safe_str(get_row_value(row, "Document Status", "Pending")) in ["Pending", "Partially Received", "Received"]
                    else 0,
                )

            with s2:
                edit_audit_status = st.selectbox(
                    "Audit Status",
                    ["Pending", "In Progress", "Completed"],
                    index=["Pending", "In Progress", "Completed"].index(
                        safe_str(get_row_value(row, "Audit Status", "Pending"))
                    )
                    if safe_str(get_row_value(row, "Audit Status", "Pending")) in ["Pending", "In Progress", "Completed"]
                    else 0,
                )

            with s3:
                edit_tax_audit_filing = st.selectbox(
                    "3CD/3CA Filing Status",
                    ["Not Filed", "Filed"],
                    index=["Not Filed", "Filed"].index(
                        safe_str(get_row_value(row, "3CD/3CA Filing Status", "Not Filed"))
                    )
                    if safe_str(get_row_value(row, "3CD/3CA Filing Status", "Not Filed")) in ["Not Filed", "Filed"]
                    else 0,
                )

            with s4:
                edit_itr_status = st.selectbox(
                    "ITR Filing Status",
                    ["Not Filed", "Filed"],
                    index=["Not Filed", "Filed"].index(
                        safe_str(get_row_value(row, "ITR Filing Status", "Not Filed"))
                    )
                    if safe_str(get_row_value(row, "ITR Filing Status", "Not Filed")) in ["Not Filed", "Filed"]
                    else 0,
                )

            save_master_btn = st.form_submit_button("💾 Save Client Master Data")

        if save_master_btn:
            final_state_code = get_state_code(edit_state_code_display)
            final_gst_state_code = get_state_code(edit_gst_state_display)

            df.loc[selected_index, "Client Name"] = edit_client_name.strip()
            df.loc[selected_index, "Client Legal Name"] = edit_client_legal_name.strip() or edit_client_name.strip()
            df.loc[selected_index, "First Name"] = edit_first_name.strip()
            df.loc[selected_index, "Middle Name"] = edit_middle_name.strip()
            df.loc[selected_index, "Last Name / Entity Name"] = edit_last_name.strip() or edit_client_legal_name.strip() or edit_client_name.strip()
            df.loc[selected_index, "PAN"] = edit_pan.strip().upper()
            df.loc[selected_index, "Aadhaar"] = edit_aadhaar.strip()
            df.loc[selected_index, "GSTIN"] = edit_gstin.strip().upper()
            df.loc[selected_index, "Indirect Tax Applicable"] = edit_indirect
            df.loc[selected_index, "GST State Code"] = final_gst_state_code
            df.loc[selected_index, "Status of Assessee"] = edit_status
            df.loc[selected_index, "Country Code"] = edit_country_code.strip() or "91"
            df.loc[selected_index, "Flat / Door / Building"] = edit_flat.strip()
            df.loc[selected_index, "Road / Street / Block / Sector"] = edit_road.strip()
            df.loc[selected_index, "Area / Locality"] = edit_area.strip()
            df.loc[selected_index, "Post Office"] = edit_post_office.strip()
            df.loc[selected_index, "District / City"] = edit_district.strip()
            df.loc[selected_index, "State Code"] = final_state_code
            df.loc[selected_index, "PIN Code"] = edit_pin.strip()
            df.loc[selected_index, "AY"] = edit_ay.strip()
            df.loc[selected_index, "Previous Year Start Date"] = edit_py_start.strip()
            df.loc[selected_index, "Previous Year End Date"] = edit_py_end.strip()
            df.loc[selected_index, "Audited Under Other Law"] = edit_audited_other_law
            df.loc[selected_index, "Law Under Which Audited"] = edit_law
            df.loc[selected_index, "Statutory Auditor / Firm Name"] = edit_stat_auditor.strip()
            df.loc[selected_index, "Statutory Audit Report Date"] = edit_stat_audit_date.strip()
            df.loc[selected_index, "Books Head Office Address"] = edit_books_head_office.strip()
            df.loc[selected_index, "Branch Details"] = edit_branch_details.strip()
            df.loc[selected_index, "Document Status"] = edit_document_status
            df.loc[selected_index, "Audit Status"] = edit_audit_status
            df.loc[selected_index, "3CD/3CA Filing Status"] = edit_tax_audit_filing
            df.loc[selected_index, "ITR Filing Status"] = edit_itr_status
            df.loc[selected_index, "Assigned Staff"] = edit_assigned_staff.strip()

            save_clients(df)
            st.success("✅ Client master data saved successfully.")
            st.rerun()

    # ---------------------------------------------------------
    # CLIENT DATABASE SUMMARY
    # ---------------------------------------------------------

    st.divider()

    title_col, download_col = st.columns([9, 1])

    with title_col:
        st.subheader("📋 Client Database")

    with download_col:
        st.download_button(
            label="⬇",
            data=filtered_df.to_csv(index=False),
            file_name=download_file_name,
            mime="text/csv",
            help="Download client data",
        )

    display_columns = [
        "Client Name",
        "Client Legal Name",
        "PAN",
        "GSTIN",
        "Status of Assessee",
        "AY",
        "Audited Under Other Law",
        "Document Status",
        "Audit Status",
        "3CD/3CA Filing Status",
        "ITR Filing Status",
        "Assigned Staff",
        "Checklist Completion %",
    ]

    display_columns = [col for col in display_columns if col in filtered_df.columns]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )