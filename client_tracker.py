import streamlit as st
import pandas as pd
import os

FILE_PATH = "data/clients.xlsx"

st.set_page_config(page_title="Tax Audit Client Tracker", page_icon="📊", layout="wide")
st.title("📊 Tax Audit Client Tracker")

COLUMNS = [
    "Client Name", "PAN", "GSTIN", "AY",
    "Document Status", "Audit Status",
    "3CD/3CA Filing Status", "ITR Filing Status",
    "Assigned Staff", "Checklist Completion %"
]


def get_document_status(percentage):
    if percentage == 0:
        return "Pending"
    elif percentage == 100:
        return "Received"
    else:
        return "Partially Received"


# Load data
if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
else:
    df = pd.DataFrame(columns=COLUMNS)

# Old column migration
if "Docs Status" in df.columns and "Document Status" not in df.columns:
    df["Document Status"] = df["Docs Status"]

if "Filing Status" in df.columns:
    if "3CD/3CA Filing Status" not in df.columns:
        df["3CD/3CA Filing Status"] = df["Filing Status"].replace("Pending", "Not Filed")
    if "ITR Filing Status" not in df.columns:
        df["ITR Filing Status"] = df["Filing Status"].replace("Pending", "Not Filed")

for col in COLUMNS:
    if col not in df.columns:
        if col == "Checklist Completion %":
            df[col] = 0
        elif col == "Document Status":
            df[col] = "Pending"
        elif col == "Audit Status":
            df[col] = "Pending"
        elif col in ["3CD/3CA Filing Status", "ITR Filing Status"]:
            df[col] = "Not Filed"
        else:
            df[col] = ""

df = df[COLUMNS]
df["Checklist Completion %"] = df["Checklist Completion %"].fillna(0)
df["Document Status"] = df["Checklist Completion %"].apply(get_document_status)
df.to_excel(FILE_PATH, index=False)

# Sidebar Add Client
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
        df.to_excel(FILE_PATH, index=False)

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

        st.sidebar.success("✅ Client Added, Folders & Checklist Created!")
        st.rerun()

# Summary
st.subheader("📌 Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Clients", len(df))

with col2:
    st.metric("Documents Pending", len(df[df["Document Status"] != "Received"]))

with col3:
    st.metric("Audit Pending", len(df[df["Audit Status"] != "Completed"]))

with col4:
    st.metric("ITR Not Filed", len(df[df["ITR Filing Status"] == "Not Filed"]))

# Search & Filter
st.subheader("🔎 Search & Filter Clients")

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

# Client Database
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

    df.to_excel(FILE_PATH, index=False)
    st.success("✅ Client status updated successfully!")
    st.rerun()

# Checklist Editor
st.subheader("📂 Client Document Checklist Editor")

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

            df.to_excel(FILE_PATH, index=False)

            st.success(
                f"✅ Checklist saved! Document Status: {document_status}, Completion: {completion_percentage}%"
            )
            st.rerun()

    else:
        st.warning("Checklist file not found for this client.")
else:
    st.info("Please select a client.")

# Pending Documents Report
report_title_col, report_download_col = st.columns([9, 1])

with report_title_col:
    st.subheader("📑 Pending Documents Report")

if len(df) > 0 and selected_client:
    selected_row = df[df["Client Name"] == selected_client].iloc[0]
    selected_ay = selected_row["AY"]

    checklist_path = f"clients/{selected_client}/AY {selected_ay}/document_checklist.xlsx"

    if os.path.exists(checklist_path):
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

        with report_download_col:
            st.download_button(
                label="⬇",
                data=pending_df.to_csv(index=False),
                file_name=f"{selected_client}_pending_documents.csv",
                mime="text/csv",
                help="Download pending documents report"
            )

        st.write("### Pending Document List")
        st.dataframe(pending_df, use_container_width=True)

    else:
        st.warning("Checklist file not found for pending report.")
else:
    st.info("Select a client to view pending documents report.")

# Follow-up Message Dialog
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