from __future__ import unicode_literals
from frappe import _
import frappe
import erpnext
from frappe import auth
import datetime
import json, ast
from erpnext.accounts.utils import get_balance_on
from erpnext.stock.doctype.repost_item_valuation.repost_item_valuation import repost_entries

frappe.whitelist()
def all():
    repost_entries()
    repost_entries()
    repost_entries()
    repost_entries()
    repost_entries()
    frappe.db.sql(""" update `tabSingles` set value = '0' where doctype = 'Stock Settings' and field = 'allow_negative_stock' """)
