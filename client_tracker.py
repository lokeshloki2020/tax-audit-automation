import streamlit as st
import pandas as pd
import os

# File Path
FILE_PATH = "data/clients.xlsx"

# Page Config
st.set_page_config(
    page_title="Tax Audit Client Tracker",
    page_icon="📊",
    layout="wide"
)

# Dashboard Title
st.title("📊 Tax Audit Client Tracker")

# Load Existing Excel Data
if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
else:
    df = pd.DataFrame(columns=[
        "Client Name",
        "PAN",
        "GSTIN",
        "AY",
        "Audit Status",
        "Docs Status",
        "Filing Status",
        "Assigned Staff"
    ])

# Sidebar Form
st.sidebar.header("➕ Add New Client")

client_name = st.sidebar.text_input("Client Name")
pan = st.sidebar.text_input("PAN")
gstin = st.sidebar.text_input("GSTIN")
ay = st.sidebar.text_input("Assessment Year")

audit_status = st.sidebar.selectbox(
    "Audit Status",
    ["Pending", "In Progress", "Completed"]
)

docs_status = st.sidebar.selectbox(
    "Documents Status",
    ["Pending", "Partially Received", "Received"]
)

filing_status = st.sidebar.selectbox(
    "Filing Status",
    ["Pending", "Filed"]
)

assigned_staff = st.sidebar.text_input("Assigned Staff")

# Add Client Button
if st.sidebar.button("Add Client"):

    # Validation
    if client_name == "" or pan == "":
        st.sidebar.error("Client Name and PAN are mandatory!")

    else:
        new_client = {
            "Client Name": client_name,
            "PAN": pan,
            "GSTIN": gstin,
            "AY": ay,
            "Audit Status": audit_status,
            "Docs Status": docs_status,
            "Filing Status": filing_status,
            "Assigned Staff": assigned_staff
        }

        # Append Data
        df = pd.concat([df, pd.DataFrame([new_client])], ignore_index=True)

        # Save Back to Excel
        df.to_excel(FILE_PATH, index=False)
                # Create client folder structure
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
                    # Create document checklist
        checklist_path = f"{base_path}/document_checklist.xlsx"

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

        checklist_df.to_excel(checklist_path, index=False)

        st.sidebar.success("✅ Client Added, Folders & Checklist Created!")

# Summary Metrics
st.subheader("📌 Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Clients", len(df))

with col2:
    pending_audit = len(df[df["Audit Status"] == "Pending"])
    st.metric("Pending Audits", pending_audit)

with col3:
    completed_audit = len(df[df["Audit Status"] == "Completed"])
    st.metric("Completed Audits", completed_audit)

with col4:
    filed_returns = len(df[df["Filing Status"] == "Filed"])
    st.metric("Filed Returns", filed_returns)

# Display Table
st.subheader("📋 Client Database")

st.dataframe(df, use_container_width=True)

# Download Option
st.download_button(
    label="⬇ Download Client Data",
    data=df.to_csv(index=False),
    file_name="client_data.csv",
    mime="text/csv"
)