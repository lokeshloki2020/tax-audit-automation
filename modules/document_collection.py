import os
import pandas as pd
import streamlit as st

from utils.common import load_clients, save_clients, get_document_status


# ---------------------------------------------------------
# MASTER DOCUMENT CATEGORIES
# ---------------------------------------------------------

DOCUMENT_CATEGORIES = {
    "Basic Books Data": [
        "Trial_Balance",
        "Ledger_Master",
        "Ledger_Details",
        "Opening_Balances",
        "Financial_Statements",
        "Profit_and_Loss",
        "Balance_Sheet",
        "Previous_Year_Financials",
        "Income_Ledgers",
        "Expense_Ledgers",
        "Journal_Register",
    ],

    "Sales and Purchase Data": [
        "Books_Sales",
        "Books_Purchases",
        "Sales_Register",
        "Purchase_Register",
        "Customer_Master",
        "Vendor_Master",
    ],

    "GST Data": [
        "GSTR1",
        "GSTR3B",
        "GSTR2A",
        "GSTR2B",
        "GST_Output_Ledger",
        "GST_Input_Ledger",
        "GST_Ledger",
        "GST_ITC_Books",
        "GST_Payments",
        "GST_Return_Status",
        "GSTIN_Master",
    ],

    "TDS / TCS Data": [
        "Expense_Ledgers",
        "TDS_Deducted",
        "TDS_Payments",
        "TDS_Returns",
        "TDS_Ledger",
        "TDS_Receivable_Ledger",
        "Form_26Q",
        "Form_24Q",
        "Form_27Q",
        "Form_27EQ",
        "Form_26AS",
        "AIS_TIS",
        "Vendor_Master",
        "Customer_Master",
        "Payment_Register",
        "Receipt_Register",
        "Salary_Register",
    ],

    "Statutory Dues and 43B Data": [
        "Statutory_Dues",
        "GST_Return_Status",
        "GST_Ledger",
        "GST_Payments",
        "GSTR3B",
        "TDS_Ledger",
        "TDS_Deducted",
        "TDS_Payments",
        "TDS_Returns",
        "PF_ESI_Details",
        "PF_Returns",
        "ESI_Returns",
        "Professional_Tax_Returns",
        "Bonus_Details",
        "Leave_Encashment_Details",
        "Interest_To_Banks_FI",
        "Loan_Interest_Details",
        "Payment_Register",
        "Bank_Book",
        "Ledger_Details",
    ],

    "Payroll / PF / ESI Data": [
        "Salary_Register",
        "PF_ESI_Details",
        "PF_Returns",
        "ESI_Returns",
        "PF_Challans",
        "ESI_Challans",
        "Payment_Register",
        "Ledger_Details",
        "Bank_Book",
    ],

    "Loans and Finance Data": [
        "Loan_Details",
        "Interest_To_Banks_FI",
        "Loan_Interest_Details",
        "Party_Master",
        "Bank_Book",
        "Cash_Book",
        "Receipt_Register",
        "Payment_Register",
    ],

    "Fixed Assets and Depreciation Data": [
        "Fixed_Asset_Register",
        "Additions",
        "Deletions",
        "Depreciation_As_Per_Books",
        "Depreciation_As_Per_IT",
        "Purchase_Register",
        "Trial_Balance",
        "Ledger_Details",
    ],

    "Related Party Data": [
        "Related_Party_Master",
        "Partner_Director_Details",
        "Ledger_Details",
        "Expense_Ledgers",
        "Payment_Register",
        "Loan_Details",
    ],

    "MSME Data": [
        "MSME_Vendor_List",
        "Creditor_Ageing",
        "Outstanding_Payables",
        "Vendor_Master",
        "Purchase_Register",
        "Payment_Register",
        "Ledger_Details",
    ],

    "Stock and Quantitative Data": [
        "Stock_Register",
        "Production_Register",
        "Opening_Stock",
        "Closing_Stock",
        "Physical_Verification_Report",
        "Purchase_Register",
        "Sales_Register",
        "Trial_Balance",
    ],

    "Balance Sheet Supporting Data": [
        "Debtor_Ageing",
        "Creditor_Ageing",
        "Outstanding_Receivables",
        "Outstanding_Payables",
        "Capital_Account",
        "Loan_Details",
        "Fixed_Asset_Register",
        "Statutory_Dues",
    ],

    "Other Tax and Reporting Data": [
        "Tax_Demand_Refund_Details",
        "GST_Orders",
        "VAT_Orders",
        "Professional_Tax_Orders",
        "Other_Tax_Orders",
        "Appeal_Details",
        "SFT_Transactions",
        "Form_61_61A_61B_Status",
        "High_Value_Transactions",
    ],

    "Final Audit Review Data": [
        "Exception_Report",
        "Management_Reply",
        "Auditor_Remarks",
        "Final_Adjustments",
        "Tax_Report_Linkage",
    ],
}


# ---------------------------------------------------------
# STYLE
# ---------------------------------------------------------

def apply_document_collection_style():
    st.markdown("""
    <style>
    .doc-hero {
        padding: 24px;
        border-radius: 22px;
        background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.22);
    }
    .doc-hero h2 {
        margin: 0;
        font-size: 34px;
        font-weight: 800;
    }
    .doc-hero p {
        margin-top: 8px;
        font-size: 16px;
        opacity: 0.95;
    }
    .active-client-strip {
        padding: 14px 18px;
        border-radius: 16px;
        background: #ecfdf5;
        border-left: 6px solid #10b981;
        color: #064e3b;
        margin-bottom: 18px;
        font-weight: 700;
    }
    .category-card {
        padding: 18px;
        border-radius: 18px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.08);
        margin-bottom: 12px;
    }
    .category-title {
        font-size: 18px;
        font-weight: 800;
        color: #111827;
    }
    .category-sub {
        color: #6b7280;
        font-size: 14px;
    }
    .section-banner {
        padding: 14px 18px;
        border-radius: 16px;
        background: #f8fafc;
        border-left: 6px solid #2563eb;
        margin-top: 12px;
        margin-bottom: 16px;
    }
    </style>
    """, unsafe_allow_html=True)


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
# CHECKLIST HELPERS
# ---------------------------------------------------------

def get_default_checklist_df():
    rows = []

    for category, documents in DOCUMENT_CATEGORIES.items():
        for doc in documents:
            rows.append({
                "Category": category,
                "Document Name": doc,
                "Status": "Pending",
                "Remarks": ""
            })

    return pd.DataFrame(rows)


def clean_checklist_df(checklist_df):
    if checklist_df is None or checklist_df.empty:
        checklist_df = get_default_checklist_df()

    required_columns = ["Category", "Document Name", "Status", "Remarks"]

    for col in required_columns:
        if col not in checklist_df.columns:
            checklist_df[col] = ""

    checklist_df["Category"] = checklist_df["Category"].astype(str)
    checklist_df["Document Name"] = checklist_df["Document Name"].astype(str)
    checklist_df["Status"] = checklist_df["Status"].astype(str)
    checklist_df["Remarks"] = checklist_df["Remarks"].astype(str).replace("nan", "")

    checklist_df.loc[
        ~checklist_df["Status"].isin(["Pending", "Received", "Not Applicable"]),
        "Status"
    ] = "Pending"

    doc_to_category = {}

    for category, documents in DOCUMENT_CATEGORIES.items():
        for doc in documents:
            doc_to_category[doc] = category

    checklist_df["Category"] = checklist_df.apply(
        lambda row: (
            doc_to_category.get(row["Document Name"], "Other Documents")
            if str(row["Category"]).strip() in ["", "nan", "None"]
            else row["Category"]
        ),
        axis=1
    )

    existing_pairs = set(
        zip(
            checklist_df["Category"].astype(str),
            checklist_df["Document Name"].astype(str)
        )
    )

    new_rows = []

    for category, documents in DOCUMENT_CATEGORIES.items():
        for doc in documents:
            if (category, doc) not in existing_pairs:
                new_rows.append({
                    "Category": category,
                    "Document Name": doc,
                    "Status": "Pending",
                    "Remarks": ""
                })

    if new_rows:
        checklist_df = pd.concat(
            [checklist_df, pd.DataFrame(new_rows)],
            ignore_index=True
        )

    checklist_df = checklist_df[["Category", "Document Name", "Status", "Remarks"]]

    return checklist_df


def load_or_create_checklist(checklist_path):
    if os.path.exists(checklist_path):
        checklist_df = pd.read_excel(checklist_path)
        checklist_df = clean_checklist_df(checklist_df)
    else:
        checklist_df = get_default_checklist_df()

    os.makedirs(os.path.dirname(checklist_path), exist_ok=True)
    checklist_df.to_excel(checklist_path, index=False)

    return checklist_df


def build_category_summary(checklist_df):
    rows = []

    for category in DOCUMENT_CATEGORIES.keys():
        cat_df = checklist_df[checklist_df["Category"] == category]

        total_docs = len(cat_df)
        received_docs = len(cat_df[cat_df["Status"].isin(["Received", "Not Applicable"])])
        pending_docs = len(cat_df[cat_df["Status"] == "Pending"])

        completion = round((received_docs / total_docs) * 100, 2) if total_docs > 0 else 0

        rows.append({
            "Category": category,
            "Data Received": total_docs > 0 and pending_docs == 0,
            "Total Documents": total_docs,
            "Received / N.A.": received_docs,
            "Pending": pending_docs,
            "Completion %": completion
        })

    return pd.DataFrame(rows)


def apply_category_ticks_to_checklist(checklist_df, edited_category_df):
    updated_df = checklist_df.copy()

    for _, row in edited_category_df.iterrows():
        category = row["Category"]
        data_received = bool(row["Data Received"])

        if data_received:
            updated_df.loc[
                (updated_df["Category"] == category) &
                (updated_df["Status"] == "Pending"),
                "Status"
            ] = "Received"

    return updated_df


def prepare_detail_editor_df(category_df):
    detail_df = category_df.copy()

    detail_df["Received"] = detail_df["Status"] == "Received"
    detail_df["Not Applicable"] = detail_df["Status"] == "Not Applicable"

    detail_df = detail_df[
        [
            "Category",
            "Document Name",
            "Received",
            "Not Applicable",
            "Remarks",
            "Status"
        ]
    ]

    return detail_df


def apply_detail_editor_changes(checklist_df, selected_category, edited_detail_df):
    updated_df = checklist_df.copy()

    for _, row in edited_detail_df.iterrows():
        document_name = row["Document Name"]

        if bool(row["Not Applicable"]):
            status = "Not Applicable"
        elif bool(row["Received"]):
            status = "Received"
        else:
            status = "Pending"

        mask = (
            (updated_df["Category"] == selected_category) &
            (updated_df["Document Name"] == document_name)
        )

        updated_df.loc[mask, "Status"] = status
        updated_df.loc[mask, "Remarks"] = str(row.get("Remarks", ""))

    return updated_df


def calculate_overall_status(checklist_df):
    total_docs = len(checklist_df)

    if total_docs == 0:
        return 0, "Pending"

    completed_docs = len(
        checklist_df[
            checklist_df["Status"].isin(["Received", "Not Applicable"])
        ]
    )

    completion_percentage = round((completed_docs / total_docs) * 100, 2)
    document_status = get_document_status(completion_percentage)

    return completion_percentage, document_status


def update_client_document_status(df, selected_client, completion_percentage, document_status):
    df.loc[df["Client Name"] == selected_client, "Checklist Completion %"] = completion_percentage
    df.loc[df["Client Name"] == selected_client, "Document Status"] = document_status

    return df


def get_pending_documents_by_category(checklist_df):
    pending_df = checklist_df[checklist_df["Status"] == "Pending"].copy()

    grouped = {}

    for category in DOCUMENT_CATEGORIES.keys():
        cat_pending = pending_df[pending_df["Category"] == category]["Document Name"].tolist()

        if cat_pending:
            grouped[category] = cat_pending

    other_pending = pending_df[
        ~pending_df["Category"].isin(DOCUMENT_CATEGORIES.keys())
    ]

    if len(other_pending) > 0:
        grouped["Other Documents"] = other_pending["Document Name"].tolist()

    return grouped, pending_df


# ---------------------------------------------------------
# MAIN MODULE
# ---------------------------------------------------------

def show_document_collection():
    apply_document_collection_style()

    st.markdown("""
    <div class="doc-hero">
        <h2>📄 Document Collection Control Center</h2>
        <p>Category-wise document tracking for tax audit automation, follow-up, and audit procedure mapping.</p>
    </div>
    """, unsafe_allow_html=True)

    selected_client, selected_ay = get_active_client_from_global_selection()

    if not selected_client or not selected_ay:
        st.info("Please add/select a client from the top-right Active Audit Client selector.")
        return

    st.markdown(f"""
    <div class="active-client-strip">
        Active Client: {selected_client} | AY: {selected_ay}
    </div>
    """, unsafe_allow_html=True)

    df = load_clients()

    checklist_path = f"clients/{selected_client}/AY {selected_ay}/document_checklist.xlsx"

    checklist_df = load_or_create_checklist(checklist_path)

    completion_percentage, document_status = calculate_overall_status(checklist_df)

    # ---------------------------------------------------------
    # TOP METRICS
    # ---------------------------------------------------------

    total_documents = len(checklist_df)
    received_documents = len(checklist_df[checklist_df["Status"].isin(["Received", "Not Applicable"])])
    pending_documents = len(checklist_df[checklist_df["Status"] == "Pending"])
    total_categories = len(DOCUMENT_CATEGORIES)

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric("Categories", total_categories)

    with m2:
        st.metric("Total Documents", total_documents)

    with m3:
        st.metric("Received / N.A.", received_documents)

    with m4:
        st.metric("Pending", pending_documents)

    with m5:
        st.metric("Completion", f"{completion_percentage}%")

    st.progress(completion_percentage / 100)

    st.divider()

    # ---------------------------------------------------------
    # CATEGORY SUMMARY
    # ---------------------------------------------------------

    st.markdown("""
    <div class="section-banner">
        <b>Step 1:</b> Review category-wise document status. 
        Tick <b>Data Received</b> to mark all pending documents in that category as received.
    </div>
    """, unsafe_allow_html=True)

    category_summary_df = build_category_summary(checklist_df)

    edited_category_df = st.data_editor(
        category_summary_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Data Received": st.column_config.CheckboxColumn(
                "Data Received",
                help="Tick this if all documents under this category are received."
            ),
            "Category": st.column_config.TextColumn(
                "Category",
                width="large"
            ),
            "Completion %": st.column_config.ProgressColumn(
                "Completion %",
                min_value=0,
                max_value=100,
                format="%.2f%%"
            )
        },
        disabled=[
            "Category",
            "Total Documents",
            "Received / N.A.",
            "Pending",
            "Completion %"
        ],
        key=f"category_editor_{selected_client}_{selected_ay}"
    )

    st.divider()

    # ---------------------------------------------------------
    # CATEGORY SELECTION
    # ---------------------------------------------------------

    st.markdown("""
    <div class="section-banner">
        <b>Step 2:</b> Select a category to view and update the document checklist under that category.
    </div>
    """, unsafe_allow_html=True)

    selected_category = st.radio(
        "Select Document Category",
        list(DOCUMENT_CATEGORIES.keys()),
        horizontal=False,
        key=f"selected_document_category_{selected_client}_{selected_ay}"
    )

    selected_category_df = checklist_df[checklist_df["Category"] == selected_category].copy()
    selected_category_summary = category_summary_df[
        category_summary_df["Category"] == selected_category
    ].iloc[0]

    st.markdown(f"""
    <div class="category-card">
        <div class="category-title">📂 {selected_category}</div>
        <div class="category-sub">
            Total: {selected_category_summary["Total Documents"]} |
            Received / N.A.: {selected_category_summary["Received / N.A."]} |
            Pending: {selected_category_summary["Pending"]} |
            Completion: {selected_category_summary["Completion %"]}%
        </div>
    </div>
    """, unsafe_allow_html=True)

    detail_editor_df = prepare_detail_editor_df(selected_category_df)

    edited_detail_df = st.data_editor(
        detail_editor_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Received": st.column_config.CheckboxColumn(
                "Received",
                help="Tick if this document/data sheet is received."
            ),
            "Not Applicable": st.column_config.CheckboxColumn(
                "N.A.",
                help="Tick if this document/data sheet is not applicable."
            ),
            "Remarks": st.column_config.TextColumn(
                "Remarks",
                width="large"
            ),
            "Status": st.column_config.TextColumn(
                "Current Status"
            )
        },
        disabled=[
            "Category",
            "Document Name",
            "Status"
        ],
        key=f"detail_editor_{selected_client}_{selected_ay}_{selected_category}"
    )

    # ---------------------------------------------------------
    # SAVE CHECKLIST
    # ---------------------------------------------------------

    st.divider()

    save_col, refresh_col = st.columns([1, 1])

    with save_col:
        if st.button("💾 Save Checklist", help="Save checklist", use_container_width=True):

            updated_checklist_df = checklist_df.copy()

            updated_checklist_df = apply_category_ticks_to_checklist(
                updated_checklist_df,
                edited_category_df
            )

            updated_checklist_df = apply_detail_editor_changes(
                updated_checklist_df,
                selected_category,
                edited_detail_df
            )

            updated_checklist_df = clean_checklist_df(updated_checklist_df)
            updated_checklist_df.to_excel(checklist_path, index=False)

            completion_percentage, document_status = calculate_overall_status(updated_checklist_df)

            df_updated = update_client_document_status(
                df,
                selected_client,
                completion_percentage,
                document_status
            )

            save_clients(df_updated)

            st.success(
                f"✅ Checklist saved! Document Status: {document_status}, Completion: {completion_percentage}%"
            )

            st.rerun()

    with refresh_col:
        if st.button("🔄 Refresh Checklist", use_container_width=True):
            st.rerun()

    # ---------------------------------------------------------
    # PENDING DOCUMENT REPORT
    # ---------------------------------------------------------

    st.divider()

    st.subheader("📑 Pending Documents Report")

    latest_report_df = pd.read_excel(checklist_path)
    latest_report_df = clean_checklist_df(latest_report_df)

    pending_grouped, pending_df = get_pending_documents_by_category(latest_report_df)

    total_documents = len(latest_report_df)
    received_documents = len(
        latest_report_df[
            latest_report_df["Status"].isin(["Received", "Not Applicable"])
        ]
    )
    pending_documents = len(latest_report_df[latest_report_df["Status"] == "Pending"])
    completion_percentage = round((received_documents / total_documents) * 100, 2) if total_documents > 0 else 0

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric("Total Documents", total_documents)

    with r2:
        st.metric("Received / N.A.", received_documents)

    with r3:
        st.metric("Pending Documents", pending_documents)

    with r4:
        st.metric("Completion %", completion_percentage)

    report_title_col, report_download_col = st.columns([9, 1])

    with report_title_col:
        st.write("### Pending Document List")

    with report_download_col:
        st.download_button(
            label="⬇",
            data=pending_df.to_csv(index=False),
            file_name=f"{selected_client}_pending_documents.csv",
            mime="text/csv",
            help="Download pending documents report"
        )

    if len(pending_df) > 0:
        st.dataframe(
            pending_df[["Category", "Document Name", "Remarks"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ No pending documents. All required documents are received / marked as Not Applicable.")

    # ---------------------------------------------------------
    # FOLLOW-UP MESSAGE
    # ---------------------------------------------------------

    followup_title_col, followup_btn_col = st.columns([9, 1])

    with followup_title_col:
        st.subheader("📩 Pending Documents Follow-up Message")

    @st.dialog("Pending Documents Follow-up Message")
    def show_followup_message():
        if len(pending_grouped) > 0:
            message_lines = []

            for category, docs in pending_grouped.items():
                message_lines.append(f"\n{category}:")
                for i, doc in enumerate(docs, start=1):
                    message_lines.append(f"{i}. {doc}")

            pending_list_text = "\n".join(message_lines)

            followup_message = f"""Dear Sir/Madam,

For completing the Tax Audit and Income Tax Return filing for AY {selected_ay}, the following documents / data sheets are still pending from your side:

{pending_list_text}

Kindly share the above documents at the earliest so that we can proceed further with audit verification, reconciliation, and reporting.

Regards,
Lokesh"""

            st.text_area(
                "Copy this message and send to client",
                followup_message,
                height=360
            )
        else:
            st.success("✅ No pending documents. All required documents are received / marked as Not Applicable.")

    with followup_btn_col:
        if st.button("✉️", help="Open follow-up message"):
            show_followup_message()