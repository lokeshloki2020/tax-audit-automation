import pandas as pd
import streamlit as st

from utils.common import load_clients


def show_final_review():

    st.subheader("✅ Tax Audit Final Review")

    df = load_clients()

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    selected_client = st.selectbox(
        "Search / Select Client",
        client_list,
        index=0 if len(client_list) > 0 else None,
        placeholder="Search client name..."
    )

    if len(df) > 0 and selected_client:

        selected_row = df[df["Client Name"] == selected_client].iloc[0]

        document_status = selected_row["Document Status"]
        audit_status = selected_row["Audit Status"]
        tax_audit_status = selected_row["3CD/3CA Filing Status"]
        itr_status = selected_row["ITR Filing Status"]
        checklist_completion = selected_row["Checklist Completion %"]

        review_items = [
            {
                "Review Point": "Document collection completed",
                "Status": "Completed" if document_status == "Received" else "Pending",
                "Remarks": f"Document completion: {checklist_completion}%"
            },
            {
                "Review Point": "Working papers completed",
                "Status": "Check WP Dashboard",
                "Remarks": "Verify all working papers are completed"
            },
            {
                "Review Point": "Audit status completed",
                "Status": "Completed" if audit_status == "Completed" else "Pending",
                "Remarks": f"Current audit status: {audit_status}"
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

        st.dataframe(review_df, use_container_width=True)

    else:
        st.info("Please select a client.")