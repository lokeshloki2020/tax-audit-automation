import os
import pandas as pd
import streamlit as st

from utils.common import load_clients, save_clients


def show_client_management():
    st.subheader("👥 Client Management")

    df = load_clients()

    st.sidebar.header("➕ Add New Client")

    client_name = st.sidebar.text_input("Client Name")
    pan = st.sidebar.text_input("PAN")
    gstin = st.sidebar.text_input("GSTIN")
    ay = st.sidebar.text_input("Assessment Year")
    assigned_staff = st.sidebar.text_input("Assigned Staff")

    audit_status = st.sidebar.selectbox(
        "Audit Status",
        ["Pending", "In Progress", "Completed"]
    )

    if st.sidebar.button("➕ Add Client"):
        if client_name == "" or pan == "":
            st.sidebar.error("Client Name and PAN are mandatory!")
        else:
            new_client = {
                "Client Name": client_name,
                "PAN": pan,
                "GSTIN": gstin,
                "AY": ay,
                "Document Status": "Pending",
                "Audit Status": audit_status,
                "3CD/3CA Filing Status": "Not Filed",
                "ITR Filing Status": "Not Filed",
                "Assigned Staff": assigned_staff,
                "Checklist Completion %": 0
            }

            df = pd.concat([df, pd.DataFrame([new_client])], ignore_index=True)
            save_clients(df)

            base_path = f"clients/{client_name}/AY {ay}"

            folders = [
                "Bank Statements",
                "GST Returns",
                "TDS",
                "Financial Statements",
                "Audit Working Papers",
                "Form 3CD",
                "Final Filing"
            ]

            for folder in folders:
                os.makedirs(f"{base_path}/{folder}", exist_ok=True)

            checklist_items = [
                "Bank Statements",
                "Sales Register",
                "Purchase Register",
                "GST Returns - GSTR-1",
                "GST Returns - GSTR-3B",
                "GSTR-2B",
                "Trial Balance",
                "Profit & Loss Account",
                "Balance Sheet",
                "Fixed Asset Register",
                "Loan Statements",
                "TDS Returns",
                "Form 26AS",
                "AIS/TIS",
                "Previous Year ITR",
                "Previous Year Tax Audit Report",
                "Stock Details",
                "Cash Book",
                "Debtors List",
                "Creditors List"
            ]

            checklist_df = pd.DataFrame({
                "Document Name": checklist_items,
                "Status": ["Pending"] * len(checklist_items),
                "Remarks": [""] * len(checklist_items)
            })

            checklist_df.to_excel(f"{base_path}/document_checklist.xlsx", index=False)

            working_papers = [
                ["Trial Balance Verification", "General"],
                ["Depreciation Schedule", "Clause 18"],
                ["TDS Reconciliation", "Clause 34"],
                ["GST Reconciliation", "Clause 44"],
                ["Clause 44 Working", "Clause 44"],
                ["Cash Payment Verification", "Clause 21(d)"],
                ["Loan Verification", "Clause 31"],
                ["Related Party Transactions", "Clause 23"],
                ["Quantitative Details", "Clause 35"],
                ["Stock Verification", "Clause 35"],
                ["Form 26AS Reconciliation", "General"],
                ["AIS/TIS Verification", "General"]
            ]

            wp_df = pd.DataFrame(
                working_papers,
                columns=["Working Paper", "Clause Reference"]
            )

            wp_df["Status"] = "Pending"
            wp_df["Prepared By"] = ""
            wp_df["Reviewed By"] = ""
            wp_df["Remarks"] = ""

            wp_df.to_excel(f"{base_path}/working_papers_tracker.xlsx", index=False)

            st.sidebar.success("✅ Client Added, Folders, Checklist & WP Tracker Created!")
            st.rerun()

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    selected_client = st.selectbox(
        "Search / Select Client",
        client_list,
        index=0 if len(client_list) > 0 else None,
        placeholder="Search client name..."
    )

    if selected_client:
        filtered_df = df[df["Client Name"] == selected_client].copy()
    else:
        filtered_df = df.copy()

    title_col, download_col = st.columns([9, 1])

    with title_col:
        st.subheader("📋 Client Database")

    with download_col:
        st.download_button(
            label="⬇",
            data=filtered_df.to_csv(index=False),
            file_name="selected_client_data.csv",
            mime="text/csv",
            help="Download selected client data"
        )

    editable_df = filtered_df.reset_index()

    edited_clients = st.data_editor(
        editable_df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Audit Status": st.column_config.SelectboxColumn(
                "Audit Status",
                options=["Pending", "In Progress", "Completed"]
            ),
            "3CD/3CA Filing Status": st.column_config.SelectboxColumn(
                "3CD/3CA Filing Status",
                options=["Not Filed", "Filed"]
            ),
            "ITR Filing Status": st.column_config.SelectboxColumn(
                "ITR Filing Status",
                options=["Not Filed", "Filed"]
            )
        },
        disabled=[
            "index",
            "Client Name",
            "PAN",
            "GSTIN",
            "AY",
            "Document Status",
            "Assigned Staff",
            "Checklist Completion %"
        ]
    )

    if st.button("💾 Save Changes", help="Save client status changes"):
        for _, row in edited_clients.iterrows():
            original_index = row["index"]

            df.loc[original_index, "Audit Status"] = row["Audit Status"]
            df.loc[original_index, "3CD/3CA Filing Status"] = row["3CD/3CA Filing Status"]
            df.loc[original_index, "ITR Filing Status"] = row["ITR Filing Status"]

        save_clients(df)
        st.success("✅ Client status updated successfully!")
        st.rerun()