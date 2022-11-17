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
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 60
        },
        {
            "label": _("Barcode"),
            "fieldname": "barcode",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 270
        },
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Buying Price List"),
            "fieldname": "buying_price_list",
            "fieldtype": "Currency",
            "width": 135
        },
        {
            "label": _("Price List A"),
            "fieldname": "price_list_a",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Profit A"),
            "fieldname": "profit_a",
            "fieldtype": "Currency",
            "width": 80
        },
        {
            "label": _("Price List B"),
            "fieldname": "price_list_b",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Profit B"),
            "fieldname": "profit_b",
            "fieldtype": "Currency",
            "width": 80
        },
        {
            "label": _("Price List C"),
            "fieldname": "price_list_c",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Profit C"),
            "fieldname": "profit_c",
            "fieldtype": "Currency",
            "width": 80
        }
    ]


def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
    conditions = ""
    if filters.get("item_group"):
        conditions += " and `tabItem`.item_group=%(item_group)s"

    result = []
    item_results = frappe.db.sql("""
            SELECT 
                `tabItem`.item_code as item_code, 
                `tabItem`.item_name as item_name,
                `tabItem`.item_group as item_group,
                (select barcode from `tabItem Barcode` where parent = `tabItem`.item_code) as barcode,
                (select max(price_list_rate) from `tabItem Price` where `tabItem Price`.item_code = `tabItem`.item_code and `tabItem Price`.buying = 1) as buying_price_list,
                (select max(price_list_rate) from `tabItem Price` where `tabItem Price`.item_code = `tabItem`.item_code and `tabItem Price`.price_list = "A") as price_list_a,
                (select max(price_list_rate) from `tabItem Price` where `tabItem Price`.item_code = `tabItem`.item_code and `tabItem Price`.price_list = "B") as price_list_b,
                (select max(price_list_rate) from `tabItem Price` where `tabItem Price`.item_code = `tabItem`.item_code and `tabItem Price`.price_list = "C") as price_list_c
            FROM
                `tabItem`
            WHERE
                `tabItem`.disabled = 0
                and `tabItem`.is_sales_item = 1
                {conditions}     
            ORDER BY `tabItem`.item_code
            """.format(conditions=conditions), filters, as_dict=1)

    if item_results:
        for item_dict in item_results:
            data = {
                'item_code': item_dict.item_code,
                'item_name': item_dict.item_name,
                'item_group': item_dict.item_group,
                'barcode': item_dict.barcode,
                'buying_price_list': item_dict.buying_price_list if item_dict.buying_price_list else 0,
                'price_list_a': item_dict.price_list_a if item_dict.price_list_a else 0,
                'price_list_b': item_dict.price_list_b if item_dict.price_list_b else 0,
                'price_list_c': item_dict.price_list_c if item_dict.price_list_c else 0,
                'profit_a': (item_dict.price_list_a if item_dict.price_list_a else 0) - (item_dict.buying_price_list if item_dict.buying_price_list else 0),
                'profit_b': (item_dict.price_list_b if item_dict.price_list_b else 0) - (item_dict.buying_price_list if item_dict.buying_price_list else 0),
                'profit_c': (item_dict.price_list_c if item_dict.price_list_c else 0) - (item_dict.buying_price_list if item_dict.buying_price_list else 0),
            }
            result.append(data)
    return result

