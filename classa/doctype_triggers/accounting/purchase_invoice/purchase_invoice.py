from __future__ import unicode_literals
import frappe
from frappe import auth
import datetime
from frappe.utils import getdate
import json, ast, requests
from six import iteritems, string_types
from frappe.utils import money_in_words
import urllib.request


@frappe.whitelist()
def before_insert(doc, method=None):
    pass
@frappe.whitelist()
def after_insert(doc, method=None):
    pass
@frappe.whitelist()
def onload(doc, method=None):
    pass
@frappe.whitelist()
def before_validate(doc, method=None):
    '''
    ## Calculate Item Rate If Supplier Tax Type Is Taxable
    if doc.tax_type == "Commercial":
        doc.set("taxes", [])
        for d in doc.items:
            if d.item_tax_template:
                item_tax_rate = frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template},
                                                    "tax_rate")
                if item_tax_rate > 0 and d.rate <= d.price_list_rate:
                    new_rate = d.rate + (item_tax_rate * d.rate / 100)
                    d.rate = new_rate

                else:
                    pass
            else:
                pass
    '''

    ##fetch_tax_type_from_Supplier
    default_tax_type = frappe.db.get_value("Supplier", doc.supplier, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    ## Calculate Item Rate If Supplier Tax Type Is Commercial
    if doc.tax_type == "Commercial" and doc.purchase_request_type != "Imported":
        doc.set("taxes", [])
        for d in doc.items:
            if d.item_tax_template:
                item_tax_rate = float(
                    frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template},
                                        "tax_rate"))
                if item_tax_rate > 0:
                    if d.discount_percentage:
                        new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                        new_discounted_rate = new_rate - ((d.discount_percentage * new_rate) / 100)
                        d.rate = new_discounted_rate
                        d.net_rate = new_discounted_rate
                        d.base_net_rate = new_discounted_rate
                        d.base_rate = new_discounted_rate
                        d.net_amount = new_discounted_rate * d.qty
                        d.base_net_amount = new_discounted_rate * d.qty
                        d.amount = new_discounted_rate * d.qty
                        d.base_amount = new_discounted_rate * d.qty
                        d.tax_rate = new_rate
                        d.discounted_amount = new_rate * d.discount_percentage / 100
                    else:
                        new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                        d.rate = new_rate
                        d.base_rate = new_rate
                        d.amount = new_rate * d.qty
                        d.base_amount = new_rate * d.qty
                        d.tax_rate = new_rate
                else:
                    new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                    d.tax_rate = new_rate
        totals = 0
        for x in doc.items:
            totals += x.amount
        if doc.additional_discount_percentage:
            doc.total = totals
            doc.grand_total = totals - doc.discount_amount
            doc.base_grand_total = totals - doc.discount_amount
            doc.net_total = totals - doc.discount_amount
            doc.base_net_total = totals - doc.discount_amount
            doc.base_total = totals - doc.discount_amount
            doc.outstanding_amount = totals - doc.discount_amount
            doc.total_taxes_and_charges = 0

        else:
            doc.total = totals
            doc.grand_total = totals
            doc.base_grand_total = totals
            doc.net_total = totals
            doc.base_net_total = totals
            doc.base_total = totals
            doc.outstanding_amount = totals
            doc.total_taxes_and_charges = 0

    ## Remove Taxes Table
    for d in doc.taxes:
        account_type = frappe.db.get_value("Account", d.account_head, "account_type")
        if doc.tax_type == "Taxable" and doc.purchase_request_type == "Imported" and account_type == "Tax":
            doc.set("taxes", [])

    ## Calculate Taxes Table
    if doc.tax_type == "Taxable" and (
            doc.purchase_request_type == "Local" or doc.purchase_request_type == "Spare Parts"):
        doc.set("taxes", [])
        new_taxes = 0
        for d in doc.items:
            if d.item_tax_template:
                item_tax_rate = frappe.db.get_value("Item Tax Template Detail",
                                                    {'parent': d.item_tax_template},
                                                    "tax_rate")
                d.tax_amount = d.net_amount * item_tax_rate / 100
                new_taxes += d.tax_amount

        taxes1 = doc.append("taxes", {})
        taxes1.category = "Total"
        taxes1.add_deduct_tax = "Add"
        taxes1.charge_type = "On Net Total"
        taxes1.account_head = "2301 - ضريبة القيمة المضافة VAT - CA"
        taxes1.description = "2301 - ضريبة القيمة المضافة VAT"

        if doc.ci_profits == "1%":
            taxes2 = doc.append("taxes", {})
            taxes2.category = "Total"
            taxes2.add_deduct_tax = "Deduct"
            taxes2.charge_type = "On Net Total"
            taxes2.rate = 1
            taxes2.account_head = "2302 - ارباح تجارية وصناعية - موردين - CA"
            taxes2.description = "2302 - ارباح تجارية وصناعية - موردين"

        if doc.ci_profits == "3%":
            taxes2 = doc.append("taxes", {})
            taxes2.category = "Total"
            taxes2.add_deduct_tax = "Deduct"
            taxes2.charge_type = "On Net Total"
            taxes2.rate = 3
            taxes2.account_head = "2302 - ارباح تجارية وصناعية - موردين - CA"
            taxes2.description = "2302 - ارباح تجارية وصناعية - موردين"

        if doc.ci_profits == "5%":
            taxes2 = doc.append("taxes", {})
            taxes2.category = "Total"
            taxes2.add_deduct_tax = "Deduct"
            taxes2.charge_type = "On Net Total"
            taxes2.rate = 5
            taxes2.account_head = "2302 - ارباح تجارية وصناعية - موردين - CA"
            taxes2.description = "2302 - ارباح تجارية وصناعية - موردين"

    ## Fetch Cost Center From Supplier Group
    supplier_group = frappe.db.get_value("Supplier", doc.supplier, "supplier_group")
    doc.cost_center = frappe.db.get_value("Supplier Group", supplier_group, "cost_center")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Accounting Dimensions In Items Table
    for y in doc.items:
        y.department = doc.department
        y.cost_center = doc.cost_center


@frappe.whitelist()
def validate(doc, method=None):
    ##fetch_tax_type_from_Supplier
    default_tax_type = frappe.db.get_value("Supplier", doc.supplier, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass

@frappe.whitelist()
def on_submit(doc, method=None):
    ## Calculate Item Rate If Supplier Tax Type Is Commercial
    if doc.tax_type == "Commercial":
        doc.set("taxes", [])
        for d in doc.items:
            if d.item_tax_template:
                item_tax_rate = float(
                    frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template},
                                        "tax_rate"))
                if item_tax_rate > 0:
                    if d.discount_percentage:
                        new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                        new_discounted_rate = new_rate - ((d.discount_percentage * new_rate) / 100)
                        d.rate = new_discounted_rate
                        d.net_rate = new_discounted_rate
                        d.base_net_rate = new_discounted_rate
                        d.base_rate = new_discounted_rate
                        d.net_amount = new_discounted_rate * d.qty
                        d.base_net_amount = new_discounted_rate * d.qty
                        d.amount = new_discounted_rate * d.qty
                        d.base_amount = new_discounted_rate * d.qty
                        d.tax_rate = new_rate
                        d.discounted_amount = new_rate * d.discount_percentage / 100
                    else:
                        new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                        d.rate = new_rate
                        d.base_rate = new_rate
                        d.amount = new_rate * d.qty
                        d.base_amount = new_rate * d.qty
                        d.tax_rate = new_rate
                else:
                    new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                    d.tax_rate = new_rate
        totals = 0
        for x in doc.items:
            totals += x.amount
        if doc.additional_discount_percentage:
            doc.total = totals
            doc.grand_total = totals - doc.discount_amount
            doc.base_grand_total = totals - doc.discount_amount
            doc.net_total = totals - doc.discount_amount
            doc.base_net_total = totals - doc.discount_amount
            doc.base_total = totals - doc.discount_amount
            doc.outstanding_amount = totals - doc.discount_amount
            doc.total_taxes_and_charges = 0

        else:
            doc.total = totals
            doc.grand_total = totals
            doc.base_grand_total = totals
            doc.net_total = totals
            doc.base_net_total = totals
            doc.base_total = totals
            doc.outstanding_amount = totals
            doc.total_taxes_and_charges = 0

@frappe.whitelist()
def on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def before_save(doc, method=None):
    pass
@frappe.whitelist()
def before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def on_update(doc, method=None):
    pass
