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
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 170,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 280,
        },
        {
            "label": _("Sales Invoice"),
            "fieldname": "sales_invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 150,
        },
        {
            "label": _("Status"),
            "fieldname": "docstatus",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Total"),
            "fieldname": "grand_total",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": _("Remarks"),
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 260,
        },
    ]


def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
    conditions = ""
    if filters.get("customer"):
        conditions += " and `tabSales Invoice`.customer=%(customer)s"

    to_date = filters.get("to_date")
    from_date = filters.get("from_date")

    result = []
    item_results = frappe.db.sql(
        """
			SELECT 
			sales_invoice1.name as sales_invoice,
			sales_invoice1.customer as customer,
			sales_invoice1.posting_date as posting_date,
			sales_invoice1.remarks as remarks,
			sales_invoice1.status as docstatus,
            IF (sales_invoice1.grand_total and sales_invoice2.grand_total, sales_invoice1.grand_total+ sales_invoice2.grand_total, sales_invoice1.grand_total) as grand_total
			FROM
				`tabSales Invoice` sales_invoice1
            LEFT JOIN
                `tabSales Invoice` sales_invoice2 ON sales_invoice1.name = sales_invoice2.return_against
			WHERE
				sales_invoice1.docstatus = 1
				and sales_invoice1.posting_date between '{from_date}' and '{to_date}'
				
				{conditions} 
			
			""".format(
            conditions=conditions, from_date=from_date, to_date=to_date
        ),
        filters,
        as_dict=1,
    )

    return item_results

