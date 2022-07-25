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
#def share_se(doc, method=None):permission
    pass
    '''
    if doc.from_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.from_warehouse),as_dict=1)
        read = 1
        write = 1
        submit = 0
        share = 1
        everyone = 0
        for x in users:
            add('Stock Entry', doc.name, x.user, read, write, submit, share, everyone)

    if doc.to_warehouse:
        users = frappe.db.sql(
            """ select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(
                from_warehouse=doc.to_warehouse), as_dict=1)
        read = 1
        write = 1
        submit = 0
        share = 1
        everyone = 0
        for x in users:
            add('Stock Entry', doc.name, x.user, read, write, submit, share, everyone)
    '''
@frappe.whitelist()
def onload(doc, method=None):
    pass
@frappe.whitelist()
def before_validate(doc, method=None):
    stock_entry_type_account = frappe.db.get_value('Stock Entry Type', {'name': doc.stock_entry_type}, 'account')
    for q in doc.items:
        q.expense_account = stock_entry_type_account

    for t in doc.items:
        allowed_uom = frappe.db.get_value('UOM Conversion Detail', {'parent': t.item_code, 'uom': t.uom}, ['uom'])
        if allowed_uom != t.uom:
            frappe.throw("Row #" + str(t.idx) + ": وحدة القياس غير معرفة للصنف " + t.item_code)

    if doc.sales_order:
        so = frappe.get_doc("Sales Order", doc.sales_order)
        doc.customer = so.customer
        doc.customer_address = so.customer_address
        for x in doc.items:
            if not x.so_item:
                frappe.throw("Row #" + str(x.idx) + ": لا يمكن اضافة اصناف يدويا غير موجوده بامر البيع ")
        # doc.save()

    ## Fetch Vehcile From Target Warehouse
    doc.vehicle = frappe.db.get_value("Warehouse", doc.to_warehouse, "vehicle")

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    if doc.customer:
        customer_group = frappe.db.get_value("Customer", doc.customer, "customer_group")
        doc.cost_center = frappe.db.get_value("Customer Group", customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Items Table
    for x in doc.items:
        x.vehicle = doc.vehicle
        x.territory = doc.territory
        x.branch = doc.branch
        x.department = doc.department
        x.cost_center = doc.cost_center


@frappe.whitelist()
def validate(doc, method=None):
    for d in doc.items:
        d.barcode = frappe.db.get_value("Item Barcode", {'parent': d.item_code}, "barcode")


@frappe.whitelist()
def on_submit(doc, method=None):
    for d in doc.items:
        #warehouse_type = frappe.db.get_value("Warehouse", d.s_warehouse, "warehouse_type")
        #if d.transfer_qty > d.actual_qty and warehouse_type != "فحص مردود مبيعات":
        #    frappe.throw("الكمية عير متاحة للصنف {0} في الصف رقم {1}".format(d.item_code, d.idx))
        so_ite = d.so_item
        # so_qt = d.qty
        frappe.db.sql(""" update `tabSales Order Item` set st_item = '{st_item}' where name = '{so_ite}' """.format(
            st_item=d.name, so_ite=so_ite))
        frappe.db.sql(
            """ update `tabSales Order Item` set st_qty = '{st_qty}' where name = '{so_ite}' """.format(st_qty=d.qty,
                                                                                                        so_ite=so_ite))
    # if doc.sales_order:
    #    frappe.db_set_value('Sales Order', doc.sales_order, 'se_submitted', 1)

    ## Auto Create Draft Sales Invoice On Submit
    if doc.sales_order:
        so = frappe.get_doc('Sales Order', doc.sales_order)
        if so.tax_type == "Commercial":
            serialq = "SINV-"
        else:
            serialq = "INV-"
        new_doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "naming_series": serialq,
            "update_stock": 1,
            "sales_person": so.sales_person,
            "stock_entry": doc.name,
            "customer": so.customer,
            "customer_group": so.customer_group,
            "territory": so.territory,
            "sales_order": so.name,
            "posting_date": so.delivery_date,
            "tax_type": so.tax_type,
            "po_no": so.po_no,
            "po_date": so.po_date,
            "customer_address": so.customer_address,
            "shipping_address_name": so.shipping_address_name,
            "dispatch_address_name": so.dispatch_address_name,
            "company_address": so.company_address,
            "contact_person": so.contact_person,
            "tax_id": so.tax_id,
            "currency": so.currency,
            "conversion_rate": so.conversion_rate,
            "selling_price_list": so.selling_price_list,
            "price_list_currency": so.price_list_currency,
            "plc_conversion_rate": so.plc_conversion_rate,
            "ignore_pricing_rule": so.ignore_pricing_rule,
            "set_warehouse": doc.to_warehouse,
            "tc_name": so.tc_name,
            "terms": so.terms,
            "apply_discount_on": so.apply_discount_on,
            "base_discount_amount": so.base_discount_amount,
            "additional_discount_percentage": so.additional_discount_percentage,
            "discount_amount": so.discount_amount,
            "driver": so.driver,
            "project": so.project,
            "vehicle": so.vehicle,
        })
        so_items = frappe.db.sql(""" select d.so_item, d.idx, d.item_code, d.item_name, d.description, d.qty, a.stock_qty, a.uom, a.stock_uom, a.conversion_factor, a.rate, a.amount,
                                               a.price_list_rate, a.base_price_list_rate, a.base_rate, a.base_amount, a.net_rate, a.net_amount, a.margin_type, a.margin_rate_or_amount, a.rate_with_margin,
                                               a.discount_percentage, a.discount_amount, a.base_rate_with_margin, a.item_tax_template
                                               from `tabStock Entry Detail` d join`tabSales Order Item` a on d.so_item = a.name 
                                               join `tabStock Entry` b on d.parent = b.name
                                               where b.name = '{name}'
                                           """.format(name=doc.name), as_dict=1)

        for c in so_items:
            items = new_doc.append("items", {})
            items.idx = c.idx
            items.item_code = c.item_code
            items.item_name = c.item_name
            items.description = c.description
            items.qty = c.qty
            items.uom = c.uom
            items.stock_uom = c.stock_uom
            items.conversion_factor = c.conversion_factor
            items.price_list_rate = c.price_list_rate
            items.base_price_list_rate = c.base_price_list_rate
            items.base_rate = c.base_rate
            items.base_amount = c.base_amount
            items.rate = c.rate
            items.net_rate = c.net_rate
            items.net_amount = c.net_amount
            items.amount = c.amount
            items.margin_type = c.margin_type
            items.margin_rate_or_amount = c.margin_rate_or_amount
            items.rate_with_margin = c.rate_with_margin
            items.discount_percentage = c.discount_percentage
            items.discount_amount = c.discount_amount
            items.base_rate_with_margin = c.base_rate_with_margin
            items.item_tax_template = c.item_tax_template
            items.sales_order = doc.sales_order
            items.so_detail = c.so_item

        so_taxes = frappe.db.sql(""" select a.charge_type, a.row_id, a.account_head, a.description, a.included_in_print_rate, a.included_in_paid_amount, a.rate, a.account_currency, a.tax_amount,
                                            a.total, a.tax_amount_after_discount_amount, a.base_tax_amount, a.base_total, a.base_tax_amount_after_discount_amount, a.item_wise_tax_detail, a.dont_recompute_tax,
                                            a.vehicle, a.department, a.cost_center, a.branch
                                           from `tabSales Taxes and Charges` a join `tabSales Order` b
                                           on a.parent = b.name
                                           where b.name = '{name}'
                                       """.format(name=doc.sales_order), as_dict=1)

        for x in so_taxes:
            taxes = new_doc.append("taxes", {})
            taxes.charge_type = x.charge_type
            taxes.row_id = x.row_id
            taxes.account_head = x.account_head
            taxes.description = x.description
            taxes.included_in_print_rate = x.included_in_print_rate
            taxes.included_in_paid_amount = x.included_in_paid_amount
            # taxes.rate = x.rate
            # taxes.account_currency = x.account_currency
            # taxes.tax_amount = x.tax_amount
            # taxes.total = x.total
            # taxes.tax_amount_after_discount_amount = x.tax_amount_after_discount_amount
            # taxes.base_tax_amount = x.base_tax_amount
            # taxes.base_total = x.base_total
            # taxes.base_tax_amount_after_discount_amount = x.base_tax_amount_after_discount_amount
            taxes.item_wise_tax_detail = x.item_wise_tax_detail
            taxes.dont_recompute_tax = x.dont_recompute_tax
            taxes.vehicle = x.vehicle
            taxes.department = x.department
            taxes.branch = x.branch
            taxes.cost_center = x.cost_center

        new_doc.insert(ignore_permissions=True)
        doc.sales_invoice = new_doc.name
        frappe.msgprint(new_doc.name + " تم إنشاء فاتورة مبيعات بحالة مسودة رقم ")


@frappe.whitelist()
def on_cancel(doc, method=None):
    for d in doc.items:
        so_ite = d.so_item
        frappe.db.sql(
            """ update `tabSales Order Item` set st_item = '' where name = '{so_ite}'""".format(st_item=d.name,
                                                                                                so_ite=so_ite))
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
