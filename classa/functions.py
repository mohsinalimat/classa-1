from __future__ import unicode_literals
import frappe
import erpnext
from frappe import auth
import datetime
import json, ast
from erpnext.accounts.utils import get_balance_on

@frappe.whitelist()
def sales_order_validate(doc, method=None):
    for d in doc.items:
        if not d.rate == d.price_list_rate and not doc.allow_price:
            frappe.throw("Row #" + d.idx + ": Check Price List For Item " + d.item_code)

@frappe.whitelist()
def quotation_validate(doc, method=None):
    for d in doc.items:
        if not d.rate == d.price_list_rate:
            frappe.msgprint("Row #" + d.idx + ": Check Price List For Item " + d.item_code)

        if not d.price_list_rate:
            frappe.throw("Row #" + d.idx + ": Item " + d.item_code + " Is Not Listed For The Current Customer")

@frappe.whitelist()
def quotation_submit(doc, method=None):
    for d in doc.items:
        if not d.rate == d.price_list_rate and not doc.allow_price:
            frappe.throw("Row #" + d.idx + ": Check Price List For Item " + d.item_code)
