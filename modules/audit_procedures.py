import os
import pandas as pd
import streamlit as st

from utils.common import load_clients


def get_selected_client():
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
        return None, None, None

    selected_row = df[df["Client Name"] == selected_client].iloc[0]
    selected_ay = selected_row["AY"]

    return df, selected_client, selected_ay


def save_uploaded_file(uploaded_file, folder_path, file_name):
    os.makedirs(folder_path, exist_ok=True)
    file_path = f"{folder_path}/{file_name}"

    if uploaded_file is not None:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ File uploaded successfully!")

    return file_path


def read_excel_file(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


def generic_upload_preview(folder_path, upload_label, saved_file_name, uploader_key):
    uploaded_file = st.file_uploader(
        upload_label,
        type=["xlsx", "xls", "csv"],
        key=uploader_key
    )

    file_path = save_uploaded_file(uploaded_file, folder_path, saved_file_name)

    if os.path.exists(file_path):
        df = read_excel_file(file_path)
        if df is not None:
            st.write("### File Preview")
            st.dataframe(df.head(20), use_container_width=True)
            st.write("### Detected Columns")
            st.write(list(df.columns))
            return df, file_path

    return None, file_path


def show_audit_procedures():
    st.subheader("🔍 Audit Procedures")

    procedure = st.sidebar.radio(
        "Audit Procedure Menu",
        [
            "📘 Trial Balance Verification",
            "📉 Depreciation Schedule",
            "🧾 TDS Reconciliation",
            "🧮 GST Reconciliation",
            "📑 Clause 44 Working",
            "💵 Cash Payment Verification",
            "🏦 Loan Verification",
            "👥 Related Party Transactions",
            "📦 Quantitative Details",
            "🏬 Stock Verification"
        ]
    )

    if procedure == "📘 Trial Balance Verification":
        trial_balance_verification()
    elif procedure == "📉 Depreciation Schedule":
        depreciation_schedule()
    elif procedure == "🧾 TDS Reconciliation":
        tds_reconciliation()
    elif procedure == "🧮 GST Reconciliation":
        gst_reconciliation()
    elif procedure == "📑 Clause 44 Working":
        clause_44_working()
    elif procedure == "💵 Cash Payment Verification":
        cash_payment_verification()
    elif procedure == "🏦 Loan Verification":
        loan_verification()
    elif procedure == "👥 Related Party Transactions":
        related_party_transactions()
    elif procedure == "📦 Quantitative Details":
        quantitative_details()
    elif procedure == "🏬 Stock Verification":
        stock_verification()


def trial_balance_verification():
    st.subheader("📘 Trial Balance Verification")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Financial Statements"

    tb_df, _ = generic_upload_preview(
        folder_path,
        "Upload Trial Balance Excel",
        "trial_balance.xlsx",
        "trial_balance_upload"
    )

    if tb_df is not None:
        ledger_column = st.selectbox("Select Ledger Name Column", tb_df.columns)
        amount_column = st.selectbox("Select Amount / Closing Balance Column", tb_df.columns)

        if st.button("🔍 Analyze Trial Balance"):
            analysis_df = tb_df.copy()
            analysis_df[ledger_column] = analysis_df[ledger_column].astype(str)

            keywords = {
                "Cash Ledgers": ["cash"],
                "Bank Ledgers": ["bank"],
                "Loan Ledgers": ["loan", "unsecured", "secured", "borrow"],
                "Fixed Asset Ledgers": ["fixed asset", "plant", "machinery", "computer", "furniture", "vehicle"],
                "GST Ledgers": ["gst", "cgst", "sgst", "igst"],
                "TDS Ledgers": ["tds", "tax deducted"],
                "Sales Ledgers": ["sales", "revenue", "turnover"],
                "Purchase Ledgers": ["purchase"],
                "Expense Ledgers": ["expense", "charges", "rent", "salary", "wages", "repair", "commission", "interest"],
                "Capital Ledgers": ["capital", "proprietor", "partner"],
                "Debtors": ["debtor", "receivable"],
                "Creditors": ["creditor", "payable"]
            }

            results = []

            for category, words in keywords.items():
                matched = analysis_df[
                    analysis_df[ledger_column].str.lower().apply(
                        lambda x: any(word in x for word in words)
                    )
                ]

                for _, row in matched.iterrows():
                    results.append({
                        "Category": category,
                        "Ledger Name": row[ledger_column],
                        "Amount": row[amount_column]
                    })

            result_df = pd.DataFrame(results)

            if len(result_df) > 0:
                st.dataframe(result_df, use_container_width=True)
                result_df.to_excel(f"{folder_path}/trial_balance_analysis.xlsx", index=False)
                st.success("✅ Trial Balance analysis saved.")
            else:
                st.warning("No audit-focus ledgers detected.")


def depreciation_schedule():
    st.subheader("📉 Depreciation Schedule Verification")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/Depreciation"

    dep_df, _ = generic_upload_preview(
        folder_path,
        "Upload Depreciation / Fixed Asset Schedule",
        "depreciation_schedule.xlsx",
        "depreciation_upload"
    )

    if dep_df is not None:
        asset_col = st.selectbox("Select Asset / Block Column", dep_df.columns)
        wdv_col = st.selectbox("Select WDV / Opening Balance Column", dep_df.columns)
        addition_col = st.selectbox("Select Additions Column", dep_df.columns)
        dep_col = st.selectbox("Select Depreciation Column", dep_df.columns)

        if st.button("🔍 Analyze Depreciation"):
            result_df = dep_df.copy()

            result_df["Audit Observation"] = ""

            result_df.loc[
                pd.to_numeric(result_df[addition_col], errors="coerce").fillna(0) > 0,
                "Audit Observation"
            ] = "Verify invoice, capitalization date and GST treatment"

            result_df.loc[
                pd.to_numeric(result_df[dep_col], errors="coerce").fillna(0) == 0,
                "Audit Observation"
            ] = "Check why depreciation is not charged"

            st.dataframe(result_df, use_container_width=True)
            result_df.to_excel(f"{folder_path}/depreciation_analysis.xlsx", index=False)
            st.success("✅ Depreciation analysis saved.")


def tds_reconciliation():
    st.subheader("🧾 TDS Reconciliation")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/TDS"

    books_df, _ = generic_upload_preview(
        folder_path,
        "Upload Books TDS Ledger / TDS Expense Data",
        "books_tds.xlsx",
        "books_tds_upload"
    )

    form26as_df, _ = generic_upload_preview(
        folder_path,
        "Upload Form 26AS / TDS Statement",
        "form26as_tds.xlsx",
        "form26as_tds_upload"
    )

    if books_df is not None and form26as_df is not None:
        books_party = st.selectbox("Books: Select Party / Deductor Column", books_df.columns, key="books_party")
        books_amount = st.selectbox("Books: Select TDS Amount Column", books_df.columns, key="books_tds_amount")

        form_party = st.selectbox("26AS: Select Party / Deductor Column", form26as_df.columns, key="form_party")
        form_amount = st.selectbox("26AS: Select TDS Amount Column", form26as_df.columns, key="form_tds_amount")

        if st.button("🔍 Reconcile TDS"):
            books_summary = books_df.groupby(books_party)[books_amount].sum().reset_index()
            form_summary = form26as_df.groupby(form_party)[form_amount].sum().reset_index()

            books_summary.columns = ["Party", "Books TDS"]
            form_summary.columns = ["Party", "26AS TDS"]

            recon_df = pd.merge(books_summary, form_summary, on="Party", how="outer").fillna(0)
            recon_df["Difference"] = recon_df["Books TDS"] - recon_df["26AS TDS"]

            st.dataframe(recon_df, use_container_width=True)
            recon_df.to_excel(f"{folder_path}/tds_reconciliation.xlsx", index=False)
            st.success("✅ TDS reconciliation saved.")


def gst_reconciliation():
    st.subheader("🧮 GST Reconciliation")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/GST"

    books_df, _ = generic_upload_preview(
        folder_path,
        "Upload Books Sales Register",
        "books_sales.xlsx",
        "books_sales_upload"
    )

    gstr1_df, _ = generic_upload_preview(
        folder_path,
        "Upload GSTR-1 Sales Data",
        "gstr1_sales.xlsx",
        "gstr1_sales_upload"
    )

    if books_df is not None and gstr1_df is not None:
        books_inv = st.selectbox("Books: Select Invoice Number Column", books_df.columns, key="books_inv")
        books_taxable = st.selectbox("Books: Select Taxable Value Column", books_df.columns, key="books_taxable")
        books_tax = st.selectbox("Books: Select Tax Amount Column", books_df.columns, key="books_tax")

        gstr_inv = st.selectbox("GSTR-1: Select Invoice Number Column", gstr1_df.columns, key="gstr_inv")
        gstr_taxable = st.selectbox("GSTR-1: Select Taxable Value Column", gstr1_df.columns, key="gstr_taxable")
        gstr_tax = st.selectbox("GSTR-1: Select Tax Amount Column", gstr1_df.columns, key="gstr_tax")

        if st.button("🔍 Reconcile GST"):
            books_summary = books_df.groupby(books_inv)[[books_taxable, books_tax]].sum().reset_index()
            gstr_summary = gstr1_df.groupby(gstr_inv)[[gstr_taxable, gstr_tax]].sum().reset_index()

            books_summary.columns = ["Invoice No", "Books Taxable", "Books Tax"]
            gstr_summary.columns = ["Invoice No", "GSTR Taxable", "GSTR Tax"]

            recon_df = pd.merge(books_summary, gstr_summary, on="Invoice No", how="outer").fillna(0)

            recon_df["Taxable Difference"] = recon_df["Books Taxable"] - recon_df["GSTR Taxable"]
            recon_df["Tax Difference"] = recon_df["Books Tax"] - recon_df["GSTR Tax"]

            recon_df["Status"] = "Matched"
            recon_df.loc[recon_df["Books Taxable"] == 0, "Status"] = "Missing in Books"
            recon_df.loc[recon_df["GSTR Taxable"] == 0, "Status"] = "Missing in GSTR-1"
            recon_df.loc[
                (recon_df["Taxable Difference"] != 0) | (recon_df["Tax Difference"] != 0),
                "Status"
            ] = "Difference"

            st.dataframe(recon_df, use_container_width=True)
            recon_df.to_excel(f"{folder_path}/gst_reconciliation.xlsx", index=False)
            st.success("✅ GST reconciliation saved.")


def clause_44_working():
    st.subheader("📑 Clause 44 Working")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/Clause 44"

    expense_df, _ = generic_upload_preview(
        folder_path,
        "Upload Expense Ledger / Purchase Register",
        "clause44_expenses.xlsx",
        "clause44_upload"
    )

    if expense_df is not None:
        nature_col = st.selectbox("Select Nature of Expense Column", expense_df.columns)
        gst_col = st.selectbox("Select GST Registration Type Column", expense_df.columns)
        amount_col = st.selectbox("Select Amount Column", expense_df.columns)

        if st.button("🔍 Generate Clause 44 Summary"):
            summary_df = expense_df.groupby([nature_col, gst_col])[amount_col].sum().reset_index()
            summary_df.columns = ["Nature of Expense", "GST Registration Type", "Amount"]

            st.dataframe(summary_df, use_container_width=True)
            summary_df.to_excel(f"{folder_path}/clause44_summary.xlsx", index=False)
            st.success("✅ Clause 44 summary saved.")


def cash_payment_verification():
    st.subheader("💵 Cash Payment Verification")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/Cash Payments"

    cash_df, _ = generic_upload_preview(
        folder_path,
        "Upload Cash Book / Payment Register",
        "cash_payments.xlsx",
        "cash_payment_upload"
    )

    if cash_df is not None:
        date_col = st.selectbox("Select Date Column", cash_df.columns)
        party_col = st.selectbox("Select Party / Ledger Column", cash_df.columns)
        amount_col = st.selectbox("Select Amount Column", cash_df.columns)
        mode_col = st.selectbox("Select Payment Mode Column", cash_df.columns)

        threshold = st.number_input("Cash Payment Threshold", value=10000)

        if st.button("🔍 Verify Cash Payments"):
            result_df = cash_df.copy()
            result_df[amount_col] = pd.to_numeric(result_df[amount_col], errors="coerce").fillna(0)
            result_df[mode_col] = result_df[mode_col].astype(str)

            exception_df = result_df[
                (result_df[amount_col] > threshold) &
                (result_df[mode_col].str.lower().str.contains("cash"))
            ]

            st.dataframe(exception_df, use_container_width=True)
            exception_df.to_excel(f"{folder_path}/cash_payment_exceptions.xlsx", index=False)
            st.success("✅ Cash payment verification saved.")


def loan_verification():
    st.subheader("🏦 Loan Verification")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/Loans"

    loan_df, _ = generic_upload_preview(
        folder_path,
        "Upload Loan Register / Loan Ledger",
        "loan_register.xlsx",
        "loan_upload"
    )

    if loan_df is not None:
        lender_col = st.selectbox("Select Lender Column", loan_df.columns)
        opening_col = st.selectbox("Select Opening Balance Column", loan_df.columns)
        received_col = st.selectbox("Select Loan Received Column", loan_df.columns)
        repaid_col = st.selectbox("Select Loan Repaid Column", loan_df.columns)
        closing_col = st.selectbox("Select Closing Balance Column", loan_df.columns)

        if st.button("🔍 Verify Loans"):
            result_df = loan_df.copy()

            for col in [opening_col, received_col, repaid_col, closing_col]:
                result_df[col] = pd.to_numeric(result_df[col], errors="coerce").fillna(0)

            result_df["Calculated Closing"] = result_df[opening_col] + result_df[received_col] - result_df[repaid_col]
            result_df["Difference"] = result_df["Calculated Closing"] - result_df[closing_col]

            st.dataframe(result_df, use_container_width=True)
            result_df.to_excel(f"{folder_path}/loan_verification.xlsx", index=False)
            st.success("✅ Loan verification saved.")


def related_party_transactions():
    st.subheader("👥 Related Party Transactions")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/Related Parties"

    transaction_df, _ = generic_upload_preview(
        folder_path,
        "Upload Ledger / Transaction Data",
        "related_party_transactions.xlsx",
        "related_party_upload"
    )

    if transaction_df is not None:
        party_col = st.selectbox("Select Party Name Column", transaction_df.columns)
        amount_col = st.selectbox("Select Amount Column", transaction_df.columns)

        related_parties_text = st.text_area(
            "Enter related party names, one per line"
        )

        if st.button("🔍 Detect Related Party Transactions"):
            related_parties = [
                name.strip().lower()
                for name in related_parties_text.split("\n")
                if name.strip() != ""
            ]

            result_df = transaction_df.copy()
            result_df[party_col] = result_df[party_col].astype(str)

            matched_df = result_df[
                result_df[party_col].str.lower().apply(
                    lambda x: any(name in x for name in related_parties)
                )
            ]

            st.dataframe(matched_df, use_container_width=True)
            matched_df.to_excel(f"{folder_path}/related_party_matches.xlsx", index=False)
            st.success("✅ Related party analysis saved.")


def quantitative_details():
    st.subheader("📦 Quantitative Details")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/Quantitative Details"

    qty_df, _ = generic_upload_preview(
        folder_path,
        "Upload Quantitative Stock / Goods Movement Details",
        "quantitative_details.xlsx",
        "qty_upload"
    )

    if qty_df is not None:
        item_col = st.selectbox("Select Item Column", qty_df.columns)
        opening_col = st.selectbox("Select Opening Qty Column", qty_df.columns)
        purchase_col = st.selectbox("Select Purchase Qty Column", qty_df.columns)
        sales_col = st.selectbox("Select Sales Qty Column", qty_df.columns)
        closing_col = st.selectbox("Select Closing Qty Column", qty_df.columns)

        if st.button("🔍 Verify Quantitative Details"):
            result_df = qty_df.copy()

            for col in [opening_col, purchase_col, sales_col, closing_col]:
                result_df[col] = pd.to_numeric(result_df[col], errors="coerce").fillna(0)

            result_df["Calculated Closing Qty"] = result_df[opening_col] + result_df[purchase_col] - result_df[sales_col]
            result_df["Difference"] = result_df["Calculated Closing Qty"] - result_df[closing_col]

            st.dataframe(result_df, use_container_width=True)
            result_df.to_excel(f"{folder_path}/quantitative_details_verification.xlsx", index=False)
            st.success("✅ Quantitative details verification saved.")


def stock_verification():
    st.subheader("🏬 Stock Verification")

    df, selected_client, selected_ay = get_selected_client()
    if selected_client is None:
        return

    folder_path = f"clients/{selected_client}/AY {selected_ay}/Audit Working Papers/Stock Verification"

    stock_df, _ = generic_upload_preview(
        folder_path,
        "Upload Stock Statement",
        "stock_statement.xlsx",
        "stock_upload"
    )

    if stock_df is not None:
        item_col = st.selectbox("Select Item Column", stock_df.columns)
        qty_col = st.selectbox("Select Quantity Column", stock_df.columns)
        rate_col = st.selectbox("Select Rate Column", stock_df.columns)
        value_col = st.selectbox("Select Value Column", stock_df.columns)

        if st.button("🔍 Verify Stock Valuation"):
            result_df = stock_df.copy()

            result_df[qty_col] = pd.to_numeric(result_df[qty_col], errors="coerce").fillna(0)
            result_df[rate_col] = pd.to_numeric(result_df[rate_col], errors="coerce").fillna(0)
            result_df[value_col] = pd.to_numeric(result_df[value_col], errors="coerce").fillna(0)

            result_df["Calculated Value"] = result_df[qty_col] * result_df[rate_col]
            result_df["Difference"] = result_df["Calculated Value"] - result_df[value_col]

            st.dataframe(result_df, use_container_width=True)
            result_df.to_excel(f"{folder_path}/stock_valuation_verification.xlsx", index=False)
            st.success("✅ Stock verification saved.")