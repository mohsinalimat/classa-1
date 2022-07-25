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
    ## Fetch Vehicle From Vehicle Log
    doc.vehicle = frappe.db.get_value("Vehicle Log", doc.vehicle_log, "license_plate")

    ## Fetch Cost Center From Department
    # doc.cost_center = frappe.db.get_value("Department", doc.department, "payroll_cost_center")

    ## Fetch Accounting Dimensions In Expenses Table
    for x in doc.expenses:
        x.vehicle = doc.vehicle
        x.territory = doc.territory
        x.branch = doc.branch
        x.department = doc.department

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.vehicle = doc.vehicle
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department

@frappe.whitelist()
def validate(doc, method=None):
    pass
@frappe.whitelist()
def on_submit(doc, method=None):
    if doc.workflow_state == "Accounts Manager Approved" and doc.grand_total == 0:
        frappe.throw(" من فضلك اعتمد المبلغ ")

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
