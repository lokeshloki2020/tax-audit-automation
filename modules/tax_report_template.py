# modules/tax_report_template.py

"""
Tax Audit Report Template Module

This module contains:
1. Form 3CA report fields
2. Form 3CB report fields
3. Form 3CD clause-wise reporting template

Used by:
- modules/tax_report.py

Important:
Do not place Streamlit UI code here.
This file is only a reusable template / knowledge base.
"""


# ---------------------------------------------------------
# FORM 3CA / 3CB REPORT LEVEL TEMPLATE
# ---------------------------------------------------------

TAX_AUDIT_REPORT_FORMS = {
    "Form 3CA-3CD": {
        "form_code": "3CA",
        "title": "Form 3CA - Audit report under section 44AB where accounts are audited under any other law",
        "applicability": "Applicable where accounts of the assessee are required to be audited under any other law.",
        "fields": [
            "Name of the assessee",
            "Address of the assessee",
            "PAN / Aadhaar Number",
            "Assessment Year",
            "Previous Year",
            "Law under which accounts are audited",
            "Date of audit report under other law",
            "Name of auditor under other law",
            "Whether statutory audit report has any qualification / adverse remark",
            "Details of qualification / adverse remark, if any",
            "Whether attached Form 3CD particulars are true and correct",
            "Place of signing",
            "Date of signing",
            "Name of Chartered Accountant",
            "Membership Number",
            "Firm Registration Number",
            "UDIN",
            "Auditor Observation / Remark"
        ]
    },

    "Form 3CB-3CD": {
        "form_code": "3CB",
        "title": "Form 3CB - Audit report under section 44AB where accounts are not audited under any other law",
        "applicability": "Applicable where accounts of the assessee are not required to be audited under any other law.",
        "fields": [
            "Name of the assessee",
            "Address of the assessee",
            "PAN / Aadhaar Number",
            "Assessment Year",
            "Previous Year",
            "Balance Sheet date",
            "Profit and Loss Account period from",
            "Profit and Loss Account period to",
            "Books of account examined",
            "Whether Balance Sheet agrees with books of account",
            "Whether Profit and Loss Account agrees with books of account",
            "Observations / comments / discrepancies / inconsistencies, if any",
            "Subject to observations, whether financial statements give true and fair view",
            "Whether attached Form 3CD particulars are true and correct",
            "Place of signing",
            "Date of signing",
            "Name of Chartered Accountant",
            "Membership Number",
            "Firm Registration Number",
            "UDIN",
            "Auditor Observation / Remark"
        ]
    }
}


def get_tax_audit_form_details(audit_form):
    return TAX_AUDIT_REPORT_FORMS.get(audit_form, {})


def get_tax_audit_form_fields(audit_form):
    return TAX_AUDIT_REPORT_FORMS.get(audit_form, {}).get("fields", [])


def get_tax_audit_form_title(audit_form):
    return TAX_AUDIT_REPORT_FORMS.get(audit_form, {}).get("title", "")


def get_tax_audit_form_code(audit_form):
    return TAX_AUDIT_REPORT_FORMS.get(audit_form, {}).get("form_code", "")


def is_valid_tax_audit_form(audit_form):
    return audit_form in TAX_AUDIT_REPORT_FORMS


# ---------------------------------------------------------
# FORM 3CD CLAUSE-WISE TEMPLATE
# AY 2025-26 FRIENDLY STRUCTURE
# ---------------------------------------------------------

FORM_3CD_TEMPLATE = {
    "1": {
        "title": "Name of the assessee",
        "sheet": "Form-3CD",
        "fields": [
            "Name of the assessee"
        ]
    },

    "2": {
        "title": "Address of the assessee",
        "sheet": "Form-3CD",
        "fields": [
            "Address line 1",
            "Address line 2",
            "City / Town",
            "State",
            "PIN Code"
        ]
    },

    "3": {
        "title": "Permanent Account Number or Aadhaar Number",
        "sheet": "Form-3CD",
        "fields": [
            "PAN",
            "Aadhaar Number, if applicable"
        ]
    },

    "4": {
        "title": "Whether the assessee is liable to pay indirect tax like excise duty, service tax, sales tax, goods and services tax, customs duty, etc.",
        "sheet": "Form-3CD",
        "fields": [
            "Whether liable to indirect tax",
            "Type of indirect tax",
            "Registration number / GSTIN",
            "Remarks"
        ]
    },

    "5": {
        "title": "Status",
        "sheet": "Form-3CD",
        "fields": [
            "Status of assessee"
        ]
    },

    "6": {
        "title": "Previous year",
        "sheet": "Form-3CD",
        "fields": [
            "Previous year from",
            "Previous year to"
        ]
    },

    "7": {
        "title": "Assessment year",
        "sheet": "Form-3CD",
        "fields": [
            "Assessment year"
        ]
    },

    "8": {
        "title": "Indicate the relevant clause of section 44AB under which audit has been conducted",
        "sheet": "Form-3CD",
        "fields": [
            "Relevant clause of section 44AB",
            "Reason for applicability",
            "Whether auto-filled from Tax Audit Applicability module"
        ]
    },

    "9": {
        "title": "If firm or association of persons, indicate names of partners/members and their profit sharing ratios",
        "sheet": "Form-3CD",
        "fields": [
            "Name of partner / member",
            "PAN of partner / member",
            "Profit sharing ratio",
            "Changes during the previous year",
            "Remarks"
        ]
    },

    "10": {
        "title": "Nature of business or profession",
        "sheet": "Form-3CD",
        "fields": [
            "Nature of business / profession",
            "Business code / profession code",
            "Whether there was change during the year",
            "Details of change, if any"
        ]
    },

    "11": {
        "title": "Books of account prescribed, maintained and examined",
        "sheet": "Form-3CD",
        "fields": [
            "Books prescribed under section 44AA",
            "Books of account maintained",
            "Books of account examined",
            "Address where books are kept",
            "Whether books are maintained electronically",
            "Remarks"
        ]
    },

    "12": {
        "title": "Whether profit and loss account includes profits and gains assessable on presumptive basis",
        "sheet": "Form-3CD",
        "fields": [
            "Whether presumptive income included",
            "Relevant section: 44AD / 44ADA / 44AE / 44BBC / Other",
            "Gross receipts / turnover",
            "Amount of presumptive income",
            "Remarks"
        ]
    },

    "13": {
        "title": "Method of accounting employed",
        "sheet": "annex-13-c / annex-13-e / annex-13-f",
        "fields": [
            "Method of accounting employed",
            "Whether there was change in method of accounting",
            "Effect on profit due to change",
            "ICDS adjustment - increase in profit",
            "ICDS adjustment - decrease in profit",
            "Remarks"
        ]
    },

    "14": {
        "title": "Method of valuation of closing stock",
        "sheet": "Annex-14-b",
        "fields": [
            "Class of goods / stock",
            "Method of valuation",
            "Whether there was change in method",
            "Effect on profit due to change",
            "Remarks"
        ]
    },

    "15": {
        "title": "Capital asset converted into stock-in-trade",
        "sheet": "Form-3CD",
        "fields": [
            "Description of capital asset",
            "Date of acquisition",
            "Cost of acquisition",
            "Amount at which converted into stock-in-trade",
            "Remarks"
        ]
    },

    "16": {
        "title": "Amounts not credited to profit and loss account",
        "sheet": "Form-3CD",
        "fields": [
            "Nature of amount",
            "Amount",
            "Reason for not crediting to profit and loss account",
            "Relevant section, if any",
            "Remarks"
        ]
    },

    "17": {
        "title": "Transfer of land or building or both for consideration less than stamp duty value",
        "sheet": "Annex-17",
        "fields": [
            "Details of property",
            "Consideration received or accrued",
            "Value adopted / assessed / assessable for stamp duty",
            "Difference",
            "Remarks"
        ]
    },

    "18": {
        "title": "Depreciation allowable under the Income-tax Act",
        "sheet": "Form-3CD",
        "fields": [
            "Block of asset",
            "Rate of depreciation",
            "Opening WDV",
            "Additions before 180 days",
            "Additions after 180 days",
            "Deletions",
            "Depreciation allowable",
            "Closing WDV",
            "Remarks"
        ]
    },

    "19": {
        "title": "Amounts admissible under specified sections",
        "sheet": "Annex-19",
        "fields": [
            "Section",
            "Amount debited to profit and loss account",
            "Amount admissible",
            "Remarks"
        ]
    },

    "20": {
        "title": "Bonus, commission and employees contribution to funds",
        "sheet": "Annex-20-b",
        "fields": [
            "Nature of sum",
            "Amount payable",
            "Due date",
            "Actual payment date",
            "Amount allowable",
            "Amount disallowable",
            "Remarks"
        ]
    },

    "21": {
        "title": "Amounts inadmissible under sections 36, 37, 40, 40A, 43B etc.",
        "sheet": "Annex-21-a / Annex-21-b-i / Annex-21-b-ii / Annex-21-d",
        "fields": [
            "Nature of expenditure / disallowance",
            "Relevant section",
            "Amount debited to profit and loss account",
            "Amount inadmissible",
            "Reason",
            "Remarks"
        ]
    },

    "22": {
        "title": "Amount of interest inadmissible under section 23 of the Micro, Small and Medium Enterprises Development Act, 2006",
        "sheet": "Form-3CD",
        "fields": [
            "Name of MSME supplier",
            "Udyam registration number",
            "Principal amount outstanding",
            "Interest amount inadmissible",
            "Due date",
            "Payment date",
            "Remarks"
        ]
    },

    "23": {
        "title": "Payments to persons specified under section 40A(2)(b)",
        "sheet": "Form-3CD",
        "fields": [
            "Name of specified person",
            "PAN",
            "Relationship",
            "Nature of payment",
            "Amount paid",
            "Auditor remark on reasonableness"
        ]
    },

    "24": {
        "title": "Amounts deemed to be profits and gains under section 32AC / 33AB / 33ABA / 33AC",
        "sheet": "Form-3CD",
        "fields": [
            "Section",
            "Nature of deemed profit",
            "Amount",
            "Remarks"
        ]
    },

    "25": {
        "title": "Amount of profit chargeable to tax under section 41",
        "sheet": "Form-3CD",
        "fields": [
            "Nature of amount",
            "Amount",
            "Section 41 reference",
            "Remarks"
        ]
    },

    "26": {
        "title": "Amounts covered under section 43B",
        "sheet": "Form-3CD",
        "fields": [
            "Nature of liability",
            "Amount",
            "Whether paid on or before due date",
            "Date of payment",
            "Amount allowable",
            "Amount disallowable",
            "Remarks"
        ]
    },

    "27": {
        "title": "CENVAT / GST input credit and prior period items",
        "sheet": "Form-3CD",
        "fields": [
            "Opening balance of credit",
            "Credit availed during the year",
            "Credit utilised during the year",
            "Closing balance",
            "Treatment in books of account",
            "Prior period income / expenditure",
            "Remarks"
        ]
    },

    "28": {
        "title": "Shares received without adequate consideration under section 56(2)(viia), if applicable",
        "sheet": "Form-3CD",
        "fields": [
            "Name of company",
            "Number of shares received",
            "Fair market value",
            "Consideration paid",
            "Amount taxable",
            "Remarks"
        ]
    },

    "29": {
        "title": "Income chargeable under section 56(2)(ix)",
        "sheet": "Form-3CD",
        "fields": [
            "Nature of income",
            "Amount",
            "Remarks"
        ]
    },

    "29A": {
        "title": "Income chargeable under section 56(2)(x)",
        "sheet": "Form-3CD",
        "fields": [
            "Nature of property / money received",
            "Fair market value",
            "Consideration paid",
            "Amount taxable",
            "Remarks"
        ]
    },

    "30": {
        "title": "Details of any amount borrowed on hundi or repayment otherwise than through account payee cheque",
        "sheet": "Form-3CD",
        "fields": [
            "Name of person",
            "PAN",
            "Amount borrowed / repaid",
            "Mode of transaction",
            "Remarks"
        ]
    },

    "30A": {
        "title": "Primary adjustment to transfer price under section 92CE",
        "sheet": "Form-3CD",
        "fields": [
            "Whether primary adjustment made",
            "Amount of primary adjustment",
            "Whether excess money repatriated",
            "Imputed interest income, if any",
            "Remarks"
        ]
    },

    "30B": {
        "title": "Limitation on interest deduction under section 94B",
        "sheet": "Form-3CD",
        "fields": [
            "Interest expenditure",
            "EBITDA",
            "Allowable interest",
            "Disallowance under section 94B",
            "Remarks"
        ]
    },

    "30C": {
        "title": "Impermissible avoidance arrangement",
        "sheet": "Form-3CD",
        "fields": [
            "Whether any impermissible avoidance arrangement entered",
            "Nature of arrangement",
            "Tax benefit arising",
            "Remarks"
        ]
    },

    "31": {
        "title": "Loans, deposits, specified sums and specified advances",
        "sheet": "Annex-31-a / Annex-31-b / Annex-31-ba / Annex-31-bb / Annex-31-bc / Annex-31-bd / Annex-31-c / Annex-31-d / Annex-31-e",
        "fields": [
            "Transaction type",
            "Name of party",
            "PAN",
            "Address",
            "Amount",
            "Mode",
            "Nature code",
            "Whether accepted / repaid otherwise than prescribed mode",
            "Remarks"
        ]
    },

    "32": {
        "title": "Brought forward loss or depreciation allowance",
        "sheet": "Annex-32-a",
        "fields": [
            "Assessment year",
            "Nature of loss / allowance",
            "Amount brought forward",
            "Amount set off",
            "Amount carried forward",
            "Remarks"
        ]
    },

    "33": {
        "title": "Deductions admissible under Chapter VIA or Chapter III",
        "sheet": "Form-3CD",
        "fields": [
            "Section",
            "Amount claimed",
            "Amount admissible",
            "Remarks"
        ]
    },

    "34": {
        "title": "TDS / TCS compliance",
        "sheet": "Annex-34-a / Annex-34-b / Annex-34-c",
        "fields": [
            "Section",
            "Nature of payment",
            "Amount paid / credited",
            "Tax deductible / collectible",
            "Tax deducted / collected",
            "Tax deposited",
            "Due date",
            "Actual date of deposit",
            "Short deduction / late payment, if any",
            "Remarks"
        ]
    },

    "35": {
        "title": "Trading concern / manufacturing concern quantitative details",
        "sheet": "Form-3CD",
        "fields": [
            "Item name",
            "Unit",
            "Opening stock",
            "Purchases",
            "Sales",
            "Closing stock",
            "Shortage / excess",
            "Remarks"
        ]
    },

    "36": {
        "title": "Dividend Distribution Tax details, if applicable",
        "sheet": "Form-3CD",
        "fields": [
            "Amount of dividend",
            "Date of declaration / distribution",
            "Tax paid",
            "Date of payment",
            "Remarks"
        ]
    },

    "36A": {
        "title": "Deemed dividend under section 2(22)(e)",
        "sheet": "Form-3CD",
        "fields": [
            "Name of company",
            "PAN of company",
            "Amount received",
            "Nature of payment",
            "Remarks"
        ]
    },

    "36B": {
        "title": "Amount received for buyback of shares under section 2(22)(f)",
        "sheet": "Form-3CD",
        "fields": [
            "Whether amount received for buyback of shares",
            "Amount received",
            "Cost of acquisition of shares bought back",
            "Remarks"
        ]
    },

    "37": {
        "title": "Cost audit details",
        "sheet": "Form-3CD",
        "fields": [
            "Whether cost audit applicable",
            "Date of cost audit report",
            "Details of qualification / observation",
            "Remarks"
        ]
    },

    "38": {
        "title": "Audit under Central Excise Act, if applicable",
        "sheet": "Form-3CD",
        "fields": [
            "Whether audit conducted",
            "Date of audit report",
            "Details of qualification / observation",
            "Remarks"
        ]
    },

    "39": {
        "title": "Audit under section 72A of the Finance Act relating to valuation of taxable services, if applicable",
        "sheet": "Form-3CD",
        "fields": [
            "Whether audit conducted",
            "Date of audit report",
            "Details of qualification / observation",
            "Remarks"
        ]
    },

    "40": {
        "title": "Accounting ratios",
        "sheet": "Form-3CD",
        "fields": [
            "Gross profit ratio",
            "Net profit ratio",
            "Stock turnover ratio",
            "Material consumed / finished goods produced ratio",
            "Remarks"
        ]
    },

    "41": {
        "title": "Demand raised or refund issued under tax laws other than Income-tax Act and Wealth-tax Act",
        "sheet": "Form-3CD",
        "fields": [
            "Name of tax law",
            "Demand / refund",
            "Amount",
            "Assessment year / period",
            "Status",
            "Remarks"
        ]
    },

    "42": {
        "title": "Reporting of Form 61, Form 61A and Form 61B",
        "sheet": "Annex-42-b",
        "fields": [
            "Type of form",
            "Whether required to be furnished",
            "Due date",
            "Date of furnishing",
            "Acknowledgement number",
            "Remarks"
        ]
    },

    "43": {
        "title": "Country-by-Country Reporting and Master File",
        "sheet": "Annex-43-b",
        "fields": [
            "Whether international group applicable",
            "Whether Master File applicable",
            "Whether CbCR applicable",
            "Date of furnishing",
            "Acknowledgement number",
            "Remarks"
        ]
    },

    "44": {
        "title": "Break-up of total expenditure of entities registered or not registered under GST",
        "sheet": "Annexure-44",
        "fields": [
            "Total amount of expenditure",
            "Expenditure relating to entities registered under GST",
            "Expenditure relating to entities not registered under GST",
            "Expenditure relating to composition dealers",
            "Expenditure relating to exempt supply",
            "Other expenditure",
            "Remarks"
        ]
    }
}


# ---------------------------------------------------------
# FORM 3CD HELPER FUNCTIONS
# ---------------------------------------------------------

def get_clause_title(clause_no):
    return FORM_3CD_TEMPLATE.get(str(clause_no), {}).get("title", "")


def get_clause_sheet(clause_no):
    return FORM_3CD_TEMPLATE.get(str(clause_no), {}).get("sheet", "")


def get_clause_fields(clause_no):
    return FORM_3CD_TEMPLATE.get(
        str(clause_no),
        {
            "fields": [
                "Details / Particulars",
                "Amount, if applicable",
                "Auditor Remarks"
            ]
        }
    )["fields"]


def get_all_clauses():
    return [
        (clause_no, details["title"])
        for clause_no, details in FORM_3CD_TEMPLATE.items()
    ]


def get_form_3cd_template():
    return FORM_3CD_TEMPLATE