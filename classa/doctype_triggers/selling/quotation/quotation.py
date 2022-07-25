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
    doc.ignore_pricing_rule = doc.ignore_pricing_rule_2

    for t in doc.items:
        #item_price_hold = frappe.db.get_value('Item Price', {'item_code': t.item_code,'price_list':doc.price_list}, ['hold'])
        #if item_price_hold == 1 :
        #    frappe.throw("الصنف {0} غير مفعل في قائمة اسعار العميل  ".format(t.item_code,t.idx))

        allowed_uom = frappe.db.get_value('UOM Conversion Detail', {'parent': t.item_code, 'uom': t.uom}, ['uom'])
        if allowed_uom != t.uom:
            frappe.throw("Row #" + str(t.idx) + ": وحدة القياس غير معرفة للصنف " + t.item_code)

    ## Make Customer Address 2 Field Mandatory If Customer Group Is Chain
    parent_group = frappe.db.get_value("Customer Group", doc.customer_group, "parent_customer_group")
    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل") and not doc.customer_address_2:
        frappe.throw("Please Select The Customer's Address")
    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل"):
        doc.customer_address = doc.customer_address_2
    if (doc.customer_group == "مجموعة التجزئة" or parent_group == "مجموعة التجزئة"):
        doc.customer_address_2 = doc.customer_address

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    doc.cost_center = frappe.db.get_value("Customer Group", doc.customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center

    ## Fetch Price List Rate In Items Table
    for x in doc.items:
        x.price_list_rate = frappe.db.get_value("Item Price",
                                                {'price_list': doc.selling_price_list, 'item_code': x.item_code},
                                                "price_list_rate")

    ## Fetch Tax Type From Customer
    default_tax_type = frappe.db.get_value("Customer", doc.party_name, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    ## Calculate Item Rate If Customer Tax Type Is Commercial
    if doc.tax_type == "Commercial":
        doc.set("taxes", [])

    if doc.tax_type == "Commercial" and doc.edit_rate == 0:
        for d in doc.items:
            if not d.margin_type:
                d.discount_percentage = 0
            if d.item_tax_template:
                item_tax_rate = float(
                    frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template}, "tax_rate"))
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

    ## Calculate Taxes Table If Customer Tax Type Is Taxable
    if doc.tax_type == "Taxable":
        doc.set("taxes", [])
        new_taxes = 0
        for d in doc.items:
            if d.item_tax_template:
                item_tax_rate = frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template},
                                                    "tax_rate")
                d.tax_amount = d.net_amount * item_tax_rate / 100
                new_taxes += d.tax_amount

        taxes1 = doc.append("taxes", {})
        taxes1.charge_type = "On Net Total"
        taxes1.account_head = "2301 - ضريبة القيمة المضافة VAT - CA"
        taxes1.description = "2301 - ضريبة القيمة المضافة VAT"
        '''
        taxes1.rate = 0
        taxes1.account_currency = "EGP"
        taxes1.tax_amount = new_taxes
        taxes1.total = doc.total + new_taxes
        taxes1.base_tax_amount = new_taxes
        taxes1.base_total = doc.total + new_taxes
        taxes1.tax_amount_after_discount_amount = new_taxes
        taxes1.base_tax_amount_after_discount_amount = new_taxes
        taxes1.vehicle = doc.vehicle
        taxes1.territory = doc.territory
        taxes1.branch = doc.branch
        taxes1.department = doc.department
        taxes1.cost_center = doc.cost_center
        '''

@frappe.whitelist()
def validate(doc, method=None):
    for t in doc.items:
        item_price_hold = frappe.db.get_value("Item Price", {'item_code': t.item_code,'price_list': doc.selling_price_list}, "hold")
        if item_price_hold ==1 :
            frappe.throw("تم ايقاف التعامل على السعر الخاص بالمنتج {0} في الصف {1}".format(t.item_code,t.idx))
    for d in doc.items:
        x = d.price_list_rate + (d.price_list_rate * 0.01)
        y = d.rate + (d.rate * 0.01)
        if (d.rate > x or d.price_list_rate > y):
            frappe.msgprint("Row #" + str(d.idx) + ": Check Price List For Item Code " + d.item_code)

        if not d.price_list_rate:
            frappe.msgprint("Row #" + str(
                d.idx) + ": Item Code " + d.item_code + " Is Not Listed For Customer " + doc.customer_name)

@frappe.whitelist()
def on_submit(doc, method=None):
    for d in doc.items:
        x = d.price_list_rate + (d.price_list_rate * 0.01)
        y = d.rate + (d.rate * 0.01)
        if (d.rate > x or d.price_list_rate > y) and not doc.allow_price:
            frappe.msgprint("Row #" + str(d.idx) + ": Check Price List For Item Code " + d.item_code)

        if not d.price_list_rate:
            frappe.msgprint("Row #" + str(
                d.idx) + ": Item Code " + d.item_code + " Is Not Listed For Customer " + doc.customer_name)

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
