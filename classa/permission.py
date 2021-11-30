from __future__ import unicode_literals
import frappe
import erpnext
from frappe import auth
import datetime
import json, ast
from frappe.share import add

@frappe.whitelist()
def share_mr(doc, method=None):
    if doc.set_from_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.set_from_warehouse),as_dict=1)
        read = 1
        write = 1
        share = 1
        everyone = 0
        for x in users:
            add('Material Request', doc.name, x.user, read, write, share, everyone)

    if doc.set_warehouse:
        users = frappe.db.sql(
            """ select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(
                from_warehouse=doc.set_warehouse), as_dict=1)
        read = 1
        write = 1
        share = 1
        everyone = 0
        for x in users:
            add('Material Request', doc.name, x.user, read, write, share, everyone)

@frappe.whitelist()
def share_se(doc, method=None):
    if doc.from_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.from_warehouse),as_dict=1)
        read = 1
        write = 1
        share = 1
        everyone = 0
        for x in users:
            add('Stock Entry', doc.name, x.user, read, write, share, everyone)

    if doc.to_warehouse:
        users = frappe.db.sql(
            """ select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(
                from_warehouse=doc.to_warehouse), as_dict=1)
        read = 1
        write = 1
        share = 1
        everyone = 0
        for x in users:
            add('Stock Entry', doc.name, x.user, read, write, share, everyone)

@frappe.whitelist()
def share_dn(doc, method=None):
    if doc.set_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.set_warehouse),as_dict=1)
        read = 1
        write = 1
        share = 1
        everyone = 0
        for x in users:
            add('Delivery Note', doc.name, x.user, read, write, share, everyone)

@frappe.whitelist()
def share_so(doc, method=None):
    if doc.set_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.set_warehouse),as_dict=1)
        read = 1
        write = 1
        share = 1
        everyone = 0
        for x in users:
            add('Sales Order', doc.name, x.user, read, write, share, everyone)

@frappe.whitelist()
def share_po(doc, method=None):
    if doc.set_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.set_warehouse),as_dict=1)
        read = 1
        write = 1
        share = 1
        everyone = 0
        for x in users:
            add('Purchase Order', doc.name, x.user, read, write, share, everyone)

@frappe.whitelist()
def share_pr(doc, method=None):
    if doc.set_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.set_warehouse),as_dict=1)
        read = 1
        write = 1
        share = 1
        everyone = 0
        for x in users:
            add('Purchase Receipt', doc.name, x.user, read, write, share, everyone)


@frappe.whitelist()
def share_pe(doc, method=None):
    users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Account' and share_name = '{paid_to}' """.format(paid_to=doc.paid_to),as_dict=1)
    read = 1
    write = 1
    share = 1
    everyone = 0
    if users:
        for x in users:
            add('Payment Entry', doc.name, x.user, read, write, share, everyone)