import os
from datetime import date

import pandas as pd
import streamlit as st

from utils.common import load_clients


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Tax Audit Automation System",
    page_icon="📊",
    layout="wide"
)


# ---------------------------------------------------------
# HTML RENDER HELPER
# ---------------------------------------------------------

def render_html(html):
    compact_html = " ".join(str(html).replace("\n", " ").split())
    st.markdown(compact_html, unsafe_allow_html=True)


# ---------------------------------------------------------
# CUSTOM CSS - DARK THEME
# ---------------------------------------------------------

render_html("""
<style>

.stApp {
    background:
        radial-gradient(circle at top left, rgba(34,197,94,0.08), transparent 28%),
        radial-gradient(circle at top right, rgba(59,130,246,0.10), transparent 30%),
        linear-gradient(135deg, #020617 0%, #0f172a 50%, #111827 100%);
    color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

header[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

html, body, [class*="css"] {
    color: #f8fafc;
}

h1, h2, h3, h4, h5, h6,
p, span, label, div {
    color: inherit;
}

label,
.stMarkdown,
.stText,
.stCaption,
small {
    color: #e5e7eb !important;
}

div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] span {
    color: #f8fafc !important;
}

input, textarea {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}

[data-testid="stDateInput"] input {
    background-color: #1e293b !important;
    color: #f8fafc !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #1e293b !important;
    color: #f8fafc !important;
}

[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 16px;
    padding: 14px 16px;
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-weight: 700;
}

[data-testid="stMetricValue"] {
    color: #f8fafc !important;
    font-weight: 900;
}

[data-testid="stDataFrame"] {
    background: rgba(15, 23, 42, 0.75);
    border-radius: 12px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a, #1e293b);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #e5e7eb;
    font-weight: 700;
}

[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 14px;
    padding: 12px 14px !important;
    margin-bottom: 10px;
    min-height: 50px;
    cursor: pointer;
    transition: all 0.22s ease-in-out;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(59,130,246,0.22);
    border: 1px solid rgba(96,165,250,0.65);
    transform: translateX(3px);
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(135deg, #16a34a, #2563eb);
    border: 2px solid #f8fafc;
    border-radius: 18px;
    padding: 17px 16px !important;
    min-height: 62px;
    transform: scale(1.03);
    box-shadow: 0 10px 28px rgba(37,99,235,0.42);
}

[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 16px !important;
    font-weight: 750 !important;
    color: #f8fafc !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    font-size: 17px !important;
    font-weight: 900 !important;
    letter-spacing: 0.2px;
}

.main-header-box {
    padding: 20px 24px;
    border-radius: 22px;
    background: linear-gradient(135deg, #064e3b, #1d4ed8, #581c87);
    color: white;
    margin-bottom: 18px;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
}

.main-header-title-row {
    display: flex;
    align-items: center;
    gap: 14px;
}

.main-header-icon {
    font-size: 40px;
}

.main-header-title {
    font-size: 36px;
    font-weight: 900;
    line-height: 1.08;
    color: white;
}

.main-header-taas {
    font-size: 16px;
    font-style: italic;
    opacity: 0.98;
    margin-top: 8px;
    margin-bottom: 12px;
    color: #f8fafc;
}

.ca-title-box {
    margin-top: 14px;
    padding: 16px 18px;
    border-radius: 16px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.22);
}

.ca-title-main {
    font-size: 25px;
    font-weight: 900;
    color: white;
    line-height: 1.2;
}

.ca-title-sub {
    font-size: 13px;
    opacity: 0.92;
    margin-top: 4px;
    color: white;
}

.client-panel-box {
    padding-top: 8px;
}

.client-selector-title {
    font-size: 28px;
    font-weight: 900;
    color: #f8fafc;
    margin-bottom: 8px;
}

.client-selector-label {
    font-size: 14px;
    font-weight: 700;
    color: #cbd5e1;
    margin-bottom: 8px;
}

.active-client-card {
    padding: 16px 18px;
    border-radius: 18px;
    background: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(148, 163, 184, 0.18);
    margin-top: 18px;
    margin-bottom: 18px;
    box-shadow: 0 5px 18px rgba(0, 0, 0, 0.16);
}

.active-client-title {
    font-size: 15px;
    font-weight: 850;
    color: #f8fafc;
    margin-bottom: 8px;
}

.active-client-sub {
    font-size: 13px;
    color: #cbd5e1;
}

.hero {
    padding: 18px 22px;
    border-radius: 20px;
    background: linear-gradient(135deg, #065f46, #1d4ed8, #6d28d9);
    color: white;
    margin-bottom: 18px;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
}

.hero h1 {
    font-size: 30px;
    margin-bottom: 4px;
    font-weight: 900;
    color: white;
}

.hero p {
    font-size: 14px;
    margin-bottom: 2px;
    opacity: 0.96;
    color: #f8fafc;
}

.summary-heading {
    padding: 12px 16px;
    border-radius: 14px;
    background: rgba(15, 23, 42, 0.72);
    border-left: 6px solid #2563eb;
    font-size: 20px;
    font-weight: 900;
    color: #f8fafc;
    margin-top: 12px;
    margin-bottom: 12px;
}

[data-testid="stAlert"] {
    border-radius: 14px;
}

</style>
""")


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def financial_year(today):
    if today.month >= 4:
        return f"FY {today.year}-{str(today.year + 1)[-2:]}"
    return f"FY {today.year - 1}-{str(today.year)[-2:]}"


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


def calculate_wp_completion(client_name, ay):
    wp_path = f"clients/{client_name}/AY {ay}/working_papers_tracker.xlsx"

    if not os.path.exists(wp_path):
        return 0

    try:
        wp_df = pd.read_excel(wp_path)

        if len(wp_df) == 0 or "Status" not in wp_df.columns:
            return 0

        completed = len(wp_df[wp_df["Status"].astype(str) == "Completed"])
        return round((completed / len(wp_df)) * 100, 2)

    except Exception:
        return 0


def calculate_client_progress(row):
    doc_progress = safe_float(row.get("Checklist Completion %", 0))
    wp_progress = calculate_wp_completion(
        row.get("Client Name", ""),
        row.get("AY", "")
    )

    audit_status = str(row.get("Audit Status", "Pending"))
    form_status = str(row.get("3CD/3CA Filing Status", "Not Filed"))
    itr_status = str(row.get("ITR Filing Status", "Not Filed"))

    audit_progress = 100 if audit_status == "Completed" else 50 if audit_status == "In Progress" else 0
    form_progress = 100 if form_status == "Filed" else 0
    itr_progress = 100 if itr_status == "Filed" else 0

    total = (
        doc_progress * 0.25 +
        wp_progress * 0.35 +
        audit_progress * 0.20 +
        form_progress * 0.10 +
        itr_progress * 0.10
    )

    return round(total, 2)


# ---------------------------------------------------------
# GLOBAL CLIENT SELECTION
# ---------------------------------------------------------

def initialise_global_client_selection():
    df = load_clients()

    if df.empty or "Client Name" not in df.columns:
        st.session_state["global_selected_client"] = None
        st.session_state["global_selected_ay"] = None
        return df

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    if len(client_list) == 0:
        st.session_state["global_selected_client"] = None
        st.session_state["global_selected_ay"] = None
        return df

    if "global_selected_client" not in st.session_state:
        st.session_state["global_selected_client"] = None

    if st.session_state["global_selected_client"] not in client_list:
        st.session_state["global_selected_client"] = None
        st.session_state["global_selected_ay"] = None

    return df


def show_top_header():
    df = load_clients()
    today = date.today()

    left_col, right_col = st.columns([7, 3])

    with left_col:
        render_html(f"""
        <div class="main-header-box">
            <div class="main-header-title-row">
                <div class="main-header-icon">📊</div>
                <div class="main-header-title">Tax Audit Automation System</div>
            </div>

            <div class="main-header-taas">
                <b><i>(TAAS)</i></b> | {financial_year(today)} | Current Date: {today.strftime("%d-%m-%Y")}
            </div>

            <div class="ca-title-box">
                <div class="ca-title-main">Chartered Accountant</div>
                <div class="ca-title-sub">
                    Professional Tax Audit, Reporting and Compliance Workspace
                </div>
            </div>
        </div>
        """)

    with right_col:
        render_html("""
        <div class="client-panel-box">
            <div class="client-selector-title">🔎 Active Audit Client</div>
            <div class="client-selector-label">Search / Select Client for Audit Process</div>
        </div>
        """)

        if df.empty or "Client Name" not in df.columns:
            st.warning("No clients available.")
            st.session_state["global_selected_client"] = None
            st.session_state["global_selected_ay"] = None
            return

        client_list = sorted(df["Client Name"].dropna().unique().tolist())

        if len(client_list) == 0:
            st.warning("No clients available.")
            st.session_state["global_selected_client"] = None
            st.session_state["global_selected_ay"] = None
            return

        client_options = ["Select Client"] + client_list

        current_client = st.session_state.get("global_selected_client")

        if current_client in client_list:
            selected_index = client_options.index(current_client)
        else:
            selected_index = 0

        selected_client_display = st.selectbox(
            "Search / Select Client for Audit Process",
            client_options,
            index=selected_index,
            key="global_client_selector_display",
            label_visibility="collapsed"
        )

        if selected_client_display == "Select Client":
            st.session_state["global_selected_client"] = None
            st.session_state["global_selected_ay"] = None

            render_html("""
            <div class="active-client-card">
                <div class="active-client-title">Selected Client</div>
                <div class="active-client-sub">
                    <b>No client selected</b><br>
                    Please select a client to start audit process.
                </div>
            </div>
            """)
        else:
            st.session_state["global_selected_client"] = selected_client_display

            selected_row = df[df["Client Name"] == selected_client_display].iloc[0]
            selected_ay = selected_row["AY"]

            st.session_state["global_selected_ay"] = selected_ay

            render_html(f"""
            <div class="active-client-card">
                <div class="active-client-title">Selected Client</div>
                <div class="active-client-sub">
                    <b>{selected_client_display}</b><br>
                    Assessment Year: <b>{selected_ay}</b>
                </div>
            </div>
            """)


def get_active_client_context():
    selected_client = st.session_state.get("global_selected_client")
    selected_ay = st.session_state.get("global_selected_ay")

    if not selected_client or not selected_ay:
        return None, None

    return selected_client, selected_ay


# ---------------------------------------------------------
# HOME DASHBOARD
# ---------------------------------------------------------

def show_home():
    df = load_clients()
    today = date.today()

    render_html(f"""
    <div class="hero">
        <h1>Executive Audit Control Center</h1>
        <p>Welcome, Lokesh 👋</p>
        <p>{financial_year(today)} | Current Date: {today.strftime("%d-%m-%Y")}</p>
    </div>
    """)

    preferred_due_date = st.date_input(
        "Preferred Internal Due Date",
        value=date(today.year, 9, 15)
    )

    remaining_days = (preferred_due_date - today).days

    due_col1, due_col2 = st.columns(2)

    with due_col1:
        st.metric("Preferred Due Date", preferred_due_date.strftime("%d-%m-%Y"))

    with due_col2:
        st.metric("Days Remaining", remaining_days)

    render_html("""
    <div class="summary-heading">
        📌 Summary
    </div>
    """)

    c1, c2, c3, c4 = st.columns(4)

    if df.empty:
        total_clients = 0
        documents_pending = 0
        audit_pending = 0
        itr_not_filed = 0
    else:
        total_clients = len(df)

        documents_pending = (
            len(df[df["Document Status"] != "Received"])
            if "Document Status" in df.columns else 0
        )

        audit_pending = (
            len(df[df["Audit Status"] != "Completed"])
            if "Audit Status" in df.columns else 0
        )

        itr_not_filed = (
            len(df[df["ITR Filing Status"] == "Not Filed"])
            if "ITR Filing Status" in df.columns else 0
        )

    with c1:
        st.metric("Total Clients", total_clients)

    with c2:
        st.metric("Documents Pending", documents_pending)

    with c3:
        st.metric("Audit Pending", audit_pending)

    with c4:
        st.metric("ITR Not Filed", itr_not_filed)

    if not df.empty:
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
        if not df.empty:
            progress_rows = []

            for _, row in df.iterrows():
                progress_rows.append({
                    "Client Name": row.get("Client Name", ""),
                    "AY": row.get("AY", ""),
                    "Document %": row.get("Checklist Completion %", 0),
                    "Working Paper %": calculate_wp_completion(
                        row.get("Client Name", ""),
                        row.get("AY", "")
                    ),
                    "Overall Audit Progress %": calculate_client_progress(row)
                })

            progress_df = pd.DataFrame(progress_rows)
            st.dataframe(progress_df, use_container_width=True, hide_index=True)

        else:
            st.info("No clients available.")

    if st.button("📊 View Client-wise Progress"):
        show_client_progress_dialog()


# ---------------------------------------------------------
# MAIN APP
# ---------------------------------------------------------

initialise_global_client_selection()
show_top_header()

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "👥 Client Management",
        "📄 Document Collection",
        "🔍 Audit Procedures",
        "🗂️ Working Papers",
        "🧭 Tax Audit Applicability",
        "📑 Tax Report",
        "✅ Final Review",
    ]
)


# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------

if menu == "🏠 Home":
    show_home()

elif menu == "👥 Client Management":
    from modules.client_management import show_client_management
    show_client_management()

elif menu == "📄 Document Collection":
    from modules.document_collection import show_document_collection
    show_document_collection()

elif menu == "🔍 Audit Procedures":
    from modules.audit_procedures import show_audit_procedures
    show_audit_procedures()

elif menu == "🗂️ Working Papers":
    from modules.working_papers import show_working_papers
    show_working_papers()

elif menu == "🧭 Tax Audit Applicability":
    from modules.tax_audit_applicability import show_tax_audit_applicability
    show_tax_audit_applicability()

elif menu == "📑 Tax Report":
    from modules.tax_report import show_tax_report
    show_tax_report()

elif menu == "✅ Final Review":
    try:
        from modules.final_review import show_final_review
        show_final_review()
    except ModuleNotFoundError:
        st.warning("Final Review module is not available yet.")