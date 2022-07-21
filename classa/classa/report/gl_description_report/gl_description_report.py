# Copyright (c) 2013, erpcloud.systems and contributors
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
            "label": _("Journal Entry"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Journal Entry",
            "width": 200
        },

        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 200
        },



        {
            "label": _("Debit"),
            "fieldname": "debit",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Credit"),
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Cost Center"),
            "fieldname": "cost_center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 200
        },

		{
			"label": _("Description"),
			"fieldname": "description",
			"fieldtype": "Small text",
			"width": 200
		}

    ]


def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " and `tabJournal Entry`.posting_date>=%(from_date)s"
    if filters.get("to_date"):
        conditions += " and `tabJournal Entry`.posting_date<=%(to_date)s"

    if filters.get("account"):
        conditions += " and `tabJournal Entry Account`.account = %(account)s"
    if filters.get("cost_center"):
        conditions += " and `tabJournal Entry Account`.cost_center = %(cost_center)s"
    if filters.get("name"):
        conditions += " and `tabJournal Entry`.name = %(name)s"
    item_results = frappe.db.sql("""
				select
						`tabJournal Entry`.name as name,
						`tabJournal Entry`.posting_date as posting_date,
						`tabJournal Entry Account`.account as account,
						`tabJournal Entry Account`.debit as debit,
						`tabJournal Entry Account`.credit as credit,
						`tabJournal Entry Account`.cost_center as cost_center,
						`tabJournal Entry Account`.description as description

				from
				`tabJournal Entry` join `tabJournal Entry Account` on `tabJournal Entry`.name = `tabJournal Entry Account`.parent

				where
				`tabJournal Entry`.docstatus = 1
				{conditions}

                order by
				`tabJournal Entry`.posting_date asc



				""".format(conditions=conditions), filters, as_dict=1)

    # price_list_names = list(set([item.price_list_name for item in item_results]))

    # buying_price_map = get_price_map(price_list_names, buying=1)
    # selling_price_map = get_price_map(price_list_names, selling=1)

    result = []
    if item_results:
        for item_dict in item_results:
            data = {
                'name': item_dict.name,
                'posting_date': _(item_dict.posting_date),
                'description': _(item_dict.description),
                'account': _(item_dict.account),
                'debit': item_dict.debit,
                'credit': item_dict.credit,
                'cost_center': item_dict.cost_center,
            }
            result.append(data)

    return result
