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
            frappe.throw("Row #"+str(d.idx)+": Check Price List For Item Code " + d.item_code)

@frappe.whitelist()
def quotation_validate(doc, method=None):
    '''
    for d in doc.items:
        if not d.rate == d.price_list_rate:
            frappe.msgprint("Row #"+str(d.idx)+": Check Price List For Item Code " + d.item_code)

        if not d.price_list_rate:
            frappe.throw("Row #"+str(d.idx)+": Item Code " + d.item_code + " Is Not Listed For Customer " + doc.customer_name)
    '''


@frappe.whitelist()
def quotation_submit(doc, method=None):
    '''
    for d in doc.items:
        if not d.rate == d.price_list_rate and not doc.allow_price:
            frappe.throw("Row #"+str(d.idx)+": Check Price List For Item Code " + d.item_code)
'''


@frappe.whitelist()
def fetch_tax_type_from_customer(doc, method=None):
    default_tax_type = frappe.db.get_value("Customer", doc.customer, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass

@frappe.whitelist()
def fetch_tax_type_from_supplier(doc, method=None):
    default_tax_type = frappe.db.get_value("Supplier", doc.supplier, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass

@frappe.whitelist()
def validate_payment_entry(doc, method=None):
    customer_tax_type = frappe.db.get_value("Customer", doc.customer, "tax_type")
    supplier_tax_type = frappe.db.get_value("Supplier", doc.supplier, "tax_type")
    if not doc.tax_type and doc.party_type == "Customer":
        doc.tax_type = customer_tax_type

    if not doc.tax_type and doc.party_type == "Supplier":
        doc.tax_type = supplier_tax_type

    else:
        pass

