import pandas as pd
import streamlit as st

from utils.common import load_clients


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
# MAIN MODULE
# ---------------------------------------------------------

def show_final_review():

    st.subheader("✅ Tax Audit Final Review")

    df = load_clients()

    if df.empty or "Client Name" not in df.columns:
        st.info("Please add clients first.")
        return

    selected_client, selected_ay = get_active_client_from_global_selection()

    if not selected_client:
        st.info("Please select a client from the top-right Active Audit Client selector.")
        return

    selected_rows = df[df["Client Name"] == selected_client]

    if selected_rows.empty:
        st.warning("Selected client not found in client database.")
        return

    selected_row = selected_rows.iloc[0]

    document_status = selected_row.get("Document Status", "Pending")
    audit_status = selected_row.get("Audit Status", "Pending")
    tax_audit_status = selected_row.get("3CD/3CA Filing Status", "Not Filed")
    itr_status = selected_row.get("ITR Filing Status", "Not Filed")
    checklist_completion = selected_row.get("Checklist Completion %", 0)

    review_items = [
        {
            "Review Point": "Document collection completed",
            "Status": "Completed" if document_status == "Received" else "Pending",
            "Remarks": f"Document completion: {checklist_completion}%"
        },
        {
            "Review Point": "Audit procedures completed",
            "Status": "Completed" if audit_status == "Completed" else "Pending",
            "Remarks": f"Current audit status: {audit_status}"
        },
        {
            "Review Point": "Working papers completed",
            "Status": "Check WP Dashboard",
            "Remarks": "Verify all working papers are completed"
        },
        {
            "Review Point": "3CD/3CA filed",
            "Status": "Completed" if tax_audit_status == "Filed" else "Pending",
            "Remarks": f"Current status: {tax_audit_status}"
        },
        {
            "Review Point": "ITR filed",
            "Status": "Completed" if itr_status == "Filed" else "Pending",
            "Remarks": f"Current status: {itr_status}"
        }
    ]

    review_df = pd.DataFrame(review_items)

    st.dataframe(review_df, use_container_width=True, hide_index=True)