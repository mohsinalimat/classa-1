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
			"width": 170
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 280
		},
		{
			"label": _("Sales Invoice"),
			"fieldname": "sales_invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150
		},
		{
			"label": _("Status"),
			"fieldname": "docstatus",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Total"),
			"fieldname": "grand_total",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Remarks"),
			"fieldname": "remarks",
			"fieldtype": "Data",
			"width": 260
		}
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
	item_results = frappe.db.sql("""
			SELECT 
			`tabSales Invoice`.name as name,
			`tabSales Invoice`.customer as customer,
			`tabSales Invoice`.posting_date as posting_date,
			`tabSales Invoice`.remarks as remarks,
			`tabSales Invoice`.grand_total as grand_total,
			`tabSales Invoice`.status as status
			FROM
				`tabSales Invoice`
			WHERE
				
				`tabSales Invoice`.docstatus = 1
				and `tabSales Invoice`.posting_date between '{from_date}' and '{to_date}'
				and `tabSales Invoice`.return_against is null
				
				{conditions} 
			
			""".format(conditions=conditions, from_date=from_date, to_date=to_date), filters, as_dict=1)
	
	if item_results:
		for item_dict in item_results:
			data = {
				'posting_date': item_dict.posting_date,
				'customer': item_dict.customer,
				'sales_invoice': item_dict.name,
				'docstatus': item_dict.status,
				'remarks': item_dict.remarks,
				
			}
			item_results2 = frappe.db.sql("""
							SELECT 
							
							`tabSales Invoice`.grand_total as grand_total,
							`tabSales Invoice`.docstatus as docstatus
							FROM
								`tabSales Invoice`
							WHERE
								
								`tabSales Invoice`.docstatus = 1
								and `tabSales Invoice`.return_against = '{name}'
								and `tabSales Invoice`.is_return = 1
								{conditions} 
							
							""".format(name = item_dict.name, conditions=conditions, from_date=from_date, to_date=to_date), filters, as_dict=1)
			if item_results2:
				for s in item_results2:
					data['grand_total'] = item_dict.grand_total + s.grand_total if item_dict.grand_total and s.grand_total else item_dict.grand_total
			else:
				data['grand_total'] = item_dict.grand_total




			result.append(data)


	
	return result
