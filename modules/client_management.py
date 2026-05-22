import os
import re
import shutil

import pandas as pd
import streamlit as st

from utils.common import load_clients, save_clients


CLIENT_COLUMNS = [
    "Client Name",
    "Client Legal Name",
    "First Name",
    "Middle Name",
    "Last Name / Entity Name",
    "PAN",
    "Aadhaar",
    "Is GST Registered",
    "GSTIN",
    "GST State Code",
    "Indirect Tax Applicable",
    "Status of Assessee",
    "Country Code",
    "Flat / Door / Building",
    "Road / Street / Block / Sector",
    "Area / Locality",
    "Post Office",
    "District / City",
    "State",
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
    "Is GST Registered": "No",
    "GSTIN": "",
    "GST State Code": "",
    "Indirect Tax Applicable": "No",
    "Status of Assessee": "",
    "Country Code": "91",
    "Flat / Door / Building": "",
    "Road / Street / Block / Sector": "",
    "Area / Locality": "",
    "Post Office": "",
    "District / City": "",
    "State": "",
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


DOCUMENT_STATUS_OPTIONS = ["Pending", "Partially Received", "Received"]
AUDIT_STATUS_OPTIONS = ["Pending", "In Progress", "Completed"]
FILING_STATUS_OPTIONS = ["Not Filed", "Filed"]


def apply_client_management_style():
    st.markdown(
        """
        <style>
        .client-summary-card {
            padding: 18px 20px;
            border-radius: 18px;
            background: rgba(30, 41, 59, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.20);
            margin: 14px 0 22px 0;
        }
        .client-summary-title {
            font-size: 22px;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 8px;
        }
        .client-summary-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 12px;
        }
        .client-summary-item {
            padding: 12px 14px;
            border-radius: 14px;
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.14);
        }
        .client-summary-label {
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 4px;
        }
        .client-summary-value {
            font-size: 15px;
            color: #e5e7eb;
            font-weight: 700;
        }
        .section-card {
            padding: 18px;
            border-radius: 18px;
            background: rgba(15, 23, 42, 0.52);
            border: 1px solid rgba(148, 163, 184, 0.18);
            margin-bottom: 18px;
        }
        .danger-card {
            padding: 18px;
            border-radius: 18px;
            background: rgba(127, 29, 29, 0.18);
            border: 1px solid rgba(248, 113, 113, 0.28);
            margin-bottom: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_str(value):
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except Exception:
        pass

    return str(value)


def safe_key(value):
    return re.sub(r"[^A-Za-z0-9_]", "_", safe_str(value))


def ensure_client_columns(df):
    if df is None or df.empty:
        df = pd.DataFrame(columns=CLIENT_COLUMNS)

    for col in CLIENT_COLUMNS:
        if col not in df.columns:
            df[col] = DEFAULT_VALUES.get(col, "")

    return df


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


def get_index(options, value):
    value = safe_str(value)

    if value in options:
        return options.index(value)

    return 0


def calculate_previous_year_dates(ay):
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


def clear_global_selected_client_if_deleted(client_name, ay):
    if (
        st.session_state.get("global_selected_client") == client_name
        and safe_str(st.session_state.get("global_selected_ay")) == safe_str(ay)
    ):
        st.session_state["global_selected_client"] = None
        st.session_state["global_selected_ay"] = None


def delete_client_record(df, selected_index, delete_folder=False):
    client_name = safe_str(df.loc[selected_index, "Client Name"])
    ay = safe_str(df.loc[selected_index, "AY"])
    client_folder_path = get_client_folder_path(client_name, ay)

    df = df.drop(index=selected_index).reset_index(drop=True)
    save_clients(df)

    if delete_folder and os.path.exists(client_folder_path):
        shutil.rmtree(client_folder_path)

    clear_global_selected_client_if_deleted(client_name, ay)

    return client_name, ay


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
        "Audit Procedures",
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


@st.dialog("Confirm Delete Client")
def confirm_delete_client_dialog(df, selected_index, selected_client, selected_ay):
    st.markdown(f"**Client:** {selected_client}")
    st.markdown(f"**Assessment Year:** {selected_ay}")

    delete_folder = st.checkbox(
        "Delete client folder also",
        value=False,
        key=f"dialog_delete_folder_{safe_key(selected_client)}_{safe_key(selected_ay)}",
    )

    if delete_folder:
        st.warning("Client record and saved files for this AY will be deleted.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with c2:
        if st.button("Confirm Delete", type="primary", use_container_width=True):
            deleted_client, deleted_ay = delete_client_record(
                df=df,
                selected_index=selected_index,
                delete_folder=delete_folder,
            )

            st.session_state["global_selected_client"] = None
            st.session_state["global_selected_ay"] = None

            if "client_management_selected_client" in st.session_state:
                st.session_state["client_management_selected_client"] = "Select Client"

            st.success(f"Deleted: {deleted_client} | AY: {deleted_ay}")
            st.rerun()


def show_client_summary(row, selected_client, selected_ay):
    pan = safe_str(get_row_value(row, "PAN", ""))

    st.markdown(
        f"""
        <div class="client-summary-card">
            <div class="client-summary-title">{selected_client}</div>
            <div class="client-summary-grid">
                <div class="client-summary-item">
                    <div class="client-summary-label">PAN</div>
                    <div class="client-summary-value">{pan or "-"}</div>
                </div>
                <div class="client-summary-item">
                    <div class="client-summary-label">Assessment Year</div>
                    <div class="client-summary-value">{selected_ay or "-"}</div>
                </div>
                <div class="client-summary-item">
                    <div class="client-summary-label">Audit Status</div>
                    <div class="client-summary-value">{safe_str(get_row_value(row, "Audit Status", "Pending"))}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_client_management():
    apply_client_management_style()

    st.subheader("👥 Client Management")

    df = ensure_client_columns(load_clients())

    st.sidebar.header("➕ Add New Client")

    client_name = st.sidebar.text_input("Client Name", key="add_client_name")
    pan = st.sidebar.text_input("PAN Number", key="add_client_pan")
    ay = st.sidebar.text_input("Assessment Year", placeholder="Example: 2026-27", key="add_client_ay")

    add_client_btn = st.sidebar.button(
        "➕ Add Client",
        key="add_client_button",
        use_container_width=True,
    )

    if add_client_btn:
        if client_name.strip() == "" or pan.strip() == "" or ay.strip() == "":
            st.sidebar.error("Client Name, PAN Number and Assessment Year are mandatory.")
        else:
            py_start, py_end = calculate_previous_year_dates(ay)

            existing_match = df[
                (df["Client Name"].astype(str).str.lower() == client_name.strip().lower())
                & (df["AY"].astype(str) == ay.strip())
            ]

            if len(existing_match) > 0:
                st.sidebar.warning("Client already exists for this Assessment Year.")
            else:
                new_client = DEFAULT_VALUES.copy()

                new_client.update({
                    "Client Name": client_name.strip(),
                    "Client Legal Name": client_name.strip(),
                    "Last Name / Entity Name": client_name.strip(),
                    "PAN": pan.strip().upper(),
                    "AY": ay.strip(),
                    "Previous Year Start Date": py_start,
                    "Previous Year End Date": py_end,
                    "Document Status": "Pending",
                    "Audit Status": "Pending",
                    "3CD/3CA Filing Status": "Not Filed",
                    "ITR Filing Status": "Not Filed",
                    "Checklist Completion %": 0,
                })

                df = pd.concat([df, pd.DataFrame([new_client])], ignore_index=True)
                save_clients(df)
                create_client_folders_and_trackers(client_name.strip(), ay.strip())

                st.sidebar.success("Client added successfully.")
                st.rerun()

    df = ensure_client_columns(load_clients())

    if df.empty or "Client Name" not in df.columns:
        st.info("No clients added yet.")
        return

    client_list = sorted(df["Client Name"].dropna().astype(str).unique().tolist())
    client_options = ["Select Client"] + client_list

    if "client_management_selected_client" in st.session_state:
        if st.session_state["client_management_selected_client"] not in client_options:
            st.session_state["client_management_selected_client"] = "Select Client"

    selected_client = st.selectbox(
        "Search / Select Client",
        client_options,
        index=0,
        placeholder="Select client...",
        key="client_management_selected_client",
    )

    selected_record_ay = None
    selected_index = None

    if selected_client == "Select Client":
        filtered_df = df.copy()
        download_file_name = "all_clients_data.csv"
    else:
        client_records = df[df["Client Name"].astype(str) == selected_client].copy()

        if client_records.empty:
            st.warning("Selected client record not found.")
            return

        ay_options = client_records["AY"].dropna().astype(str).unique().tolist()

        if len(ay_options) > 1:
            selected_record_ay = st.selectbox(
                "Select Assessment Year",
                ay_options,
                index=0,
                key="client_management_selected_ay",
            )
            filtered_df = client_records[client_records["AY"].astype(str) == selected_record_ay].copy()
        else:
            selected_record_ay = safe_str(client_records.iloc[0]["AY"])
            filtered_df = client_records.copy()

        selected_index = filtered_df.index[0]
        download_file_name = f"{selected_client}_client_data.csv"

    if selected_client != "Select Client" and selected_index is not None and not filtered_df.empty:
        row = df.loc[selected_index]

        show_client_summary(row, selected_client, selected_record_ay)

        st.markdown("## 📌 Filing Status")

        with st.form("client_filing_status_form"):
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                edit_document_status = st.selectbox(
                    "Document Status",
                    DOCUMENT_STATUS_OPTIONS,
                    index=get_index(DOCUMENT_STATUS_OPTIONS, get_row_value(row, "Document Status", "Pending")),
                )

            with c2:
                edit_audit_status = st.selectbox(
                    "Audit Status",
                    AUDIT_STATUS_OPTIONS,
                    index=get_index(AUDIT_STATUS_OPTIONS, get_row_value(row, "Audit Status", "Pending")),
                )

            with c3:
                edit_tax_audit_filing = st.selectbox(
                    "3CD/3CA Filing Status",
                    FILING_STATUS_OPTIONS,
                    index=get_index(FILING_STATUS_OPTIONS, get_row_value(row, "3CD/3CA Filing Status", "Not Filed")),
                )

            with c4:
                edit_itr_status = st.selectbox(
                    "ITR Filing Status",
                    FILING_STATUS_OPTIONS,
                    index=get_index(FILING_STATUS_OPTIONS, get_row_value(row, "ITR Filing Status", "Not Filed")),
                )

            save_status_btn = st.form_submit_button("💾 Save Filing Status")

        if save_status_btn:
            df.loc[selected_index, "Document Status"] = edit_document_status
            df.loc[selected_index, "Audit Status"] = edit_audit_status
            df.loc[selected_index, "3CD/3CA Filing Status"] = edit_tax_audit_filing
            df.loc[selected_index, "ITR Filing Status"] = edit_itr_status

            save_clients(df)
            st.success("Filing status saved successfully.")
            st.rerun()

        st.divider()

        delete_col1, delete_col2 = st.columns([3, 1])

        with delete_col1:
            st.markdown("## 🗑️ Delete Client")

        with delete_col2:
            if st.button(
                "Delete Client",
                type="primary",
                key=f"open_delete_dialog_{safe_key(selected_client)}_{safe_key(selected_record_ay)}",
                use_container_width=True,
            ):
                confirm_delete_client_dialog(
                    df=df,
                    selected_index=selected_index,
                    selected_client=selected_client,
                    selected_ay=selected_record_ay,
                )

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
        "PAN",
        "AY",
        "Previous Year Start Date",
        "Previous Year End Date",
        "Document Status",
        "Audit Status",
        "3CD/3CA Filing Status",
        "ITR Filing Status",
    ]

    display_columns = [col for col in display_columns if col in filtered_df.columns]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )
