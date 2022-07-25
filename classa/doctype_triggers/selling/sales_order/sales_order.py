from future import unicode_literals
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
#def share_so(doc, method=None):permission
    pass
    '''
    if doc.set_warehouse:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Warehouse' and share_name = '{from_warehouse}' """.format(from_warehouse=doc.set_warehouse),as_dict=1)
        read = 1
        write = 1
        submit = 0
        share = 1
        everyone = 0
        for x in users:
            add('Sales Order', doc.name, x.user, read, write, submit, share, everyone)
    '''

@frappe.whitelist()
def onload(doc, method=None):
    pass
@frappe.whitelist()
def before_validate(doc, method=None):
    doc.ignore_pricing_rule = doc.ignore_pricing_rule_2
    doc.disable_rounded_total = 0
    ## Fetch Vehicle Warehouse From Vehicle
    doc.vehicle_warehouse = frappe.db.get_value("Vehicle", doc.vehicle, "warehouse")

    for t in doc.items:
        allowed_uom = frappe.db.get_value('UOM Conversion Detail', {'parent': t.item_code, 'uom': t.uom}, ['uom'])
        if allowed_uom != t.uom:
            frappe.throw("Row #" + str(t.idx) + ": وحدة القياس غير معرفة للصنف " + t.item_code)

    ## Make Customer Address 2 Field Mandatory If Customer Group Is Chain
    ## Auto Set Warehouse Based On Customer Group & Territory
    parent_group = frappe.db.get_value("Customer Group", doc.customer_group, "parent_customer_group")
    parent_territory = frappe.db.get_value("Territory", doc.territory, "parent_territory")
    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل") and not doc.customer_address_2:
        frappe.throw("Please Select The Customer's Address")

    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل"):
        doc.customer_address = doc.customer_address_2
    if (doc.customer_group == "مجموعة التجزئة" or parent_group == "مجموعة التجزئة"):
        doc.customer_address_2 = doc.customer_address
    '''
    if (doc.customer_group == "مجموعة التجزئة" or parent_group == "مجموعة التجزئة") and (doc.territory == "القاهرة" or parent_territory == "القاهرة"):
        doc.set_warehouse = "مخزن التجمع رئيسي - CA"
    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل") and (doc.territory == "القاهرة" or parent_territory == "القاهرة"):
        doc.set_warehouse = "مخزن بدر رئيسي - CA"
    if (doc.territory == "الاسكندرية" or parent_territory == "الاسكندرية"):
        doc.set_warehouse = "مخزن الأسكندرية رئيسي - CA"
    if (doc.territory == "الغردقة" or parent_territory == "الغردقة"):
        doc.set_warehouse = "مخزن الغردقة رئيسي - CA"
    if (doc.territory == "المنصورة" or parent_territory == "المنصورة"):
        doc.set_warehouse = "مخزن المنصورة رئيسي - CA"
    '''
    ## Fetch Sales Persons
    parent_group = frappe.db.get_value("Customer Group", doc.customer_group, "parent_customer_group")
    if (doc.customer_group == "مجموعة التجزئة" or parent_group == "مجموعة التجزئة") and not doc.sales_person:
        doc.sales_person = frappe.db.get_value("Customer", doc.customer, "sales_person")
        doc.sales_supervisor = frappe.db.get_value("Sales Person", doc.sales_person, "parent_sales_person")
        doc.territory_manager = frappe.db.get_value("Customer", doc.customer, "sales_person")
        doc.sales_manager = frappe.db.get_value("Customer Group", doc.customer_group, "sales_person")
    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل") and not doc.sales_person:
        doc.sales_person = frappe.db.get_value("Address", doc.customer_address, "sales_person")
        doc.sales_supervisor = frappe.db.get_value("Address", doc.customer_address, "sales_supervisor")
        doc.territory_manager = frappe.db.get_value("Address", doc.customer_address, "territory_manager")
        doc.sales_manager = frappe.db.get_value("Address", doc.customer_address, "sales_manager")

    ## Fetch Branch From Sales Person
    emp = frappe.db.get_value("Sales Person", doc.sales_person, "employee")
    doc.branch = frappe.db.get_value("Employee", emp, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    doc.cost_center = frappe.db.get_value("Customer Group", doc.customer_group, "cost_center")

    ## Fetch Vehicle Warehouse From Vehicle
    doc.vehicle_warehouse = frappe.db.get_value("Vehicle", doc.vehicle, "warehouse")

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.vehicle = doc.vehicle
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center

    ## Fetch Sales Person In Sales Team Table
    if doc.sales_person:
        doc.set("sales_team", [])
        sales_persons = doc.append("sales_team", {})
        sales_persons.sales_person = doc.sales_person
        sales_persons.allocated_percentage = 100

    ## Fetch Tax Type From Customer
    default_tax_type = frappe.db.get_value("Customer", doc.customer, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    ## Calculate Item Rate If Customer Tax Type Is Commercial
    if doc.tax_type == "Commercial":
        doc.set("taxes", [])
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
            totals += x.amount if x.amount else 0
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

    sales_order_list = frappe.db.get_list('Sales Order', filters=[{'docstatus': ['!=', 2]}],
                                          fields=["quotation", "name"])
    for x in sales_order_list:
        if doc.quotation == x.quotation and doc.quotation is not None and doc.name != x.name:
            frappe.throw("Another Sales Order " + x.name + " Is Linked With The Same Quotation. ")


@frappe.whitelist()
def validate(doc, method=None):
    for t in doc.items:
        item_price_hold = frappe.db.get_value("Item Price", {'item_code': t.item_code,'price_list': doc.selling_price_list}, "hold")
        if item_price_hold ==1 :
            frappe.throw("تم ايقاف التعامل على السعر الخاص بالمنتج {0} في الصف {1}".format(t.item_code,t.idx))
    for d in doc.items:
        x = d.price_list_rate + (d.price_list_rate * 0.01)
        y = d.rate + (d.rate * 0.01)
        if (doc.tax_type == "Taxable") and (d.rate > x or d.price_list_rate > y) and not (
                doc.allow_price or d.pricing_rules):
            frappe.msgprint("Row #" + str(d.idx) + ": Check Price List For Item Code " + d.item_code)

        if not d.price_list_rate:
            frappe.msgprint("Row #" + str(
                d.idx) + ": Item Code " + d.item_code + " Is Not Listed For Customer " + doc.customer_name)

        if not doc.sales_person:
            frappe.throw("مندوب البيع الزامي")

@frappe.whitelist()
def on_submit(doc, method=None):
    user = frappe.session.user
    lang = frappe.db.get_value("User", {'name': user}, "language")

    if doc.tax_type == "Taxable":
        for d in doc.items:
            x = d.price_list_rate + (d.price_list_rate * 0.01)
            y = d.rate + (d.rate * 0.01)
            if (d.rate > x or d.price_list_rate > y) and not (doc.allow_price or d.pricing_rules):
                frappe.throw("Row #" + str(d.idx) + ": Check Price List For Item Code " + d.item_code)
            # if d.qty > d.actual_qty:
            #   frappe.throw("Row #" + str(d.idx) + ": Ordered Qty Is More Than Available Qty For Item " + d.item_code)
            if (d.rate == 0 or d.price_list_rate == 0):
                frappe.throw("Row #" + str(d.idx) + ": Rate Cannot Be Zero For Item Code " + d.item_code)

    ## Make Vehicle & Vehicle Warehouse Fields Mandatory On Submit
    if not doc.vehicle:
        frappe.throw("Please Select The Vehicle")
    if not doc.vehicle_warehouse:
        frappe.throw("Please Add Warehouse For The Vehicle" + doc.vehicle)

    ## Auto Create Draft Delivery Note On Submit
    '''
    new_doc = frappe.get_doc({
        "doctype": "Delivery Note",
        "customer": doc.customer,
        "customer_group": doc.customer_group,
        "territory": doc.territory,
        "sales_order": doc.name,
        "posting_date": doc.delivery_date,
        "tax_type": doc.tax_type,
        "po_no": doc.po_no,
        "po_date": doc.po_date,
        "customer_address": doc.customer_address,
        "shipping_address_name": doc.shipping_address_name,
        "dispatch_address_name": doc.dispatch_address_name,
        "company_address": doc.company_address,
        "contact_person": doc.contact_person,
        "tax_id": doc.tax_id,
        "currency": doc.currency,
        "conversion_rate": doc.conversion_rate,
        "selling_price_list": doc.selling_price_list,
        "price_list_currency": doc.price_list_currency,
        "plc_conversion_rate": doc.plc_conversion_rate,
        "ignore_pricing_rule": doc.ignore_pricing_rule,
        "set_warehouse": doc.set_warehouse,
        "tc_name": doc.tc_name,
        "terms": doc.terms,
        "apply_discount_on": doc.apply_discount_on,
        "base_discount_amount": doc.base_discount_amount,
        "additional_discount_percentage": doc.additional_discount_percentage,
        "discount_amount": doc.discount_amount,
        "driver": doc.driver,
        "project": doc.project,
        "cost_center": doc.cost_center,
        "branch": doc.branch,
        "department": doc.department,
        "vehicle": doc.vehicle,
    })
    so_items = frappe.db.sql(""" select a.name, a.idx, a.item_code, a.item_name, a.description, a.qty, a.stock_qty, a.uom, a.stock_uom, a.conversion_factor, a.rate, a.amount,
                                   a.price_list_rate, a.base_price_list_rate, a.base_rate, a.base_amount, a.net_rate, a.net_amount, a.margin_type, a.margin_rate_or_amount, a.rate_with_margin,
                                   a.discount_percentage, a.discount_amount, a.base_rate_with_margin, a.item_tax_template
                                   from `tabSales Order Item` a join `tabSales Order` b
                                   on a.parent = b.name
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
        items.so_detail = c.name
        items.against_sales_order = doc.name

    so_taxes = frappe.db.sql(""" select a.charge_type, a.row_id, a.account_head, a.description, a.included_in_print_rate, a.included_in_paid_amount, a.rate, a.account_currency, a.tax_amount,
                                a.total, a.tax_amount_after_discount_amount, a.base_tax_amount, a.base_total, a.base_tax_amount_after_discount_amount, a.item_wise_tax_detail, a.dont_recompute_tax,
                                a.vehicle, a.department, a.cost_center, a.branch
                               from `tabSales Taxes and Charges` a join `tabSales Order` b
                               on a.parent = b.name
                               where b.name = '{name}'
                           """.format(name=doc.name), as_dict=1)

    for x in so_taxes:
        taxes = new_doc.append("taxes", {})
        taxes.charge_type = x.charge_type
        taxes.row_id = x.row_id
        taxes.account_head = x.account_head
        taxes.description = x.description
        taxes.included_in_print_rate = x.included_in_print_rate
        taxes.included_in_paid_amount = x.included_in_paid_amount
        taxes.rate = x.rate
        taxes.account_currency = x.account_currency
        taxes.tax_amount = x.tax_amount
        taxes.total = x.total
        taxes.tax_amount_after_discount_amount = x.tax_amount_after_discount_amount
        taxes.base_tax_amount = x.base_tax_amount
        taxes.base_total = x.base_total
        taxes.base_tax_amount_after_discount_amount = x.base_tax_amount_after_discount_amount
        taxes.item_wise_tax_detail = x.item_wise_tax_detail
        taxes.dont_recompute_tax = x.dont_recompute_tax
        taxes.vehicle = x.vehicle
        taxes.department = x.department
        taxes.branch = x.branch
        taxes.cost_center = x.cost_center

    new_doc.insert()
    frappe.msgprint("  تم إنشاء إذن تسليم العميل بحالة مسودة رقم " + new_doc.name)

    '''
    ## Auto Create Draft Stock Entry On Submit
    new_doc = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Transfer",
        "purpose": "Material Transfer",
        "posting_date": doc.transaction_date,
        "sales_order": doc.name,
        "customer": doc.customer,
        "customer_address": doc.customer_address,
        "from_warehouse": doc.set_warehouse,
        "to_warehouse": doc.vehicle_warehouse,
        "vehicle": doc.vehicle,
        "territory": doc.territory,

    })
    so_items = frappe.db.sql(""" select a.idx, a.name, a.item_code, a.item_name, a.description, a.qty, a.stock_qty, a.uom, a.stock_uom, a.conversion_factor
                                                           from `tabSales Order Item` a join `tabSales Order` b
                                                           on a.parent = b.name
                                                           where b.name = '{name}'
                                                       """.format(name=doc.name), as_dict=1)

    for c in so_items:
        items = new_doc.append("items", {})
        items.idx = c.idx
        items.item_code = c.item_code
        items.item_name = c.item_name
        items.description = c.description
        items.t_warehouse = doc.vehicle_warehouse
        items.qty = c.qty
        items.transfer_qty = c.transfer_qty
        items.uom = c.uom
        items.stock_uom = c.stock_uom
        items.conversion_factor = c.conversion_factor
        items.so_item = c.name
        items.so = doc.name

    new_doc.insert()
    frappe.msgprint("  تم إنشاء حركة مخزنية بحالة مسودة رقم " + new_doc.name)


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

@frappe.whitelist()
def delete_different_price_items(doc, method=None):
    [doc.items.remove(d) for d in doc.items if
     (d.rate != d.price_list_rate) or (d.rate == 0) or (d.price_list_rate == 0)]


@frappe.whitelist()
def delete_insufficient_stock_items(doc, method=None):
    [doc.items.remove(d) for d in doc.items if (d.qty > d.actual_qty)]
