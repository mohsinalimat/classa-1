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
#def share_sin(doc, method=None):permission
    pass
    '''
    if doc.customer_group:
        users = frappe.db.sql(""" select user from `tabDocShare` where share_doctype = 'Customer Group' and share_name = '{customer_group}' """.format(customer_group=doc.customer_group),as_dict=1)
        read = 1
        write = 1
        submit = 0
        share = 1
        everyone = 0
        for x in users:
            add('Sales Invoice', doc.name, x.user, read, write, submit, share, everyone)
    '''
@frappe.whitelist()
def onload(doc, method=None):
    pass
@frappe.whitelist()
def before_validate(doc, method=None):
    doc.ignore_pricing_rule = doc.ignore_pricing_rule_2
    # doc.update_stock = 1
    # if doc.tax_type == "Taxable":
    #    doc.set_warehouse = frappe.db.get_value("Vehicle", doc.vehicle, "warehouse")

    ## Fetch Sales Persons
    parent_group = frappe.db.get_value("Customer Group", doc.customer_group, "parent_customer_group")
    if (doc.customer_group == "مجموعة التجزئة" or parent_group == "مجموعة التجزئة") and not doc.sales_person:
        sales_person = frappe.db.get_value("Customer", doc.customer, "sales_person")
        if sales_person:
            doc.sales_person = sales_person
        else:
            user = frappe.session.user
            emp = frappe.db.get_value("Employee", {'user_id': user}, "name")
            sp = frappe.db.get_value("Sales Person", {'employee': emp}, "name")
            doc.sales_person = sp

        doc.sales_supervisor = frappe.db.get_value("Sales Person", doc.sales_person, "parent_sales_person")
        doc.territory_manager = frappe.db.get_value("Customer", doc.customer, "sales_person")
        doc.sales_manager = frappe.db.get_value("Customer Group", doc.customer_group, "sales_person")

    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل") and not doc.sales_person:
        sales_person2 = frappe.db.get_value("Address", doc.customer_address, "sales_person")
        if sales_person2:
            doc.sales_person = sales_person2
        else:
            user = frappe.session.user
            emp = frappe.db.get_value("Employee", {'user_id': user}, "name")
            sp = frappe.db.get_value("Sales Person", {'employee': emp}, "name")
            doc.sales_person = sp
        doc.sales_supervisor = frappe.db.get_value("Address", doc.customer_address, "sales_supervisor")
        doc.territory_manager = frappe.db.get_value("Address", doc.customer_address, "territory_manager")
        doc.sales_manager = frappe.db.get_value("Address", doc.customer_address, "sales_manager")

    if not doc.delivery_note and not doc.update_stock and not doc.not_stock:
        frappe.throw("برجاء تحديد المخزن المسحوب منه حيث ان الفاتورة غير مربوطة باذن تسليم للعميل")

    if doc.customer == "عميل مسحوبات عاملين" and not doc.sell_to_employees:
        frappe.throw("برجاء تحديد الموظف")

    for t in doc.items:
        allowed_uom = frappe.db.get_value('UOM Conversion Detail', {'parent': t.item_code, 'uom': t.uom}, ['uom'])
        if allowed_uom != t.uom:
            frappe.throw("Row #" + str(t.idx) + ": وحدة القياس غير معرفة للصنف " + t.item_code)

    ## Fetch Branch From Sales Person
    emp = frappe.db.get_value("Sales Person", doc.sales_person, "employee")
    doc.branch = frappe.db.get_value("Employee", emp, "branch")

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
        if doc.set_warehouse:
            x.warehouse = doc.set_warehouse

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.vehicle = doc.vehicle
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center

    sales_invoice_list = frappe.db.get_list('Sales Invoice', filters=[{'docstatus': ['!=', 2]}],
                                            fields=["delivery_note", "name"])

    for x in sales_invoice_list:
        if doc.delivery_note == x.delivery_note and doc.delivery_note is not None and doc.name != x.name and doc.is_return == 0:
            frappe.throw("Another Sales Invoice " + x.name + " Is Linked With The Same Delivery Note. ")
    

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
            if d.item_tax_template:
                item_tax_rate = float(frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template},
                                                          "tax_rate"))
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
                        d.total_with_tax_before_discount_ = new_rate * d.qty
                        d.discounted_amount = new_rate * d.discount_percentage / 100
                    else:
                        new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                        d.rate = new_rate
                        d.base_rate = new_rate
                        d.amount = new_rate * d.qty
                        d.base_amount = new_rate * d.qty
                        d.total_with_tax_before_discount_ = new_rate * d.qty
                        d.tax_rate = new_rate
                else:
                    new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                    d.total_with_tax_before_discount_ = new_rate * d.qty
                    d.tax_rate = new_rate
        totals = 0
        for x in doc.items:
            totals += x.amount if x.amount else 0
        if doc.additional_discount_percentage:
            doc.total = totals
            doc.grand_total = totals - doc.discount_amount
            doc.rounded_total = totals - doc.discount_amount
            doc.base_rounded_total = totals - doc.discount_amount
            doc.in_words = money_in_words(doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total),
                                          doc.currency)
            doc.base_in_words = money_in_words(
                doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total), doc.currency)
            doc.base_grand_total = totals - doc.discount_amount
            doc.net_total = totals - doc.discount_amount
            doc.base_net_total = totals - doc.discount_amount
            doc.base_total = totals - doc.discount_amount
            doc.outstanding_amount = totals - doc.discount_amount
            doc.total_taxes_and_charges = 0

        else:
            doc.total = totals
            doc.grand_total = totals
            doc.rounded_total = totals
            doc.base_rounded_total = totals
            doc.in_words = money_in_words(doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total),
                                          doc.currency)
            doc.base_in_words = money_in_words(
                doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total), doc.currency)
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

    '''
    ## validate sales invoice items with stock entry items

    for c in doc.items:
        update_qty = frappe.db.sql(""" select qty as qty from `tabStock Entry Detail` where so_item = '{so_item1}' and docstatus = 1""".format(so_item1=c.so_detail),as_dict=1)
        if update_qty:
            for d in update_qty:
                c.qty = d.qty
        
    [doc.items.remove(d) for d in doc.items if not d.st_item]

    '''

    """
    def removeSingleRow(master, detailName):
        theDetail = None
        for detail in master.details:
            if detail.name == detailName:
                theDetail = detail

    
    master.remove(theDetail)
    #master.save()
    #frappe.db.commit()
    """

@frappe.whitelist()
def validate(doc, method=None):
    for t in doc.items:
        item_price_hold = frappe.db.get_value("Item Price", {'item_code': t.item_code,'price_list': doc.selling_price_list}, "hold")
        if item_price_hold ==1 :
            frappe.throw("تم ايقاف التعامل على السعر الخاص بالمنتج {0} في الصف {1}".format(t.item_code,t.idx))
    if doc.stock_entry:
        frappe.db.sql(
            """ update `tabStock Entry` set sales_invoice = '{invoice}' where name = '{stock_entry}' """.format(
                invoice=doc.name, stock_entry=doc.stock_entry))
        frappe.db.sql(
            """ update `tabStock Entry` set sales_invoice_status = 'Draft' where name = '{stock_entry}' and sales_invoice_status is null """.format(
                invoice=doc.name, stock_entry=doc.stock_entry))
    ## Remove Returned Qty From Sales Invoice
    for p in doc.items:
        if p.dn_detail:
            qty_del = frappe.db.get_value("Delivery Note Item", {'name': p.dn_detail}, "qty")
            qty = frappe.db.get_value("Delivery Note Item", {'name': p.dn_detail}, "returned_qty")
            convert_factor = frappe.db.get_value("Delivery Note Item", {'name': p.dn_detail}, "conversion_factor")
            if qty > 0:
                returned_qty = qty / convert_factor
                new_qty = qty_del - returned_qty
                p.qty = new_qty

    # doc.ignore_pricing_rule = 0

    if not doc.sales_person:
        frappe.throw("مندوب البيع الزامي")

    ## Calculate Item Rate If Customer Tax Type Is Commercial
    if doc.tax_type == "Commercial":
        doc.set("taxes", [])
        # if doc.edit_items_rate_discount:
        for d in doc.items:
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
                        d.total_with_tax_before_discount_ = new_rate * d.qty
                        d.discounted_amount = new_rate * d.discount_percentage / 100
                    else:
                        new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                        d.rate = new_rate
                        d.base_rate = new_rate
                        d.amount = new_rate * d.qty
                        d.base_amount = new_rate * d.qty
                        d.total_with_tax_before_discount_ = new_rate * d.qty
                        d.tax_rate = new_rate
                else:
                    new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                    d.total_with_tax_before_discount_ = new_rate * d.qty
                    d.tax_rate = new_rate

        totals = 0
        for x in doc.items:
            totals += x.amount if x.amount else 0
        if doc.additional_discount_percentage:
            doc.total = totals
            doc.grand_total = totals - doc.discount_amount
            doc.rounded_total = totals - doc.discount_amount
            doc.base_rounded_total = totals - doc.discount_amount
            doc.in_words = money_in_words(doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total),
                                          doc.currency)
            doc.base_in_words = money_in_words(
                doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total), doc.currency)
            doc.base_grand_total = totals - doc.discount_amount
            doc.net_total = totals - doc.discount_amount
            doc.base_net_total = totals - doc.discount_amount
            doc.base_total = totals - doc.discount_amount
            doc.outstanding_amount = totals - doc.discount_amount
            doc.total_taxes_and_charges = 0

        else:
            doc.total = totals
            doc.grand_total = totals
            doc.rounded_total = totals
            doc.base_rounded_total = totals
            doc.in_words = money_in_words(doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total),
                                          doc.currency)
            doc.base_in_words = money_in_words(
                doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total), doc.currency)
            doc.base_grand_total = totals
            doc.net_total = totals
            doc.base_net_total = totals
            doc.base_total = totals
            doc.outstanding_amount = totals
            doc.total_taxes_and_charges = 0

@frappe.whitelist()
def on_submit(doc, method=None):
    '''
    for d in doc.items:
        warehouse_type = frappe.db.get_value("Warehouse", d.warehouse, "warehouse_type")
        if d.stock_qty > d.actual_qty and warehouse_type != "فحص مردود مبيعات" and doc.update_stock == 1:
            frappe.throw("الكمية عير متاحة للصنف {0} في الصف رقم {1}".format(d.item_code, d.idx))
    '''
    # doc.ignore_pricing_rule = 0
    if doc.stock_entry:
        frappe.db.sql(
            """ update `tabStock Entry` set sales_invoice_status = 'Submitted' where name = '{stock_entry}' """.format(
                invoice=doc.name, stock_entry=doc.stock_entry))

    if doc.tax_type == "Commercial":
        doc.set("taxes", [])
        # if doc.edit_items_rate_discount:
        for d in doc.items:
            if d.item_tax_template:
                item_tax_rate = int(
                    frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template}, "tax_rate"))
                if item_tax_rate > 0 and d.rate <= d.price_list_rate:
                    if d.discount_percentage:
                        new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                        new_discounted_rate = new_rate - (d.discount_percentage * new_rate / 100)
                        d.rate = new_discounted_rate
                        d.net_rate = new_discounted_rate
                        d.base_net_rate = new_discounted_rate
                        d.base_rate = new_discounted_rate
                        d.net_amount = new_discounted_rate * d.qty
                        d.base_net_amount = new_discounted_rate * d.qty
                        d.amount = new_discounted_rate * d.qty
                        d.base_amount = new_discounted_rate * d.qty
                        d.tax_rate = new_rate
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
            else:
                item_tax_rate = frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template},
                                                    "tax_rate")
                new_rate = (d.price_list_rate + (item_tax_rate * d.price_list_rate / 100))
                d.tax_rate = new_rate

        totals = 0
        for x in doc.items:
            totals += x.amount if x.amount else 0
        if doc.additional_discount_percentage:
            doc.total = totals
            doc.grand_total = totals - doc.discount_amount
            doc.rounded_total = totals - doc.discount_amount
            doc.base_rounded_total = totals - doc.discount_amount
            doc.in_words = money_in_words(doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total),
                                          doc.currency)
            doc.base_in_words = money_in_words(
                doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total), doc.currency)
            doc.base_grand_total = totals - doc.discount_amount
            doc.net_total = totals - doc.discount_amount
            doc.base_net_total = totals - doc.discount_amount
            doc.base_total = totals - doc.discount_amount
            doc.outstanding_amount = totals - doc.discount_amount
            doc.total_taxes_and_charges = 0

        else:
            doc.total = totals
            doc.grand_total = totals
            doc.rounded_total = totals
            doc.base_rounded_total = totals
            doc.in_words = money_in_words(doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total),
                                          doc.currency)
            doc.base_in_words = money_in_words(
                doc.disable_rounded_total and abs(doc.grand_total) or abs(doc.rounded_total), doc.currency)
            doc.base_grand_total = totals
            doc.net_total = totals
            doc.base_net_total = totals
            doc.base_total = totals
            doc.outstanding_amount = totals
            doc.total_taxes_and_charges = 0

    if doc.sell_to_employees and doc.is_return == 0:
        references = [
            {
                "doctype": "Payment Entry Reference",
                "reference_doctype": "Sales Invoice",
                "reference_name": doc.name,
                "due_date": doc.posting_date,
                "allocated_amount": doc.grand_total,
                "outstanding_amount": doc.grand_total
            }
        ]
        pe_doc = frappe.get_doc({
            "doctype": "Payment Entry",
            "posting_date": doc.posting_date,
            "payment_type": "Receive",
            "mode_of_payment": "مشتريات عاملين",
            "paid_to": "1321 - تسوية مشتريات عاملين - CA",
            "party_type": "Customer",
            "party": doc.customer,
            "total_allocated_amount": doc.grand_total,
            "paid_amount": doc.net_total,
            "received_amount": doc.net_total,
            "reference_date": doc.posting_date,
            "source_exchange_rate": 1,
            "target_exchange_rate": 1,
            "references": references
        })
        pe_doc.insert(ignore_permissions=True)
        pe_doc.submit()

        new_doc = frappe.new_doc('Loan')
        new_doc.applicant_type = 'Employee'
        new_doc.applicant = doc.employee_code
        new_doc.applicant_name = doc.employee_name
        new_doc.repay_from_salary = 1
        new_doc.repayment_start_date = doc.posting_date
        new_doc.loan_type = 'مشتريات'
        new_doc.loan_amount = doc.net_total
        new_doc.repayment_method = 'Repay Fixed Amount per Period'
        new_doc.invoice = doc.name
        new_doc.monthly_repayment_amount = doc.net_total
        new_doc.insert(ignore_permissions=True)
        new_doc.submit()

        '''
        for x in doc.sell_to_employee_table:
            new_doc = frappe.new_doc('Loan')
            new_doc.applicant_type = 'Employee'
            new_doc.applicant = x.employee_code
            new_doc.applicant_name = x.employee_name
            new_doc.repay_from_salary = 1
            new_doc.repayment_start_date = doc.posting_date
            new_doc.loan_type = 'مشتريات'
            new_doc.loan_amount = x.amount
            new_doc.repayment_method = 'Repay Fixed Amount per Period'
            new_doc.monthly_repayment_amount = x.amount
            new_doc.insert()
            new_doc.submit()
        '''

    if doc.sell_to_employees and doc.is_return == 1 and doc.return_against:
        loan = frappe.get_doc('Loan', {'invoice': doc.return_against})
        repayment = frappe.new_doc('Loan Repayment')
        repayment.against_loan = loan.name
        repayment.applicant_type = "Employee"
        repayment.applicant = loan.applicant
        repayment.posting_date = doc.posting_date
        repayment.amount_paid = -1 * doc.grand_total
        repayment.insert(ignore_permissions=True)
        repayment.submit()

    ### migration to tax instance
    if doc.tax_type == "Taxable" and doc.naming_series == "INV-":
        data = {}
        data["doctype"] = "Sales Invoice"
        data["serial"] = doc.name
        data["set_posting_time"] = 1
        data["amended_from"] = doc.amended_from if doc.amended_from else ''
        data["return_against"] = doc.return_against if doc.return_against else ''
        data["remote_docname"] = doc.name
        data["customer"] = doc.customer
        data["tax_type"] = doc.tax_type
        data["customer_name"] = doc.customer_name
        data["posting_date"] = doc.posting_date
        data["due_date"] = doc.due_date
        data["tax_id"] = doc.tax_id
        data["amended_from"] = doc.amended_from
        data["return_against"] = doc.return_against
        data["customer_group"] = doc.customer_group
        data["territory"] = doc.territory
        data["customer_address"] = doc.customer_address
        data["contact_person"] = doc.contact_person
        data["is_return"] = doc.is_return
        data["cost_center"] = "قسم مبيعات كبار عملاء السلاسل - CA"
        data["currency"] = "EGP"
        data["conversion_rate"] = 1.0
        data["selling_price_list"] = "2022"
        data["price_list_currency"] = "EGP"
        data["plc_conversion_rate"] = 1.0
        data["update_stock"] = 1
        data["set_warehouse"] = "مخزن رئيسي - CA"
        data["payment_terms_template"] = doc.payment_terms_template
        # data["taxes_and_charges"] = "Default Tax Template"
        data["tc_name"] = doc.tc_name
        data["sales_partner"] = "ahmed"
        data["apply_discount_on"] = "Net Total"
        data["additional_discount_percentage"] = doc.additional_discount_percentage
        # data["total_taxes_and_charges"] = doc.total_taxes_and_charges
        data["discount_amount"] = doc.discount_amount

        child_data_1 = frappe.db.get_list('Sales Invoice Item', filters={'parent': doc.name}, order_by='idx',
                                          fields=[
                                              'item_code',
                                              'item_name',
                                              'qty',
                                              'stock_uom',
                                              'uom',
                                              'conversion_factor',
                                              'stock_qty',
                                              'price_list_rate',
                                              'base_price_list_rate',
                                              'margin_type',
                                              'margin_rate_or_amount',
                                              'rate_with_margin',
                                              'discount_percentage',
                                              'discount_amount',
                                              'base_rate_with_margin',
                                              'rate',
                                              'item_tax_rate',
                                              'amount',
                                              'item_tax_template',
                                              'base_rate',
                                              'base_amount',
                                          ])
        data['items'] = [child_data_1]

        child_data_2 = frappe.db.get_list('Sales Taxes and Charges', filters={'parent': doc.name}, order_by='idx',
                                          fields=[
                                              'charge_type',
                                              'account_head',
                                              'description',
                                              'rate',
                                              'tax_amount',
                                              'total',
                                              'parenttype',
                                              'parent',
                                              'parentfield'
                                          ])
        data['taxes'] = [child_data_2]

        '''
        item_results = frappe.db.sql("""
                                    SELECT
                                        `tabSales Taxes and Charges`.charge_type,
                                        `tabSales Taxes and Charges`.account_head, 
                                        `tabSales Taxes and Charges`.description, 
                                        `tabSales Taxes and Charges`.rate, 
                                        `tabSales Taxes and Charges`.tax_amount, 
                                        `tabSales Taxes and Charges`.total
                                    FROM
                                        `tabSales Taxes and Charges` join `tabSales Invoice` on `tabSales Taxes and Charges`.parent = `tabSales Invoice`.name
                                    WHERE
                                       `tabSales Taxes and Charges`.parent = '{name}'
                                    """.format(name=doc.name), as_dict=1)
        data['taxes'] = [
            {
                "charge_type": "On Net Total",
                "account_head": "2301 - ضريبة القيمة المضافة VAT - CA",
                "description": "2301 - ضريبة القيمة المضافة VAT"
            }
        ]
        '''

        url = 'https://system.classatrading.com/api/method/classa_taxable.functions.sales_invoice_add'
        headers = {'content-type': 'application/json; charset=utf-8', 'Accept': 'application/json',
                   'Authorization': 'token 1aac25006d5422a:3ad3ead24dee921'}
        response = requests.post(url, json=data, headers=headers)
        #frappe.msgprint(response.text)
        # doc.db_set('taxable_no', response.text, commit=True)
        # frappe.msgprint(data)
        # todo = frappe.get_doc('ToDo')
        # todo.description = data
        # todo.save()

    # Accounting Periods
    accounting_periods = frappe.db.sql("""
                                    SELECT
                                        `tabAccounting Period`.start_date as start,
                                        `tabAccounting Period`.end_date as end

                                    FROM
                                        `tabAccounting Period` join `tabClosed Document` on `tabClosed Document`.parent = `tabAccounting Period`.name
                                    WHERE
                                       `tabClosed Document`.document_type = 'Sales Invoice'
                                       and `tabClosed Document`.closed = 0
                                    """, as_dict=1)
    for x in accounting_periods:
        if getdate(x.start) <= getdate(doc.posting_date) and getdate(x.end) >= getdate(doc.posting_date):
            frappe.throw("لا يمكن تسجيل فواتير خلال الفترات المحاسبية المغلقة")


@frappe.whitelist()
def on_cancel(doc, method=None):
    if doc.stock_entry:
        frappe.db.sql(
            """ update `tabStock Entry` set sales_invoice_status = 'Cancelled' where name = '{stock_entry}' """.format(
                invoice=doc.name, stock_entry=doc.stock_entry))
        frappe.db.sql(""" update `tabStock Entry` set sales_invoice = Null where name = '{stock_entry}' """.format(
            invoice=doc.name, stock_entry=doc.stock_entry))
    if doc.tax_type == "Taxable":
        headersAPI = {
            'accept': 'application/json',
            'Authorization': 'token 1aac25006d5422a:3ad3ead24dee921',
        }
        link = "https://system.classatrading.com/api/method/classa_taxable.functions.sales_invoice_cancel?si=" + doc.name
        response = requests.get(link, headers=headersAPI)

    # if doc.sell_to_employees:
    # pe_name = frappe.db.sql(""" select parent as parent from `tabPayment Entry Reference` where reference_name = '{invoice}' """.format(invoice=doc.name),as_dict=1)
    # for g in pe_name :
    #    pe = frappe.get_doc('Payment Entry', g.parent)
    #    frappe.throw(pe)
    # loan = frappe.db.get_value('Loan', {'invoice': doc.name}, ['name'])
    # loan1 = frappe.get_doc('Loan', loan)
    # loan1.cancel()

    # Accounting Periods
    accounting_periods = frappe.db.sql("""
                                    SELECT
                                        `tabAccounting Period`.start_date as start,
                                        `tabAccounting Period`.end_date as end
                                        
                                    FROM
                                        `tabAccounting Period` join `tabClosed Document` on `tabClosed Document`.parent = `tabAccounting Period`.name
                                    WHERE
                                       `tabClosed Document`.document_type = 'Sales Invoice'
                                       and `tabClosed Document`.closed = 0
                                    """, as_dict=1)
    for x in accounting_periods:
        if getdate(x.start) <= getdate(doc.posting_date) and getdate(x.end) >= getdate(doc.posting_date):
            frappe.throw("لا يمكن إلغاء فواتير خلال الفترات المحاسبية المغلقة")

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
