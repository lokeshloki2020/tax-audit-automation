import os
import pandas as pd
import streamlit as st

from utils.common import load_clients, save_clients, get_document_status


def show_document_collection():
    st.subheader("📄 Document Collection")

    df = load_clients()

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    selected_client = st.selectbox(
        "Search / Select Client",
        client_list,
        index=0 if len(client_list) > 0 else None,
        placeholder="Search client name..."
    )

    pending_docs_for_message = []
    selected_ay = ""

    if len(df) > 0 and selected_client:
        selected_row = df[df["Client Name"] == selected_client].iloc[0]
        selected_ay = selected_row["AY"]

        checklist_path = f"clients/{selected_client}/AY {selected_ay}/document_checklist.xlsx"

        if os.path.exists(checklist_path):
            checklist_df = pd.read_excel(checklist_path)

            checklist_df["Document Name"] = checklist_df["Document Name"].astype(str)
            checklist_df["Status"] = checklist_df["Status"].astype(str)
            checklist_df["Remarks"] = checklist_df["Remarks"].astype(str)
            checklist_df["Remarks"] = checklist_df["Remarks"].replace("nan", "")

            st.write(f"### Checklist for {selected_client} - AY {selected_ay}")

            edited_checklist = st.data_editor(
                checklist_df,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Pending", "Received", "Not Applicable"],
                        required=True
                    ),
                    "Remarks": st.column_config.TextColumn("Remarks")
                },
                disabled=["Document Name"]
            )

            if st.button("💾 Save Checklist", help="Save checklist"):
                edited_checklist.to_excel(checklist_path, index=False)

                total_docs = len(edited_checklist)
                completed_docs = len(
                    edited_checklist[
                        edited_checklist["Status"].isin(["Received", "Not Applicable"])
                    ]
                )

                completion_percentage = round((completed_docs / total_docs) * 100, 2)
                document_status = get_document_status(completion_percentage)

                df.loc[df["Client Name"] == selected_client, "Checklist Completion %"] = completion_percentage
                df.loc[df["Client Name"] == selected_client, "Document Status"] = document_status

                save_clients(df)

                st.success(
                    f"✅ Checklist saved! Document Status: {document_status}, Completion: {completion_percentage}%"
                )
                st.rerun()

            st.subheader("📑 Pending Documents Report")

            report_df = pd.read_excel(checklist_path)
            report_df["Status"] = report_df["Status"].astype(str)

            total_documents = len(report_df)
            received_documents = len(
                report_df[report_df["Status"].isin(["Received", "Not Applicable"])]
            )
            pending_documents = len(report_df[report_df["Status"] == "Pending"])

            completion_percentage = round((received_documents / total_documents) * 100, 2)

            r1, r2, r3, r4 = st.columns(4)

            with r1:
                st.metric("Total Documents", total_documents)

            with r2:
                st.metric("Received / N.A.", received_documents)

            with r3:
                st.metric("Pending Documents", pending_documents)

            with r4:
                st.metric("Completion %", completion_percentage)

            pending_df = report_df[report_df["Status"] == "Pending"]
            pending_docs_for_message = pending_df["Document Name"].tolist()

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

            st.dataframe(pending_df, use_container_width=True)

            followup_title_col, followup_btn_col = st.columns([9, 1])

            with followup_title_col:
                st.subheader("📩 Pending Documents Follow-up Message")

            @st.dialog("Pending Documents Follow-up Message")
            def show_followup_message():
                if len(pending_docs_for_message) > 0:
                    pending_list_text = "\n".join(
                        [f"{i + 1}. {doc}" for i, doc in enumerate(pending_docs_for_message)]
                    )

                    followup_message = f"""Dear Sir/Madam,

For completing the Tax Audit and Income Tax Return filing for AY {selected_ay}, the following documents are still pending from your side:

{pending_list_text}

Kindly share the above documents at the earliest so that we can proceed further.

Regards,
Lokesh"""

                    st.text_area(
                        "Copy this message and send to client",
                        followup_message,
                        height=300
                    )
                else:
                    st.success("✅ No pending documents. All required documents are received / marked as Not Applicable.")

            with followup_btn_col:
                if st.button("✉️", help="Open follow-up message"):
                    show_followup_message()

        else:
            st.warning("Checklist file not found for this client.")
    else:
        st.info("Please select a client.")