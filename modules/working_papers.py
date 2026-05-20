import os
import pandas as pd
import streamlit as st

from utils.common import load_clients


# ---------------------------------------------------------
# WORKING PAPER MASTER LIST
# ---------------------------------------------------------

WORKING_PAPER_CATEGORIES = {
    "Basic Books Verification": [
        {
            "Working Paper": "Trial Balance Verification",
            "Clause Reference": "Clause 11 / Clause 13 / Clause 40",
            "Linked Audit Procedure": "Trial Balance Verification",
        },
        {
            "Working Paper": "Profit and Loss Verification",
            "Clause Reference": "Clause 13 / Clause 16 / Clause 21 / Clause 27 / Clause 40",
            "Linked Audit Procedure": "Profit and Loss Verification",
        },
        {
            "Working Paper": "Balance Sheet Verification",
            "Clause Reference": "Clause 11 / Clause 18 / Clause 22 / Clause 26 / Clause 31 / Clause 40",
            "Linked Audit Procedure": "Balance Sheet Verification",
        },
    ],

    "GST Verification": [
        {
            "Working Paper": "Books Turnover vs GSTR-1 Sales Reconciliation",
            "Clause Reference": "Clause 4 / Clause 44",
            "Linked Audit Procedure": "GST Reconciliation",
        },
        {
            "Working Paper": "Books Purchases vs GSTR-2B Purchase Reconciliation",
            "Clause Reference": "Clause 27 / Clause 44",
            "Linked Audit Procedure": "GST Reconciliation",
        },
        {
            "Working Paper": "GST Input as per Books vs GSTR-2A / 2B",
            "Clause Reference": "Clause 27 / Clause 44",
            "Linked Audit Procedure": "GST Reconciliation",
        },
        {
            "Working Paper": "GSTR-1 vs GSTR-3B Reconciliation",
            "Clause Reference": "Clause 4 / Clause 41",
            "Linked Audit Procedure": "GST Reconciliation",
        },
    ],

    "TDS / TCS Verification": [
        {
            "Working Paper": "TDS Payable and Paid Verification",
            "Clause Reference": "Clause 21 / Clause 34",
            "Linked Audit Procedure": "TDS / TCS Verification",
        },
        {
            "Working Paper": "TDS Receivable and Received Verification",
            "Clause Reference": "ITR Credit Verification / Clause 34",
            "Linked Audit Procedure": "TDS / TCS Verification",
        },
        {
            "Working Paper": "TCS Verification",
            "Clause Reference": "Clause 34",
            "Linked Audit Procedure": "TDS / TCS Verification",
        },
    ],

    "Statutory Dues and 43B Verification": [
        {
            "Working Paper": "Section 43B Statutory Dues Verification",
            "Clause Reference": "Clause 26",
            "Linked Audit Procedure": "Section 43B Verification",
        },
        {
            "Working Paper": "GST Liability vs GSTR-3B Filed Returns",
            "Clause Reference": "Clause 26 / Clause 41",
            "Linked Audit Procedure": "Section 43B Verification",
        },
        {
            "Working Paper": "TDS Deducted and Deposited Within Due Dates",
            "Clause Reference": "Clause 26 / Clause 34",
            "Linked Audit Procedure": "Section 43B Verification",
        },
        {
            "Working Paper": "PF / ESI Contribution and Return Verification",
            "Clause Reference": "Clause 20 / Clause 26",
            "Linked Audit Procedure": "Section 43B Verification",
        },
    ],

    "Cash and Banking Verification": [
        {
            "Working Paper": "Cash Payment Verification",
            "Clause Reference": "Clause 21",
            "Linked Audit Procedure": "Cash Payment Verification",
        },
        {
            "Working Paper": "Bank Book Verification",
            "Clause Reference": "General Audit Procedure",
            "Linked Audit Procedure": "Bank Verification",
        },
    ],

    "Loans and Deposits Verification": [
        {
            "Working Paper": "Loans, Deposits and Specified Sums Verification",
            "Clause Reference": "Clause 30 / Clause 31",
            "Linked Audit Procedure": "Loans, Deposits and Specified Sums Verification",
        },
        {
            "Working Paper": "269SS / 269T / 269ST Compliance Verification",
            "Clause Reference": "Clause 31",
            "Linked Audit Procedure": "Loans, Deposits and Specified Sums Verification",
        },
    ],

    "Related Party Verification": [
        {
            "Working Paper": "Related Party Transaction Verification",
            "Clause Reference": "Clause 23",
            "Linked Audit Procedure": "Related Party Verification",
        },
    ],

    "MSME Verification": [
        {
            "Working Paper": "MSME Vendor and Delayed Payment Verification",
            "Clause Reference": "Clause 22 / Clause 26",
            "Linked Audit Procedure": "MSME Verification",
        },
    ],

    "Fixed Assets and Depreciation": [
        {
            "Working Paper": "Fixed Asset Register Verification",
            "Clause Reference": "Clause 18",
            "Linked Audit Procedure": "Depreciation Verification",
        },
        {
            "Working Paper": "Depreciation as per Income Tax Act",
            "Clause Reference": "Clause 18",
            "Linked Audit Procedure": "Depreciation Verification",
        },
        {
            "Working Paper": "Capital Asset Converted into Stock-in-Trade",
            "Clause Reference": "Clause 15",
            "Linked Audit Procedure": "Depreciation Verification",
        },
    ],

    "Clause 44 Verification": [
        {
            "Working Paper": "GST Expenditure Break-up for Clause 44",
            "Clause Reference": "Clause 44",
            "Linked Audit Procedure": "Clause 44 GST Expenditure Break-up",
        },
    ],

    "Stock and Quantitative Details": [
        {
            "Working Paper": "Stock and Quantitative Details Verification",
            "Clause Reference": "Clause 14 / Clause 35 / Clause 40",
            "Linked Audit Procedure": "Stock and Quantitative Details Verification",
        },
    ],

    "Other Tax and Reporting": [
        {
            "Working Paper": "Tax Demand and Refund Verification",
            "Clause Reference": "Clause 41",
            "Linked Audit Procedure": "Tax Demand / Refund Verification",
        },
        {
            "Working Paper": "Form 61 / 61A / 61B Verification",
            "Clause Reference": "Clause 42",
            "Linked Audit Procedure": "Form 61 / 61A / 61B Verification",
        },
    ],

    "Final Audit Review": [
        {
            "Working Paper": "Final Audit Observation Summary",
            "Clause Reference": "All Relevant Clauses",
            "Linked Audit Procedure": "Final Audit Observation Summary",
        },
        {
            "Working Paper": "Management Reply and Final Adjustments",
            "Clause Reference": "Final Review",
            "Linked Audit Procedure": "Final Audit Observation Summary",
        },
    ],
}


# ---------------------------------------------------------
# STYLE
# ---------------------------------------------------------

def apply_working_paper_style():
    st.markdown("""
    <style>
    .wp-hero {
        padding: 24px;
        border-radius: 22px;
        background: linear-gradient(135deg, #14532d, #1d4ed8, #7e22ce);
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.25);
    }
    .wp-hero h2 {
        margin: 0;
        font-size: 34px;
        font-weight: 800;
    }
    .wp-hero p {
        margin-top: 8px;
        font-size: 16px;
        opacity: 0.95;
    }
    .wp-card {
        padding: 18px;
        border-radius: 18px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.08);
        margin-bottom: 12px;
    }
    .wp-card-title {
        font-size: 18px;
        font-weight: 800;
        color: #111827;
    }
    .wp-card-sub {
        color: #6b7280;
        font-size: 14px;
    }
    .wp-banner {
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
# DATA HELPERS
# ---------------------------------------------------------

def get_default_working_papers_df():
    rows = []

    for category, papers in WORKING_PAPER_CATEGORIES.items():
        for item in papers:
            rows.append({
                "Category": category,
                "Working Paper": item["Working Paper"],
                "Clause Reference": item["Clause Reference"],
                "Linked Audit Procedure": item["Linked Audit Procedure"],
                "Status": "Pending",
                "Prepared By": "",
                "Reviewed By": "",
                "Remarks": "",
            })

    return pd.DataFrame(rows)


def clean_working_papers_df(wp_df):
    if wp_df is None or wp_df.empty:
        return get_default_working_papers_df()

    required_columns = [
        "Category",
        "Working Paper",
        "Clause Reference",
        "Linked Audit Procedure",
        "Status",
        "Prepared By",
        "Reviewed By",
        "Remarks",
    ]

    for col in required_columns:
        if col not in wp_df.columns:
            wp_df[col] = ""

    wp_df = wp_df[required_columns]

    for col in required_columns:
        wp_df[col] = wp_df[col].astype(str).replace("nan", "")

    valid_status = ["Pending", "In Progress", "Completed", "Under Review"]

    wp_df.loc[
        ~wp_df["Status"].isin(valid_status),
        "Status"
    ] = "Pending"

    # Add newly introduced working papers if missing
    existing = set(
        zip(
            wp_df["Category"].astype(str),
            wp_df["Working Paper"].astype(str)
        )
    )

    new_rows = []

    for category, papers in WORKING_PAPER_CATEGORIES.items():
        for item in papers:
            key = (category, item["Working Paper"])

            if key not in existing:
                new_rows.append({
                    "Category": category,
                    "Working Paper": item["Working Paper"],
                    "Clause Reference": item["Clause Reference"],
                    "Linked Audit Procedure": item["Linked Audit Procedure"],
                    "Status": "Pending",
                    "Prepared By": "",
                    "Reviewed By": "",
                    "Remarks": "",
                })

    if new_rows:
        wp_df = pd.concat([wp_df, pd.DataFrame(new_rows)], ignore_index=True)

    return wp_df


def load_or_create_working_papers(wp_path):
    os.makedirs(os.path.dirname(wp_path), exist_ok=True)

    if os.path.exists(wp_path):
        wp_df = pd.read_excel(wp_path)
        wp_df = clean_working_papers_df(wp_df)
    else:
        wp_df = get_default_working_papers_df()

    wp_df.to_excel(wp_path, index=False)

    return wp_df


def build_category_summary(wp_df):
    rows = []

    for category in WORKING_PAPER_CATEGORIES.keys():
        cat_df = wp_df[wp_df["Category"] == category]

        total = len(cat_df)
        completed = len(cat_df[cat_df["Status"] == "Completed"])
        pending = len(cat_df[cat_df["Status"] == "Pending"])
        in_progress = len(cat_df[cat_df["Status"] == "In Progress"])
        under_review = len(cat_df[cat_df["Status"] == "Under Review"])

        completion = round((completed / total) * 100, 2) if total > 0 else 0

        rows.append({
            "Category": category,
            "All Completed": total > 0 and completed == total,
            "Total WPs": total,
            "Completed": completed,
            "Pending": pending,
            "In Progress": in_progress,
            "Under Review": under_review,
            "Completion %": completion,
        })

    return pd.DataFrame(rows)


def apply_category_completion(wp_df, edited_category_df):
    updated_df = wp_df.copy()

    for _, row in edited_category_df.iterrows():
        category = row["Category"]
        all_completed = bool(row["All Completed"])

        if all_completed:
            updated_df.loc[
                updated_df["Category"] == category,
                "Status"
            ] = "Completed"

    return updated_df


def calculate_wp_completion(wp_df):
    total_wp = len(wp_df)

    if total_wp == 0:
        return 0, 0, 0, 0, 0, 0

    completed_wp = len(wp_df[wp_df["Status"] == "Completed"])
    pending_wp = len(wp_df[wp_df["Status"] == "Pending"])
    in_progress_wp = len(wp_df[wp_df["Status"] == "In Progress"])
    under_review_wp = len(wp_df[wp_df["Status"] == "Under Review"])

    completion = round((completed_wp / total_wp) * 100, 2)

    return total_wp, completed_wp, pending_wp, in_progress_wp, under_review_wp, completion


def get_safe_key(value):
    return str(value).replace(" ", "_").replace("/", "_").replace("\\", "_")


# ---------------------------------------------------------
# MAIN MODULE
# ---------------------------------------------------------

def show_working_papers():
    apply_working_paper_style()

    st.markdown("""
    <div class="wp-hero">
        <h2>🗂️ Working Papers Control Center</h2>
        <p>Procedure-wise working paper tracking aligned with document collection and automated audit procedures.</p>
    </div>
    """, unsafe_allow_html=True)

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
        key="working_paper_client"
    )

    if not selected_client:
        st.info("Please select a client.")
        return

    selected_row = df[df["Client Name"] == selected_client].iloc[0]
    selected_ay = selected_row["AY"]

    st.write(f"### Working Papers for {selected_client} - AY {selected_ay}")

    wp_path = f"clients/{selected_client}/AY {selected_ay}/working_papers_tracker.xlsx"
    wp_df = load_or_create_working_papers(wp_path)

    safe_client = get_safe_key(selected_client)
    safe_ay = get_safe_key(selected_ay)

    total_wp, completed_wp, pending_wp, in_progress_wp, under_review_wp, wp_completion = calculate_wp_completion(wp_df)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total WPs", total_wp)

    with col2:
        st.metric("Completed", completed_wp)

    with col3:
        st.metric("Pending", pending_wp)

    with col4:
        st.metric("In Progress", in_progress_wp)

    with col5:
        st.metric("Under Review", under_review_wp)

    with col6:
        st.metric("Completion", f"{wp_completion}%")

    st.progress(wp_completion / 100)

    st.divider()

    # ---------------------------------------------------------
    # CATEGORY SUMMARY
    # ---------------------------------------------------------

    st.markdown("""
    <div class="wp-banner">
        <b>Step 1:</b> Review working paper status category-wise. 
        Tick <b>All Completed</b> only when the full category is completed.
    </div>
    """, unsafe_allow_html=True)

    category_summary_df = build_category_summary(wp_df)

    edited_category_df = st.data_editor(
        category_summary_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "All Completed": st.column_config.CheckboxColumn(
                "All Completed",
                help="Tick this to mark all working papers in this category as completed."
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
            ),
        },
        disabled=[
            "Category",
            "Total WPs",
            "Completed",
            "Pending",
            "In Progress",
            "Under Review",
            "Completion %"
        ],
        key=f"wp_category_editor_{safe_client}_{safe_ay}"
    )

    st.divider()

    # ---------------------------------------------------------
    # CATEGORY DETAIL
    # ---------------------------------------------------------

    st.markdown("""
    <div class="wp-banner">
        <b>Step 2:</b> Select a working paper category and update status, preparer, reviewer and remarks.
    </div>
    """, unsafe_allow_html=True)

    selected_category = st.radio(
        "Select Working Paper Category",
        list(WORKING_PAPER_CATEGORIES.keys()),
        horizontal=False,
        key=f"wp_selected_category_{safe_client}_{safe_ay}"
    )

    selected_wp_df = wp_df[wp_df["Category"] == selected_category].copy()

    selected_summary = category_summary_df[
        category_summary_df["Category"] == selected_category
    ].iloc[0]

    st.markdown(f"""
    <div class="wp-card">
        <div class="wp-card-title">📂 {selected_category}</div>
        <div class="wp-card-sub">
            Total: {selected_summary["Total WPs"]} |
            Completed: {selected_summary["Completed"]} |
            Pending: {selected_summary["Pending"]} |
            In Progress: {selected_summary["In Progress"]} |
            Under Review: {selected_summary["Under Review"]} |
            Completion: {selected_summary["Completion %"]}%
        </div>
    </div>
    """, unsafe_allow_html=True)

    edited_wp_df = st.data_editor(
        selected_wp_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=[
                    "Pending",
                    "In Progress",
                    "Completed",
                    "Under Review"
                ],
                required=True
            ),
            "Prepared By": st.column_config.TextColumn(
                "Prepared By"
            ),
            "Reviewed By": st.column_config.TextColumn(
                "Reviewed By"
            ),
            "Remarks": st.column_config.TextColumn(
                "Remarks",
                width="large"
            ),
        },
        disabled=[
            "Category",
            "Working Paper",
            "Clause Reference",
            "Linked Audit Procedure"
        ],
        key=f"wp_detail_editor_{safe_client}_{safe_ay}_{get_safe_key(selected_category)}"
    )

    st.divider()

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    save_col, refresh_col = st.columns(2)

    with save_col:
        if st.button("💾 Save Working Papers", use_container_width=True):
            updated_wp_df = wp_df.copy()

            updated_wp_df = apply_category_completion(
                updated_wp_df,
                edited_category_df
            )

            # Replace selected category details
            updated_wp_df = updated_wp_df[
                updated_wp_df["Category"] != selected_category
            ]

            updated_wp_df = pd.concat(
                [updated_wp_df, edited_wp_df],
                ignore_index=True
            )

            updated_wp_df = clean_working_papers_df(updated_wp_df)

            updated_wp_df.to_excel(wp_path, index=False)

            _, _, _, _, _, new_completion = calculate_wp_completion(updated_wp_df)

            st.success(f"✅ Working Papers Updated! Completion: {new_completion}%")
            st.rerun()

    with refresh_col:
        if st.button("🔄 Refresh Working Papers", use_container_width=True):
            st.rerun()

    st.divider()

    # ---------------------------------------------------------
    # DASHBOARD
    # ---------------------------------------------------------

    st.subheader("📊 Working Paper Completion Dashboard")

    latest_wp_df = pd.read_excel(wp_path)
    latest_wp_df = clean_working_papers_df(latest_wp_df)

    total_wp, completed_wp, pending_wp, in_progress_wp, under_review_wp, wp_completion = calculate_wp_completion(latest_wp_df)

    d1, d2, d3, d4, d5 = st.columns(5)

    with d1:
        st.metric("Total WPs", total_wp)

    with d2:
        st.metric("Completed", completed_wp)

    with d3:
        st.metric("Pending", pending_wp)

    with d4:
        st.metric("In Progress", in_progress_wp)

    with d5:
        st.metric("Under Review", under_review_wp)

    st.write(f"**Overall Working Paper Completion: {wp_completion}%**")
    st.progress(wp_completion / 100)

    st.write("### Pending / Incomplete Working Papers")

    incomplete_wp_df = latest_wp_df[
        latest_wp_df["Status"].isin([
            "Pending",
            "In Progress",
            "Under Review"
        ])
    ]

    st.dataframe(
        incomplete_wp_df,
        use_container_width=True,
        hide_index=True
    )

    csv_data = incomplete_wp_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Pending Working Papers",
        data=csv_data,
        file_name=f"{selected_client}_pending_working_papers.csv",
        mime="text/csv",
        use_container_width=True
    )