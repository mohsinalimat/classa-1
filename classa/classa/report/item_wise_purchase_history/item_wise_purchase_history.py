# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt


def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    data = get_data(filters, columns)
    return columns, data


def get_columns():
    return [
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 60
        },
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 250
		},
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 150
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "float",
            "width": 80
        },
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Data",
			"width": 90
		},
        {
            "label": _("Rate"),
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 100
        },
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Data",
			"width": 160
		},
        {
            "label": _("Purchase Order"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Purchase Order",
            "width": 170
        },
        {
            "label": _("Date"),
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            "width": 100
        },
    ]


def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " and transaction_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " and transaction_date <= %(to_date)s"
    if filters.get("item_code"):
        conditions += "and po_item.item_code = %(item_code)s"
    if filters.get("item_group"):
        conditions += "and po_item.item_group = %(item_group)s"

    result = []
    item_results = frappe.db.sql("""
        	select
				po_item.item_code as item_code,
				po_item.item_name as item_name,
				po_item.item_group as item_group,
				po_item.qty as qty,
				po_item.uom as uom,
				po_item.base_rate as rate,
				po_item.base_amount as amount,
				po_item.warehouse as warehouse,
				po.name as name,
				po.transaction_date as transaction_date,
				sup.supplier_name as supplier_name
			from
				`tabPurchase Order` po, `tabPurchase Order Item` po_item, `tabSupplier` sup
			where
				po.name = po_item.parent and po.supplier = sup.name and po.docstatus = 1
				{conditions}
			order by po.name desc
        """.format(conditions=conditions), filters, as_dict=1)

    for item_dict in item_results:
        data = {
            'item_code': item_dict.item_code,
            'item_name': item_dict.item_name,
            'item_group': item_dict.item_group,
            'qty': item_dict.qty,
            'uom': item_dict.uom,
            'rate': item_dict.rate,
            'amount': item_dict.amount,
            'warehouse': item_dict.warehouse,
            'name': item_dict.name,
            'transaction_date': item_dict.transaction_date,
        }
        result.append(data)
    return result