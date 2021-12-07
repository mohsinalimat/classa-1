from __future__ import unicode_literals
import frappe
from frappe import auth
import datetime
import json, ast


################ Quotation

@frappe.whitelist()
def quot_onload(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_validate(doc, method=None):

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
        x.price_list_rate = frappe.db.get_value("Item Price", {'price_list': doc.selling_price_list, 'item_code': x.item_code}, "price_list_rate")



@frappe.whitelist()
def quot_validate(doc, method=None):
    for d in doc.items:
        if not d.rate == d.price_list_rate:
            frappe.msgprint("Row #"+str(d.idx)+": Check Price List For Item Code " + d.item_code)

        if not d.price_list_rate:
            frappe.msgprint("Row #"+str(d.idx)+": Item Code " + d.item_code + " Is Not Listed For Customer " + doc.customer_name)


@frappe.whitelist()
def quot_on_submit(doc, method=None):
    for d in doc.items:
        if not d.rate == d.price_list_rate and not doc.allow_price:
            frappe.throw("Row #"+str(d.idx)+": Check Price List For Item Code " + d.item_code)

        if not d.price_list_rate:
            frappe.throw("Row #"+str(d.idx)+": Item Code " + d.item_code + " Is Not Listed For Customer " + doc.customer_name)


@frappe.whitelist()
def quot_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def quot_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_save(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def quot_on_update(doc, method=None):
    pass


################ Sales Order


@frappe.whitelist()
def so_onload(doc, method=None):
    pass
@frappe.whitelist()
def so_before_validate(doc, method=None):

    ## Fetch Vehicle Warehouse From Vehicle
    doc.vehicle_warehouse = frappe.db.get_value("Vehicle", doc.vehicle, "warehouse")

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

    ## Fetch Sales Persons
    doc.sales_person = frappe.db.get_value("Address", doc.customer_address, "sales_person")
    doc.sales_supervisor = frappe.db.get_value("Sales Person", doc.sales_person, "parent_sales_person")
    doc.territory_manager = frappe.db.get_value("Customer", doc.customer, "sales_person")
    doc.sales_manager = frappe.db.get_value("Customer Group", doc.customer_group, "sales_person")

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    doc.cost_center = frappe.db.get_value("Customer Group", doc.customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.vehicle = doc.vehicle
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center

@frappe.whitelist()
def so_validate(doc, method=None):
    for d in doc.items:
        if not d.rate == d.price_list_rate and not doc.allow_price:
            frappe.throw("Row #" + str(d.idx) + ": Check Price List For Item Code " + d.item_code)

@frappe.whitelist()
def so_on_submit(doc, method=None):

    ## Make Vehicle Field Mandatory On Submit
    if not doc.vehicle:
        frappe.throw("Please Select The Vehicle")

@frappe.whitelist()
def so_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def so_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def so_before_save(doc, method=None):
    pass
@frappe.whitelist()
def so_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def so_on_update(doc, method=None):
    pass


################ Delivery Note

@frappe.whitelist()
def dn_onload(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_validate(doc, method=None):
    ## Fetch Driver Name and Transporter Name
    doc.driver_name = frappe.db.get_value("Driver", doc.driver, "full_name")
    doc.transporter_name = frappe.db.get_value("Supplier", doc.transporter, "name")

    ## Fetch Vehicle From Target Warehouse
    doc.vehicle = frappe.db.get_value("Warehouse", doc.set_warehouse, "vehicle")

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    customer_group = frappe.db.get_value("Customer", doc.customer, "customer_group")
    doc.cost_center = frappe.db.get_value("Customer Group", customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Items Table
    for x in doc.items:
        x.vehicle = doc.vehicle
        x.territory = doc.territory
        x.branch = doc.branch
        x.department = doc.department
        x.cost_center = doc.cost_center

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.vehicle = doc.vehicle
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center


@frappe.whitelist()
def dn_validate(doc, method=None):
    # fetch_tax_type_from_customer
    default_tax_type = frappe.db.get_value("Customer", doc.customer, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass
@frappe.whitelist()
def dn_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_save(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_update(doc, method=None):
    pass

################ Sales Invoice


@frappe.whitelist()
def siv_onload(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_validate(doc, method=None):
    ##Calculate Item Rate If Supplier Tax Type Is Taxable
    if doc.tax_type == "Commercial":
        doc.set("taxes", [])
        for d in doc.items:
            item_tax_rate = frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template}, "tax_rate")
            if item_tax_rate > 0 and d.rate <= d.price_list_rate:
                new_rate = d.rate + (item_tax_rate * d.rate / 100)
                d.rate = new_rate

            else:
                pass

    else:
        pass

    ## Fetch Sales Persons
    doc.sales_person = frappe.db.get_value("Address", doc.customer_address, "sales_person")
    doc.sales_supervisor = frappe.db.get_value("Sales Person", doc.sales_person, "parent_sales_person")
    doc.territory_manager = frappe.db.get_value("Customer", doc.customer, "sales_person")
    doc.sales_manager = frappe.db.get_value("Customer Group", doc.customer_group, "sales_person")

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    doc.cost_center = frappe.db.get_value("Customer Group", doc.customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Items Table
    for x in doc.items:
        x.vehicle = doc.vehicle
        x.territory = doc.territory
        x.branch = doc.branch
        x.department = doc.department
        x.cost_center = doc.cost_center

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.vehicle = doc.vehicle
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center

@frappe.whitelist()
def siv_validate(doc, method=None):
    #fetch_tax_type_from_customer
    default_tax_type = frappe.db.get_value("Customer", doc.customer, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass
@frappe.whitelist()
def siv_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_save(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_update(doc, method=None):
    pass


################ Payment Entry

@frappe.whitelist()
def pe_onload(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_validate(doc, method=None):
    ## Fetch Sales Persons
    if doc.party_type == "Customer":
        user = frappe.session.user
        employee = frappe.db.get_value("Employee", {'user_id': user}, "name")
        customer_group = frappe.db.get_value("Customer", doc.party, "customer_group")
        doc.sales_person = frappe.db.get_value("Sales Person", {'employee': employee}, "name")
        doc.sales_supervisor = frappe.db.get_value("Sales Person", doc.sales_person, "parent_sales_person")
        doc.territory_manager = frappe.db.get_value("Customer", doc.party, "sales_person")
        doc.sales_manager = frappe.db.get_value("Customer Group", customer_group, "sales_person")

    ## Fetch Territory From Customer
    doc.territory = frappe.db.get_value("Customer", doc.party, "territory")

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    customer_group = frappe.db.get_value("Customer", doc.party, "customer_group")
    doc.cost_center = frappe.db.get_value("Customer Group", customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Taxes Table
    for x in doc.taxes:
        x.cost_center = doc.cost_center

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.deductions:
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center

@frappe.whitelist()
def pe_validate(doc, method=None):
    customer_tax_type = frappe.db.get_value("Customer", doc.party, "tax_type")
    supplier_tax_type = frappe.db.get_value("Supplier", doc.party, "tax_type")
    if not doc.tax_type and doc.party_type == "Customer":
        doc.tax_type = customer_tax_type

    if not doc.tax_type and doc.party_type == "Supplier":
        doc.tax_type = supplier_tax_type

    else:
        pass


@frappe.whitelist()
def pe_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_save(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_update(doc, method=None):
    pass

################ Material Request

@frappe.whitelist()
def mr_onload(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def mr_validate(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_save(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_update(doc, method=None):
    pass

################ Purchase Order

@frappe.whitelist()
def po_onload(doc, method=None):
    pass
@frappe.whitelist()
def po_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def po_validate(doc, method=None):
    pass
@frappe.whitelist()
def po_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def po_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def po_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def po_before_save(doc, method=None):
    pass
@frappe.whitelist()
def po_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def po_on_update(doc, method=None):
    pass

################ Purchase Receipt

@frappe.whitelist()
def pr_onload(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def pr_validate(doc, method=None):
    ##fetch_tax_type_from_Supplier
    default_tax_type = frappe.db.get_value("Supplier", doc.supplier, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass
@frappe.whitelist()
def pr_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_save(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_update(doc, method=None):
    pass


################ Purchase Invoice

@frappe.whitelist()
def piv_onload(doc, method=None):
    pass
@frappe.whitelist()
def piv_before_validate(doc, method=None):
    ##Calculate Item Rate If Supplier Tax Type Is Taxable
    if doc.tax_type == "Commercial":
        doc.set("taxes", [])
        for d in doc.items:
            item_tax_rate = frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template}, "tax_rate")
            if item_tax_rate > 0 and d.rate <= d.price_list_rate:
                new_rate = d.rate + (item_tax_rate * d.rate / 100)
                d.rate = new_rate

            else:
                pass

    else:
        pass

@frappe.whitelist()
def piv_validate(doc, method=None):
    ##fetch_tax_type_from_Supplier
    default_tax_type = frappe.db.get_value("Supplier", doc.supplier, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass

@frappe.whitelist()
def piv_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def piv_before_save(doc, method=None):
    pass

@frappe.whitelist()
def piv_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_update(doc, method=None):
    pass

################ Employee Advance

@frappe.whitelist()
def emad_onload(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def emad_validate(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_save(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_update(doc, method=None):
    pass

################ Expense Claim

@frappe.whitelist()
def excl_onload(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def excl_validate(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_save(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_update(doc, method=None):
    pass

################ Stock Entry

@frappe.whitelist()
def ste_onload(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_validate(doc, method=None):
    ## Fetch Vehcile From Target Warehouse
    doc.vehicle = frappe.db.get_value("Warehouse", doc.to_warehouse, "vehicle")

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    if doc.customer:
        customer_group = frappe.db.get_value("Customer", doc.party, "customer_group")
        doc.cost_center = frappe.db.get_value("Customer Group", customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Items Table
    for x in doc.items:
        x.vehicle = doc.vehicle
        x.territory = doc.territory
        x.branch = doc.branch
        x.department = doc.department
        x.cost_center = doc.cost_center

@frappe.whitelist()
def ste_validate(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_save(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_update(doc, method=None):
    pass

################ Blanket Order

@frappe.whitelist()
def blank_onload(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def blank_validate(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_save(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_update(doc, method=None):
    pass
