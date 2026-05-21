
# modules/tax_report_template.py

"""
Tax Audit Report Template System for TAAS.

This file contains:
1. Form 3CA structured report fields.
2. Form 3CB structured report fields.
3. Form 3CD clause-wise schema mapping based on Income-tax utility schema keys.
4. Helper functions used by modules/tax_report.py.

Important:
- Form 3CA and Form 3CB report fields remain structured.
- Form 3CD is now implemented as a schema-aware clause system.
- Final utility JSON export can be built on top of the schema_key mapping.
"""


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
        "schema_file": "schema_3CA.json",
        "root": "FORM3CA",
        "inner_root": "F3CA",
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
        "schema_file": "schema_3CB.json",
        "root": "FORM3CB",
        "inner_root": "F3CB",
    },
    "Not Applicable": {
        "code": "NA",
        "title": "Tax Audit Not Applicable",
        "description": "Tax audit report is not applicable.",
        "schema_file": "",
        "root": "",
        "inner_root": "",
    },
}


# ---------------------------------------------------------
# FORM 3CD CLAUSE MASTER - SCHEMA AWARE
# ---------------------------------------------------------
# block type:
# - "object" => single set of fields
# - "table"  => repeating rows / data editor
#
# schema_key:
# Official utility backend key available in schema_3CA/schema_3CB.
#
# fallback_fields:
# Used when schema file is not found or definition extraction fails.
# ---------------------------------------------------------

FORM_3CD_CLAUSES = {
    "1": {
        "title": "Name of the assessee",
        "utility_sheet": "PartA",
        "blocks": [
            {
                "name": "Assessee Name",
                "schema_key": "PartA.AssesseeName",
                "type": "object",
                "fallback_fields": ["FirstName", "MiddleName", "LastName"],
            }
        ],
    },
    "2": {
        "title": "Address of the assessee",
        "utility_sheet": "PartA",
        "blocks": [
            {
                "name": "Address Detail",
                "schema_key": "PartA.AddressDetail",
                "type": "object",
                "fallback_fields": [
                    "AddrDetail1",
                    "AddrDetail2",
                    "CityOrTownOrDistrict",
                    "LocalityOrArea",
                    "PostOffice",
                    "StateCode",
                    "CountryCode",
                    "PinCode",
                ],
            }
        ],
    },
    "3": {
        "title": "Permanent Account Number or Aadhaar Number",
        "utility_sheet": "PartA",
        "blocks": [
            {
                "name": "PAN / Aadhaar",
                "schema_key": "PartA",
                "type": "object",
                "include_fields": ["PAN", "AadhaarCardNo"],
                "fallback_fields": ["PAN", "AadhaarCardNo"],
            }
        ],
    },
    "4": {
        "title": "Whether the assessee is liable to pay indirect tax like excise duty, service tax, sales tax, GST, customs duty, etc.",
        "utility_sheet": "PartA / Form3cdIndirectTax",
        "blocks": [
            {
                "name": "Indirect Tax Applicability",
                "schema_key": "PartA",
                "type": "object",
                "include_fields": ["IndirectTaxFlag"],
                "fallback_fields": ["IndirectTaxFlag"],
            },
            {
                "name": "Indirect Tax Registration Details",
                "schema_key": "Form3cdIndirectTax",
                "type": "table",
                "fallback_fields": ["IndirectTaxType", "StateCode", "OtherIndirectTaxType", "RegNo"],
            },
        ],
    },
    "5": {
        "title": "Status of the assessee",
        "utility_sheet": "PartA",
        "blocks": [
            {
                "name": "Status",
                "schema_key": "PartA",
                "type": "object",
                "include_fields": ["Status"],
                "fallback_fields": ["Status"],
            }
        ],
    },
    "6": {
        "title": "Previous year",
        "utility_sheet": "PartA",
        "blocks": [
            {
                "name": "Previous Year",
                "schema_key": "PartA",
                "type": "object",
                "include_fields": ["PartAStartDate", "PartAEndDate"],
                "fallback_fields": ["PartAStartDate", "PartAEndDate"],
            }
        ],
    },
    "7": {
        "title": "Assessment year",
        "utility_sheet": "PartA",
        "blocks": [
            {
                "name": "Assessment Year",
                "schema_key": "PartA",
                "type": "object",
                "include_fields": ["AssessmentYear"],
                "fallback_fields": ["AssessmentYear"],
            }
        ],
    },
    "8": {
        "title": "Relevant clause of section 44AB under which audit has been conducted",
        "utility_sheet": "PartA",
        "blocks": [
            {
                "name": "Section 44AB Clause",
                "schema_key": "PartA.Clause",
                "type": "table",
                "fallback_fields": ["ClauseNo"],
            },
            {
                "name": "TAAS Applicability Linkage",
                "schema_key": "TAAS_AUDIT_APPLICABILITY",
                "type": "object",
                "fallback_fields": [
                    "Relevant clause of section 44AB",
                    "Reason for applicability",
                    "Whether auto-filled from Tax Audit Applicability module",
                ],
            },
        ],
    },
    "9": {
        "title": "If firm or AOP, indicate names of partners or members and their profit sharing ratios",
        "utility_sheet": "Form3cdFirmAopDetailNew / Form3cdChangeInPartners",
        "blocks": [
            {
                "name": "Current Profit Sharing Ratio",
                "schema_key": "Form3cdFirmAopDetailNew.Form3cdFirmAopDetailPK",
                "type": "table",
                "fallback_fields": ["ChangeType", "FirmAopDesc", "FirmAopPerc"],
            },
            {
                "name": "Change in Partners / Members",
                "schema_key": "Form3cdChangeInPartners",
                "type": "table",
                "fallback_fields": [
                    "DateOfChange",
                    "NameOfPartner",
                    "TypeOfChange",
                    "OldProfShareRatio",
                    "NewProfShareRatio",
                    "Remarks",
                ],
            },
        ],
    },
    "10": {
        "title": "Nature of business or profession and change therein",
        "utility_sheet": "F3cdFirmAopDtlNatOfBusiness / F3cdFirmAopDtlChangeInNature",
        "blocks": [
            {
                "name": "Nature of Business / Profession",
                "schema_key": "F3cdFirmAopDtlNatOfBusiness.Form3cdFirmAopDetailPK",
                "type": "table",
                "fallback_fields": ["ChangeType", "Sector", "FirmAopDesc"],
            },
            {
                "name": "Change in Nature of Business / Profession",
                "schema_key": "F3cdFirmAopDtlChangeInNature.Form3cdFirmAopDetailPK",
                "type": "table",
                "fallback_fields": ["ChangeType", "FirmAopBuss", "Sector", "FirmAopDesc"],
            },
        ],
    },
    "11": {
        "title": "Books of account prescribed, maintained and examined",
        "utility_sheet": "Form3cdBooksOfAccLst / Form3cdBooksOfAccLstAddress",
        "blocks": [
            {
                "name": "Books of Account Maintained / Examined",
                "schema_key": "Form3cdBooksOfAccLst",
                "type": "table",
                "fallback_fields": ["BooksOfAccount", "WhetherExamined", "Remarks"],
            },
            {
                "name": "Address where Books are Kept",
                "schema_key": "Form3cdBooksOfAccLstAddress",
                "type": "table",
                "fallback_fields": ["Address", "Remarks"],
            },
        ],
    },
    "12": {
        "title": "Whether profit and loss account includes profits assessable on presumptive basis",
        "utility_sheet": "Form3cdProfGainsPresum",
        "blocks": [
            {
                "name": "Presumptive Income Details",
                "schema_key": "Form3cdProfGainsPresum",
                "type": "table",
                "fallback_fields": ["Section", "Amount", "Remarks"],
            }
        ],
    },
    "13": {
        "title": "Method of accounting employed and ICDS disclosure",
        "utility_sheet": "Form3cdChngMethAccVal / Form3cdDisclVal",
        "blocks": [
            {
                "name": "Method of Accounting",
                "schema_key": "Form3cdChngMethAccDtl",
                "type": "object",
                "fallback_fields": ["MethodOfAccounting", "Remarks"],
            },
            {
                "name": "Change in Method of Accounting",
                "schema_key": "Form3cdChngMethAccValChange",
                "type": "object",
                "fallback_fields": ["ChangeInMethod", "EffectOnProfit", "Remarks"],
            },
            {
                "name": "ICDS / Accounting Standard Disclosure",
                "schema_key": "Form3cdChngMethAccVal",
                "type": "table",
                "fallback_fields": ["ICDS", "Disclosure", "Amount", "Remarks"],
            },
            {
                "name": "Disclosure of Valuation",
                "schema_key": "Form3cdDisclVal",
                "type": "table",
                "fallback_fields": ["Particulars", "Amount", "Remarks"],
            },
        ],
    },
    "14": {
        "title": "Method of valuation of closing stock",
        "utility_sheet": "MethodValCS",
        "blocks": [
            {
                "name": "Closing Stock Valuation",
                "schema_key": "MethodValCS",
                "type": "object",
                "fallback_fields": [
                    "MethodOfValuation",
                    "DeviationFromPrescribedMethod",
                    "EffectOnProfit",
                    "Remarks",
                ],
            }
        ],
    },
    "15": {
        "title": "Capital asset converted into stock-in-trade",
        "utility_sheet": "Form3cdCapAsstSit",
        "blocks": [
            {
                "name": "Capital Asset Converted into Stock-in-trade",
                "schema_key": "Form3cdCapAsstSit",
                "type": "table",
                "fallback_fields": [
                    "DescriptionOfCapitalAsset",
                    "DateOfAcquisition",
                    "CostOfAcquisition",
                    "AmountAtWhichConverted",
                    "Remarks",
                ],
            }
        ],
    },
    "16": {
        "title": "Amounts not credited to profit and loss account",
        "utility_sheet": "Form3cdAmtNotCredit / Form3cdDrawbackRefundetc",
        "blocks": [
            {
                "name": "Amounts not credited to Profit and Loss Account",
                "schema_key": "Form3cdAmtNotCredit",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Remarks"],
            },
            {
                "name": "Drawback / Refund / Credits",
                "schema_key": "Form3cdDrawbackRefundetc",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Remarks"],
            },
        ],
    },
    "17": {
        "title": "Transfer of land or building or both under section 43CA or 50C",
        "utility_sheet": "Form3cdLandBuildProperty",
        "blocks": [
            {
                "name": "Land / Building Transfer",
                "schema_key": "Form3cdLandBuildProperty",
                "type": "table",
                "fallback_fields": [
                    "DetailsOfProperty",
                    "ConsiderationReceived",
                    "ValueAdoptedOrAssessed",
                    "Remarks",
                ],
            }
        ],
    },
    "18": {
        "title": "Depreciation allowable under the Income-tax Act",
        "utility_sheet": "Form3cdDeprAllw",
        "blocks": [
            {
                "name": "Depreciation Allowable",
                "schema_key": "Form3cdDeprAllw",
                "type": "table",
                "fallback_fields": [
                    "BlockOfAsset",
                    "RateOfDepreciation",
                    "OpeningWDV",
                    "Additions",
                    "Deletions",
                    "DepreciationAllowable",
                    "ClosingWDV",
                    "Remarks",
                ],
            }
        ],
    },
    "19": {
        "title": "Amounts admissible under specified sections",
        "utility_sheet": "Form3cdDebitPlTotAllw",
        "blocks": [
            {
                "name": "Deductions / Allowances Admissible",
                "schema_key": "Form3cdDebitPlTotAllw",
                "type": "table",
                "fallback_fields": ["Section", "AmountDebitedToPL", "AmountAdmissible", "Remarks"],
            }
        ],
    },
    "20": {
        "title": "Bonus / commission and employee contribution to welfare funds",
        "utility_sheet": "Form3cdEmpBonusComm / Form3cdEmpPfSuperann",
        "blocks": [
            {
                "name": "Bonus / Commission to Employees",
                "schema_key": "Form3cdEmpBonusComm",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Remarks"],
            },
            {
                "name": "Employee Contribution to Welfare Funds",
                "schema_key": "Form3cdEmpPfSuperann",
                "type": "table",
                "fallback_fields": [
                    "NatureOfFund",
                    "SumReceivedFromEmployees",
                    "DueDate",
                    "ActualDateOfPayment",
                    "AmountPaid",
                    "Remarks",
                ],
            },
        ],
    },
    "21": {
        "title": "Amounts inadmissible under sections 40, 40A and other disallowances",
        "utility_sheet": "Form3cdDebPLExpnditure / Form3cdAmtInadm40A / related blocks",
        "blocks": [
            {
                "name": "Expenditure Debited to P&L - Disallowance",
                "schema_key": "Form3cdDebPLExpnditure",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Section", "Remarks"],
            },
            {
                "name": "Amount Inadmissible under Section 40(a)",
                "schema_key": "Form3cdAmtInadm40A",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Remarks"],
            },
            {
                "name": "40A Sub-Clause iC",
                "schema_key": "Form3cdAmtInadm40ASubClauseiC",
                "type": "table",
                "fallback_fields": ["Name", "Amount", "Remarks"],
            },
            {
                "name": "40A Sub-Clause iia",
                "schema_key": "Form3cdAmtInadm40ASubClauseiia",
                "type": "table",
                "fallback_fields": ["Name", "Amount", "Remarks"],
            },
            {
                "name": "40A Sub-Clause iib",
                "schema_key": "Form3cdAmtInadm40ASubClauseiib",
                "type": "table",
                "fallback_fields": ["Name", "Amount", "Remarks"],
            },
            {
                "name": "40A Sub-Clause iii",
                "schema_key": "Form3cdAmtInadm40ASubClauseiii",
                "type": "table",
                "fallback_fields": ["Name", "Amount", "Remarks"],
            },
            {
                "name": "40A Sub-Clause iv",
                "schema_key": "Form3cdAmtInadm40ASubClauseiv",
                "type": "table",
                "fallback_fields": ["Name", "Amount", "Remarks"],
            },
            {
                "name": "40A Sub-Clause v",
                "schema_key": "Form3cdAmtInadm40ASubClausev",
                "type": "table",
                "fallback_fields": ["Name", "Amount", "Remarks"],
            },
            {
                "name": "Amount Debited / Other Disallowances",
                "schema_key": "Form3cdAmtInadm40AAmtDebit",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Remarks"],
            },
            {
                "name": "Section 40A(3) Income / Expenditure",
                "schema_key": "Form3cdIncomeUnderSec40A_3",
                "type": "table",
                "fallback_fields": ["Name", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Expenditure under Section 40A(3)",
                "schema_key": "ExpendSec40A_3",
                "type": "table",
                "fallback_fields": ["Name", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Other Expenditure",
                "schema_key": "Form3cdExpOth",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Remarks"],
            },
            {
                "name": "Other Inadmissible Amounts",
                "schema_key": "Form3cdInadm",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Remarks"],
            },
        ],
    },
    "22": {
        "title": "Amount of interest inadmissible under the Micro, Small and Medium Enterprises Development Act",
        "utility_sheet": "Form3cdInadm / MSME",
        "blocks": [
            {
                "name": "MSME Interest Inadmissible",
                "schema_key": "Form3cdInadm",
                "type": "table",
                "fallback_fields": ["MSMEVendorName", "AmountOfInterestInadmissible", "Remarks"],
            }
        ],
    },
    "23": {
        "title": "Payments to persons specified under section 40A(2)(b)",
        "utility_sheet": "Form3cdPymtSec40a2bDetail",
        "blocks": [
            {
                "name": "Related Party Payments",
                "schema_key": "Form3cdPymtSec40a2bDetail",
                "type": "table",
                "fallback_fields": [
                    "NameOfRelatedParty",
                    "Relation",
                    "NatureOfPayment",
                    "Amount",
                    "ReasonablenessCheck",
                    "Remarks",
                ],
            }
        ],
    },
    "24": {
        "title": "Amounts deemed to be profits and gains",
        "utility_sheet": "Form3cdProfGainsTax",
        "blocks": [
            {
                "name": "Deemed Profits and Gains",
                "schema_key": "Form3cdProfGainsTax",
                "type": "table",
                "fallback_fields": ["Section", "Amount", "Remarks"],
            }
        ],
    },
    "25": {
        "title": "Amount of profit chargeable to tax under section 41",
        "utility_sheet": "Form3cdProfGainsTaxSec41",
        "blocks": [
            {
                "name": "Section 41 Profits",
                "schema_key": "Form3cdProfGainsTaxSec41",
                "type": "table",
                "fallback_fields": ["Description", "AmountChargeable", "Remarks"],
            }
        ],
    },
    "26": {
        "title": "Liabilities covered under section 43B",
        "utility_sheet": "Form3cdUnpaidStrySec43b",
        "blocks": [
            {
                "name": "Section 43B Statutory Liabilities",
                "schema_key": "Form3cdUnpaidStrySec43b",
                "type": "table",
                "fallback_fields": [
                    "NatureOfLiability",
                    "Amount",
                    "DueDate",
                    "ActualDateOfPayment",
                    "WhetherPaidBeforeDueDate",
                    "AmountAllowable",
                    "AmountDisallowable",
                    "Remarks",
                ],
            },
            {
                "name": "Section 43B Additional Block 1",
                "schema_key": "Form3cdUnpaidStrySec43b1",
                "type": "table",
                "fallback_fields": ["NatureOfLiability", "Amount", "DueDate", "ActualDateOfPayment", "Remarks"],
            },
            {
                "name": "Section 43B Additional Block 2",
                "schema_key": "Form3cdUnpaidStrySec43b2",
                "type": "table",
                "fallback_fields": ["NatureOfLiability", "Amount", "DueDate", "ActualDateOfPayment", "Remarks"],
            },
            {
                "name": "Section 43B Additional Block 3",
                "schema_key": "Form3cdUnpaidStrySec43b3",
                "type": "table",
                "fallback_fields": ["NatureOfLiability", "Amount", "DueDate", "ActualDateOfPayment", "Remarks"],
            },
        ],
    },
    "27": {
        "title": "CENVAT / GST credits and prior period items",
        "utility_sheet": "Form3cdTaxPassedThrPl / Form3cdModvat / Form3cdIncExpPriorPlAcc",
        "blocks": [
            {
                "name": "Tax Passed through P&L",
                "schema_key": "Form3cdTaxPassedThrPl",
                "type": "object",
                "fallback_fields": ["Amount", "Remarks"],
            },
            {
                "name": "MODVAT / CENVAT / GST Credit",
                "schema_key": "Form3cdModvat",
                "type": "table",
                "fallback_fields": ["Nature", "Opening", "CreditAvailed", "CreditUtilised", "Closing", "Remarks"],
            },
            {
                "name": "Prior Period Income / Expense",
                "schema_key": "Form3cdIncExpPriorPlAcc",
                "type": "table",
                "fallback_fields": ["Nature", "Amount", "Remarks"],
            },
        ],
    },
    "28": {
        "title": "Shares received without consideration or for inadequate consideration under section 56(2)(viia)",
        "utility_sheet": "Form3cdSec562viia",
        "blocks": [
            {
                "name": "Section 56(2)(viia)",
                "schema_key": "Form3cdSec562viia",
                "type": "table",
                "fallback_fields": ["NameOfCompany", "NoOfShares", "FairMarketValue", "ConsiderationPaid", "AmountTaxable", "Remarks"],
            }
        ],
    },
    "29": {
        "title": "Income from issue of shares in excess of fair market value under section 56(2)(viib)",
        "utility_sheet": "Form3cdSec562viib",
        "blocks": [
            {
                "name": "Section 56(2)(viib)",
                "schema_key": "Form3cdSec562viib",
                "type": "table",
                "fallback_fields": ["NatureOfShares", "ConsiderationReceived", "FairMarketValue", "ExcessAmountTaxable", "Remarks"],
            }
        ],
    },
    "29A": {
        "title": "Income chargeable under section 56(2)(ix)",
        "utility_sheet": "Form3cdSec29IncOtherSourcesAb",
        "blocks": [
            {
                "name": "Section 56(2)(ix)",
                "schema_key": "Form3cdSec29IncOtherSourcesAb",
                "type": "table",
                "fallback_fields": ["NatureOfIncome", "AmountChargeable", "Remarks"],
            }
        ],
    },
    "29B": {
        "title": "Income chargeable under section 56(2)(x)",
        "utility_sheet": "Form3cdSec29IncOtherSourcesBb",
        "blocks": [
            {
                "name": "Section 56(2)(x)",
                "schema_key": "Form3cdSec29IncOtherSourcesBb",
                "type": "table",
                "fallback_fields": ["NatureOfReceipt", "AmountOrValueReceived", "AmountChargeable", "Remarks"],
            }
        ],
    },
    "30": {
        "title": "Amount borrowed on hundi or repayment otherwise than through account payee cheque",
        "utility_sheet": "Form3cdSec69d",
        "blocks": [
            {
                "name": "Section 69D Hundi",
                "schema_key": "Form3cdSec69d",
                "type": "table",
                "fallback_fields": ["Name", "AmountBorrowedOrRepaid", "Mode", "Remarks"],
            }
        ],
    },
    "30A": {
        "title": "Primary adjustment to transfer price under section 92CE",
        "utility_sheet": "Form3cdSec92CE",
        "blocks": [
            {
                "name": "Section 92CE",
                "schema_key": "Form3cdSec92CE",
                "type": "table",
                "fallback_fields": ["WhetherPrimaryAdjustmentMade", "AmountOfPrimaryAdjustment", "WhetherRepatriated", "Remarks"],
            }
        ],
    },
    "30B": {
        "title": "Limitation on interest deduction under section 94B",
        "utility_sheet": "Form3cdIncurredExpenditure",
        "blocks": [
            {
                "name": "Section 94B Interest Limitation",
                "schema_key": "Form3cdIncurredExpenditure",
                "type": "table",
                "fallback_fields": ["InterestExpenditure", "EBITDA", "InterestDisallowable", "Remarks"],
            }
        ],
    },
    "30C": {
        "title": "Impermissible avoidance arrangement under GAAR",
        "utility_sheet": "Form3cdImpermissibleSec96",
        "blocks": [
            {
                "name": "Section 96 Impermissible Arrangement",
                "schema_key": "Form3cdImpermissibleSec96",
                "type": "table",
                "fallback_fields": ["NatureOfArrangement", "TaxBenefit", "Remarks"],
            }
        ],
    },
    "31": {
        "title": "Loans, deposits, specified sums and specified advances",
        "utility_sheet": "Form3cdAmtSec269ssDetail / 269SS / 269ST / 269T",
        "blocks": [
            {
                "name": "Section 269SS Amount Details",
                "schema_key": "Form3cdAmtSec269ssDetail",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Section 269SS Party Details",
                "schema_key": "Form3cdSec269SSDtls",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Section 269ST 31ba",
                "schema_key": "Form3cdSec269ST31ba",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Section 269ST 31bb",
                "schema_key": "Form3cdSec269ST31bb",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Section 269ST 31bc",
                "schema_key": "Form3cdSec269ST31bc",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Section 269ST 31bd",
                "schema_key": "Form3cdSec269ST31bd",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Section 269T Amount Details",
                "schema_key": "Form3cdAmtSec269tDetail",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Section 269T Details",
                "schema_key": "Form3cdSec269TDtls",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
            {
                "name": "Section 269T New Details",
                "schema_key": "Form3cdSec269TNewDtls",
                "type": "table",
                "fallback_fields": ["Name", "PAN", "Amount", "Mode", "Remarks"],
            },
        ],
    },
    "32": {
        "title": "Brought forward loss or depreciation allowance",
        "utility_sheet": "Form3cdBflDa / Form3cdSpecloss73 / Form3cdSpec73A / Form3cdSpecdeemdBus73",
        "blocks": [
            {
                "name": "Brought Forward Loss / Depreciation",
                "schema_key": "Form3cdBflDa",
                "type": "table",
                "fallback_fields": ["AssessmentYear", "NatureOfLoss", "AmountAsReturned", "AmountAsAssessed", "Remarks"],
            },
            {
                "name": "Speculative Loss Section 73",
                "schema_key": "Form3cdSpecloss73",
                "type": "object",
                "fallback_fields": ["Amount", "Remarks"],
            },
            {
                "name": "Specified Business Loss Section 73A",
                "schema_key": "Form3cdSpec73A",
                "type": "object",
                "fallback_fields": ["Amount", "Remarks"],
            },
            {
                "name": "Deemed Speculative Business Loss",
                "schema_key": "Form3cdSpecdeemdBus73",
                "type": "object",
                "fallback_fields": ["Amount", "Remarks"],
            },
        ],
    },
    "33": {
        "title": "Deductions admissible under Chapter VIA or Chapter III",
        "utility_sheet": "Form3cdChapVIaChapIII",
        "blocks": [
            {
                "name": "Chapter VIA / Chapter III Deductions",
                "schema_key": "Form3cdChapVIaChapIII",
                "type": "table",
                "fallback_fields": ["Section", "AmountClaimed", "AmountAdmissible", "Remarks"],
            }
        ],
    },
    "34": {
        "title": "TDS / TCS compliance",
        "utility_sheet": "Form3cdChapXVII / Form3cdTaxDedCollect / Form3cdSec2011A206C7",
        "blocks": [
            {
                "name": "Chapter XVII-B / TDS Compliance",
                "schema_key": "Form3cdChapXVII",
                "type": "table",
                "fallback_fields": ["TAN", "NatureOfPayment", "AmountPaidOrCredited", "TaxDeductible", "TaxDeducted", "TaxDeposited", "Remarks"],
            },
            {
                "name": "TDS / TCS Deduction and Collection Details",
                "schema_key": "Form3cdTaxDedCollect",
                "type": "table",
                "fallback_fields": ["TAN", "Section", "Amount", "TaxDeductedOrCollected", "TaxDeposited", "Remarks"],
            },
            {
                "name": "Interest under Section 201(1A) / 206C(7)",
                "schema_key": "Form3cdSec2011A206C7",
                "type": "table",
                "fallback_fields": ["TAN", "AmountOfInterest", "DateOfPayment", "Remarks"],
            },
        ],
    },
    "35": {
        "title": "Trading concern / manufacturing concern quantitative details",
        "utility_sheet": "Form3cdTradeRawProdDet",
        "blocks": [
            {
                "name": "Quantitative Details",
                "schema_key": "Form3cdTradeRawProdDet",
                "type": "table",
                "fallback_fields": ["ItemName", "Unit", "OpeningStock", "PurchasesOrProduction", "SalesOrConsumption", "ClosingStock", "ShortageOrExcess", "Remarks"],
            }
        ],
    },
    "36": {
        "title": "Dividend / deemed dividend reporting",
        "utility_sheet": "Form3cdDistribtedProf115O / Form3cdNatureOfDividend",
        "blocks": [
            {
                "name": "Distributed Profits / Dividend",
                "schema_key": "Form3cdDistribtedProf115O",
                "type": "table",
                "fallback_fields": ["Amount", "Date", "Remarks"],
            },
            {
                "name": "Nature of Dividend",
                "schema_key": "Form3cdNatureOfDividend",
                "type": "table",
                "fallback_fields": ["NatureOfDividend", "Amount", "Remarks"],
            },
        ],
    },
    "36A": {
        "title": "Deemed income under section 2(24)(xviii)",
        "utility_sheet": "Form3cd36BRecievedAmt",
        "blocks": [
            {
                "name": "Amounts Received",
                "schema_key": "Form3cd36BRecievedAmt",
                "type": "table",
                "fallback_fields": ["NatureOfReceipt", "Amount", "Remarks"],
            }
        ],
    },
    "37": {
        "title": "Cost audit details",
        "utility_sheet": "CostAudit",
        "blocks": [
            {
                "name": "Cost Audit",
                "schema_key": "CostAudit",
                "type": "object",
                "fallback_fields": ["WhetherCostAuditCarriedOut", "DetailsOfDisqualificationOrDisagreement", "Remarks"],
            }
        ],
    },
    "38": {
        "title": "Audit under Central Excise Act",
        "utility_sheet": "AuditExcise",
        "blocks": [
            {
                "name": "Excise Audit",
                "schema_key": "AuditExcise",
                "type": "object",
                "fallback_fields": ["WhetherAuditConducted", "DetailsOfDisqualificationOrDisagreement", "Remarks"],
            }
        ],
    },
    "39": {
        "title": "Audit under section 72A of the Finance Act relating to valuation of taxable services",
        "utility_sheet": "AuditSec72",
        "blocks": [
            {
                "name": "Audit under Section 72A",
                "schema_key": "AuditSec72",
                "type": "object",
                "fallback_fields": ["WhetherAuditConducted", "DetailsOfDisqualificationOrDisagreement", "Remarks"],
            }
        ],
    },
    "40": {
        "title": "Accounting ratios",
        "utility_sheet": "Form3cdAccountingRatioCalculations",
        "blocks": [
            {
                "name": "Accounting Ratio Calculations",
                "schema_key": "Form3cdAccountingRatioCalculations",
                "type": "object",
                "fallback_fields": ["GrossProfitRatio", "NetProfitRatio", "StockTurnoverRatio", "MaterialConsumedRatio", "Remarks"],
            }
        ],
    },
    "41": {
        "title": "Demand raised or refund issued under any tax laws other than Income-tax Act and Wealth-tax Act",
        "utility_sheet": "Form3cdRefundDmdPrevYr",
        "blocks": [
            {
                "name": "Demand / Refund Details",
                "schema_key": "Form3cdRefundDmdPrevYr",
                "type": "table",
                "fallback_fields": ["NameOfTaxLaw", "DemandOrRefundOrderDetails", "Amount", "Remarks"],
            }
        ],
    },
    "42": {
        "title": "Form 61, Form 61A and Form 61B reporting",
        "utility_sheet": "Form3cdFurnishStatemnt",
        "blocks": [
            {
                "name": "Statement Furnishing Details",
                "schema_key": "Form3cdFurnishStatemnt",
                "type": "table",
                "fallback_fields": ["FormType", "DueDate", "DateOfFurnishing", "Remarks"],
            }
        ],
    },
    "43": {
        "title": "Country-by-country reporting under section 286",
        "utility_sheet": "Form3cdFurnishAltReportSec286 / ExpectedDate",
        "blocks": [
            {
                "name": "Section 286 Reporting",
                "schema_key": "Form3cdFurnishAltReportSec286",
                "type": "object",
                "fallback_fields": ["WhetherSection286Applicable", "ParentEntityDetails", "AlternateReportingEntityDetails", "Remarks"],
            },
            {
                "name": "Expected Date",
                "schema_key": "ExpectedDate",
                "type": "object",
                "fallback_fields": ["ExpectedDate", "Remarks"],
            },
        ],
    },
    "44": {
        "title": "Break-up of total expenditure of entities registered or not registered under GST",
        "utility_sheet": "Form3cdBreakUpGST",
        "blocks": [
            {
                "name": "GST Expenditure Break-up",
                "schema_key": "Form3cdBreakUpGST",
                "type": "table",
                "fallback_fields": [
                    "TotalAmountOfExpenditure",
                    "ExpenditureRelatingToGSTRegisteredEntities",
                    "ExpenditureRelatingToGSTUnregisteredEntities",
                    "ExemptGoodsOrServices",
                    "CompositionSchemeEntities",
                    "OtherRegisteredEntities",
                    "Remarks",
                ],
            }
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
    return FORM_3CD_CLAUSES.get(str(clause_no), {}).get("utility_sheet", "")


def get_clause_fields(clause_no):
    """
    Backward-compatible function.
    Returns combined fallback fields for old rendering/export logic.
    """
    clause = FORM_3CD_CLAUSES.get(str(clause_no), {})
    fields = []

    for block in clause.get("blocks", []):
        for field in block.get("fallback_fields", []):
            if field not in fields:
                fields.append(field)

    return fields


def get_clause_schema_blocks(clause_no):
    return FORM_3CD_CLAUSES.get(str(clause_no), {}).get("blocks", [])


def get_tax_audit_form_title(audit_form):
    return TAX_AUDIT_FORMS.get(audit_form, TAX_AUDIT_FORMS["Not Applicable"]).get("title", "")


def get_tax_audit_form_description(audit_form):
    return TAX_AUDIT_FORMS.get(audit_form, TAX_AUDIT_FORMS["Not Applicable"]).get("description", "")


def get_tax_audit_form_code(audit_form):
    return TAX_AUDIT_FORMS.get(audit_form, TAX_AUDIT_FORMS["Not Applicable"]).get("code", "")


def get_tax_audit_schema_file_name(audit_form):
    return TAX_AUDIT_FORMS.get(audit_form, TAX_AUDIT_FORMS["Not Applicable"]).get("schema_file", "")


def get_tax_audit_root_keys(audit_form):
    form = TAX_AUDIT_FORMS.get(audit_form, TAX_AUDIT_FORMS["Not Applicable"])
    return form.get("root", ""), form.get("inner_root", "")


def is_valid_tax_audit_form(audit_form):
    return audit_form in ["Form 3CA-3CD", "Form 3CB-3CD"]


# ---------------------------------------------------------
# FALLBACK SIMPLE REPORT FIELDS
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
# COMMON STRUCTURED FIELDS FOR 3CA / 3CB
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
