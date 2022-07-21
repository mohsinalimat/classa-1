from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def before_insert(doc, method=None):
    if doc.payment_type == "Internal Transfer":
        doc.paid_to = frappe.db.get_value("Mode of Payment Account", {'parent': doc.mode_of_payment_2},
                                          'default_account')

@frappe.whitelist()
def after_insert(doc, method=None):
#def share_pe(doc, method=None):permission
    pass
    '''
    users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Account' and share_name = '{paid_to}' """.format(paid_to=doc.paid_to),as_dict=1)
    read = 1
    write = 1
    submit = 0
    share = 1
    everyone = 0
    if users:
        for x in users:
            add('Payment Entry', doc.name, x.user, read, write, submit, share, everyone)

    customer_group = frappe.db.get_value("Customer", doc.party, "customer_group")
    if doc.party_type == "Customer":
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Customer Group' and share_name = '{customer_group}' """.format(customer_group=customer_group),as_dict=1)
        read = 1
        write = 1
        submit = 0
        share = 1
        everyone = 0
        for x in users:
            add('Payment Entry', doc.name, x.user, read, write, submit, share, everyone)
    '''

@frappe.whitelist()
def onload(doc, method=None):
    if doc.payment_type == "Internal Transfer":
        doc.paid_to = frappe.db.get_value("Mode of Payment Account", {'parent': doc.mode_of_payment_2},
                                          'default_account')

@frappe.whitelist()
def before_validate(doc, method=None):
    ## Fetch Sales Persons
    if doc.party_type == "Customer":
        user = frappe.session.user
        employee = frappe.db.get_value("Employee", {'user_id': user}, "name")
        customer_group = frappe.db.get_value("Customer", doc.party, "customer_group")
        current_sales_person = frappe.db.get_value("Sales Person", {'employee': employee}, "name")
        # if current_sales_person:
        # doc.sales_person = current_sales_person
        if not current_sales_person and not doc.sales_person and doc.mode_of_payment != "مشتريات عاملين":
            # frappe.throw(" قم باختيار مندوب البيع")
            pass
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

    if doc.payment_type == "Internal Transfer":
        doc.paid_to = frappe.db.get_value("Mode of Payment Account", {'parent': doc.mode_of_payment_2},
                                          'default_account')

    if doc.mode_of_payment_type == "Cheque":
        doc.current_mode_of_payment = doc.mode_of_payment


@frappe.whitelist()
def validate(doc, method=None):
    customer_tax_type = frappe.db.get_value("Customer", doc.party, "tax_type")
    supplier_tax_type = frappe.db.get_value("Supplier", doc.party, "tax_type")
    if not doc.tax_type and doc.party_type == "Customer":
        doc.tax_type = customer_tax_type

    if not doc.tax_type and doc.party_type == "Supplier":
        doc.tax_type = supplier_tax_type

    else:
        pass


@frappe.whitelist()
def on_submit(doc, method=None):
    pass
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
