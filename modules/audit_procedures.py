import os
import pandas as pd
import streamlit as st

from utils.common import load_clients


def show_audit_procedures():
    st.subheader("🔍 Audit Procedures")

    procedure = st.selectbox(
        "Select Audit Procedure",
        [
            "Trial Balance Verification",
            "Depreciation Schedule",
            "TDS Reconciliation",
            "GST Reconciliation",
            "Clause 44 Working",
            "Cash Payment Verification",
            "Loan Verification",
            "Related Party Transactions",
            "Quantitative Details",
            "Stock Verification"
        ]
    )

    if procedure == "Trial Balance Verification":
        trial_balance_verification()


def trial_balance_verification():
    st.subheader("📘 Trial Balance Verification")

    df = load_clients()

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    selected_client = st.selectbox(
        "Search / Select Client",
        client_list,
        index=0 if len(client_list) > 0 else None,
        placeholder="Search client name..."
    )

    if len(df) == 0 or not selected_client:
        st.info("Please select a client.")
        return

    selected_row = df[df["Client Name"] == selected_client].iloc[0]
    selected_ay = selected_row["AY"]

    tb_folder = f"clients/{selected_client}/AY {selected_ay}/Financial Statements"
    os.makedirs(tb_folder, exist_ok=True)

    st.write(f"### Client: {selected_client} | AY: {selected_ay}")

    uploaded_tb = st.file_uploader(
        "Upload Trial Balance Excel",
        type=["xlsx", "xls"],
        key="trial_balance_upload"
    )

    tb_path = f"{tb_folder}/trial_balance.xlsx"

    if uploaded_tb is not None:
        with open(tb_path, "wb") as f:
            f.write(uploaded_tb.getbuffer())

        st.success("✅ Trial Balance uploaded successfully!")

    if os.path.exists(tb_path):
        try:
            tb_df = pd.read_excel(tb_path)

            st.write("### Trial Balance Preview")
            st.dataframe(tb_df.head(20), use_container_width=True)

            st.write("### Detected Columns")
            st.write(list(tb_df.columns))

            ledger_column = st.selectbox(
                "Select Ledger Name Column",
                tb_df.columns,
                key="ledger_column"
            )

            amount_column = st.selectbox(
                "Select Amount / Closing Balance Column",
                tb_df.columns,
                key="amount_column"
            )

            if st.button("🔍 Analyze Trial Balance"):

                analysis_df = tb_df.copy()
                analysis_df[ledger_column] = analysis_df[ledger_column].astype(str)

                keywords = {
                    "Cash Ledgers": ["cash"],
                    "Bank Ledgers": ["bank"],
                    "Loan Ledgers": ["loan", "unsecured", "secured", "borrow"],
                    "Fixed Asset Ledgers": [
                        "fixed asset", "plant", "machinery",
                        "computer", "furniture", "vehicle"
                    ],
                    "GST Ledgers": ["gst", "cgst", "sgst", "igst"],
                    "TDS Ledgers": ["tds", "tax deducted"],
                    "Sales Ledgers": ["sales", "revenue", "turnover"],
                    "Purchase Ledgers": ["purchase"],
                    "Expense Ledgers": [
                        "expense", "charges", "rent", "salary",
                        "wages", "repair", "commission", "professional",
                        "interest", "freight"
                    ],
                    "Capital Ledgers": ["capital", "proprietor", "partner"],
                    "Sundry Debtors": ["debtor", "receivable"],
                    "Sundry Creditors": ["creditor", "payable"]
                }

                results = []

                for category, words in keywords.items():
                    matched = analysis_df[
                        analysis_df[ledger_column]
                        .str.lower()
                        .apply(lambda x: any(word in x for word in words))
                    ]

                    for _, row in matched.iterrows():
                        results.append({
                            "Category": category,
                            "Ledger Name": row[ledger_column],
                            "Amount": row[amount_column]
                        })

                result_df = pd.DataFrame(results)

                if len(result_df) > 0:
                    st.write("### Ledger Analysis Result")
                    st.dataframe(result_df, use_container_width=True)

                    output_path = f"{tb_folder}/trial_balance_analysis.xlsx"
                    result_df.to_excel(output_path, index=False)

                    st.success("✅ Trial Balance analysis completed and saved.")
                else:
                    st.warning("No matching audit-focus ledgers found.")

        except Exception as e:
            st.error(f"Error reading Trial Balance: {e}")

    else:
        st.info("Upload Trial Balance Excel to start verification.")