# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt


def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters, columns)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Voucher No"),
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 150
        },
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 110
        },
        {
            "label": _("Payment Type"),
            "fieldname": "payment_type",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Mode Of Payment"),
            "fieldname": "mode_of_payment",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("To Mode Of Payment"),
            "fieldname": "mode_of_payment_2",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("Party Type"),
            "fieldname": "party_type",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": _("Party"),
            "fieldname": "party",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Debit"),
            "fieldname": "debit",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Credit"),
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 120
        }
    ]


def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " and `tabGL Entry`.posting_date>=%(from_date)s"
    if filters.get("to_date"):
        conditions += " and `tabGL Entry`.posting_date<=%(to_date)s"
    a = "(Select `tabPayment Entry`.mode_of_payment from `tabPayment Entry` where `tabPayment Entry`.name = `tabGL Entry`.voucher_no)"
    b = "(Select `tabLoan`.mode_of_payment from `tabLoan` join `tabLoan Disbursement` on `tabLoan`.name = `tabLoan Disbursement`.against_loan where `tabLoan Disbursement`.name = `tabGL Entry`.voucher_no)"
    c = "(Select `tabPayment Entry`.party_name from `tabPayment Entry` where `tabPayment Entry`.name = `tabGL Entry`.voucher_no)"
    d = "(Select `tabLoan`.applicant_name from `tabLoan` join `tabLoan Disbursement` on `tabLoan`.name = `tabLoan Disbursement`.against_loan where `tabLoan Disbursement`.name = `tabGL Entry`.voucher_no)"

    item_results = frappe.db.sql("""
        SELECT 
            `tabGL Entry`.voucher_type as voucher_type,
            `tabGL Entry`.voucher_no as voucher_no,
            `tabGL Entry`.posting_date as posting_date,
            (Select `tabPayment Entry`.payment_type from `tabPayment Entry` where `tabPayment Entry`.name = `tabGL Entry`.voucher_no) as payment_type,            
            IF(`tabGL Entry`.voucher_type = "Payment Entry", {a} , {b}) as mode_of_payment,            
            (Select `tabPayment Entry`.mode_of_payment_2 from `tabPayment Entry` where `tabPayment Entry`.name = `tabGL Entry`.voucher_no) as mode_of_payment_2,
            `tabGL Entry`.party_type as party_type,
            IF(`tabGL Entry`.voucher_type = "Payment Entry", {c} , {d}) as party,
            `tabGL Entry`.debit as debit,
            `tabGL Entry`.credit as credit
       
        FROM
            `tabGL Entry`
        WHERE
            `tabGL Entry`.voucher_type in ("Payment Entry", "Loan Disbursement") 
            and `tabGL Entry`.is_cancelled = 0
            {conditions}
        """.format(conditions=conditions, a=a, b=b, c=c, d=d), filters, as_dict=1)

    result = []
    if item_results:
        for item_dict in item_results:
            data = {
                'voucher_type': item_dict.voucher_type,
                'voucher_no': item_dict.voucher_no,
                'posting_date': item_dict.posting_date,
                'party_type': item_dict.party_type,
                'party': item_dict.party,
                'debit': item_dict.debit,
                'credit': item_dict.credit,
                'payment_type': item_dict.payment_type,
                'mode_of_payment': item_dict.mode_of_payment,
                'mode_of_payment_2': item_dict.mode_of_payment_2,
            }

            result.append(data)

    return result
