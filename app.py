import streamlit as st
from utils.common import load_clients

st.set_page_config(
    page_title="Tax Audit Automation System",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Tax Audit Automation System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "👥 Client Management",
        "📄 Document Collection",
        "🗂️ Working Papers",
        "🔍 Audit Procedures",
        "✅ Final Review"
    ]
)

df = load_clients()

if menu == "🏠 Home":
    st.subheader("🏠 Home Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Clients", len(df))

    with col2:
        st.metric("Documents Pending", len(df[df["Document Status"] != "Received"]))

    with col3:
        st.metric("Audit Pending", len(df[df["Audit Status"] != "Completed"]))

    with col4:
        st.metric("ITR Not Filed", len(df[df["ITR Filing Status"] == "Not Filed"]))

elif menu == "👥 Client Management":
    from modules.client_management import show_client_management
    show_client_management()

elif menu == "📄 Document Collection":
    from modules.document_collection import show_document_collection
    show_document_collection()

elif menu == "🗂️ Working Papers":
    from modules.working_papers import show_working_papers
    show_working_papers()

elif menu == "🔍 Audit Procedures":
    from modules.audit_procedures import show_audit_procedures
    show_audit_procedures()

elif menu == "✅ Final Review":
    from modules.final_review import show_final_review
    show_final_review()