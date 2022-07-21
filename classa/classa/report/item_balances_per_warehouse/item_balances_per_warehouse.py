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
            "width": 60
        },
        {
            "label": _("اسم الصنف"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 220
        },
		{
			"label": _("مجموعة الصنف"),
			"fieldname": "item_group",
			"fieldtype": "Data",
			"width": 120
		},
        {
            "label": _("معامل التحويل"),
            "fieldname": "conversion_factor",
            "fieldtype": "Float",
            "width": 110
        },
		{
			"label": _("مخزن بدر"),
			"fieldname": "badr_store",
			"fieldtype": "Float",
			"width": 80
		},
        {
            "label": _("مخزن 30"),
            "fieldname": "thirty_store",
            "fieldtype": "Float",
            "width": 80
        },
        {
            "label": _("مخزن التجمع"),
            "fieldname": "tagamo3_store",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("مخزن الاسكندرية"),
            "fieldname": "alex_store",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("مخزن الغردقة"),
            "fieldname": "hurghada_store",
            "fieldtype": "Float",
            "width": 115
        },
        {
            "label": _("مخزن المنصورة"),
            "fieldname": "mansoura_store",
            "fieldtype": "Float",
            "width": 115
        },
        {
            "label": _("الاجمالي"),
            "fieldname": "total",
            "fieldtype": "Float",
            "width": 100
        },
    ]


def get_data(filters, columns):
    item_qty_data = []
    item_qty_data = get_item_qty_data(filters)
    return item_qty_data


def get_item_qty_data(filters):
    conditions = ""
    if filters.get("item_group"):
        conditions += "and `tabItem`.item_group = %(item_group)s"
    item_group = filters.get("item_group")
	
    result = []
    item_results = frappe.db.sql("""
            SELECT
                `tabItem`.item_code as item_code,
                `tabItem`.item_name as item_name,
                `tabItem`.item_group as item_group,
                (select IFNULL(sum(conversion_factor),1) from `tabUOM Conversion Detail` where `tabUOM Conversion Detail`.parent = `tabItem`.item_code and `tabUOM Conversion Detail`.uom = "كرتونه") as uom1,
                (select IFNULL(sum(conversion_factor),1) from `tabUOM Conversion Detail` where `tabUOM Conversion Detail`.parent = `tabItem`.item_code and `tabUOM Conversion Detail`.uom = "علبه") as uom2,
                (select IFNULL(sum(conversion_factor),1) from `tabUOM Conversion Detail` where `tabUOM Conversion Detail`.parent = `tabItem`.item_code and `tabUOM Conversion Detail`.uom = "قطعه") as uom3,
                (select IFNULL(sum(actual_qty),0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن بدر رئيسي - CA") as badr_store,
                (select IFNULL(sum(actual_qty),0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن 30رئيسي - CA") as thirty_store,
                (select IFNULL(sum(actual_qty),0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن التجمع رئيسي - CA") as tagamo3_store,
                (select IFNULL(sum(actual_qty),0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن الأسكندرية رئيسي - CA") as alex_store,
                (select IFNULL(sum(actual_qty),0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن الغردقة رئيسي - CA") as hurghada_store,
                (select IFNULL(sum(actual_qty),0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن المنصورة رئيسي - CA") as mansoura_store
            
            FROM
                `tabItem`
            WHERE
                `tabItem`.disabled = 0
                and `tabItem`.has_variants = 0
                and `tabItem`.is_stock_item = 1
                {conditions}
                ORDER BY `tabItem`.item_code
            """.format(conditions=conditions), filters, as_dict=1)

    
    if item_results:
        for item_dict in item_results:
            if filters.get("uom") == "قطعه":
                data = {
                    'item_code': item_dict.item_code,
                    'item_name': item_dict.item_name,
                    'item_group': item_dict.item_group,
                    'conversion_factor': item_dict.uom3,
                    'badr_store': item_dict.badr_store / item_dict.uom1,
                    'thirty_store': item_dict.thirty_store / item_dict.uom1,
                    'tagamo3_store': item_dict.tagamo3_store / item_dict.uom1,
                    'alex_store': item_dict.alex_store / item_dict.uom1,
                    'hurghada_store': item_dict.hurghada_store / item_dict.uom1,
                    'mansoura_store': item_dict.mansoura_store / item_dict.uom1,
                    'total': (item_dict.mansoura_store + item_dict.hurghada_store + item_dict.alex_store + item_dict.tagamo3_store + item_dict.thirty_store + item_dict.badr_store) / item_dict.uom1,
                }
                result.append(data)

            if filters.get("uom") == "كرتونه":
                data = {
                    'item_code': item_dict.item_code,
                    'item_name': item_dict.item_name,
                    'item_group': item_dict.item_group,
                    'conversion_factor': item_dict.uom1,
                    'badr_store': item_dict.badr_store / item_dict.uom1,
                    'thirty_store': item_dict.thirty_store / item_dict.uom1,
                    'tagamo3_store': item_dict.tagamo3_store / item_dict.uom1,
                    'alex_store': item_dict.alex_store / item_dict.uom1,
                    'hurghada_store': item_dict.hurghada_store / item_dict.uom1,
                    'mansoura_store': item_dict.mansoura_store / item_dict.uom1,
                    'total': (item_dict.mansoura_store + item_dict.hurghada_store + item_dict.alex_store + item_dict.tagamo3_store + item_dict.thirty_store + item_dict.badr_store) / item_dict.uom1,
                }
                result.append(data)

            if filters.get("uom") == "علبه":
                data = {
                    'item_code': item_dict.item_code,
                    'item_name': item_dict.item_name,
                    'item_group': item_dict.item_group,
                    'conversion_factor': item_dict.uom2,
                    'badr_store': item_dict.badr_store / item_dict.uom2,
                    'thirty_store': item_dict.thirty_store / item_dict.uom2,
                    'tagamo3_store': item_dict.tagamo3_store / item_dict.uom2,
                    'alex_store': item_dict.alex_store / item_dict.uom2,
                    'hurghada_store': item_dict.hurghada_store / item_dict.uom2,
                    'mansoura_store': item_dict.mansoura_store / item_dict.uom2,
                    'total': (item_dict.mansoura_store + item_dict.hurghada_store + item_dict.alex_store + item_dict.tagamo3_store + item_dict.thirty_store + item_dict.badr_store) / item_dict.uom2,
                }
                result.append(data)

    return result