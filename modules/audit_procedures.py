import os
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.common import load_clients


# ---------------------------------------------------------
# AUDIT PROCEDURE LIBRARY
# ---------------------------------------------------------

AUDIT_PROCEDURES = {
    "Trial Balance Verification": {
        "description": "Verify whether Trial Balance is balanced, ledger balances are reasonable, and books are ready for audit procedures.",
        "required_sheets": [
            "Trial_Balance",
            "Ledger_Master",
            "Ledger_Details",
            "Opening_Balances",
            "Profit_and_Loss",
            "Balance_Sheet"
        ],
        "form_3cd_linkage": [
            "Clause 11 - Books of account",
            "Clause 13 - Method of accounting",
            "Clause 40 - Accounting ratios"
        ]
    },

    "Profit and Loss Verification": {
        "description": "Verify income, expenses, prior period items, capital items, abnormal expenses and P&L classification.",
        "required_sheets": [
            "Profit_and_Loss",
            "Trial_Balance",
            "Ledger_Details",
            "Expense_Ledgers",
            "Income_Ledgers",
            "Previous_Year_Financials",
            "Journal_Register"
        ],
        "form_3cd_linkage": [
            "Clause 13 - Method of accounting",
            "Clause 16 - Amounts not credited to P&L",
            "Clause 21 - Amounts inadmissible",
            "Clause 27 - Prior period items",
            "Clause 40 - Ratios"
        ]
    },

    "Balance Sheet Verification": {
        "description": "Verify assets, liabilities, capital, loans, statutory dues, creditors, debtors, provisions and classification.",
        "required_sheets": [
            "Balance_Sheet",
            "Trial_Balance",
            "Ledger_Details",
            "Opening_Balances",
            "Loan_Details",
            "Fixed_Asset_Register",
            "Statutory_Dues",
            "Creditor_Ageing",
            "Debtor_Ageing",
            "Outstanding_Payables",
            "Outstanding_Receivables",
            "Capital_Account"
        ],
        "form_3cd_linkage": [
            "Clause 11 - Books of account",
            "Clause 18 - Depreciation",
            "Clause 22 - MSME interest",
            "Clause 26 - Section 43B liabilities",
            "Clause 31 - Loans and deposits",
            "Clause 40 - Ratios"
        ]
    },

    "GST Reconciliation": {
        "description": "Reconcile books sales, purchases, output GST, input GST, GSTR-1, GSTR-3B, GSTR-2A and GSTR-2B.",
        "required_sheets": [
            "Books_Sales",
            "Books_Purchases",
            "GSTR1",
            "GSTR3B",
            "GSTR2A",
            "GSTR2B",
            "GST_Output_Ledger",
            "GST_Input_Ledger",
            "GST_ITC_Books",
            "GST_Payments",
            "GST_Return_Status"
        ],
        "form_3cd_linkage": [
            "Clause 4 - GST registration details",
            "Clause 27 - GST input credit treatment",
            "Clause 41 - GST demand / refund",
            "Clause 44 - GST expenditure break-up"
        ]
    },

    "TDS / TCS Verification": {
        "description": "Verify TDS payable, paid, receivable, received, returns, challans, 26AS and AIS/TIS reconciliation.",
        "required_sheets": [
            "Expense_Ledgers",
            "TDS_Deducted",
            "TDS_Payments",
            "TDS_Returns",
            "TDS_Ledger",
            "TDS_Receivable_Ledger",
            "Form_26AS",
            "AIS_TIS",
            "Vendor_Master",
            "Customer_Master"
        ],
        "form_3cd_linkage": [
            "Clause 21 - TDS default disallowance",
            "Clause 34 - TDS / TCS compliance"
        ]
    },

    "Section 43B Verification": {
        "description": "Verify statutory dues with books, returns, challans, deduction, deposit and due dates.",
        "required_sheets": [
            "Statutory_Dues",
            "GST_Return_Status",
            "GST_Ledger",
            "GST_Payments",
            "GSTR3B",
            "TDS_Ledger",
            "TDS_Deducted",
            "TDS_Payments",
            "TDS_Returns",
            "PF_ESI_Details",
            "PF_Returns",
            "ESI_Returns",
            "Professional_Tax_Returns",
            "Payment_Register",
            "Bank_Book",
            "Ledger_Details"
        ],
        "form_3cd_linkage": [
            "Clause 20 - Employee contribution",
            "Clause 21 - Certain disallowances",
            "Clause 26 - Section 43B liabilities",
            "Clause 34 - TDS / TCS compliance"
        ]
    },

    "Cash Payment Verification": {
        "description": "Identify cash payments requiring reporting or disallowance review under section 40A(3).",
        "required_sheets": [
            "Cash_Book",
            "Payment_Register",
            "Ledger_Details",
            "Expense_Ledgers",
            "Vendor_Master"
        ],
        "form_3cd_linkage": [
            "Clause 21 - Cash payment disallowance"
        ]
    },

    "Loans, Deposits and Specified Sums Verification": {
        "description": "Verify loans, deposits, specified sums, specified advances and cash receipt/payment restrictions.",
        "required_sheets": [
            "Loan_Details",
            "Ledger_Details",
            "Bank_Book",
            "Cash_Book",
            "Receipt_Register",
            "Payment_Register",
            "Party_Master"
        ],
        "form_3cd_linkage": [
            "Clause 30 - Hundi transactions",
            "Clause 31 - Loans, deposits, specified sums and advances"
        ]
    },

    "Related Party Verification": {
        "description": "Verify payments and transactions with related parties / specified persons.",
        "required_sheets": [
            "Related_Party_Master",
            "Partner_Director_Details",
            "Ledger_Details",
            "Expense_Ledgers",
            "Payment_Register",
            "Loan_Details"
        ],
        "form_3cd_linkage": [
            "Clause 23 - Payments to specified persons u/s 40A(2)(b)"
        ]
    },

    "MSME Verification": {
        "description": "Verify MSME vendors, ageing, delayed payments and interest implications.",
        "required_sheets": [
            "MSME_Vendor_List",
            "Creditor_Ageing",
            "Outstanding_Payables",
            "Vendor_Master",
            "Purchase_Register",
            "Payment_Register",
            "Ledger_Details"
        ],
        "form_3cd_linkage": [
            "Clause 22 - MSME interest inadmissible",
            "Clause 26 - Payment-based liabilities"
        ]
    },

    "Depreciation Verification": {
        "description": "Verify fixed assets, additions, deletions, depreciation as per books and Income-tax Act.",
        "required_sheets": [
            "Fixed_Asset_Register",
            "Additions",
            "Deletions",
            "Depreciation_As_Per_Books",
            "Depreciation_As_Per_IT",
            "Purchase_Register",
            "Trial_Balance",
            "Ledger_Details"
        ],
        "form_3cd_linkage": [
            "Clause 18 - Depreciation",
            "Clause 15 - Capital asset converted into stock-in-trade"
        ]
    },

    "Clause 44 GST Expenditure Break-up": {
        "description": "Prepare GST registered / unregistered expenditure break-up for Clause 44.",
        "required_sheets": [
            "Expense_Ledgers",
            "Purchase_Register",
            "Vendor_Master",
            "GSTIN_Master",
            "GSTR2B",
            "Trial_Balance"
        ],
        "form_3cd_linkage": [
            "Clause 44 - GST expenditure break-up"
        ]
    },

    "Stock and Quantitative Details Verification": {
        "description": "Verify stock movement, opening stock, purchases, sales, production, closing stock and valuation.",
        "required_sheets": [
            "Stock_Register",
            "Production_Register",
            "Opening_Stock",
            "Closing_Stock",
            "Physical_Verification_Report",
            "Purchase_Register",
            "Sales_Register",
            "Trial_Balance"
        ],
        "form_3cd_linkage": [
            "Clause 14 - Stock valuation",
            "Clause 35 - Quantitative details",
            "Clause 40 - Ratios"
        ]
    },

    "Tax Demand / Refund Verification": {
        "description": "Verify demand or refund under tax laws other than Income-tax Act and Wealth-tax Act.",
        "required_sheets": [
            "Tax_Demand_Refund_Details",
            "GST_Orders",
            "VAT_Orders",
            "Professional_Tax_Orders",
            "Other_Tax_Orders",
            "Appeal_Details"
        ],
        "form_3cd_linkage": [
            "Clause 41 - Demand or refund under other tax laws"
        ]
    },

    "Form 61 / 61A / 61B Verification": {
        "description": "Verify SFT and high-value transaction reporting requirement and filing status.",
        "required_sheets": [
            "SFT_Transactions",
            "Form_61_61A_61B_Status",
            "High_Value_Transactions",
            "Customer_Master",
            "Receipt_Register",
            "Sales_Register"
        ],
        "form_3cd_linkage": [
            "Clause 42 - Form 61 / 61A / 61B"
        ]
    },

    "Final Audit Observation Summary": {
        "description": "Consolidate exceptions, management replies, auditor remarks, tax adjustments and clause-wise impact.",
        "required_sheets": [
            "Exception_Report",
            "Management_Reply",
            "Auditor_Remarks",
            "Final_Adjustments",
            "Tax_Report_Linkage"
        ],
        "form_3cd_linkage": [
            "All relevant clauses"
        ]
    },
}


# ---------------------------------------------------------
# STYLE
# ---------------------------------------------------------

def apply_audit_procedure_style():
    st.markdown("""
    <style>
    .audit-hero {
        padding: 24px;
        border-radius: 22px;
        background: linear-gradient(135deg, #064e3b, #1d4ed8, #581c87);
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.25);
    }
    .audit-hero h2 {
        margin: 0;
        font-size: 34px;
        font-weight: 800;
    }
    .audit-hero p {
        margin-top: 8px;
        font-size: 16px;
        opacity: 0.95;
    }
    .active-client-strip {
        padding: 14px 18px;
        border-radius: 16px;
        background: #ecfdf5;
        border-left: 6px solid #10b981;
        color: #064e3b;
        margin-bottom: 18px;
        font-weight: 700;
    }
    .info-card {
        padding: 18px;
        border-radius: 18px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.08);
        margin-bottom: 12px;
    }
    .info-title {
        font-size: 18px;
        font-weight: 800;
        color: #111827;
    }
    .info-sub {
        color: #6b7280;
        font-size: 14px;
    }
    .section-banner {
        padding: 14px 18px;
        border-radius: 16px;
        background: #f8fafc;
        border-left: 6px solid #2563eb;
        margin-top: 12px;
        margin-bottom: 16px;
    }
    </style>
    """, unsafe_allow_html=True)


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
# PATH HELPERS
# ---------------------------------------------------------

def get_audit_procedure_folder(client_name, ay):
    folder = f"clients/{client_name}/AY {ay}/Audit Procedures"
    os.makedirs(folder, exist_ok=True)
    return folder


def get_document_checklist_path(client_name, ay):
    return f"clients/{client_name}/AY {ay}/document_checklist.xlsx"


def get_safe_file_name(name):
    return (
        str(name)
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .replace(",", "")
        .replace(":", "")
    )


# ---------------------------------------------------------
# COMMON HELPERS
# ---------------------------------------------------------

def safe_float(value):
    try:
        return float(str(value).replace(",", "").strip())
    except:
        return 0.0


def format_indian_number(value):
    try:
        value = safe_float(value)

        if value == 0:
            return "0"

        value = int(round(value, 0))
        s = str(value)

        if len(s) <= 3:
            return s

        last_three = s[-3:]
        remaining = s[:-3]

        parts = []

        while len(remaining) > 2:
            parts.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        if remaining:
            parts.insert(0, remaining)

        return ",".join(parts) + "," + last_three

    except:
        return str(value)


def normalize_column_name(col):
    return str(col).strip().lower().replace(" ", "_").replace("-", "_")


def normalize_df_columns(df):
    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    return df


def find_column(df, possible_names):
    normalized_columns = list(df.columns)

    for name in possible_names:
        normalized_name = normalize_column_name(name)

        if normalized_name in normalized_columns:
            return normalized_name

    for col in normalized_columns:
        for name in possible_names:
            if normalize_column_name(name) in col:
                return col

    return None


def get_sum(df, possible_columns):
    if df is None or df.empty:
        return 0.0

    df = normalize_df_columns(df)

    col = find_column(df, possible_columns)

    if not col:
        return 0.0

    return df[col].apply(safe_float).sum()


def get_available_sheets(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        return xls.sheet_names
    except:
        return []


def read_uploaded_excel(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        data = {}

        for sheet in xls.sheet_names:
            try:
                data[sheet] = pd.read_excel(uploaded_file, sheet_name=sheet)
            except:
                data[sheet] = pd.DataFrame()

        return data

    except Exception as e:
        st.error(f"Unable to read uploaded Excel file. Error: {e}")
        return {}


def get_sheet_data(workbook_data, sheet_name):
    for available_sheet, df in workbook_data.items():
        if normalize_column_name(available_sheet) == normalize_column_name(sheet_name):
            return df

    return pd.DataFrame()


def check_required_sheets(required_sheets, available_sheets):
    available_normalized = [normalize_column_name(sheet) for sheet in available_sheets]

    rows = []

    for sheet in required_sheets:
        is_available = normalize_column_name(sheet) in available_normalized

        rows.append({
            "Required Sheet": sheet,
            "Available in Uploaded File": "Yes" if is_available else "No"
        })

    return pd.DataFrame(rows)


def load_document_collection_status(client_name, ay, required_sheets):
    checklist_path = get_document_checklist_path(client_name, ay)

    if not os.path.exists(checklist_path):
        return pd.DataFrame([
            {
                "Required Sheet": sheet,
                "Document Collection Status": "Checklist Not Found"
            }
            for sheet in required_sheets
        ])

    try:
        checklist_df = pd.read_excel(checklist_path)

        if "Document Name" not in checklist_df.columns or "Status" not in checklist_df.columns:
            return pd.DataFrame([
                {
                    "Required Sheet": sheet,
                    "Document Collection Status": "Invalid Checklist"
                }
                for sheet in required_sheets
            ])

        rows = []

        for sheet in required_sheets:
            match = checklist_df[
                checklist_df["Document Name"].astype(str).str.lower() == str(sheet).lower()
            ]

            if len(match) > 0:
                rows.append({
                    "Required Sheet": sheet,
                    "Document Collection Status": match.iloc[0]["Status"]
                })
            else:
                rows.append({
                    "Required Sheet": sheet,
                    "Document Collection Status": "Not in Checklist"
                })

        return pd.DataFrame(rows)

    except Exception as e:
        return pd.DataFrame([
            {
                "Required Sheet": sheet,
                "Document Collection Status": f"Error: {e}"
            }
            for sheet in required_sheets
        ])


def make_exception_row(
    procedure,
    check_name,
    status,
    observation,
    amount_as_per_books=0,
    amount_as_per_return=0,
    difference=0,
    risk_level="Low",
    form_3cd_clause="",
    auditor_action="Review"
):
    return {
        "Procedure": procedure,
        "Check Name": check_name,
        "Status": status,
        "Observation": observation,
        "Amount as per Books": amount_as_per_books,
        "Amount as per Return / External Data": amount_as_per_return,
        "Difference": difference,
        "Risk Level": risk_level,
        "Form 3CD Linkage": form_3cd_clause,
        "Auditor Action": auditor_action
    }


def save_procedure_result(client_name, ay, procedure_name, result_df, summary_data):
    folder = get_audit_procedure_folder(client_name, ay)
    safe_name = get_safe_file_name(procedure_name)

    excel_path = f"{folder}/{safe_name}_result.xlsx"
    json_path = f"{folder}/{safe_name}_summary.json"

    with pd.ExcelWriter(excel_path) as writer:
        result_df.to_excel(writer, sheet_name="Exceptions", index=False)
        pd.DataFrame([summary_data]).to_excel(writer, sheet_name="Summary", index=False)

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(summary_data, file, indent=4, ensure_ascii=False)

    return excel_path, json_path


# ---------------------------------------------------------
# PROCEDURE AUTOMATION
# ---------------------------------------------------------

def run_trial_balance_verification(workbook_data):
    procedure = "Trial Balance Verification"
    rows = []

    tb = get_sheet_data(workbook_data, "Trial_Balance")

    if tb.empty:
        rows.append(make_exception_row(
            procedure,
            "Trial Balance Sheet Availability",
            "Exception",
            "Trial_Balance sheet is not available in uploaded file.",
            risk_level="High",
            form_3cd_clause="Clause 11 / Clause 40",
            auditor_action="Upload Trial_Balance sheet"
        ))
        return pd.DataFrame(rows)

    tb_norm = normalize_df_columns(tb)

    debit_col = find_column(tb_norm, ["Debit", "Debit Amount", "Dr", "Dr Amount"])
    credit_col = find_column(tb_norm, ["Credit", "Credit Amount", "Cr", "Cr Amount"])
    balance_col = find_column(tb_norm, ["Balance", "Closing Balance", "Amount"])
    ledger_col = find_column(tb_norm, ["Ledger Name", "Particulars", "Account Name", "Ledger"])

    if debit_col and credit_col:
        total_debit = tb_norm[debit_col].apply(safe_float).sum()
        total_credit = tb_norm[credit_col].apply(safe_float).sum()
        difference = round(total_debit - total_credit, 2)

        rows.append(make_exception_row(
            procedure,
            "Debit Total vs Credit Total",
            "OK" if abs(difference) <= 1 else "Exception",
            f"Debit total ₹{format_indian_number(total_debit)} and credit total ₹{format_indian_number(total_credit)}.",
            total_debit,
            total_credit,
            difference,
            "Low" if abs(difference) <= 1 else "High",
            "Clause 11",
            "Review TB balancing difference" if abs(difference) > 1 else "No action required"
        ))
    else:
        rows.append(make_exception_row(
            procedure,
            "Trial Balance Column Check",
            "Review",
            "Debit/Credit columns were not found. Check Trial_Balance format.",
            risk_level="Medium",
            form_3cd_clause="Clause 11",
            auditor_action="Verify TB columns"
        ))

    if balance_col:
        negative_df = tb_norm[tb_norm[balance_col].apply(safe_float) < 0]

        rows.append(make_exception_row(
            procedure,
            "Negative Balances",
            "OK" if len(negative_df) == 0 else "Review",
            f"{len(negative_df)} ledgers have negative balances.",
            len(negative_df),
            0,
            len(negative_df),
            "Low" if len(negative_df) == 0 else "Medium",
            "Clause 11 / Clause 40",
            "Review negative ledger balances" if len(negative_df) > 0 else "No action required"
        ))

    if ledger_col:
        blank_ledgers = tb_norm[tb_norm[ledger_col].astype(str).str.strip().isin(["", "nan", "None"])]

        rows.append(make_exception_row(
            procedure,
            "Blank Ledger Names",
            "OK" if len(blank_ledgers) == 0 else "Exception",
            f"{len(blank_ledgers)} rows have blank ledger names.",
            len(blank_ledgers),
            0,
            len(blank_ledgers),
            "Low" if len(blank_ledgers) == 0 else "High",
            "Clause 11",
            "Correct blank ledger names" if len(blank_ledgers) > 0 else "No action required"
        ))

    return pd.DataFrame(rows)


def run_profit_and_loss_verification(workbook_data):
    procedure = "Profit and Loss Verification"
    rows = []

    pl = get_sheet_data(workbook_data, "Profit_and_Loss")
    tb = get_sheet_data(workbook_data, "Trial_Balance")
    expense_ledgers = get_sheet_data(workbook_data, "Expense_Ledgers")
    income_ledgers = get_sheet_data(workbook_data, "Income_Ledgers")
    previous_year = get_sheet_data(workbook_data, "Previous_Year_Financials")

    pl_income = get_sum(pl, ["Income", "Revenue", "Sales", "Credit", "Amount"])
    income_total = get_sum(income_ledgers, ["Amount", "Income", "Revenue", "Credit"])
    pl_expense = get_sum(pl, ["Expense", "Debit", "Amount"])
    expense_total = get_sum(expense_ledgers, ["Amount", "Expense", "Debit"])

    diff_income = round(pl_income - income_total, 2)

    rows.append(make_exception_row(
        procedure,
        "P&L Income vs Income Ledgers",
        "OK" if abs(diff_income) <= 1 else "Review",
        f"P&L income ₹{format_indian_number(pl_income)} vs income ledgers ₹{format_indian_number(income_total)}.",
        pl_income,
        income_total,
        diff_income,
        "Low" if abs(diff_income) <= 1 else "Medium",
        "Clause 16 / Clause 40",
        "Review income reconciliation" if abs(diff_income) > 1 else "No action required"
    ))

    diff_expense = round(pl_expense - expense_total, 2)

    rows.append(make_exception_row(
        procedure,
        "P&L Expenses vs Expense Ledgers",
        "OK" if abs(diff_expense) <= 1 else "Review",
        f"P&L expenses ₹{format_indian_number(pl_expense)} vs expense ledgers ₹{format_indian_number(expense_total)}.",
        pl_expense,
        expense_total,
        diff_expense,
        "Low" if abs(diff_expense) <= 1 else "Medium",
        "Clause 21 / Clause 40",
        "Review expense reconciliation" if abs(diff_expense) > 1 else "No action required"
    ))

    combined = pd.concat(
        [pl, expense_ledgers, income_ledgers],
        ignore_index=True
    ) if not pl.empty or not expense_ledgers.empty or not income_ledgers.empty else pd.DataFrame()

    if not combined.empty:
        combined_norm = normalize_df_columns(combined)
        ledger_col = find_column(combined_norm, ["Ledger Name", "Particulars", "Account Name", "Description"])
        amount_col = find_column(combined_norm, ["Amount", "Debit", "Expense Amount"])

        if ledger_col:
            prior_period = combined_norm[
                combined_norm[ledger_col].astype(str).str.lower().str.contains("prior period", na=False)
            ]

            rows.append(make_exception_row(
                procedure,
                "Prior Period Items",
                "OK" if len(prior_period) == 0 else "Review",
                f"{len(prior_period)} possible prior period items found.",
                len(prior_period),
                0,
                len(prior_period),
                "Low" if len(prior_period) == 0 else "Medium",
                "Clause 27",
                "Review prior period income/expense" if len(prior_period) > 0 else "No action required"
            ))

            capital_keywords = "asset|computer|laptop|vehicle|furniture|machinery|equipment|building|software"
            capital_like = combined_norm[
                combined_norm[ledger_col].astype(str).str.lower().str.contains(capital_keywords, na=False)
            ]

            rows.append(make_exception_row(
                procedure,
                "Possible Capital Expenditure in P&L",
                "OK" if len(capital_like) == 0 else "Review",
                f"{len(capital_like)} possible capital nature items found in P&L/expense ledgers.",
                len(capital_like),
                0,
                len(capital_like),
                "Low" if len(capital_like) == 0 else "High",
                "Clause 21 / Clause 18",
                "Review capital vs revenue classification" if len(capital_like) > 0 else "No action required"
            ))

    if not previous_year.empty:
        current_total = pl_income - pl_expense
        previous_profit = get_sum(previous_year, ["Net Profit", "Profit", "Amount"])
        variation = round(current_total - previous_profit, 2)

        rows.append(make_exception_row(
            procedure,
            "Current Year Profit vs Previous Year",
            "Review",
            f"Current profit ₹{format_indian_number(current_total)} vs previous year ₹{format_indian_number(previous_profit)}.",
            current_total,
            previous_profit,
            variation,
            "Medium",
            "Clause 40",
            "Review major variation"
        ))

    return pd.DataFrame(rows)


def run_balance_sheet_verification(workbook_data):
    procedure = "Balance Sheet Verification"
    rows = []

    bs = get_sheet_data(workbook_data, "Balance_Sheet")
    tb = get_sheet_data(workbook_data, "Trial_Balance")
    loans = get_sheet_data(workbook_data, "Loan_Details")
    statutory = get_sheet_data(workbook_data, "Statutory_Dues")
    creditors = get_sheet_data(workbook_data, "Creditor_Ageing")
    debtors = get_sheet_data(workbook_data, "Debtor_Ageing")

    assets_total = get_sum(bs, ["Assets", "Asset Amount", "Debit", "Amount"])
    liabilities_total = get_sum(bs, ["Liabilities", "Liability Amount", "Credit", "Amount"])

    diff = round(assets_total - liabilities_total, 2)

    rows.append(make_exception_row(
        procedure,
        "Total Assets vs Total Liabilities",
        "OK" if abs(diff) <= 1 else "Exception",
        f"Assets ₹{format_indian_number(assets_total)} vs liabilities ₹{format_indian_number(liabilities_total)}.",
        assets_total,
        liabilities_total,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 11 / Clause 40",
        "Review balance sheet mismatch" if abs(diff) > 1 else "No action required"
    ))

    loan_total = get_sum(loans, ["Amount", "Loan Amount", "Closing Balance"])
    statutory_total = get_sum(statutory, ["Amount", "Payable Amount", "Liability Amount"])
    creditor_total = get_sum(creditors, ["Amount", "Outstanding", "Balance"])
    debtor_total = get_sum(debtors, ["Amount", "Outstanding", "Balance"])

    rows.append(make_exception_row(
        procedure,
        "Loans Balance Review",
        "Review" if loan_total > 0 else "OK",
        f"Loans captured for review: ₹{format_indian_number(loan_total)}.",
        loan_total,
        0,
        loan_total,
        "Medium" if loan_total > 0 else "Low",
        "Clause 31",
        "Review loan acceptance/repayment mode" if loan_total > 0 else "No action required"
    ))

    rows.append(make_exception_row(
        procedure,
        "Statutory Dues Outstanding",
        "Review" if statutory_total > 0 else "OK",
        f"Statutory dues captured for review: ₹{format_indian_number(statutory_total)}.",
        statutory_total,
        0,
        statutory_total,
        "Medium" if statutory_total > 0 else "Low",
        "Clause 26",
        "Verify payment before due date" if statutory_total > 0 else "No action required"
    ))

    rows.append(make_exception_row(
        procedure,
        "Creditor Ageing Review",
        "Review" if creditor_total > 0 else "OK",
        f"Creditors captured for ageing review: ₹{format_indian_number(creditor_total)}.",
        creditor_total,
        0,
        creditor_total,
        "Medium" if creditor_total > 0 else "Low",
        "Clause 22 / Clause 26",
        "Review MSME and ageing" if creditor_total > 0 else "No action required"
    ))

    rows.append(make_exception_row(
        procedure,
        "Debtor Ageing Review",
        "Review" if debtor_total > 0 else "OK",
        f"Debtors captured for ageing review: ₹{format_indian_number(debtor_total)}.",
        debtor_total,
        0,
        debtor_total,
        "Medium" if debtor_total > 0 else "Low",
        "Clause 40",
        "Review recoverability" if debtor_total > 0 else "No action required"
    ))

    return pd.DataFrame(rows)


def run_gst_reconciliation(workbook_data):
    procedure = "GST Reconciliation"
    rows = []

    books_sales = get_sheet_data(workbook_data, "Books_Sales")
    books_purchases = get_sheet_data(workbook_data, "Books_Purchases")
    gstr1 = get_sheet_data(workbook_data, "GSTR1")
    gstr3b = get_sheet_data(workbook_data, "GSTR3B")
    gstr2a = get_sheet_data(workbook_data, "GSTR2A")
    gstr2b = get_sheet_data(workbook_data, "GSTR2B")
    gst_input_books = get_sheet_data(workbook_data, "GST_Input_Ledger")
    gst_itc_books = get_sheet_data(workbook_data, "GST_ITC_Books")

    books_sales_value = get_sum(books_sales, ["Taxable Value", "Sales Amount", "Turnover", "Invoice Value", "Amount"])
    gstr1_value = get_sum(gstr1, ["Taxable Value", "Invoice Value", "Turnover", "Amount"])
    diff = round(books_sales_value - gstr1_value, 2)

    rows.append(make_exception_row(
        procedure,
        "Books Turnover vs GSTR-1 - Sales Reco",
        "OK" if abs(diff) <= 1 else "Exception",
        f"Books sales ₹{format_indian_number(books_sales_value)} vs GSTR-1 ₹{format_indian_number(gstr1_value)}.",
        books_sales_value,
        gstr1_value,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 4 / Clause 44",
        "Review sales turnover mismatch" if abs(diff) > 1 else "No action required"
    ))

    books_purchase_value = get_sum(books_purchases, ["Taxable Value", "Purchase Amount", "Invoice Value", "Amount"])
    gstr2b_purchase_value = get_sum(gstr2b, ["Taxable Value", "Invoice Value", "Amount"])
    diff = round(books_purchase_value - gstr2b_purchase_value, 2)

    rows.append(make_exception_row(
        procedure,
        "Books Purchases vs GSTR-2B - Purchases Reco",
        "OK" if abs(diff) <= 1 else "Exception",
        f"Books purchases ₹{format_indian_number(books_purchase_value)} vs GSTR-2B purchases ₹{format_indian_number(gstr2b_purchase_value)}.",
        books_purchase_value,
        gstr2b_purchase_value,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 44",
        "Review purchase mismatch and ITC eligibility" if abs(diff) > 1 else "No action required"
    ))

    input_books_value = get_sum(gst_input_books, ["GST Amount", "Input GST", "ITC", "Tax Amount", "Amount"])

    if input_books_value == 0:
        input_books_value = get_sum(gst_itc_books, ["GST Amount", "Input GST", "ITC", "Tax Amount", "Amount"])

    gstr2a_itc = get_sum(gstr2a, ["GST Amount", "Input GST", "ITC", "Tax Amount", "Amount"])
    diff = round(input_books_value - gstr2a_itc, 2)

    rows.append(make_exception_row(
        procedure,
        "GST as per Books vs GSTR-2A - Input Reco",
        "OK" if abs(diff) <= 1 else "Exception",
        f"Input GST as per books ₹{format_indian_number(input_books_value)} vs GSTR-2A ₹{format_indian_number(gstr2a_itc)}.",
        input_books_value,
        gstr2a_itc,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 27 / Clause 44",
        "Review input GST difference" if abs(diff) > 1 else "No action required"
    ))

    gstr2b_itc = get_sum(gstr2b, ["GST Amount", "Input GST", "ITC", "Tax Amount", "Amount"])
    diff = round(input_books_value - gstr2b_itc, 2)

    rows.append(make_exception_row(
        procedure,
        "GST as per Books vs GSTR-2B - Input Reco",
        "OK" if abs(diff) <= 1 else "Exception",
        f"Input GST as per books ₹{format_indian_number(input_books_value)} vs GSTR-2B ₹{format_indian_number(gstr2b_itc)}.",
        input_books_value,
        gstr2b_itc,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 27 / Clause 44",
        "Review ITC as per books and 2B difference" if abs(diff) > 1 else "No action required"
    ))

    gstr3b_turnover = get_sum(gstr3b, ["Taxable Value", "Turnover", "Outward Taxable Supplies", "Amount"])
    diff = round(gstr1_value - gstr3b_turnover, 2)

    rows.append(make_exception_row(
        procedure,
        "GSTR-1 vs GSTR-3B",
        "OK" if abs(diff) <= 1 else "Exception",
        f"GSTR-1 turnover ₹{format_indian_number(gstr1_value)} vs GSTR-3B turnover ₹{format_indian_number(gstr3b_turnover)}.",
        gstr1_value,
        gstr3b_turnover,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 4 / Clause 41",
        "Review GST return mismatch" if abs(diff) > 1 else "No action required"
    ))

    return pd.DataFrame(rows)


def run_tds_tcs_verification(workbook_data):
    procedure = "TDS / TCS Verification"
    rows = []

    expense_ledgers = get_sheet_data(workbook_data, "Expense_Ledgers")
    tds_deducted = get_sheet_data(workbook_data, "TDS_Deducted")
    tds_payments = get_sheet_data(workbook_data, "TDS_Payments")
    tds_returns = get_sheet_data(workbook_data, "TDS_Returns")
    tds_receivable = get_sheet_data(workbook_data, "TDS_Receivable_Ledger")
    form_26as = get_sheet_data(workbook_data, "Form_26AS")
    ais_tis = get_sheet_data(workbook_data, "AIS_TIS")

    expense_tds_base = get_sum(expense_ledgers, ["TDS Applicable Amount", "Amount", "Expense Amount"])
    tds_deducted_amount = get_sum(tds_deducted, ["TDS Amount", "Tax Deducted", "Amount"])
    tds_paid_amount = get_sum(tds_payments, ["TDS Paid", "Challan Amount", "Amount"])
    tds_return_amount = get_sum(tds_returns, ["TDS Amount", "Tax Deducted", "Amount"])

    diff = round(tds_deducted_amount - tds_paid_amount, 2)

    rows.append(make_exception_row(
        procedure,
        "TDS Payable vs TDS Paid",
        "OK" if abs(diff) <= 1 else "Exception",
        f"TDS deducted ₹{format_indian_number(tds_deducted_amount)} vs TDS paid ₹{format_indian_number(tds_paid_amount)}.",
        tds_deducted_amount,
        tds_paid_amount,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 34",
        "Verify unpaid / short-paid TDS" if abs(diff) > 1 else "No action required"
    ))

    diff = round(tds_deducted_amount - tds_return_amount, 2)

    rows.append(make_exception_row(
        procedure,
        "TDS Deducted vs TDS Return",
        "OK" if abs(diff) <= 1 else "Exception",
        f"TDS deducted as per books ₹{format_indian_number(tds_deducted_amount)} vs TDS return ₹{format_indian_number(tds_return_amount)}.",
        tds_deducted_amount,
        tds_return_amount,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 34",
        "Verify TDS return mismatch" if abs(diff) > 1 else "No action required"
    ))

    if expense_tds_base > 0 and tds_deducted_amount == 0:
        rows.append(make_exception_row(
            procedure,
            "Possible Non-deduction of TDS",
            "Review",
            "Expense ledgers have amounts but TDS deducted data is zero / missing.",
            expense_tds_base,
            0,
            expense_tds_base,
            "High",
            "Clause 21 / Clause 34",
            "Review TDS applicability on expense ledgers"
        ))

    tds_receivable_books = get_sum(tds_receivable, ["TDS Receivable", "TDS Amount", "Amount"])
    tds_as_per_26as = get_sum(form_26as, ["TDS Amount", "Tax Deducted", "Amount", "Credit Amount"])
    tds_as_per_ais = get_sum(ais_tis, ["TDS Amount", "Tax Deducted", "Amount", "Credit Amount"])

    diff = round(tds_receivable_books - tds_as_per_26as, 2)

    rows.append(make_exception_row(
        procedure,
        "TDS Receivable as per Books vs Form 26AS",
        "OK" if abs(diff) <= 1 else "Exception",
        f"TDS receivable as per books ₹{format_indian_number(tds_receivable_books)} vs Form 26AS ₹{format_indian_number(tds_as_per_26as)}.",
        tds_receivable_books,
        tds_as_per_26as,
        diff,
        "Low" if abs(diff) <= 1 else "Medium",
        "ITR Credit Verification / Clause 34",
        "Review TDS credit mismatch" if abs(diff) > 1 else "No action required"
    ))

    diff = round(tds_receivable_books - tds_as_per_ais, 2)

    rows.append(make_exception_row(
        procedure,
        "TDS Receivable as per Books vs AIS/TIS",
        "OK" if abs(diff) <= 1 else "Review",
        f"TDS receivable as per books ₹{format_indian_number(tds_receivable_books)} vs AIS/TIS ₹{format_indian_number(tds_as_per_ais)}.",
        tds_receivable_books,
        tds_as_per_ais,
        diff,
        "Low" if abs(diff) <= 1 else "Medium",
        "ITR Credit Verification",
        "Review AIS/TIS mismatch" if abs(diff) > 1 else "No action required"
    ))

    return pd.DataFrame(rows)


def run_section_43b_verification(workbook_data):
    procedure = "Section 43B Verification"
    rows = []

    statutory_dues = get_sheet_data(workbook_data, "Statutory_Dues")
    gst_ledger = get_sheet_data(workbook_data, "GST_Ledger")
    gst_payments = get_sheet_data(workbook_data, "GST_Payments")
    gstr3b = get_sheet_data(workbook_data, "GSTR3B")
    tds_ledger = get_sheet_data(workbook_data, "TDS_Ledger")
    tds_deducted = get_sheet_data(workbook_data, "TDS_Deducted")
    tds_payments = get_sheet_data(workbook_data, "TDS_Payments")
    pf_esi = get_sheet_data(workbook_data, "PF_ESI_Details")
    pf_returns = get_sheet_data(workbook_data, "PF_Returns")
    esi_returns = get_sheet_data(workbook_data, "ESI_Returns")

    statutory_books = get_sum(statutory_dues, ["Amount", "Payable Amount", "Liability Amount"])
    gst_books = get_sum(gst_ledger, ["Amount", "GST Payable", "Liability"])
    gst_paid = get_sum(gst_payments, ["Amount", "Paid Amount", "Challan Amount"])
    gst_return_liability = get_sum(gstr3b, ["Tax Payable", "GST Payable", "Liability", "Amount"])

    tds_books = get_sum(tds_ledger, ["Amount", "TDS Payable", "Liability"])
    tds_deducted_amount = get_sum(tds_deducted, ["TDS Amount", "Tax Deducted", "Amount"])
    tds_paid = get_sum(tds_payments, ["Amount", "Paid Amount", "Challan Amount"])

    pf_esi_books = get_sum(pf_esi, ["Amount", "Contribution", "Payable Amount"])
    pf_return_amount = get_sum(pf_returns, ["Amount", "Contribution", "Payable Amount"])
    esi_return_amount = get_sum(esi_returns, ["Amount", "Contribution", "Payable Amount"])

    diff = round(gst_books - gst_return_liability, 2)

    rows.append(make_exception_row(
        procedure,
        "GST Liability as per Books vs GSTR-3B",
        "OK" if abs(diff) <= 1 else "Exception",
        f"GST as per books ₹{format_indian_number(gst_books)} vs GSTR-3B ₹{format_indian_number(gst_return_liability)}.",
        gst_books,
        gst_return_liability,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 26 / Clause 41",
        "Review GST liability mismatch" if abs(diff) > 1 else "No action required"
    ))

    diff = round(gst_books - gst_paid, 2)

    rows.append(make_exception_row(
        procedure,
        "GST Payable vs GST Deposited",
        "OK" if abs(diff) <= 1 else "Review",
        f"GST payable ₹{format_indian_number(gst_books)} vs GST deposited ₹{format_indian_number(gst_paid)}.",
        gst_books,
        gst_paid,
        diff,
        "Low" if abs(diff) <= 1 else "Medium",
        "Clause 26",
        "Check payment dates and unpaid GST" if abs(diff) > 1 else "No action required"
    ))

    diff = round(tds_books - tds_deducted_amount, 2)

    rows.append(make_exception_row(
        procedure,
        "TDS Payable vs TDS Deducted",
        "OK" if abs(diff) <= 1 else "Exception",
        f"TDS payable as per books ₹{format_indian_number(tds_books)} vs TDS deducted ₹{format_indian_number(tds_deducted_amount)}.",
        tds_books,
        tds_deducted_amount,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 34",
        "Check whether TDS was correctly deducted" if abs(diff) > 1 else "No action required"
    ))

    diff = round(tds_deducted_amount - tds_paid, 2)

    rows.append(make_exception_row(
        procedure,
        "TDS Deducted vs TDS Deposited",
        "OK" if abs(diff) <= 1 else "Exception",
        f"TDS deducted ₹{format_indian_number(tds_deducted_amount)} vs TDS deposited ₹{format_indian_number(tds_paid)}.",
        tds_deducted_amount,
        tds_paid,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 26 / Clause 34",
        "Check short deposit / late deposit" if abs(diff) > 1 else "No action required"
    ))

    pf_esi_return_total = pf_return_amount + esi_return_amount
    diff = round(pf_esi_books - pf_esi_return_total, 2)

    rows.append(make_exception_row(
        procedure,
        "PF/ESI as per Books vs Filed Returns",
        "OK" if abs(diff) <= 1 else "Review",
        f"PF/ESI as per books ₹{format_indian_number(pf_esi_books)} vs returns ₹{format_indian_number(pf_esi_return_total)}.",
        pf_esi_books,
        pf_esi_return_total,
        diff,
        "Low" if abs(diff) <= 1 else "Medium",
        "Clause 20 / Clause 26",
        "Review employee contribution and return matching" if abs(diff) > 1 else "No action required"
    ))

    if statutory_books > 0:
        rows.append(make_exception_row(
            procedure,
            "Overall Statutory Dues Captured from Books",
            "Review",
            f"Total statutory dues captured from books: ₹{format_indian_number(statutory_books)}.",
            statutory_books,
            0,
            statutory_books,
            "Medium",
            "Clause 26",
            "Review due dates and payment dates manually where required"
        ))

    return pd.DataFrame(rows)


def run_cash_payment_verification(workbook_data):
    procedure = "Cash Payment Verification"
    rows = []

    cash_book = get_sheet_data(workbook_data, "Cash_Book")
    payment_register = get_sheet_data(workbook_data, "Payment_Register")

    df = cash_book if not cash_book.empty else payment_register

    if df.empty:
        rows.append(make_exception_row(
            procedure,
            "Cash Data Availability",
            "Exception",
            "Cash_Book / Payment_Register sheet not available.",
            risk_level="High",
            form_3cd_clause="Clause 21",
            auditor_action="Upload Cash_Book or Payment_Register"
        ))
        return pd.DataFrame(rows)

    df_norm = normalize_df_columns(df)

    amount_col = find_column(df_norm, ["Amount", "Payment Amount", "Cash Amount"])
    mode_col = find_column(df_norm, ["Mode", "Payment Mode"])
    party_col = find_column(df_norm, ["Party Name", "Ledger Name", "Vendor Name", "Name"])
    date_col = find_column(df_norm, ["Date", "Voucher Date", "Payment Date"])

    if not amount_col:
        rows.append(make_exception_row(
            procedure,
            "Amount Column Availability",
            "Exception",
            "Amount column not found in cash payment data.",
            risk_level="High",
            form_3cd_clause="Clause 21",
            auditor_action="Add Amount column"
        ))
        return pd.DataFrame(rows)

    df_norm["_amount"] = df_norm[amount_col].apply(safe_float)

    if mode_col:
        cash_df = df_norm[df_norm[mode_col].astype(str).str.lower().str.contains("cash", na=False)]
    else:
        cash_df = df_norm.copy()

    high_cash_df = cash_df[cash_df["_amount"] > 10000]

    rows.append(make_exception_row(
        procedure,
        "Cash Payments Above ₹10,000",
        "OK" if len(high_cash_df) == 0 else "Review",
        f"{len(high_cash_df)} cash payments above ₹10,000 identified.",
        len(high_cash_df),
        0,
        len(high_cash_df),
        "Low" if len(high_cash_df) == 0 else "High",
        "Clause 21",
        "Review section 40A(3) applicability" if len(high_cash_df) > 0 else "No action required"
    ))

    if party_col and date_col:
        grouped = cash_df.groupby([party_col, date_col])["_amount"].sum().reset_index()
        repeated_cash = grouped[grouped["_amount"] > 10000]

        rows.append(make_exception_row(
            procedure,
            "Same Party Same Day Cash Payments Above ₹10,000",
            "OK" if len(repeated_cash) == 0 else "Review",
            f"{len(repeated_cash)} party-date combinations exceed ₹10,000 in cash.",
            len(repeated_cash),
            0,
            len(repeated_cash),
            "Low" if len(repeated_cash) == 0 else "High",
            "Clause 21",
            "Review split cash payments" if len(repeated_cash) > 0 else "No action required"
        ))

    return pd.DataFrame(rows)


def run_generic_procedure(procedure_name, workbook_data):
    rows = []

    details = AUDIT_PROCEDURES.get(procedure_name, {})
    required_sheets = details.get("required_sheets", [])

    available_count = 0

    for sheet in required_sheets:
        df = get_sheet_data(workbook_data, sheet)

        if not df.empty:
            available_count += 1

    total_required = len(required_sheets)

    rows.append(make_exception_row(
        procedure_name,
        "Procedure Data Availability",
        "Review",
        f"{available_count} out of {total_required} required sheets are available. Detailed automation for this procedure will be added in next phase.",
        available_count,
        total_required,
        total_required - available_count,
        "Medium",
        " / ".join(details.get("form_3cd_linkage", [])),
        "Review uploaded data and proceed manually until full automation is added"
    ))

    return pd.DataFrame(rows)


def run_selected_procedure(procedure_name, workbook_data):
    if procedure_name == "Trial Balance Verification":
        return run_trial_balance_verification(workbook_data)

    if procedure_name == "Profit and Loss Verification":
        return run_profit_and_loss_verification(workbook_data)

    if procedure_name == "Balance Sheet Verification":
        return run_balance_sheet_verification(workbook_data)

    if procedure_name == "GST Reconciliation":
        return run_gst_reconciliation(workbook_data)

    if procedure_name == "TDS / TCS Verification":
        return run_tds_tcs_verification(workbook_data)

    if procedure_name == "Section 43B Verification":
        return run_section_43b_verification(workbook_data)

    if procedure_name == "Cash Payment Verification":
        return run_cash_payment_verification(workbook_data)

    return run_generic_procedure(procedure_name, workbook_data)


# ---------------------------------------------------------
# MAIN UI
# ---------------------------------------------------------

def show_audit_procedures():
    apply_audit_procedure_style()

    st.markdown("""
    <div class="audit-hero">
        <h2>🔍 Automated Audit Procedures</h2>
        <p>Run tax audit verification procedures using uploaded working files, books data, GST, TDS and statutory records.</p>
    </div>
    """, unsafe_allow_html=True)

    selected_client, selected_ay = get_active_client_from_global_selection()

    if not selected_client or not selected_ay:
        st.info("Please add/select a client from the top-right Active Audit Client selector.")
        return

    st.markdown(f"""
    <div class="active-client-strip">
        Active Client: {selected_client} | AY: {selected_ay}
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    procedure_name = st.selectbox(
        "Select Audit Procedure",
        list(AUDIT_PROCEDURES.keys()),
        key=f"selected_audit_procedure_{selected_client}_{selected_ay}"
    )

    procedure_details = AUDIT_PROCEDURES[procedure_name]

    st.markdown(f"""
    <div class="info-card">
        <div class="info-title">📌 {procedure_name}</div>
        <div class="info-sub">{procedure_details["description"]}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.write("### Required Data Sheets")
        required_df = pd.DataFrame({
            "Required Sheet": procedure_details["required_sheets"]
        })
        st.dataframe(required_df, use_container_width=True, hide_index=True)

    with c2:
        st.write("### Form 3CD Linkage")
        linkage_df = pd.DataFrame({
            "Linked Clause": procedure_details["form_3cd_linkage"]
        })
        st.dataframe(linkage_df, use_container_width=True, hide_index=True)

    st.divider()

    st.write("### Document Collection Readiness")

    doc_status_df = load_document_collection_status(
        selected_client,
        selected_ay,
        procedure_details["required_sheets"]
    )

    st.dataframe(doc_status_df, use_container_width=True, hide_index=True)

    received_count = len(
        doc_status_df[
            doc_status_df["Document Collection Status"].astype(str).isin(["Received", "Not Applicable"])
        ]
    )

    total_required = len(doc_status_df)
    collection_percent = round((received_count / total_required) * 100, 2) if total_required > 0 else 0

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric("Required Sheets", total_required)

    with p2:
        st.metric("Received / N.A.", received_count)

    with p3:
        st.metric("Collection Readiness", f"{collection_percent}%")

    st.progress(collection_percent / 100)

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Audit Working Excel File",
        type=["xlsx", "xls"],
        key=f"audit_working_file_{selected_client}_{selected_ay}_{procedure_name}"
    )

    if uploaded_file is None:
        st.info("Upload an Excel file to continue with automation.")
        return

    available_sheets = get_available_sheets(uploaded_file)

    if len(available_sheets) == 0:
        st.error("No readable sheets found in the uploaded file.")
        return

    st.write("### Available Sheets in Uploaded File")
    st.dataframe(
        pd.DataFrame({"Available Sheet": available_sheets}),
        use_container_width=True,
        hide_index=True
    )

    sheet_check_df = check_required_sheets(
        procedure_details["required_sheets"],
        available_sheets
    )

    st.write("### Required Sheet Availability Check")
    st.dataframe(sheet_check_df, use_container_width=True, hide_index=True)

    missing_sheets = sheet_check_df[
        sheet_check_df["Available in Uploaded File"] == "No"
    ]["Required Sheet"].tolist()

    if missing_sheets:
        st.warning(
            "Some required sheets are missing. You can still run the procedure, "
            "but the result may be incomplete."
        )

    st.divider()

    if st.button("🚀 Run Automated Audit Procedure", use_container_width=True):
        workbook_data = read_uploaded_excel(uploaded_file)

        result_df = run_selected_procedure(procedure_name, workbook_data)

        if result_df.empty:
            st.warning("No result generated from this procedure.")
            return

        total_checks = len(result_df)
        exceptions = len(result_df[result_df["Status"].astype(str).isin(["Exception", "Review"])])
        high_risk = len(result_df[result_df["Risk Level"].astype(str) == "High"])

        summary_data = {
            "Client Name": selected_client,
            "AY": selected_ay,
            "Procedure": procedure_name,
            "Run Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total Checks": total_checks,
            "Exceptions / Review Points": exceptions,
            "High Risk Points": high_risk,
            "Missing Sheets": ", ".join(missing_sheets),
            "Form 3CD Linkage": " | ".join(procedure_details["form_3cd_linkage"])
        }

        st.session_state[f"last_audit_result_{selected_client}_{selected_ay}_{procedure_name}"] = result_df
        st.session_state[f"last_audit_summary_{selected_client}_{selected_ay}_{procedure_name}"] = summary_data

        st.success("✅ Audit procedure completed successfully.")

    result_key = f"last_audit_result_{selected_client}_{selected_ay}_{procedure_name}"
    summary_key = f"last_audit_summary_{selected_client}_{selected_ay}_{procedure_name}"

    if result_key in st.session_state:
        result_df = st.session_state[result_key]
        summary_data = st.session_state[summary_key]

        st.subheader("📊 Procedure Result Summary")

        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric("Total Checks", summary_data["Total Checks"])

        with s2:
            st.metric("Exceptions / Review", summary_data["Exceptions / Review Points"])

        with s3:
            st.metric("High Risk Points", summary_data["High Risk Points"])

        st.write("### Exception / Observation Report")
        st.dataframe(result_df, use_container_width=True, hide_index=True)

        st.divider()

        save_col, download_col = st.columns(2)

        with save_col:
            if st.button("💾 Save Procedure Result", use_container_width=True):
                excel_path, json_path = save_procedure_result(
                    selected_client,
                    selected_ay,
                    procedure_name,
                    result_df,
                    summary_data
                )

                st.success(f"✅ Excel result saved: {excel_path}")
                st.success(f"✅ JSON summary saved: {json_path}")

        with download_col:
            csv_data = result_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "⬇ Download Result CSV",
                data=csv_data,
                file_name=f"{get_safe_file_name(procedure_name)}_result.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.divider()

    st.caption(
        "Trial Balance, P&L, Balance Sheet, GST, TDS/TCS, Section 43B and Cash Payment checks are automated. "
        "Other procedures are structured and ready for detailed automation phase-wise."
    )