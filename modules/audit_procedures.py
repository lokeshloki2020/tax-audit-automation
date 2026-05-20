import os
import json
from datetime import datetime

import pandas as pd
import streamlit as st

from utils.common import load_clients


AUDIT_PROCEDURES = {
    "Trial Balance Verification": {
        "description": "Verify whether Trial Balance is balanced and ledger balances are suitable for audit.",
        "required_sheets": ["Trial_Balance", "Ledger_Master", "Ledger_Details", "Opening_Balances", "Financial_Statements", "Profit_and_Loss", "Balance_Sheet"],
        "checks": [
            "Debit total vs credit total",
            "Ledger grouping verification",
            "Negative balance verification",
            "Opening balance matching",
            "P&L and Balance Sheet classification",
            "Unusual ledger balances",
            "Financial statement mapping"
        ],
        "form_3cd_linkage": ["Clause 11", "Clause 13", "Clause 40"]
    },

    "Profit and Loss Verification": {
        "description": "Verify income, expenses, abnormal items, prior period items, and tax disallowance indicators.",
        "required_sheets": ["Profit_and_Loss", "Trial_Balance", "Ledger_Details", "Expense_Ledgers", "Income_Ledgers", "Previous_Year_Financials", "Journal_Register"],
        "checks": [
            "Sales / revenue as per P&L vs Trial Balance",
            "Direct expenses verification",
            "Indirect expenses verification",
            "Major expense variation from previous year",
            "Unusual or abnormal expenses",
            "Capital expenditure wrongly debited to P&L",
            "Personal expenses booked in business",
            "Prior period expenses",
            "Prior period income",
            "Expenses requiring disallowance review",
            "Income not credited to P&L",
            "Ledger-wise expense analysis"
        ],
        "form_3cd_linkage": ["Clause 13", "Clause 16", "Clause 19", "Clause 21", "Clause 27", "Clause 40"]
    },

    "Balance Sheet Verification": {
        "description": "Verify assets, liabilities, loans, capital, creditors, debtors, statutory dues, and provisions.",
        "required_sheets": ["Balance_Sheet", "Trial_Balance", "Ledger_Details", "Opening_Balances", "Loan_Details", "Fixed_Asset_Register", "Statutory_Dues", "Creditor_Ageing", "Debtor_Ageing", "Outstanding_Payables", "Outstanding_Receivables", "Capital_Account"],
        "checks": [
            "Balance Sheet total assets vs total liabilities",
            "Balance Sheet figures vs Trial Balance",
            "Opening balances verification",
            "Secured loan verification",
            "Unsecured loan verification",
            "Sundry creditors ageing",
            "Sundry debtors ageing",
            "Statutory dues outstanding",
            "Capital account verification",
            "Fixed assets balance verification",
            "Provisions and outstanding expenses",
            "Loans and advances verification",
            "Negative asset or liability balances",
            "Classification of current and non-current items"
        ],
        "form_3cd_linkage": ["Clause 11", "Clause 18", "Clause 22", "Clause 26", "Clause 31", "Clause 40"]
    },

    "GST Reconciliation": {
        "description": "Reconcile books sales, purchases, GST output, GST input, GSTR-1, GSTR-3B, GSTR-2A and GSTR-2B.",
        "required_sheets": ["Books_Sales", "Books_Purchases", "GSTR1", "GSTR3B", "GSTR2A", "GSTR2B", "GST_Output_Ledger", "GST_Input_Ledger", "GST_ITC_Books", "GST_Payments", "GST_Return_Status"],
        "checks": [
            "Books turnover and GSTR-1 sales reconciliation",
            "Books purchases and GSTR-2B purchase reconciliation",
            "GST as per books and GSTR-2A input reconciliation",
            "GST as per books and GSTR-2B input reconciliation",
            "GSTR-1 vs GSTR-3B reconciliation",
            "Books turnover vs GSTR-3B",
            "Output tax difference",
            "Input tax credit difference",
            "RCM liability verification",
            "GST payment verification"
        ],
        "form_3cd_linkage": ["Clause 4", "Clause 27", "Clause 41", "Clause 44"]
    },

    "TDS / TCS Verification": {
        "description": "Verify TDS payable, paid, receivable, received, returns, 26AS, AIS/TIS and TCS compliance.",
        "required_sheets": ["Expense_Ledgers", "TDS_Deducted", "TDS_Payments", "TDS_Returns", "TDS_Ledger", "TDS_Receivable_Ledger", "Form_26AS", "AIS_TIS", "Vendor_Master", "Customer_Master", "TCS_Details", "TCS_Returns"],
        "checks": [
            "TDS applicable expenses",
            "Whether TDS was required to be deducted",
            "Whether TDS was correctly deducted",
            "Correct TDS section applied",
            "Correct TDS rate applied",
            "Short deduction",
            "Non-deduction",
            "Late deduction",
            "TDS payable as per books",
            "TDS paid as per challans",
            "TDS deposited within due dates",
            "TDS return amount vs books",
            "TDS receivable as per books",
            "TDS as per Form 26AS",
            "TDS as per AIS/TIS",
            "TDS receivable booked but not appearing in 26AS",
            "TDS appearing in 26AS but not booked",
            "TCS verification"
        ],
        "form_3cd_linkage": ["Clause 21", "Clause 34"]
    },

    "Section 43B Verification": {
        "description": "Verify statutory dues with books, filed returns, challans, deduction, deposit and due dates.",
        "required_sheets": ["Statutory_Dues", "GST_Return_Status", "GST_Ledger", "GST_Payments", "GSTR3B", "TDS_Ledger", "TDS_Deducted", "TDS_Payments", "TDS_Returns", "PF_ESI_Details", "PF_Returns", "ESI_Returns", "Professional_Tax_Returns", "Payment_Register", "Bank_Book", "Ledger_Details"],
        "checks": [
            "GST payable as per books",
            "GST liability as per GSTR-3B",
            "Books liability vs return liability",
            "Whether amount was correctly deducted",
            "Whether amount was correctly deposited",
            "Whether deposited within due date",
            "TDS payable as per books",
            "TDS deducted correctly",
            "TDS deposited correctly",
            "PF liability as per books",
            "PF liability as per filed return",
            "ESI liability as per books",
            "ESI liability as per filed return",
            "Professional tax liability",
            "Bonus payable",
            "Leave encashment payable",
            "Interest payable to banks / financial institutions",
            "Allowable and disallowable amount"
        ],
        "form_3cd_linkage": ["Clause 20", "Clause 21", "Clause 26", "Clause 34"]
    },

    "Fixed Assets and Depreciation Verification": {
        "description": "Verify fixed assets, additions, deletions, depreciation as per books and Income-tax Act.",
        "required_sheets": ["Fixed_Asset_Register", "Additions", "Deletions", "Depreciation_As_Per_Books", "Depreciation_As_Per_IT", "Trial_Balance", "Ledger_Details", "Purchase_Register"],
        "checks": ["Opening WDV verification", "Additions before 180 days", "Additions after 180 days", "Deletions", "Block-wise depreciation", "Book depreciation vs Income-tax depreciation", "Capitalisation date", "Asset classification", "Depreciation rate verification"],
        "form_3cd_linkage": ["Clause 18", "Clause 15"]
    },

    "Cash Payment Verification": {
        "description": "Identify cash payments requiring reporting or disallowance review under section 40A(3).",
        "required_sheets": ["Cash_Book", "Payment_Register", "Ledger_Details", "Expense_Ledgers", "Vendor_Master"],
        "checks": ["Cash payments above prescribed limit", "Multiple cash payments to same party on same day", "Cash payments against expenses", "Cash repayment of old liability", "Cash payments requiring auditor review", "Possible section 40A(3) disallowance"],
        "form_3cd_linkage": ["Clause 21"]
    },

    "Loans, Deposits and Specified Sums Verification": {
        "description": "Verify loans, deposits, specified sums, specified advances and cash receipt/payment restrictions.",
        "required_sheets": ["Loan_Details", "Ledger_Details", "Bank_Book", "Cash_Book", "Receipt_Register", "Payment_Register", "Party_Master", "Customer_Master", "Vendor_Master"],
        "checks": ["Loans accepted in cash", "Loans repaid in cash", "Deposits accepted otherwise than prescribed mode", "Deposits repaid otherwise than prescribed mode", "Specified advances", "Receipt of ₹2 lakh or more in cash", "Party-wise balance verification", "Mode of receipt and payment", "Possible 269SS / 269T / 269ST reporting"],
        "form_3cd_linkage": ["Clause 30", "Clause 31"]
    },

    "Related Party Verification": {
        "description": "Verify payments and transactions with related parties / specified persons.",
        "required_sheets": ["Related_Party_Master", "Partner_Director_Details", "Ledger_Details", "Expense_Ledgers", "Payment_Register", "Loan_Details"],
        "checks": ["Payments to related parties", "Loans from related parties", "Loans to related parties", "Interest to related parties", "Salary / remuneration to partners or directors", "Rent to related parties", "Nature of payment", "Amount paid", "Reasonableness review"],
        "form_3cd_linkage": ["Clause 23"]
    },

    "MSME Verification": {
        "description": "Verify MSME vendors, ageing, delayed payments and interest implications.",
        "required_sheets": ["Vendor_Master", "MSME_Vendor_List", "Purchase_Register", "Payment_Register", "Creditor_Ageing", "Ledger_Details", "Outstanding_Payables"],
        "checks": ["Whether vendor is MSME", "Udyam registration number", "Invoice date", "Due date", "Payment date", "Outstanding beyond allowed period", "Interest payable under MSME Act", "MSME ageing", "Delayed payment reporting"],
        "form_3cd_linkage": ["Clause 22", "Clause 26"]
    },

    "Clause 44 GST Expenditure Break-up": {
        "description": "Prepare GST registered / unregistered expenditure break-up for Clause 44.",
        "required_sheets": ["Expense_Ledgers", "Purchase_Register", "Vendor_Master", "GSTIN_Master", "GSTR2B", "Trial_Balance"],
        "checks": ["Total expenditure as per books", "Expenditure relating to GST registered entities", "Expenditure relating to unregistered entities", "Expenditure relating to composition dealers", "Expenditure relating to exempt supply", "Other expenditure", "Reconciliation with purchase register", "Reconciliation with expense ledgers"],
        "form_3cd_linkage": ["Clause 44"]
    },

    "Employee Contribution Verification": {
        "description": "Verify PF, ESI and employee contribution deduction and payment due dates.",
        "required_sheets": ["Salary_Register", "PF_ESI_Details", "PF_Returns", "ESI_Returns", "PF_Challans", "ESI_Challans", "Payment_Register", "Ledger_Details", "Bank_Book"],
        "checks": ["Employee contribution deducted", "Employer contribution recorded", "Due date under respective Act", "Actual payment date", "Delay in payment", "Amount allowable", "Amount disallowable", "Return-wise matching", "Challan-wise matching"],
        "form_3cd_linkage": ["Clause 20", "Clause 26"]
    },

    "Stock and Quantitative Details Verification": {
        "description": "Verify stock movement, production, purchases, sales, closing stock and quantitative details.",
        "required_sheets": ["Stock_Register", "Purchase_Register", "Sales_Register", "Production_Register", "Opening_Stock", "Closing_Stock", "Physical_Verification_Report", "Trial_Balance"],
        "checks": ["Opening stock verification", "Purchase quantity verification", "Sales quantity verification", "Consumption verification", "Production verification", "Closing stock verification", "Shortage / excess", "Stock valuation", "Gross profit variation"],
        "form_3cd_linkage": ["Clause 14", "Clause 35", "Clause 40"]
    },

    "Capital Expenditure Verification": {
        "description": "Identify capital expenses wrongly debited to P&L.",
        "required_sheets": ["Expense_Ledgers", "Ledger_Details", "Fixed_Asset_Register", "Purchase_Register", "Trial_Balance"],
        "checks": ["Asset-like expenses debited to P&L", "Capital items wrongly treated as revenue", "Repairs vs capital expenditure", "Software purchase", "Furniture / equipment / vehicle purchase", "Large one-time expenses", "Wrong classification"],
        "form_3cd_linkage": ["Clause 21", "Clause 18"]
    },

    "Prior Period Items Verification": {
        "description": "Verify prior period income and expenses.",
        "required_sheets": ["Ledger_Details", "Profit_and_Loss", "Journal_Register", "Trial_Balance"],
        "checks": ["Prior period expenses", "Prior period income", "Tax adjustment required", "Accounting treatment", "Auditor remarks"],
        "form_3cd_linkage": ["Clause 27"]
    },

    "Ratios Verification": {
        "description": "Compute and review accounting ratios for Form 3CD.",
        "required_sheets": ["Profit_and_Loss", "Balance_Sheet", "Stock_Register", "Trial_Balance", "Previous_Year_Financials"],
        "checks": ["Gross profit ratio", "Net profit ratio", "Stock turnover ratio", "Material consumed / finished goods produced ratio", "Previous year comparison", "Variance analysis"],
        "form_3cd_linkage": ["Clause 40"]
    },

    "Tax Demand / Refund Verification": {
        "description": "Verify demand or refund under tax laws other than Income Tax and Wealth Tax.",
        "required_sheets": ["Tax_Demand_Refund_Details", "GST_Orders", "VAT_Orders", "Professional_Tax_Orders", "Other_Tax_Orders", "Appeal_Details"],
        "checks": ["Demand raised", "Refund received", "Tax law under which demand / refund arose", "Amount", "Period", "Status", "Appeal pending or filed", "Disclosure requirement"],
        "form_3cd_linkage": ["Clause 41"]
    },

    "Form 61 / 61A / 61B Verification": {
        "description": "Verify reporting requirement and filing status of Form 61, 61A and 61B.",
        "required_sheets": ["SFT_Transactions", "Form_61_61A_61B_Status", "High_Value_Transactions", "Customer_Master", "Receipt_Register", "Sales_Register"],
        "checks": ["Whether reporting requirement applies", "Whether form was filed", "Due date", "Filing date", "Acknowledgement number", "Reportable transactions", "Mismatch with books"],
        "form_3cd_linkage": ["Clause 42"]
    },

    "Final Audit Observation Summary": {
        "description": "Consolidate unresolved exceptions, management reply, auditor remarks and Form 3CD linkage.",
        "required_sheets": ["Exception_Report", "Management_Reply", "Auditor_Remarks", "Final_Adjustments", "Tax_Report_Linkage"],
        "checks": ["All unresolved exceptions", "Management reply", "Tax adjustment required", "Clause-wise impact", "Final auditor remarks", "Whether linked to Form 3CD"],
        "form_3cd_linkage": ["All relevant clauses"]
    },
}


def apply_style():
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
    .info-card {
        padding: 18px;
        border-radius: 18px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.08);
        margin-bottom: 12px;
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


def safe_float(value):
    try:
        return float(str(value).replace(",", "").strip())
    except:
        return 0.0


def normalize_column_name(col):
    return str(col).strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")


def normalize_df_columns(df):
    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    return df


def find_column(df, possible_names):
    normalized_columns = list(df.columns)

    for name in possible_names:
        name = normalize_column_name(name)

        if name in normalized_columns:
            return name

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


def format_indian_number(value):
    try:
        value = int(round(safe_float(value), 0))
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


def get_sheet_data(workbook_data, sheet_name):
    for available_sheet, df in workbook_data.items():
        if normalize_column_name(available_sheet) == normalize_column_name(sheet_name):
            return df

    return pd.DataFrame()


def read_uploaded_excel(uploaded_file):
    try:
        xls = pd.ExcelFile(uploaded_file)
        return {
            sheet: pd.read_excel(uploaded_file, sheet_name=sheet)
            for sheet in xls.sheet_names
        }
    except Exception as e:
        st.error(f"Unable to read uploaded Excel file. Error: {e}")
        return {}


def get_available_sheets(uploaded_file):
    try:
        return pd.ExcelFile(uploaded_file).sheet_names
    except:
        return []


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


def get_audit_procedure_folder(client_name, ay):
    folder = f"clients/{client_name}/AY {ay}/Audit Procedures"
    os.makedirs(folder, exist_ok=True)
    return folder


def get_safe_file_name(name):
    return (
        str(name)
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .replace(",", "")
        .replace(":", "")
    )


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


def check_required_sheets(required_sheets, available_sheets):
    available_normalized = [normalize_column_name(sheet) for sheet in available_sheets]

    return pd.DataFrame([
        {
            "Required Sheet": sheet,
            "Available in Uploaded File": "Yes" if normalize_column_name(sheet) in available_normalized else "No"
        }
        for sheet in required_sheets
    ])


def load_document_collection_status(client_name, ay, required_sheets):
    checklist_path = f"clients/{client_name}/AY {ay}/document_checklist.xlsx"

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

            rows.append({
                "Required Sheet": sheet,
                "Document Collection Status": match.iloc[0]["Status"] if len(match) > 0 else "Not in Checklist"
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


def run_trial_balance_verification(workbook_data):
    procedure = "Trial Balance Verification"
    rows = []

    tb = get_sheet_data(workbook_data, "Trial_Balance")

    if tb.empty:
        return pd.DataFrame([
            make_exception_row(
                procedure,
                "Trial Balance Availability",
                "Exception",
                "Trial_Balance sheet is not available.",
                risk_level="High",
                form_3cd_clause="Clause 11",
                auditor_action="Upload Trial_Balance sheet"
            )
        ])

    tb = normalize_df_columns(tb)

    debit_col = find_column(tb, ["Debit", "Debit Amount", "Dr", "Dr Amount"])
    credit_col = find_column(tb, ["Credit", "Credit Amount", "Cr", "Cr Amount"])
    balance_col = find_column(tb, ["Balance", "Closing Balance", "Amount"])
    ledger_col = find_column(tb, ["Ledger Name", "Particulars", "Account Name", "Ledger"])

    if debit_col and credit_col:
        debit = tb[debit_col].apply(safe_float).sum()
        credit = tb[credit_col].apply(safe_float).sum()
        diff = round(debit - credit, 2)

        rows.append(make_exception_row(
            procedure,
            "Debit Total vs Credit Total",
            "OK" if abs(diff) <= 1 else "Exception",
            f"Debit ₹{format_indian_number(debit)} vs Credit ₹{format_indian_number(credit)}.",
            debit,
            credit,
            diff,
            "Low" if abs(diff) <= 1 else "High",
            "Clause 11",
            "Review TB difference" if abs(diff) > 1 else "No action required"
        ))

    elif balance_col:
        balance = tb[balance_col].apply(safe_float).sum()

        rows.append(make_exception_row(
            procedure,
            "Trial Balance Net Balance",
            "Review",
            f"Only balance column found. Net balance is ₹{format_indian_number(balance)}.",
            balance,
            0,
            balance,
            "Medium",
            "Clause 11",
            "Check balance sign convention"
        ))

    else:
        rows.append(make_exception_row(
            procedure,
            "Column Availability",
            "Exception",
            "Debit/Credit/Balance columns not found.",
            risk_level="High",
            form_3cd_clause="Clause 11",
            auditor_action="Correct Trial_Balance columns"
        ))

    if balance_col:
        negative_count = len(tb[tb[balance_col].apply(safe_float) < 0])

        rows.append(make_exception_row(
            procedure,
            "Negative Balances",
            "OK" if negative_count == 0 else "Review",
            f"{negative_count} negative balances found.",
            negative_count,
            0,
            negative_count,
            "Low" if negative_count == 0 else "Medium",
            "Clause 11 / Clause 40",
            "Review negative ledger balances" if negative_count > 0 else "No action required"
        ))

    if ledger_col:
        blank_count = len(tb[tb[ledger_col].astype(str).str.strip().isin(["", "nan", "None"])])

        rows.append(make_exception_row(
            procedure,
            "Blank Ledger Names",
            "OK" if blank_count == 0 else "Exception",
            f"{blank_count} blank ledger names found.",
            blank_count,
            0,
            blank_count,
            "Low" if blank_count == 0 else "High",
            "Clause 11",
            "Correct ledger names" if blank_count > 0 else "No action required"
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

    if pl.empty:
        rows.append(make_exception_row(
            procedure,
            "P&L Availability",
            "Exception",
            "Profit_and_Loss sheet is not available.",
            risk_level="High",
            form_3cd_clause="Clause 13 / Clause 40",
            auditor_action="Upload Profit_and_Loss sheet"
        ))
        return pd.DataFrame(rows)

    revenue = get_sum(pl, ["Revenue", "Sales", "Turnover", "Income", "Credit"])
    expenses = get_sum(pl, ["Expense", "Expenses", "Debit", "Amount"])
    tb_revenue = get_sum(tb, ["Revenue", "Sales", "Turnover", "Income", "Credit"])

    diff = round(revenue - tb_revenue, 2)

    rows.append(make_exception_row(
        procedure,
        "Sales / Revenue as per P&L vs Trial Balance",
        "OK" if tb.empty or abs(diff) <= 1 else "Review",
        f"P&L revenue ₹{format_indian_number(revenue)} vs TB revenue ₹{format_indian_number(tb_revenue)}.",
        revenue,
        tb_revenue,
        diff,
        "Low" if tb.empty or abs(diff) <= 1 else "Medium",
        "Clause 13 / Clause 40",
        "Review revenue mapping" if abs(diff) > 1 else "No action required"
    ))

    capex_keywords = ["asset", "laptop", "computer", "vehicle", "furniture", "machinery", "equipment", "software", "building", "capital"]

    combined_expense_df = expense_ledgers if not expense_ledgers.empty else pl
    combined_expense_df = normalize_df_columns(combined_expense_df)

    ledger_col = find_column(combined_expense_df, ["Ledger Name", "Particulars", "Expense Head", "Description", "Name"])
    amount_col = find_column(combined_expense_df, ["Amount", "Expense Amount", "Debit"])

    if ledger_col:
        capex_count = combined_expense_df[
            combined_expense_df[ledger_col].astype(str).str.lower().str.contains("|".join(capex_keywords), na=False)
        ].shape[0]

        rows.append(make_exception_row(
            procedure,
            "Capital Expenditure Keywords in P&L",
            "OK" if capex_count == 0 else "Review",
            f"{capex_count} possible capital expenditure items found in P&L / expense ledgers.",
            capex_count,
            0,
            capex_count,
            "Low" if capex_count == 0 else "High",
            "Clause 21 / Clause 18",
            "Review capital/revenue classification" if capex_count > 0 else "No action required"
        ))

        prior_count = combined_expense_df[
            combined_expense_df[ledger_col].astype(str).str.lower().str.contains("prior|previous year|earlier year", na=False)
        ].shape[0]

        rows.append(make_exception_row(
            procedure,
            "Prior Period Items",
            "OK" if prior_count == 0 else "Review",
            f"{prior_count} possible prior period items found.",
            prior_count,
            0,
            prior_count,
            "Low" if prior_count == 0 else "Medium",
            "Clause 27",
            "Review prior period tax treatment" if prior_count > 0 else "No action required"
        ))

        personal_count = combined_expense_df[
            combined_expense_df[ledger_col].astype(str).str.lower().str.contains("personal|drawings|household", na=False)
        ].shape[0]

        rows.append(make_exception_row(
            procedure,
            "Personal Expenses Indicator",
            "OK" if personal_count == 0 else "Review",
            f"{personal_count} possible personal expense items found.",
            personal_count,
            0,
            personal_count,
            "Low" if personal_count == 0 else "High",
            "Clause 21",
            "Review personal expenses for disallowance" if personal_count > 0 else "No action required"
        ))

    if not previous_year.empty:
        current_exp = expenses
        previous_exp = get_sum(previous_year, ["Expense", "Expenses", "Debit", "Amount"])
        variation = round(current_exp - previous_exp, 2)
        variation_percent = round((variation / previous_exp) * 100, 2) if previous_exp else 0

        rows.append(make_exception_row(
            procedure,
            "Major Expense Variation from Previous Year",
            "OK" if abs(variation_percent) <= 25 else "Review",
            f"Expense variation from previous year is {variation_percent}%.",
            current_exp,
            previous_exp,
            variation,
            "Low" if abs(variation_percent) <= 25 else "Medium",
            "Clause 40",
            "Obtain reason for major variation" if abs(variation_percent) > 25 else "No action required"
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

    if bs.empty:
        return pd.DataFrame([
            make_exception_row(
                procedure,
                "Balance Sheet Availability",
                "Exception",
                "Balance_Sheet sheet is not available.",
                risk_level="High",
                form_3cd_clause="Clause 11 / Clause 40",
                auditor_action="Upload Balance_Sheet sheet"
            )
        ])

    assets = get_sum(bs, ["Assets", "Asset Amount", "Debit", "Amount"])
    liabilities = get_sum(bs, ["Liabilities", "Liability Amount", "Credit", "Amount"])
    diff = round(assets - liabilities, 2)

    rows.append(make_exception_row(
        procedure,
        "Assets vs Liabilities",
        "OK" if abs(diff) <= 1 else "Exception",
        f"Assets ₹{format_indian_number(assets)} vs Liabilities ₹{format_indian_number(liabilities)}.",
        assets,
        liabilities,
        diff,
        "Low" if abs(diff) <= 1 else "High",
        "Clause 11 / Clause 40",
        "Review Balance Sheet balancing" if abs(diff) > 1 else "No action required"
    ))

    tb_total = get_sum(tb, ["Balance", "Closing Balance", "Amount"])
    bs_total = assets + liabilities

    rows.append(make_exception_row(
        procedure,
        "Balance Sheet Figures vs Trial Balance",
        "Review" if not tb.empty else "Exception",
        f"Balance Sheet total captured ₹{format_indian_number(bs_total)} and TB balance total captured ₹{format_indian_number(tb_total)}.",
        bs_total,
        tb_total,
        round(bs_total - tb_total, 2),
        "Medium",
        "Clause 11",
        "Review mapping between TB and Balance Sheet"
    ))

    loan_amount = get_sum(loans, ["Amount", "Loan Amount", "Balance"])
    statutory_amount = get_sum(statutory, ["Amount", "Payable Amount", "Liability"])
    creditor_amount = get_sum(creditors, ["Amount", "Outstanding", "Balance"])
    debtor_amount = get_sum(debtors, ["Amount", "Outstanding", "Balance"])

    rows.append(make_exception_row(procedure, "Loan Balances Review", "Review", f"Loan balances captured ₹{format_indian_number(loan_amount)}.", loan_amount, 0, loan_amount, "Medium", "Clause 31", "Verify loan confirmations and mode"))
    rows.append(make_exception_row(procedure, "Statutory Dues Outstanding", "Review", f"Statutory dues captured ₹{format_indian_number(statutory_amount)}.", statutory_amount, 0, statutory_amount, "Medium", "Clause 26", "Verify payment due dates"))
    rows.append(make_exception_row(procedure, "Creditor Ageing Review", "Review", f"Creditor ageing captured ₹{format_indian_number(creditor_amount)}.", creditor_amount, 0, creditor_amount, "Medium", "Clause 22 / Clause 26", "Review MSME and old creditors"))
    rows.append(make_exception_row(procedure, "Debtor Ageing Review", "Review", f"Debtor ageing captured ₹{format_indian_number(debtor_amount)}.", debtor_amount, 0, debtor_amount, "Low", "Clause 40", "Review recoverability"))

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

    rows.append(make_exception_row(procedure, "Books Turnover vs GSTR-1 - Sales Reco", "OK" if abs(diff) <= 1 else "Exception", f"Books sales ₹{format_indian_number(books_sales_value)} vs GSTR-1 ₹{format_indian_number(gstr1_value)}.", books_sales_value, gstr1_value, diff, "Low" if abs(diff) <= 1 else "High", "Clause 4 / Clause 44", "Review sales turnover mismatch" if abs(diff) > 1 else "No action required"))

    books_purchase_value = get_sum(books_purchases, ["Taxable Value", "Purchase Amount", "Invoice Value", "Amount"])
    gstr2b_purchase_value = get_sum(gstr2b, ["Taxable Value", "Invoice Value", "Amount"])
    diff = round(books_purchase_value - gstr2b_purchase_value, 2)

    rows.append(make_exception_row(procedure, "Books Purchases vs GSTR-2B - Purchases Reco", "OK" if abs(diff) <= 1 else "Exception", f"Books purchases ₹{format_indian_number(books_purchase_value)} vs GSTR-2B purchases ₹{format_indian_number(gstr2b_purchase_value)}.", books_purchase_value, gstr2b_purchase_value, diff, "Low" if abs(diff) <= 1 else "High", "Clause 44", "Review purchase mismatch and ITC eligibility" if abs(diff) > 1 else "No action required"))

    input_books_value = get_sum(gst_input_books, ["GST Amount", "Input GST", "ITC", "Tax Amount", "Amount"])

    if input_books_value == 0:
        input_books_value = get_sum(gst_itc_books, ["GST Amount", "Input GST", "ITC", "Tax Amount", "Amount"])

    gstr2a_itc = get_sum(gstr2a, ["GST Amount", "Input GST", "ITC", "Tax Amount", "Amount"])
    diff = round(input_books_value - gstr2a_itc, 2)

    rows.append(make_exception_row(procedure, "GST as per Books vs GSTR-2A - Input Reco", "OK" if abs(diff) <= 1 else "Exception", f"Input GST as per books ₹{format_indian_number(input_books_value)} vs GSTR-2A ₹{format_indian_number(gstr2a_itc)}.", input_books_value, gstr2a_itc, diff, "Low" if abs(diff) <= 1 else "High", "Clause 27 / Clause 44", "Review input GST difference" if abs(diff) > 1 else "No action required"))

    gstr2b_itc = get_sum(gstr2b, ["GST Amount", "Input GST", "ITC", "Tax Amount", "Amount"])
    diff = round(input_books_value - gstr2b_itc, 2)

    rows.append(make_exception_row(procedure, "GST as per Books vs GSTR-2B - Input Reco", "OK" if abs(diff) <= 1 else "Exception", f"Input GST as per books ₹{format_indian_number(input_books_value)} vs GSTR-2B ₹{format_indian_number(gstr2b_itc)}.", input_books_value, gstr2b_itc, diff, "Low" if abs(diff) <= 1 else "High", "Clause 27 / Clause 44", "Review ITC difference" if abs(diff) > 1 else "No action required"))

    gstr3b_turnover = get_sum(gstr3b, ["Taxable Value", "Turnover", "Outward Taxable Supplies", "Amount"])
    diff = round(gstr1_value - gstr3b_turnover, 2)

    rows.append(make_exception_row(procedure, "GSTR-1 vs GSTR-3B", "OK" if abs(diff) <= 1 else "Exception", f"GSTR-1 turnover ₹{format_indian_number(gstr1_value)} vs GSTR-3B turnover ₹{format_indian_number(gstr3b_turnover)}.", gstr1_value, gstr3b_turnover, diff, "Low" if abs(diff) <= 1 else "High", "Clause 4 / Clause 41", "Review GST return mismatch" if abs(diff) > 1 else "No action required"))

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
    rows.append(make_exception_row(procedure, "TDS Payable vs TDS Paid", "OK" if abs(diff) <= 1 else "Exception", f"TDS deducted ₹{format_indian_number(tds_deducted_amount)} vs paid ₹{format_indian_number(tds_paid_amount)}.", tds_deducted_amount, tds_paid_amount, diff, "Low" if abs(diff) <= 1 else "High", "Clause 34", "Verify unpaid / short-paid TDS" if abs(diff) > 1 else "No action required"))

    diff = round(tds_deducted_amount - tds_return_amount, 2)
    rows.append(make_exception_row(procedure, "TDS Deducted vs TDS Return", "OK" if abs(diff) <= 1 else "Exception", f"TDS deducted ₹{format_indian_number(tds_deducted_amount)} vs return ₹{format_indian_number(tds_return_amount)}.", tds_deducted_amount, tds_return_amount, diff, "Low" if abs(diff) <= 1 else "High", "Clause 34", "Verify TDS return mismatch" if abs(diff) > 1 else "No action required"))

    if expense_tds_base > 0 and tds_deducted_amount == 0:
        rows.append(make_exception_row(procedure, "Possible Non-deduction of TDS", "Review", "Expense ledgers have amounts but TDS deducted data is zero / missing.", expense_tds_base, 0, expense_tds_base, "High", "Clause 21 / Clause 34", "Review TDS applicability"))

    tds_receivable_books = get_sum(tds_receivable, ["TDS Receivable", "TDS Amount", "Amount"])
    tds_as_per_26as = get_sum(form_26as, ["TDS Amount", "Tax Deducted", "Amount", "Credit Amount"])
    tds_as_per_ais = get_sum(ais_tis, ["TDS Amount", "Tax Deducted", "Amount", "Credit Amount"])

    diff = round(tds_receivable_books - tds_as_per_26as, 2)
    rows.append(make_exception_row(procedure, "TDS Receivable as per Books vs Form 26AS", "OK" if abs(diff) <= 1 else "Exception", f"TDS receivable books ₹{format_indian_number(tds_receivable_books)} vs 26AS ₹{format_indian_number(tds_as_per_26as)}.", tds_receivable_books, tds_as_per_26as, diff, "Low" if abs(diff) <= 1 else "Medium", "ITR Credit / Clause 34", "Review TDS credit mismatch" if abs(diff) > 1 else "No action required"))

    diff = round(tds_receivable_books - tds_as_per_ais, 2)
    rows.append(make_exception_row(procedure, "TDS Receivable as per Books vs AIS/TIS", "OK" if abs(diff) <= 1 else "Review", f"TDS receivable books ₹{format_indian_number(tds_receivable_books)} vs AIS/TIS ₹{format_indian_number(tds_as_per_ais)}.", tds_receivable_books, tds_as_per_ais, diff, "Low" if abs(diff) <= 1 else "Medium", "ITR Credit", "Review AIS/TIS mismatch" if abs(diff) > 1 else "No action required"))

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

    gst_books = get_sum(gst_ledger, ["Amount", "GST Payable", "Liability"])
    gst_paid = get_sum(gst_payments, ["Amount", "Paid Amount", "Challan Amount"])
    gst_return_liability = get_sum(gstr3b, ["Tax Payable", "GST Payable", "Liability", "Amount"])

    tds_books = get_sum(tds_ledger, ["Amount", "TDS Payable", "Liability"])
    tds_deducted_amount = get_sum(tds_deducted, ["TDS Amount", "Tax Deducted", "Amount"])
    tds_paid = get_sum(tds_payments, ["Amount", "Paid Amount", "Challan Amount"])

    pf_esi_books = get_sum(pf_esi, ["Amount", "Contribution", "Payable Amount"])
    pf_return_amount = get_sum(pf_returns, ["Amount", "Contribution", "Payable Amount"])
    esi_return_amount = get_sum(esi_returns, ["Amount", "Contribution", "Payable Amount"])

    statutory_books = get_sum(statutory_dues, ["Amount", "Payable Amount", "Liability Amount"])

    diff = round(gst_books - gst_return_liability, 2)
    rows.append(make_exception_row(procedure, "GST Liability as per Books vs GSTR-3B", "OK" if abs(diff) <= 1 else "Exception", f"GST books ₹{format_indian_number(gst_books)} vs GSTR-3B ₹{format_indian_number(gst_return_liability)}.", gst_books, gst_return_liability, diff, "Low" if abs(diff) <= 1 else "High", "Clause 26 / Clause 41", "Review GST liability mismatch"))

    diff = round(gst_books - gst_paid, 2)
    rows.append(make_exception_row(procedure, "GST Payable vs GST Deposited", "OK" if abs(diff) <= 1 else "Review", f"GST payable ₹{format_indian_number(gst_books)} vs deposited ₹{format_indian_number(gst_paid)}.", gst_books, gst_paid, diff, "Low" if abs(diff) <= 1 else "Medium", "Clause 26", "Check payment dates"))

    diff = round(tds_books - tds_deducted_amount, 2)
    rows.append(make_exception_row(procedure, "TDS Payable vs TDS Deducted", "OK" if abs(diff) <= 1 else "Exception", f"TDS payable ₹{format_indian_number(tds_books)} vs deducted ₹{format_indian_number(tds_deducted_amount)}.", tds_books, tds_deducted_amount, diff, "Low" if abs(diff) <= 1 else "High", "Clause 34", "Check whether correctly deducted"))

    diff = round(tds_deducted_amount - tds_paid, 2)
    rows.append(make_exception_row(procedure, "TDS Deducted vs TDS Deposited", "OK" if abs(diff) <= 1 else "Exception", f"TDS deducted ₹{format_indian_number(tds_deducted_amount)} vs deposited ₹{format_indian_number(tds_paid)}.", tds_deducted_amount, tds_paid, diff, "Low" if abs(diff) <= 1 else "High", "Clause 26 / Clause 34", "Check short / late deposit"))

    pf_esi_return_total = pf_return_amount + esi_return_amount
    diff = round(pf_esi_books - pf_esi_return_total, 2)
    rows.append(make_exception_row(procedure, "PF/ESI as per Books vs Filed Returns", "OK" if abs(diff) <= 1 else "Review", f"PF/ESI books ₹{format_indian_number(pf_esi_books)} vs returns ₹{format_indian_number(pf_esi_return_total)}.", pf_esi_books, pf_esi_return_total, diff, "Low" if abs(diff) <= 1 else "Medium", "Clause 20 / Clause 26", "Review employee contribution"))

    rows.append(make_exception_row(procedure, "Overall Statutory Dues Captured from Books", "Review", f"Total statutory dues captured ₹{format_indian_number(statutory_books)}.", statutory_books, 0, statutory_books, "Medium", "Clause 26", "Review due dates and payment dates manually"))

    return pd.DataFrame(rows)


def run_cash_payment_verification(workbook_data):
    procedure = "Cash Payment Verification"
    rows = []

    cash_book = get_sheet_data(workbook_data, "Cash_Book")
    payment_register = get_sheet_data(workbook_data, "Payment_Register")
    df = cash_book if not cash_book.empty else payment_register

    if df.empty:
        return pd.DataFrame([
            make_exception_row(procedure, "Cash Data Availability", "Exception", "Cash_Book / Payment_Register sheet not available.", risk_level="High", form_3cd_clause="Clause 21", auditor_action="Upload Cash_Book or Payment_Register")
        ])

    df = normalize_df_columns(df)
    amount_col = find_column(df, ["Amount", "Payment Amount", "Cash Amount"])
    mode_col = find_column(df, ["Mode", "Payment Mode"])
    party_col = find_column(df, ["Party Name", "Ledger Name", "Vendor Name", "Name"])
    date_col = find_column(df, ["Date", "Voucher Date", "Payment Date"])

    if not amount_col:
        return pd.DataFrame([
            make_exception_row(procedure, "Amount Column Availability", "Exception", "Amount column not found.", risk_level="High", form_3cd_clause="Clause 21", auditor_action="Add Amount column")
        ])

    df["_amount"] = df[amount_col].apply(safe_float)

    if mode_col:
        cash_df = df[df[mode_col].astype(str).str.lower().str.contains("cash", na=False)]
    else:
        cash_df = df.copy()

    high_cash_df = cash_df[cash_df["_amount"] > 10000]

    rows.append(make_exception_row(procedure, "Cash Payments Above ₹10,000", "OK" if len(high_cash_df) == 0 else "Review", f"{len(high_cash_df)} cash payments above ₹10,000 identified.", len(high_cash_df), 0, len(high_cash_df), "Low" if len(high_cash_df) == 0 else "High", "Clause 21", "Review section 40A(3)"))

    if party_col and date_col:
        grouped = cash_df.groupby([party_col, date_col])["_amount"].sum().reset_index()
        repeated_cash = grouped[grouped["_amount"] > 10000]

        rows.append(make_exception_row(procedure, "Same Party Same Day Cash Payments Above ₹10,000", "OK" if len(repeated_cash) == 0 else "Review", f"{len(repeated_cash)} party-date combinations exceed ₹10,000 in cash.", len(repeated_cash), 0, len(repeated_cash), "Low" if len(repeated_cash) == 0 else "High", "Clause 21", "Review split cash payments"))

    return pd.DataFrame(rows)


def run_generic_procedure(procedure_name, workbook_data):
    details = AUDIT_PROCEDURES.get(procedure_name, {})
    rows = []

    required_sheets = details.get("required_sheets", [])
    checks = details.get("checks", [])
    form_linkage = " / ".join(details.get("form_3cd_linkage", []))

    available_count = 0

    for sheet in required_sheets:
        if not get_sheet_data(workbook_data, sheet).empty:
            available_count += 1

    rows.append(make_exception_row(
        procedure_name,
        "Procedure Data Availability",
        "OK" if available_count == len(required_sheets) else "Review",
        f"{available_count} out of {len(required_sheets)} required sheets are available.",
        available_count,
        len(required_sheets),
        len(required_sheets) - available_count,
        "Low" if available_count == len(required_sheets) else "Medium",
        form_linkage,
        "Upload missing data sheets" if available_count < len(required_sheets) else "Proceed with detailed audit review"
    ))

    for check in checks:
        rows.append(make_exception_row(
            procedure_name,
            check,
            "Review",
            f"{check} should be verified based on uploaded sheets and auditor judgement.",
            0,
            0,
            0,
            "Medium",
            form_linkage,
            "Perform detailed review / add automation rule in next phase"
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


def show_audit_procedures():
    apply_style()

    st.markdown("""
    <div class="audit-hero">
        <h2>🔍 Automated Audit Procedures</h2>
        <p>Run tax audit verification procedures using uploaded working files, books data, GST, TDS and statutory records.</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_clients()

    if df.empty or "Client Name" not in df.columns:
        st.info("Please add clients first.")
        return

    client_list = sorted(df["Client Name"].dropna().unique().tolist())

    if len(client_list) == 0:
        st.info("Please add clients first.")
        return

    selected_client = st.selectbox(
        "Search / Select Client",
        client_list,
        index=0,
        placeholder="Search client name...",
        key="audit_procedure_client"
    )

    if not selected_client:
        st.info("Please select a client.")
        return

    selected_row = df[df["Client Name"] == selected_client].iloc[0]
    selected_ay = selected_row["AY"]

    st.write(f"### Client: {selected_client} | AY: {selected_ay}")

    st.divider()

    procedure_name = st.selectbox(
        "Select Audit Procedure",
        list(AUDIT_PROCEDURES.keys()),
        key=f"selected_audit_procedure_{selected_client}_{selected_ay}"
    )

    procedure_details = AUDIT_PROCEDURES[procedure_name]

    st.markdown(f"""
    <div class="info-card">
        <h3>📌 {procedure_name}</h3>
        <p>{procedure_details["description"]}</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.write("### Required Data Sheets")
        st.dataframe(
            pd.DataFrame({"Required Sheet": procedure_details["required_sheets"]}),
            use_container_width=True,
            hide_index=True
        )

    with c2:
        st.write("### Major Checks")
        st.dataframe(
            pd.DataFrame({"Major Check": procedure_details["checks"]}),
            use_container_width=True,
            hide_index=True
        )

    with c3:
        st.write("### Form 3CD Linkage")
        st.dataframe(
            pd.DataFrame({"Linked Clause": procedure_details["form_3cd_linkage"]}),
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    st.markdown("""
    <div class="section-banner">
        <b>Step 1:</b> Check whether required data is marked as received in the Document Collection tab.
    </div>
    """, unsafe_allow_html=True)

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
        st.warning("Some required sheets are missing. You can still run the procedure, but the result may be incomplete.")

    st.divider()

    if st.button("🚀 Run Automated Audit Procedure", use_container_width=True):
        workbook_data = read_uploaded_excel(uploaded_file)

        result_df = run_selected_procedure(procedure_name, workbook_data)

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