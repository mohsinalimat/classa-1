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
    pass
@frappe.whitelist()
def validate(doc, method=None):
    pass
@frappe.whitelist()
def on_submit(doc, method=None):
    if doc.loan_type == "مشتريات" or doc.loan_type == "عجز مناديب":
        dis = frappe.new_doc('Loan Disbursement')
        dis.against_loan = doc.name
        dis.applicant_type = "Employee"
        dis.company = doc.company
        dis.applicant = doc.applicant
        dis.disbursed_amount = doc.loan_amount
        dis.insert(ignore_permissions=True)
        dis.submit()
    else:
        dis = frappe.new_doc('Loan Disbursement')
        dis.against_loan = doc.name
        dis.applicant_type = "Employee"
        dis.company = doc.company
        dis.applicant = doc.applicant
        dis.disbursed_amount = doc.loan_amount
        dis.insert(ignore_permissions=True)


@frappe.whitelist()
def on_cancel(doc, method=None):
    # ld =  frappe.db.get_value('Loan Disbursement', {'against_loan': doc.name}, ['name'])
    # ld1 = frappe.get_doc('Loan Disbursement',ld)
    # ld1.cancel()
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
