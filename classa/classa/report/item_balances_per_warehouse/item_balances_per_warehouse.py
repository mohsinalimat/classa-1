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
            "label": _("مخزن التجمع الصناعية رئيسي"),
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
    # item = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": "5576", "warehouse" : "مخزن بدر رئيسي - CA"})
    # print(item.qty_after_transaction)
    result = []
    item_results = frappe.db.sql("""
            SELECT
                `tabItem`.item_code as item_code,
                `tabItem`.item_name as item_name,
                `tabItem`.item_group as item_group,
                (select IFNULL(sum(conversion_factor),1) from `tabUOM Conversion Detail` where `tabUOM Conversion Detail`.parent = `tabItem`.item_code and `tabUOM Conversion Detail`.uom = "كرتونه") as uom1,
                (select IFNULL(sum(conversion_factor),1) from `tabUOM Conversion Detail` where `tabUOM Conversion Detail`.parent = `tabItem`.item_code and `tabUOM Conversion Detail`.uom = "علبه") as uom2,
                (select IFNULL(sum(conversion_factor),1) from `tabUOM Conversion Detail` where `tabUOM Conversion Detail`.parent = `tabItem`.item_code and `tabUOM Conversion Detail`.uom = "قطعه") as uom3,
                (select IFNULL(actual_qty,0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن التجمع الصناعية رئيسي - CA") as thirty_store,
                (select IFNULL(actual_qty,0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن التجمع رئيسي - CA") as tagamo3_store,
                (select IFNULL(actual_qty,0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن الأسكندرية رئيسي - CA") as alex_store,
                (select IFNULL(actual_qty,0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن بدر رئيسي - CA") as badr_store,
                (select IFNULL(actual_qty,0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن الغردقة رئيسي - CA") as hurghada_store,
                (select IFNULL(actual_qty,0) from `tabBin` where `tabBin`.item_code = `tabItem`.item_code and `tabBin`.warehouse = "مخزن المنصورة رئيسي - CA") as mansoura_store

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
                badr = float(0)
                thirty = float(0)
                tagamo3 = float(0)
                alex = float(0)
                hurghada = float(0)
                mansoura = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن بدر رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن بدر رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        badr = d.qty_after_transaction
                    if badr < 0:
                        badr = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن التجمع الصناعية رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن التجمع الصناعية رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        thirty = d.qty_after_transaction
                    if thirty < 0:
                        thirty = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن التجمع رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن التجمع رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        tagamo3 = d.qty_after_transaction
                    if tagamo3 < 0:
                        tagamo3 = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن الأسكندرية رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن الأسكندرية رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        alex = d.qty_after_transaction
                    if alex < 0:
                        alex = float(0)

                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن الغردقة رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن الغردقة رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        hurghada = d.qty_after_transaction
                    if hurghada < 0:
                        hurghada = float(0)

                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن المنصورة رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن المنصورة رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        mansoura = d.qty_after_transaction
                    if mansoura < 0:
                        mansoura = float(0)


                data = {
                    'item_code': item_dict.item_code,
                    'item_name': item_dict.item_name,
                    'item_group': item_dict.item_group,
                    'conversion_factor': item_dict.uom3,
                    'badr_store': float(badr) / float(item_dict.uom3),
                    'thirty_store': float(thirty) / float(item_dict.uom3),
                    'tagamo3_store': float(tagamo3) / float(item_dict.uom3),
                    'alex_store': float(alex) / float(item_dict.uom3),
                    'hurghada_store': float(hurghada) / float(item_dict.uom3),
                    'mansoura_store': float(mansoura) / float(item_dict.uom3),
                    'total': ( float(badr) + float(thirty) + float(tagamo3) + float(alex) + float(hurghada) + float(mansoura) ) / float(item_dict.uom3) ,
                }
                result.append(data)


            if filters.get("uom") == "كرتونه":
                badr = float(0)
                thirty = float(0)
                tagamo3 = float(0)
                alex = float(0)
                hurghada = float(0)
                mansoura = float(0)

                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن بدر رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن بدر رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        badr = d.qty_after_transaction
                    if badr < 0:
                        badr = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن التجمع الصناعية رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن التجمع الصناعية رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        thirty = d.qty_after_transaction
                    if thirty < 0:
                        thirty = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن التجمع رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن التجمع رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        tagamo3 = d.qty_after_transaction
                    if tagamo3 < 0:
                        tagamo3 = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن الأسكندرية رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن الأسكندرية رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        alex = d.qty_after_transaction
                    if alex < 0:
                        alex = float(0)

                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن الغردقة رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن الغردقة رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        hurghada = d.qty_after_transaction
                    if hurghada < 0:
                        hurghada = float(0)

                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن المنصورة رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن المنصورة رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        mansoura = d.qty_after_transaction
                    if mansoura < 0:
                        mansoura = float(0)

                data = {
                    'item_code': item_dict.item_code,
                    'item_name': item_dict.item_name,
                    'item_group': item_dict.item_group,
                    'conversion_factor': item_dict.uom1,
                    'badr_store': float(badr) / item_dict.uom1,
                    'thirty_store': float(thirty) / item_dict.uom1,
                    'tagamo3_store': float(tagamo3) / item_dict.uom1,
                    'alex_store': float(alex) / item_dict.uom1,
                    'hurghada_store': float(hurghada) / item_dict.uom1,
                    'mansoura_store': float(mansoura) / item_dict.uom1,
                    'total': ( float(badr) + float(thirty) + float(tagamo3) + float(alex) + float(hurghada) + float(mansoura) ) / float(item_dict.uom1) ,
                }
                result.append(data)

            if filters.get("uom") == "علبه":
                badr = float(0)
                thirty = float(0)
                tagamo3 = float(0)
                alex = float(0)
                hurghada = float(0)
                mansoura = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن بدر رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن بدر رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        badr = d.qty_after_transaction
                    if badr < 0:
                        badr = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن التجمع الصناعية رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن التجمع الصناعية رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        thirty = d.qty_after_transaction
                    if thirty < 0:
                        thirty = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن التجمع رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن التجمع رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        tagamo3 = d.qty_after_transaction
                    if tagamo3 < 0:
                        tagamo3 = float(0)


                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن الأسكندرية رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن الأسكندرية رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        alex = d.qty_after_transaction
                    if alex < 0:
                        alex = float(0)

                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن الغردقة رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن الغردقة رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        hurghada = d.qty_after_transaction
                    if hurghada < 0:
                        hurghada = float(0)

                if frappe.db.exists("Stock Ledger Entry", {"item_code": item_dict.item_code, "warehouse": "مخزن المنصورة رئيسي - CA"}):
                    d = frappe.get_last_doc('Stock Ledger Entry', filters={"item_code": item_dict.item_code,
                    "warehouse" : "مخزن المنصورة رئيسي - CA"})
                    if d:
                        # hurghada = d[0]['qty_after_transaction']
                        mansoura = d.qty_after_transaction
                    if mansoura < 0:
                        mansoura = float(0)

                data = {
                    'item_code': item_dict.item_code,
                    'item_name': item_dict.item_name,
                    'item_group': item_dict.item_group,
                    'conversion_factor': item_dict.uom2,
                    'badr_store': float(badr) / item_dict.uom2,
                    'thirty_store': float(thirty) / item_dict.uom2,
                    'tagamo3_store': float(tagamo3) / item_dict.uom2,
                    'alex_store': float(alex) / item_dict.uom2,
                    'hurghada_store': float(hurghada) / item_dict.uom2,
                    'mansoura_store': float(mansoura) / item_dict.uom2,
                    'total': ( float(badr) + float(thirty) + float(tagamo3) + float(alex) + float(hurghada) + float(mansoura) ) / float(item_dict.uom2) ,
                }
                result.append(data)

    return result
