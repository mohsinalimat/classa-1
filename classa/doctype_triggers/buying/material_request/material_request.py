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
#def share_mr(doc, method=None):permission
    pass
    '''
    if doc.set_from_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.set_from_warehouse),as_dict=1)
        read = 1
        write = 1
        submit = 1
        share = 1
        everyone = 0
        for x in users:
            add('Material Request', doc.name, x.user, read, write, submit, share, everyone)

    if doc.set_warehouse:
        users = frappe.db.sql(
        """ select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(
                from_warehouse=doc.set_warehouse), as_dict=1)
        read = 1
        write = 1
        submit = 1
        share = 1
        everyone = 0
        for x in users:
            add('Material Request', doc.name, x.user, read, write, submit, share, everyone)
    '''
@frappe.whitelist()
def onload(doc, method=None):
    pass
@frappe.whitelist()
def before_validate(doc, method=None):
    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.items:
        y.from_warehouse = doc.set_from_warehouse
        y.warehouse = doc.set_warehouse


@frappe.whitelist()
def validate(doc, method=None):
    pass
@frappe.whitelist()
def on_submit(doc, method=None):
    user = frappe.session.user
    lang = frappe.db.get_value("User", {'name': user}, "language")

    ## Auto Create Draft Stock Entry On Submit
    if doc.material_request_type == "Material Transfer":
        new_doc = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "posting_date": doc.transaction_date,
            "from_warehouse": doc.set_from_warehouse,
            "to_warehouse": doc.set_warehouse,
        })
        mr_items = frappe.db.sql(""" select a.name, a.idx, a.item_code, a.item_name, a.description, a.qty, a.stock_qty, a.uom, a.stock_uom, a.conversion_factor
                                                               from `tabMaterial Request Item` a join `tabMaterial Request` b
                                                               on a.parent = b.name
                                                               where b.name = '{name}'
                                                           """.format(name=doc.name), as_dict=1)

        for c in mr_items:
            items = new_doc.append("items", {})
            items.idx = c.idx
            items.item_code = c.item_code
            items.item_name = c.item_name
            items.description = c.description
            items.qty = c.qty
            items.transfer_qty = c.transfer_qty
            items.uom = c.uom
            items.stock_uom = c.stock_uom
            items.conversion_factor = c.conversion_factor
            items.material_request = doc.name
            items.material_request_item = c.name

        new_doc.insert()
        if lang == "ar":
            frappe.msgprint(" تم إنشاء حركة مخزنية بحالة مسودة رقم " + new_doc.name)
        else:
            frappe.msgprint(" Stock Entry record " + new_doc.name + " created ")
            # frappe.msgprint(_("Stock Entry record {0} created").format("<a href='https://erp.classatrading.com/app/stock-entry/{0}'>{0}</a>").format(x))


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
