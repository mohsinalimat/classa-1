# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters, columns)
    return columns, data


def get_columns():
    return [
        {
            "label": _("الفاتورة"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 110
        },
        {
            "label": _("التاريخ"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("اسم العميل"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 220
        },
        {
            "label": _("مجموعة العميل"),
            "fieldname": "customer_group",
            "fieldtype": "Data",
            "width": 150
        },
		{
			"label": _("الفرع"),
			"fieldname": "branch",
			"fieldtype": "Data",
			"width": 90
		},
		{
			"label": _("المنطقة"),
			"fieldname": "territory",
			"fieldtype": "Data",
			"width": 90
		},
		{
			"label": _("عنوان العميل"),
			"fieldname": "customer_address",
			"options": "Data",
			"width": 200
		},
        {
            "label": _("إجمالي المبلغ"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": _("مندوب المبيعات"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 220
        },
        {
            "label": _("السائق"),
            "fieldname": "driver",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": _("منشأ بواسطة"),
            "fieldname": "owner",
            "fieldtype": "Data",
            "width": 240
        },
    ]


def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " and `tabSales Invoice`.posting_date>=%(from_date)s"
    if filters.get("to_date"):
        conditions += " and `tabSales Invoice`.posting_date<=%(to_date)s"
    if filters.get("user"):
        conditions += " and `tabSales Invoice`.owner=%(user)s"

    result = []
    item_results = frappe.db.sql("""
            SELECT 
                `tabSales Invoice`.name as name,
                `tabSales Invoice`.posting_date as posting_date,
                `tabSales Invoice`.customer as customer,
                `tabSales Invoice`.customer_group as customer_group,
                `tabSales Invoice`.branch as branch,
                `tabSales Invoice`.territory as territory,
                `tabSales Invoice`.customer_address as customer_address,
                `tabSales Invoice`.grand_total as grand_total,
                `tabSales Invoice`.sales_person as sales_person,
                (Select `tabDriver`.full_name from `tabDriver` where `tabSales Invoice`.driver = `tabDriver`.name) as driver,
                (Select `tabUser`.full_name from `tabUser` where `tabSales Invoice`.owner = `tabUser`.name) as owner
                
               

            FROM
                `tabSales Invoice`
            WHERE
                `tabSales Invoice`.docstatus = 1
                {conditions}

            ORDER BY `tabSales Invoice`.posting_date desc
            """.format(conditions=conditions), filters, as_dict=1)

    if item_results:
        for item_dict in item_results:
            data = {
                'name': item_dict.name,
                'posting_date': item_dict.posting_date,
                'customer': item_dict.customer,
                'customer_group': item_dict.customer_group,
                'branch': item_dict.branch,
                'territory': item_dict.territory,
                'customer_address': item_dict.customer_address,
                'grand_total': item_dict.grand_total,
                'sales_person': item_dict.sales_person,
                'driver': item_dict.driver,
                'owner': item_dict.owner,
            }
            result.append(data)
    return result

