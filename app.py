import os
from datetime import date
import pandas as pd
import streamlit as st
from utils.common import load_clients

st.set_page_config(
    page_title="Tax Audit Automation System",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.hero {
    padding: 28px;
    border-radius: 22px;
    background: linear-gradient(135deg, #1f4e79, #7030a0, #0f9d58);
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    font-size: 42px;
    margin-bottom: 5px;
}
.hero p {
    font-size: 17px;
}
.card {
    padding: 20px;
    border-radius: 18px;
    background: #1e1e2f;
    border: 1px solid #3b3b52;
    text-align: center;
}
.card h3 {
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


def financial_year(today):
    if today.month >= 4:
        return f"FY {today.year}-{str(today.year + 1)[-2:]}"
    return f"FY {today.year - 1}-{str(today.year)[-2:]}"


def calculate_wp_completion(client_name, ay):
    wp_path = f"clients/{client_name}/AY {ay}/working_papers_tracker.xlsx"

    if not os.path.exists(wp_path):
        return 0

    wp_df = pd.read_excel(wp_path)

    if len(wp_df) == 0:
        return 0

    completed = len(wp_df[wp_df["Status"].astype(str) == "Completed"])
    return round((completed / len(wp_df)) * 100, 2)


def calculate_client_progress(row):
    doc_progress = float(row["Checklist Completion %"])
    wp_progress = calculate_wp_completion(row["Client Name"], row["AY"])

    audit_progress = 100 if row["Audit Status"] == "Completed" else 50 if row["Audit Status"] == "In Progress" else 0
    form_progress = 100 if row["3CD/3CA Filing Status"] == "Filed" else 0
    itr_progress = 100 if row["ITR Filing Status"] == "Filed" else 0

    total = (
        doc_progress * 0.25 +
        wp_progress * 0.35 +
        audit_progress * 0.20 +
        form_progress * 0.10 +
        itr_progress * 0.10
    )

    return round(total, 2)


def show_home():
    df = load_clients()
    today = date.today()

    st.markdown(f"""
    <div class="hero">
        <h1>Executive Audit Control Center</h1>
        <p>Welcome, Lokesh 👋</p>
        <p>{financial_year(today)} | Current Date: {today.strftime("%d-%m-%Y")}</p>
    </div>
    """, unsafe_allow_html=True)

    actual_due_date = st.date_input(
        "Tax Audit Applicable Due Date",
        value=date(today.year, 9, 30)
    )

    preferred_due_date = st.date_input(
        "Preferred Internal Due Date",
        value=date(today.year, 9, 15)
    )

    remaining_days = (preferred_due_date - today).days

    d1, d2, d3 = st.columns(3)

    with d1:
        st.metric("Actual Due Date", actual_due_date.strftime("%d-%m-%Y"))

    with d2:
        st.metric("Preferred Due Date", preferred_due_date.strftime("%d-%m-%Y"))

    with d3:
        st.metric("Days Remaining", remaining_days)

    st.subheader("📌 Progress Cards")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Clients", len(df))

    with c2:
        st.metric("Documents Pending", len(df[df["Document Status"] != "Received"]))

    with c3:
        st.metric("Audit Pending", len(df[df["Audit Status"] != "Completed"]))

    with c4:
        st.metric("ITR Not Filed", len(df[df["ITR Filing Status"] == "Not Filed"]))

    if len(df) > 0:
        client_progress_list = []

        for _, row in df.iterrows():
            client_progress_list.append(calculate_client_progress(row))

        overall_progress = round(sum(client_progress_list) / len(client_progress_list), 2)
    else:
        overall_progress = 0

    st.subheader("📊 Overall Tax Audit Progress")
    st.progress(overall_progress / 100)
    st.write(f"**Overall Progress: {overall_progress}%**")

    @st.dialog("Client-wise Audit Progress")
    def show_client_progress_dialog():
        if len(df) > 0:
            progress_rows = []

            for _, row in df.iterrows():
                progress_rows.append({
                    "Client Name": row["Client Name"],
                    "AY": row["AY"],
                    "Document %": row["Checklist Completion %"],
                    "Working Paper %": calculate_wp_completion(row["Client Name"], row["AY"]),
                    "Overall Audit Progress %": calculate_client_progress(row)
                })

            progress_df = pd.DataFrame(progress_rows)
            st.dataframe(progress_df, use_container_width=True)

            selected_client = st.selectbox(
                "Select Client to View Progress Bar",
                progress_df["Client Name"].tolist()
            )

            selected_progress = progress_df[
                progress_df["Client Name"] == selected_client
            ]["Overall Audit Progress %"].iloc[0]

            st.progress(selected_progress / 100)
            st.write(f"**{selected_client}: {selected_progress}% completed**")
        else:
            st.info("No clients available.")

    if st.button("📊 View Client-wise Progress"):
        show_client_progress_dialog()


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

if menu == "🏠 Home":
    show_home()

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