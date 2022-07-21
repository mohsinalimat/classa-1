from __future__ import unicode_literals
import frappe
from frappe import _
import erpnext
from frappe import auth
import datetime
import json, ast
from erpnext.accounts.utils import get_balance_on
from erpnext.stock.doctype.repost_item_valuation.repost_item_valuation import repost_entries
frappe.whitelist()
def hourly():
    #erpnext.stock.doctype.repost_item_valuation.repost_item_valuation.repost_entries
    frappe.db.sql("""
        update `tabSales Invoice` join `tabCustomer` on `tabSales Invoice`.customer = `tabCustomer`.name
        set `tabSales Invoice`.customer_group = `tabCustomer`.customer_group
    """)
    frappe.db.sql("""
        update `tabSales Invoice` join `tabCustomer` on `tabSales Invoice`.customer = `tabCustomer`.name
        set `tabSales Invoice`.territory = `tabCustomer`.territory
    """)
    frappe.db.sql("""
        update `tabSales Invoice` join `tabCustomer Group` on `tabSales Invoice`.customer_group = `tabCustomer Group`.name
        set `tabSales Invoice`.cost_center = `tabCustomer Group`.cost_center
    """)
    frappe.db.sql("""
        update `tabSales Invoice Item` join `tabSales Invoice` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent
        set `tabSales Invoice Item`.cost_center = `tabSales Invoice`.cost_center
    """)
    frappe.db.sql("""
        update `tabSales Invoice Item` join `tabSales Invoice` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent
        set `tabSales Invoice Item`.territory = `tabSales Invoice`.territory
    """)
    frappe.db.sql("""
        update `tabSales Invoice` join `tabSales Person` on `tabSales Invoice`.sales_person = `tabSales Person`.name 
        join `tabEmployee` on `tabSales Person`.employee = `tabEmployee`.name
        set `tabSales Invoice`.branch = `tabEmployee`.branch
    """)
    frappe.db.sql("""
        update `tabSales Invoice Item` join `tabSales Invoice` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent
        set `tabSales Invoice Item`.branch = `tabSales Invoice`.branch
    """)
    frappe.db.sql("""
    update `tabGL Entry` join `tabJournal Entry` on `tabGL Entry`.voucher_no = `tabJournal Entry`.name join `tabJournal Entry Account` on `tabJournal Entry`.name = `tabJournal Entry Account`.parent set `tabGL Entry`.description = `tabJournal Entry Account`.description
    """)
