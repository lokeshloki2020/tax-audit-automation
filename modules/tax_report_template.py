# modules/tax_report_template.py

# ---------------------------------------------------------
# TAX AUDIT REPORT TEMPLATE SYSTEM
# Form 3CA / Form 3CB / Form 3CD
# ---------------------------------------------------------
# This file controls:
# 1. Form 3CA report-level fields
# 2. Form 3CB report-level fields
# 3. Form 3CD clause-wise fields
#
# Current update:
# - New portal-style Form 3CA details added
# - Existing portal-style Form 3CB details retained
# - Form 3CD clauses retained with clauses 1 to 44
# ---------------------------------------------------------


# ---------------------------------------------------------
# TAX AUDIT FORM MASTER
# ---------------------------------------------------------

TAX_AUDIT_FORMS = {
    "Form 3CA-3CD": {
        "code": "3CA",
        "title": (
            "Audit Report under section 44AB [Audited under any other law] "
            "Statement of particulars under section 44AB [Form No. 3CA]"
        ),
        "description": (
            "Audit report under section 44AB of the Income-tax Act, 1961, "
            "where the accounts of the business or profession have been audited under any other law."
        ),
    },
    "Form 3CB-3CD": {
        "code": "3CB",
        "title": (
            "Audit Report under section 44AB [Audited under Income-tax Act] "
            "Statement of particulars under section 44AB [Form No. 3CB]"
        ),
        "description": (
            "Audit report under section 44AB of the Income-tax Act, 1961, "
            "in a case referred to in clause (b) of sub-rule (1) of rule 6G."
        ),
    },
    "Not Applicable": {
        "code": "NA",
        "title": "Tax Audit Not Applicable",
        "description": "Tax audit report is not applicable.",
    },
}


# ---------------------------------------------------------
# FORM 3CD CLAUSE MASTER
# ---------------------------------------------------------

FORM_3CD_CLAUSES = {
    "1": {
        "title": "Name of the assessee",
        "utility_sheet": "Part_A",
        "fields": [
            "Name of the assessee",
        ],
    },
    "2": {
        "title": "Address of the assessee",
        "utility_sheet": "Part_A",
        "fields": [
            "Address Line 1",
            "Address Line 2",
            "City / Town",
            "District",
            "State",
            "Country",
            "Pincode",
        ],
    },
    "3": {
        "title": "Permanent Account Number or Aadhaar Number",
        "utility_sheet": "Part_A",
        "fields": [
            "PAN",
            "Aadhaar Number, if available",
        ],
    },
    "4": {
        "title": "Whether the assessee is liable to pay indirect tax like excise duty, service tax, sales tax, GST, customs duty, etc.",
        "utility_sheet": "Part_A",
        "fields": [
            "Whether liable to pay indirect tax",
            "Type of indirect tax",
            "Registration number / GSTIN",
            "Remarks",
        ],
    },
    "5": {
        "title": "Status of the assessee",
        "utility_sheet": "Part_A",
        "fields": [
            "Status of assessee",
        ],
    },
    "6": {
        "title": "Previous year",
        "utility_sheet": "Part_A",
        "fields": [
            "Previous year from date",
            "Previous year to date",
        ],
    },
    "7": {
        "title": "Assessment year",
        "utility_sheet": "Part_A",
        "fields": [
            "Assessment year",
        ],
    },
    "8": {
        "title": "Relevant clause of section 44AB under which audit has been conducted",
        "utility_sheet": "Part_A",
        "fields": [
            "Relevant clause of section 44AB",
            "Reason for applicability",
            "Whether auto-filled from Tax Audit Applicability module",
        ],
    },
    "9": {
        "title": "If firm or AOP, indicate names of partners or members and their profit sharing ratios",
        "utility_sheet": "Clause_9",
        "fields": [
            "Name of partner / member",
            "Profit sharing ratio",
            "Remarks",
        ],
    },
    "10": {
        "title": "Nature of business or profession",
        "utility_sheet": "Clause_10",
        "fields": [
            "Nature of business or profession",
            "Sector / activity code",
            "Whether any change in nature of business or profession",
            "Details of change, if any",
        ],
    },
    "11": {
        "title": "Books of account prescribed, maintained and examined",
        "utility_sheet": "Clause_11",
        "fields": [
            "Whether books of account are prescribed under section 44AA",
            "List of books prescribed",
            "List of books maintained",
            "Address where books are kept",
            "Whether books examined",
            "Remarks",
        ],
    },
    "12": {
        "title": "Whether profit and loss account includes profits assessable on presumptive basis",
        "utility_sheet": "Clause_12",
        "fields": [
            "Whether profits assessable on presumptive basis are included",
            "Section under which presumptive income is computed",
            "Amount of presumptive income",
            "Remarks",
        ],
    },
    "13": {
        "title": "Method of accounting employed",
        "utility_sheet": "Clause_13",
        "fields": [
            "Method of accounting employed",
            "Whether there is any change in method of accounting",
            "Effect of change on profit or loss",
            "ICDS compliance details",
            "Deviation from ICDS, if any",
        ],
    },
    "14": {
        "title": "Method of valuation of closing stock",
        "utility_sheet": "Clause_14",
        "fields": [
            "Method of valuation of closing stock",
            "Whether there is any deviation from prescribed method",
            "Effect of deviation on profit or loss",
            "Remarks",
        ],
    },
    "15": {
        "title": "Capital asset converted into stock-in-trade",
        "utility_sheet": "Clause_15",
        "fields": [
            "Description of capital asset",
            "Date of acquisition",
            "Cost of acquisition",
            "Amount at which converted into stock-in-trade",
            "Remarks",
        ],
    },
    "16": {
        "title": "Amounts not credited to profit and loss account",
        "utility_sheet": "Clause_16",
        "fields": [
            "Items falling within section 28",
            "Pro forma credits, drawbacks, refunds of duty, customs, excise, GST, etc.",
            "Escalation claims accepted during the previous year",
            "Any other item of income",
            "Capital receipt, if any",
            "Remarks",
        ],
    },
    "17": {
        "title": "Transfer of land or building or both under section 43CA or 50C",
        "utility_sheet": "Clause_17",
        "fields": [
            "Details of property transferred",
            "Consideration received or accrued",
            "Value adopted or assessed or assessable",
            "Whether section 43CA / 50C applicable",
            "Remarks",
        ],
    },
    "18": {
        "title": "Depreciation allowable under the Income-tax Act",
        "utility_sheet": "Clause_18",
        "fields": [
            "Description of asset / block of asset",
            "Rate of depreciation",
            "Opening WDV",
            "Additions",
            "Deletions",
            "Depreciation allowable",
            "Closing WDV",
            "Remarks",
        ],
    },
    "19": {
        "title": "Amounts admissible under sections 32AC, 33AB, 33ABA, 35, 35ABB, 35AD, 35CCA, 35CCB, 35CCC, 35CCD, etc.",
        "utility_sheet": "Clause_19",
        "fields": [
            "Section",
            "Amount debited to profit and loss account",
            "Amount admissible",
            "Remarks",
        ],
    },
    "20": {
        "title": "Employee contribution to welfare funds and details under section 36(1)(va)",
        "utility_sheet": "Clause_20",
        "fields": [
            "Nature of fund",
            "Sum received from employees",
            "Due date for payment",
            "Actual date of payment",
            "Amount paid",
            "Remarks",
        ],
    },
    "21": {
        "title": "Amounts inadmissible under section 40, 40A and other disallowances",
        "utility_sheet": "Clause_21",
        "fields": [
            "Nature of payment / expenditure",
            "Amount debited to profit and loss account",
            "Amount inadmissible",
            "Relevant section",
            "Remarks",
        ],
    },
    "22": {
        "title": "Amount of interest inadmissible under the Micro, Small and Medium Enterprises Development Act",
        "utility_sheet": "Clause_22",
        "fields": [
            "Amount of interest inadmissible",
            "MSME vendor details",
            "Remarks",
        ],
    },
    "23": {
        "title": "Payments to persons specified under section 40A(2)(b)",
        "utility_sheet": "Clause_23",
        "fields": [
            "Name of related party",
            "Relationship",
            "Nature of payment",
            "Amount paid",
            "Reasonableness check",
            "Remarks",
        ],
    },
    "24": {
        "title": "Amounts deemed to be profits and gains under section 32AC / 33AB / 33ABA / 33AC",
        "utility_sheet": "Clause_24",
        "fields": [
            "Section",
            "Amount deemed as profits and gains",
            "Remarks",
        ],
    },
    "25": {
        "title": "Amount of profit chargeable to tax under section 41",
        "utility_sheet": "Clause_25",
        "fields": [
            "Description of amount",
            "Amount chargeable under section 41",
            "Remarks",
        ],
    },
    "26": {
        "title": "Liabilities covered under section 43B",
        "utility_sheet": "Clause_26",
        "fields": [
            "Nature of liability",
            "Amount payable",
            "Due date",
            "Actual date of payment",
            "Whether paid before due date",
            "Amount allowable",
            "Amount disallowable",
            "Remarks",
        ],
    },
    "27": {
        "title": "CENVAT / GST credits and prior period items",
        "utility_sheet": "Clause_27",
        "fields": [
            "Details of CENVAT / GST credit",
            "Treatment in books",
            "Prior period income",
            "Prior period expenses",
            "Remarks",
        ],
    },
    "28": {
        "title": "Shares received without consideration or for inadequate consideration under section 56(2)(viia)",
        "utility_sheet": "Clause_28",
        "fields": [
            "Name of company whose shares are received",
            "Number of shares",
            "Fair market value",
            "Consideration paid",
            "Amount taxable",
            "Remarks",
        ],
    },
    "29": {
        "title": "Income from issue of shares in excess of fair market value under section 56(2)(viib)",
        "utility_sheet": "Clause_29",
        "fields": [
            "Nature of shares issued",
            "Consideration received",
            "Fair market value",
            "Excess amount taxable",
            "Remarks",
        ],
    },
    "29A": {
        "title": "Income chargeable under section 56(2)(ix)",
        "utility_sheet": "Clause_29A",
        "fields": [
            "Nature of income",
            "Amount chargeable",
            "Remarks",
        ],
    },
    "29B": {
        "title": "Income chargeable under section 56(2)(x)",
        "utility_sheet": "Clause_29B",
        "fields": [
            "Nature of receipt",
            "Amount / value received",
            "Amount chargeable",
            "Remarks",
        ],
    },
    "30": {
        "title": "Amount borrowed on hundi or repayment otherwise than through account payee cheque",
        "utility_sheet": "Clause_30",
        "fields": [
            "Name of lender / borrower",
            "Amount borrowed / repaid",
            "Mode of transaction",
            "Remarks",
        ],
    },
    "30A": {
        "title": "Primary adjustment to transfer price under section 92CE",
        "utility_sheet": "Clause_30A",
        "fields": [
            "Whether primary adjustment made",
            "Amount of primary adjustment",
            "Whether excess money repatriated",
            "Remarks",
        ],
    },
    "30B": {
        "title": "Limitation on interest deduction under section 94B",
        "utility_sheet": "Clause_30B",
        "fields": [
            "Amount of expenditure by way of interest",
            "EBITDA",
            "Amount of interest disallowable",
            "Remarks",
        ],
    },
    "30C": {
        "title": "Impermissible avoidance arrangement under GAAR",
        "utility_sheet": "Clause_30C",
        "fields": [
            "Whether arrangement is impermissible avoidance arrangement",
            "Nature of arrangement",
            "Tax benefit arising",
            "Remarks",
        ],
    },
    "31": {
        "title": "Loans, deposits, specified sums and specified advances",
        "utility_sheet": "Clause_31",
        "fields": [
            "Name of party",
            "PAN of party",
            "Amount accepted / repaid",
            "Mode of acceptance / repayment",
            "Whether by account payee cheque / bank draft / ECS / prescribed mode",
            "Remarks",
        ],
    },
    "32": {
        "title": "Brought forward loss or depreciation allowance",
        "utility_sheet": "Clause_32",
        "fields": [
            "Assessment year",
            "Nature of loss / allowance",
            "Amount as returned",
            "Amount as assessed",
            "Remarks",
        ],
    },
    "33": {
        "title": "Deductions admissible under Chapter VIA or Chapter III",
        "utility_sheet": "Clause_33",
        "fields": [
            "Section",
            "Amount claimed",
            "Amount admissible",
            "Remarks",
        ],
    },
    "34": {
        "title": "TDS / TCS compliance",
        "utility_sheet": "Clause_34",
        "fields": [
            "TAN",
            "Nature of payment",
            "Amount paid / credited",
            "Tax deductible / collectible",
            "Tax deducted / collected",
            "Tax deposited",
            "Due date",
            "Date of payment",
            "Remarks",
        ],
    },
    "35": {
        "title": "Trading concern / manufacturing concern quantitative details",
        "utility_sheet": "Clause_35",
        "fields": [
            "Item name",
            "Unit",
            "Opening stock",
            "Purchases / production",
            "Sales / consumption",
            "Closing stock",
            "Shortage / excess",
            "Remarks",
        ],
    },
    "36": {
        "title": "Dividend received under section 2(22)(e)",
        "utility_sheet": "Clause_36",
        "fields": [
            "Amount deemed dividend",
            "Name of company",
            "Remarks",
        ],
    },
    "36A": {
        "title": "Deemed income under section 2(24)(xviii)",
        "utility_sheet": "Clause_36A",
        "fields": [
            "Nature of receipt",
            "Amount deemed income",
            "Remarks",
        ],
    },
    "37": {
        "title": "Cost audit details",
        "utility_sheet": "Clause_37",
        "fields": [
            "Whether cost audit was carried out",
            "Details of disqualification or disagreement, if any",
            "Remarks",
        ],
    },
    "38": {
        "title": "Audit under Central Excise Act",
        "utility_sheet": "Clause_38",
        "fields": [
            "Whether audit under Central Excise Act was carried out",
            "Details of disqualification or disagreement, if any",
            "Remarks",
        ],
    },
    "39": {
        "title": "Audit under section 72A of the Finance Act relating to valuation of taxable services",
        "utility_sheet": "Clause_39",
        "fields": [
            "Whether audit was conducted",
            "Details of disqualification or disagreement, if any",
            "Remarks",
        ],
    },
    "40": {
        "title": "Accounting ratios",
        "utility_sheet": "Clause_40",
        "fields": [
            "Gross profit ratio",
            "Net profit ratio",
            "Stock turnover ratio",
            "Material consumed / finished goods produced ratio",
            "Remarks",
        ],
    },
    "41": {
        "title": "Demand raised or refund issued under any tax laws other than Income-tax Act and Wealth-tax Act",
        "utility_sheet": "Clause_41",
        "fields": [
            "Name of tax law",
            "Demand / refund order details",
            "Amount",
            "Remarks",
        ],
    },
    "42": {
        "title": "Form 61, Form 61A and Form 61B reporting",
        "utility_sheet": "Clause_42",
        "fields": [
            "Whether liable to furnish Form 61 / 61A / 61B",
            "Income-tax Department reporting entity identification number",
            "Type of form",
            "Due date",
            "Date of furnishing",
            "Remarks",
        ],
    },
    "43": {
        "title": "Country-by-country reporting under section 286",
        "utility_sheet": "Clause_43",
        "fields": [
            "Whether section 286 applicable",
            "Parent entity details",
            "Alternate reporting entity details",
            "Date of furnishing report",
            "Remarks",
        ],
    },
    "44": {
        "title": "Break-up of total expenditure of entities registered or not registered under GST",
        "utility_sheet": "Clause_44",
        "fields": [
            "Total amount of expenditure",
            "Expenditure relating to entities registered under GST",
            "Expenditure relating to entities not registered under GST",
            "Exempt goods / services",
            "Composition scheme entities",
            "Other registered entities",
            "Remarks",
        ],
    },
}


# ---------------------------------------------------------
# BASIC FORM FUNCTIONS
# ---------------------------------------------------------

def get_all_clauses():
    return [(clause_no, data["title"]) for clause_no, data in FORM_3CD_CLAUSES.items()]


def get_clause_title(clause_no):
    clause_no = str(clause_no)
    return FORM_3CD_CLAUSES.get(clause_no, {}).get("title", "")


def get_clause_sheet(clause_no):
    clause_no = str(clause_no)
    return FORM_3CD_CLAUSES.get(clause_no, {}).get("utility_sheet", "")


def get_clause_fields(clause_no):
    clause_no = str(clause_no)
    return FORM_3CD_CLAUSES.get(clause_no, {}).get("fields", [])


def get_tax_audit_form_title(audit_form):
    return TAX_AUDIT_FORMS.get(audit_form, TAX_AUDIT_FORMS["Not Applicable"]).get("title", "")


def get_tax_audit_form_code(audit_form):
    return TAX_AUDIT_FORMS.get(audit_form, TAX_AUDIT_FORMS["Not Applicable"]).get("code", "")


def is_valid_tax_audit_form(audit_form):
    return audit_form in ["Form 3CA-3CD", "Form 3CB-3CD"]


# ---------------------------------------------------------
# FALLBACK SIMPLE FIELDS
# Used only if structured renderer is not active
# ---------------------------------------------------------

def get_tax_audit_form_fields(audit_form):
    if audit_form == "Form 3CA-3CD":
        return [
            "Declaration Type",
            "Assessee Name",
            "Assessee Address",
            "Assessee PAN",
            "Statutory Audit Conducted By",
            "Law under which statutory audit was conducted",
            "Statutory Audit Report Date",
            "Audited Statement Type",
            "Period Beginning From",
            "Period Ending On",
            "Audited Balance Sheet Date",
            "Form 3CD Observations / Qualifications",
            "Accountant Name",
            "Membership Number",
            "FRN",
            "Date of signing Tax Audit Report",
            "Place",
            "Date",
        ]

    if audit_form == "Form 3CB-3CD":
        return [
            "Declaration Type",
            "Balance Sheet Date",
            "Statement Type",
            "Period Beginning From",
            "Period Ending On",
            "Assessee Name",
            "Assessee Address",
            "Assessee PAN",
            "Books Head Office Address",
            "Books Branches",
            "Observations / Comments / Discrepancies",
            "Profit Or Loss",
            "Form 3CD Observations / Qualifications",
            "Accountant Name",
            "Membership Number",
            "FRN",
            "Date of signing Tax Audit Report",
            "Place",
            "Date",
        ]

    return []


# ---------------------------------------------------------
# COMMON STRUCTURED FIELDS
# ---------------------------------------------------------

def get_common_assessee_fields():
    return [
        {"name": "Assessee First Name", "label": "First Name", "type": "text", "default": "", "required": False},
        {"name": "Assessee Middle Name", "label": "Middle Name", "type": "text", "default": "", "required": False},
        {"name": "Assessee Last Name", "label": "Last Name", "type": "text", "default": "", "required": True},
        {
            "name": "Assessee Country Region",
            "label": "Country / Region",
            "type": "select",
            "options": ["91-India"],
            "default": "91-India",
            "required": True,
        },
        {"name": "Assessee Flat Door Building", "label": "Flat / Door / Building", "type": "text", "default": "", "required": True},
        {"name": "Assessee Road Street Block Sector", "label": "Road / Street / Block / Sector", "type": "text", "default": "", "required": False},
        {"name": "Assessee Pincode", "label": "Pincode", "type": "text", "default": "", "required": True},
        {"name": "Assessee Post Office", "label": "Post Office", "type": "text", "default": "", "required": True},
        {"name": "Assessee Area Locality", "label": "Area / Locality", "type": "text", "default": "", "required": True},
        {"name": "Assessee District", "label": "District", "type": "text", "default": "", "required": True},
        {"name": "Assessee State", "label": "State", "type": "text", "default": "", "required": True},
        {"name": "Assessee PAN", "label": "Permanent Account Number (PAN)", "type": "text", "default": "", "required": False},
        {"name": "Assessee Aadhaar", "label": "Aadhaar Number of the assessee, if available", "type": "text", "default": "", "required": False},
    ]


def get_common_accountant_fields():
    return [
        {"name": "Accountant First Name", "label": "First Name", "type": "text", "default": "", "required": False},
        {"name": "Accountant Middle Name", "label": "Middle Name", "type": "text", "default": "", "required": False},
        {"name": "Accountant Last Name", "label": "Last Name", "type": "text", "default": "", "required": True},
        {"name": "Accountant Membership Number", "label": "Membership Number", "type": "text", "default": "", "required": True},
        {"name": "Accountant FRN", "label": "FRN / Firm Registration Number", "type": "text", "default": "", "required": False},
    ]


def get_common_accountant_address_fields():
    return [
        {
            "name": "Accountant Country Region",
            "label": "Country / Region",
            "type": "select",
            "options": ["91-India"],
            "default": "91-India",
            "required": True,
        },
        {"name": "Accountant Flat Door Building", "label": "Flat / Door / Building", "type": "text", "default": "", "required": True},
        {"name": "Accountant Road Street Block Sector", "label": "Road / Street / Block / Sector", "type": "text", "default": "", "required": False},
        {"name": "Accountant ZIP Code", "label": "ZIP Code", "type": "text", "default": "", "required": True},
        {"name": "Accountant Post Office", "label": "Post Office", "type": "text", "default": "", "required": True},
        {"name": "Accountant Area Locality", "label": "Area / Locality", "type": "text", "default": "", "required": True},
        {"name": "Accountant District", "label": "District", "type": "text", "default": "", "required": True},
        {"name": "Accountant State", "label": "State", "type": "text", "default": "", "required": True},
    ]


def get_common_signing_fields():
    return [
        {
            "name": "Date of signing Tax Audit Report",
            "label": "Date of signing Tax Audit Report",
            "type": "date",
            "default": "",
            "required": True,
        },
        {
            "name": "Place",
            "label": "Place",
            "type": "text",
            "default": "",
            "required": True,
        },
        {
            "name": "Report Date",
            "label": "Date",
            "type": "date",
            "default": "",
            "required": True,
        },
    ]


# ---------------------------------------------------------
# STRUCTURED FORM 3CA / 3CB SCHEMA
# ---------------------------------------------------------

def get_tax_audit_form_field_schema(audit_form):
    """
    Structured field schema for Form 3CA and Form 3CB.
    This does not change Form 3CD clause fields.
    """

    # ---------------------------------------------------------
    # FORM 3CA
    # ---------------------------------------------------------

    if audit_form == "Form 3CA-3CD":
        return [
            {
                "section": "1. Statutory Audit Report Details",
                "fields": [
                    {
                        "name": "Declaration Type",
                        "label": "I / We report that the statutory audit of",
                        "type": "select",
                        "options": ["I", "We"],
                        "default": "I",
                        "required": True,
                    },
                ],
            },
            {
                "section": "2. Assessee Details",
                "fields": get_common_assessee_fields(),
            },
            {
                "section": "3. Statutory Audit Conducted By",
                "fields": [
                    {
                        "name": "Statutory Audit Conducted By",
                        "label": "Was conducted by",
                        "type": "select",
                        "options": ["me", "us"],
                        "default": "me",
                        "required": True,
                    },
                    {
                        "name": "Statutory Auditor Name",
                        "label": "Name of statutory auditor / audit firm",
                        "type": "text",
                        "default": "",
                        "required": True,
                    },
                    {
                        "name": "Other Law Name",
                        "label": "In pursuance of the provisions of",
                        "type": "select",
                        "options": [
                            "Companies Act, 2013",
                            "Limited Liability Partnership Act, 2008",
                            "Co-operative Societies Act",
                            "Societies Registration Act",
                            "Trust Act",
                            "Other Law",
                        ],
                        "default": "Companies Act, 2013",
                        "required": True,
                    },
                    {
                        "name": "Other Law Declaration Type",
                        "label": "And",
                        "type": "select",
                        "options": ["I", "We"],
                        "default": "I",
                        "required": True,
                    },
                    {
                        "name": "Audit Report Possessive",
                        "label": "Annex hereto a copy of",
                        "type": "select",
                        "options": ["my", "our"],
                        "default": "my",
                        "required": True,
                    },
                    {
                        "name": "Statutory Audit Report Date",
                        "label": "Audit report dated",
                        "type": "date",
                        "default": "",
                        "required": True,
                    },
                ],
            },
            {
                "section": "4. Audited Financial Statements Attached",
                "fields": [
                    {
                        "name": "Audited Statement Type",
                        "label": "A. The audited",
                        "type": "select",
                        "options": [
                            "Profit and loss account",
                            "Income and expenditure account",
                        ],
                        "default": "Profit and loss account",
                        "required": True,
                    },
                    {
                        "name": "Period Beginning From",
                        "label": "For the period beginning from",
                        "type": "date",
                        "default": "",
                        "required": True,
                    },
                    {
                        "name": "Period Ending On",
                        "label": "To ending on",
                        "type": "date",
                        "default": "",
                        "required": True,
                    },
                    {
                        "name": "Audited Balance Sheet Date",
                        "label": "B. The audited balance sheet as at",
                        "type": "date",
                        "default": "",
                        "required": True,
                    },
                    {
                        "name": "Documents Annexed Statement",
                        "label": "C. Documents declared by the said Act to be part of, or annexed to, the profit and loss account / income and expenditure account and balance sheet.",
                        "type": "readonly",
                        "default": "Confirmed",
                    },
                ],
            },
            {
                "section": "5. Form 3CD Annexure Confirmation",
                "fields": [
                    {
                        "name": "Form 3CD Annexure Statement",
                        "label": "The statement of particulars required to be furnished under section 44AB is annexed herewith in Form No. 3CD.",
                        "type": "readonly",
                        "default": "Confirmed",
                    },
                ],
            },
            {
                "section": "6. Form 3CD Opinion / Observations",
                "fields": [
                    {
                        "name": "Form 3CD Opinion Statement",
                        "label": "In my opinion and to the best of my information and according to examination of books of account including other relevant documents and explanations given to me, the particulars given in the said Form No. 3CD are true and correct subject to observations / qualifications, if any.",
                        "type": "readonly",
                        "default": "Confirmed",
                    },
                    {
                        "name": "Form 3CD Observations Qualifications",
                        "label": "Observations / qualifications in Form No. 3CD, if any",
                        "type": "textarea",
                        "default": "",
                        "height": 150,
                        "required": False,
                    },
                ],
            },
            {
                "section": "7. Accountant Details",
                "fields": get_common_accountant_fields(),
            },
            {
                "section": "8. Accountant Address Details",
                "fields": get_common_accountant_address_fields(),
            },
            {
                "section": "9. Signing Details",
                "fields": get_common_signing_fields(),
            },
        ]

    # ---------------------------------------------------------
    # FORM 3CB
    # ---------------------------------------------------------

    if audit_form == "Form 3CB-3CD":
        return [
            {
                "section": "1. Audit Report Basic Details",
                "fields": [
                    {
                        "name": "Declaration Type",
                        "label": "I / We have examined the balance sheet",
                        "type": "select",
                        "options": ["I", "We"],
                        "default": "I",
                        "required": True,
                    },
                    {
                        "name": "Balance Sheet Date",
                        "label": "Balance sheet as on 31st March",
                        "type": "text",
                        "default": "",
                        "placeholder": "Example: 2026",
                        "required": True,
                    },
                    {
                        "name": "Statement Type",
                        "label": "Statement attached",
                        "type": "select",
                        "options": [
                            "Profit and loss account",
                            "Income and expenditure account",
                        ],
                        "default": "Profit and loss account",
                        "required": True,
                    },
                    {
                        "name": "Period Beginning From",
                        "label": "For the period beginning from",
                        "type": "date",
                        "default": "",
                        "required": True,
                    },
                    {
                        "name": "Period Ending On",
                        "label": "To ending on",
                        "type": "date",
                        "default": "",
                        "required": True,
                    },
                ],
            },
            {
                "section": "2. Assessee Details",
                "fields": get_common_assessee_fields(),
            },
            {
                "section": "3. Books of Account Details",
                "fields": [
                    {
                        "name": "Books Head Office Address",
                        "label": "Books of account maintained at the head office at",
                        "type": "text",
                        "default": "",
                        "required": True,
                    },
                    {
                        "name": "Books Branches",
                        "label": "Branches",
                        "type": "text",
                        "default": "",
                        "required": True,
                    },
                ],
            },
            {
                "section": "4. Observations / Comments / Discrepancies",
                "fields": [
                    {
                        "name": "Observations Comments Discrepancies",
                        "label": "I report the following observations/comments/discrepancies/inconsistencies/not applicable, if any",
                        "type": "textarea",
                        "default": "",
                        "height": 150,
                        "required": False,
                    },
                ],
            },
            {
                "section": "5. Auditor Opinion and Certifications",
                "fields": [
                    {
                        "name": "Certification A",
                        "label": "A. I have obtained all the information and explanations which, to the best of my knowledge and belief, were necessary for the purposes of the audit.",
                        "type": "readonly",
                        "default": "Agreed",
                    },
                    {
                        "name": "Certification B",
                        "label": "B. In my opinion, proper books of account have been kept by the head office and branches of the assessee so far as appears from my examination of the books.",
                        "type": "readonly",
                        "default": "Agreed",
                    },
                    {
                        "name": "Certification C Balance Sheet",
                        "label": "C(i). In the case of the balance sheet, of the state of affairs of the assessee as at 31st March.",
                        "type": "readonly",
                        "default": "Agreed",
                    },
                    {
                        "name": "Profit Or Loss",
                        "label": "C(ii). In the case of the Profit and loss account, of the Profit / Loss of the assessee for the year ended on that date",
                        "type": "select",
                        "options": ["Profit", "Loss"],
                        "default": "Profit",
                        "required": True,
                    },
                ],
            },
            {
                "section": "6. Form 3CD Annexure Confirmation",
                "fields": [
                    {
                        "name": "Form 3CD Annexure Statement",
                        "label": "The statement of particulars required to be furnished under section 44AB is annexed herewith in Form No. 3CD.",
                        "type": "readonly",
                        "default": "Confirmed",
                    },
                    {
                        "name": "Form 3CD Observations Qualifications",
                        "label": "Observations / qualifications in Form No. 3CD, if any",
                        "type": "textarea",
                        "default": "",
                        "height": 150,
                        "required": False,
                    },
                ],
            },
            {
                "section": "7. Accountant Details",
                "fields": get_common_accountant_fields(),
            },
            {
                "section": "8. Accountant Address Details",
                "fields": get_common_accountant_address_fields(),
            },
            {
                "section": "9. Signing Details",
                "fields": get_common_signing_fields(),
            },
        ]

    return None