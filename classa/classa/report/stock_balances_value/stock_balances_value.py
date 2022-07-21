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
            "label": _("الكود"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 70
        },
		{
			"label": _("باركود"),
			"fieldname": "barcode",
			"fieldtype": "Data",
			"width": 150
		},
        {
            "label": _("اسم الصنف"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 300
        },
    
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Link",
			"options": "Item Group",
            "width": 160
        },
		{
			"label": _("Parent Item Group"),
			"fieldname": "parent_item_group",
			"fieldtype": "Data",
			"width": 160
		},
        {
            "label": _("قطعة"),
            "fieldname": "uom1",
            "fieldtype": "Float",
            "width": 70
        },
		{
			"label": _("علبه"),
			"fieldname": "uom2",
			"fieldtype": "Float",
			"width": 70
		},
		{
			"label": _("كرتونة"),
			"fieldname": "uom3",
			"fieldtype": "Float",
			"width": 70
		},
		{
			"label": _("Value"),
			"fieldname": "value",
			"fieldtype": "Float",
			"width": 90
		},
		{
			"label": _("Total Value"),
			"fieldname": "total_value",
			"fieldtype": "Float",
			"width": 110
		},
		{
			"label": _("Reserved Qty"),
			"fieldname": "reserved_qty",
			"fieldtype": "Float",
			"width": 110
		},
		{
			"label": _("Ordered Qty"),
			"fieldname": "ordered_qty",
			"fieldtype": "Float",
			"width": 110
		},
		{
			"label": _("Requested Qty"),
			"fieldname": "requested_qty",
			"fieldtype": "Float",
			"width": 110
		},
		{
			"label": _("Projected Qty"),
			"fieldname": "projected_qty",
			"fieldtype": "Float",
			"width": 110
		},
    ]


def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
	conditions = ""
	if filters.get("parent_item_group") == "سلع محلية":
		conditions += "and `tabItem Group`.parent_item_group in ('فود لاين','سلع محلية', 'اوليـــــــس','ماجيستك')"
	if filters.get("parent_item_group") == "سلع مستوردة":
		conditions += "and `tabItem Group`.parent_item_group = 'سلع مستوردة' "

	result = []
	item_results = frappe.db.sql("""
            select  
				 `tabItem`.item_code as item_code,
				 `tabItem`.item_name as item_name,
				 `tabItem Group`.parent_item_group as parent_item_group,
				 (select barcode from `tabItem Barcode` where parent = `tabItem`.item_code) as barcode,
				 `tabItem`.item_group as item_group,
				 (select IFNULL(sum(`tabBin`.actual_qty),0) from `tabBin` where tabBin.item_code = tabItem.item_code) as uom1,
				 IFNULL(((select sum(`tabBin`.actual_qty) from `tabBin` where tabBin.item_code = tabItem.item_code)/(select conversion_factor from `tabUOM Conversion Detail` where uom = 'علبه' and parent = tabItem.item_code)),0) as uom2,
				 IFNULL(((select sum(`tabBin`.actual_qty) from `tabBin` where tabBin.item_code = tabItem.item_code)/(select conversion_factor from `tabUOM Conversion Detail` where uom = 'كرتونه' and parent = tabItem.item_code)),0) as uom3,
				 (select IFNULL(max(`tabBin`.valuation_rate),0) from `tabBin` where tabBin.item_code = tabItem.item_code) as value,
				 ((select IFNULL(sum(`tabBin`.actual_qty),0) from `tabBin` where tabBin.item_code = tabItem.item_code) *(select IFNULL(avg(tabBin.valuation_rate),0) from `tabBin` where tabBin.item_code = tabItem.item_code)) as total_value,
				 (select IFNULL(sum(`tabBin`.reserved_qty),0) from `tabBin` where tabBin.item_code = tabItem.item_code) as reserved_qty,
				 (select IFNULL(sum(`tabBin`.ordered_qty),0) from `tabBin` where tabBin.item_code = tabItem.item_code) as ordered_qty,
				 (select IFNULL(sum(`tabBin`.indented_qty),0) from `tabBin` where tabBin.item_code = tabItem.item_code) as requested_qty,
				 (select IFNULL(sum(`tabBin`.projected_qty),0) from `tabBin` where tabBin.item_code = tabItem.item_code) as projected_qty
				from
				`tabItem` join `tabItem Group` on `tabItem Group`.name = `tabItem`.item_group
				where
				tabItem.has_variants = 0
				 {conditions}
            """.format(conditions=conditions), filters, as_dict=1)

	if item_results:
		for item_dict in item_results:
			data = {
				'item_code': item_dict.item_code,
				'item_name': item_dict.item_name,
				'barcode': item_dict.barcode,
				'item_group': item_dict.item_group,
				'parent_item_group': item_dict.parent_item_group,
				'uom1': item_dict.uom1,
				'uom2': item_dict.uom2,
				'uom3': item_dict.uom3,
				'value': item_dict.value,
				'total_value': item_dict.total_value,
				'reserved_qty': item_dict.reserved_qty,
				'ordered_qty': item_dict.ordered_qty,
				'projected_qty': item_dict.projected_qty,
				'requested_qty': item_dict.requested_qty,
			}
			result.append(data)
	return result
