# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    columns = get_columns(filters)
    data = get_data(filters, columns)
    return columns, data


def get_columns(filters):
    if not filters.get("group_by_item_group"):
        return [
            {
                "label": _("الكود"),
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                "width": 70,
            },
            {
                "label": _("اسم الصنف"),
                "fieldname": "item_name",
                "fieldtype": "Data",
                "width": 300,
            },
            {
                "label": _("أول المدة"),
                "fieldname": "opening_carton",
                "fieldtype": "Float",
                "width": 130,
            },
            {
                "label": _("أوامر التوريد"),
                "fieldname": "po_carton",
                "fieldtype": "Float",
                "width": 100,
            },
            {
                "label": _("المشتريات"),
                "fieldname": "pinv_carton1",
                "fieldtype": "Float",
                "width": 110,
            },
            {
                "label": _("المرتجعات"),
                "fieldname": "pinv_return",
                "fieldtype": "Float",
                "width": 110,
            },
            {
                "label": _("صافي المشتريات"),
                "fieldname": "pinv_carton",
                "fieldtype": "Float",
                "width": 120,
            },
            {
                "label": _("بونص"),
                "fieldname": "pinv_carton2",
                "fieldtype": "Float",
                "width": 110,
            },
            {
                "label": _("المشتريات %"),
                "fieldname": "p_percent",
                "fieldtype": "Percent",
                "width": 100,
            },
            {
                "label": _("متوسط سعر الشراء"),
                "fieldname": "avg_rate",
                "fieldtype": "Currency",
                "width": 130,
            },
            {
                "label": _("إجمالي المشتريات"),
                "fieldname": "amount",
                "fieldtype": "Currency",
                "width": 130,
            },
            {
                "label": _("أوامر البيع"),
                "fieldname": "so_carton",
                "fieldtype": "Float",
                "width": 100,
            },
            {
                "label": _("المبيعات"),
                "fieldname": "sinv_carton",
                "fieldtype": "Float",
                "width": 110,
            },
            {
                "label": _("المبيعات %"),
                "fieldname": "s_percent",
                "fieldtype": "Percent",
                "width": 100,
            },
            {
                "label": _("اخر المدة"),
                "fieldname": "closing_carton",
                "fieldtype": "Float",
                "width": 130,
            },
        ]

    if filters.get("group_by_item_group"):
        return [
            {
                "label": _("مجموعة الصنف"),
                "fieldname": "item_group",
                "fieldtype": "Link",
                "options": "Item Group",
                "width": 250,
            },
            {
                "label": _("أول المدة"),
                "fieldname": "opening_carton",
                "fieldtype": "Float",
                "width": 130,
            },
            {
                "label": _("أوامر التوريد"),
                "fieldname": "po_carton",
                "fieldtype": "Float",
                "width": 100,
            },
            {
                "label": _("المشتريات"),
                "fieldname": "pinv_carton1",
                "fieldtype": "Float",
                "width": 110,
            },
            {
                "label": _("المرتجعات"),
                "fieldname": "pinv_return",
                "fieldtype": "Float",
                "width": 110,
            },
            {
                "label": _("صافي المشتريات"),
                "fieldname": "pinv_carton",
                "fieldtype": "Float",
                "width": 120,
            },
            {
                "label": _("بونص"),
                "fieldname": "pinv_carton2",
                "fieldtype": "Float",
                "width": 110,
            },
            {
                "label": _("المشتريات %"),
                "fieldname": "p_percent",
                "fieldtype": "Percent",
                "width": 100,
            },
            {
                "label": _("إجمالي المشتريات"),
                "fieldname": "amount",
                "fieldtype": "Currency",
                "width": 130,
            },
            {
                "label": _("أوامر البيع"),
                "fieldname": "so_carton",
                "fieldtype": "Float",
                "width": 100,
            },
            {
                "label": _("المبيعات"),
                "fieldname": "sinv_carton",
                "fieldtype": "Float",
                "width": 110,
            },
            {
                "label": _("المبيعات %"),
                "fieldname": "s_percent",
                "fieldtype": "Percent",
                "width": 100,
            },
            {
                "label": _("اخر المدة"),
                "fieldname": "closing_carton",
                "fieldtype": "Float",
                "width": 130,
            },
        ]


def get_data(filters, columns):
    item_price_qty_data = []
    item_price_qty_data = get_item_price_qty_data(filters)
    return item_price_qty_data


def get_item_price_qty_data(filters):
    to_date = filters.get("to_date")
    from_date = filters.get("from_date")
    item_group = filters.get("item_group")

    result = []
    if not filters.get("group_by_item_group"):
        if not filters.get("item_group"):
            frappe.throw("Please Select An Item Group")
        item_uom = frappe._dict(
            frappe.db.sql(
                """
            SELECT 
                item.name,
               ifnull(tabuom.conversion_factor, 1)
            FROM `tabUOM Conversion Detail` tabuom
            JOIN `tabItem` item ON tabuom.parent =  item.item_code
            WHERE tabuom.uom = 'كرتونه' 
            """
            )
        )
        pinv1 = frappe._dict(
            frappe.db.sql(
                """         select
                                            `tabPurchase Invoice Item`.item_code,
                                            ifnull(sum(`tabPurchase Invoice Item`.stock_qty), 0) as stock_qty
                                       from 
                                            `tabPurchase Invoice Item` join `tabPurchase Invoice` on `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                                       where 
                                           `tabPurchase Invoice`.docstatus = 1
                                           and `tabPurchase Invoice Item`.stock_qty >0
                                           and `tabPurchase Invoice Item`.rate >0
                                   """,
                as_dict=0,
            )
        )
        po = frappe._dict(
            frappe.db.sql(
                """ select 
                                            `tabPurchase Order Item`.item_code,
                                            ifnull(sum(`tabPurchase Order Item`.stock_qty), 0) as stock_qty
                                       from 
                                            `tabPurchase Order Item` join `tabPurchase Order` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
                                       where 
                                           `tabPurchase Order`.docstatus = 1
                                           and `tabPurchase Order`.transaction_date between '{from_date}' and '{to_date}'
                                   """.format(
                    from_date=from_date, to_date=to_date
                )
            )
        )
        item_results = frappe.db.sql(
            """
                SELECT
                    `tabItem`.item_code as item_code,
                    `tabItem`.item_name as item_name,
                    `tabItem`.item_group as item_group,
                    (select ifnull(conversion_factor, 1) from `tabUOM Conversion Detail` where uom = 'كرتونه' and parent = `tabItem`.item_code) as carton_cf,
                    `tabItem`.name as name,
                    ifnull(`tabStock Ledger Entry`.qty_after_transaction, 0) as qty_after_transaction

                FROM
                    `tabItem`
                LEFT JOIN
                    `tabStock Ledger Entry` ON  `tabStock Ledger Entry`.item_code = `tabItem`.name
                JOIN 
                    `tabWarehouse` ON `tabStock Ledger Entry`.warehouse = `tabWarehouse`.name
                WHERE
                    `tabItem`.disabled = 0
                    and `tabWarehouse`.warehouse_type = 'مخزون سلعي' 

                    and `tabItem`.is_sales_item = 1
                    and `tabItem`.item_group = "{item_group}"
                    and `tabStock Ledger Entry`.posting_date <= '{from_date}'
                    and `tabStock Ledger Entry`.is_cancelled = 0
                """.format(
                item_group=item_group,
                from_date=from_date,
            ),
            filters,
            as_dict=1,
        )

        if item_results:
            for item_dict in item_results:
                data = {
                    "item_code": item_dict.item_code,
                    "item_name": item_dict.item_name,
                }
                data["opening_carton"] = item_uom.get(item_dict.name)
                data["po_carton"] = po.get(item_dict.item_code)
                opening_qty = item_dict.qty_after_transaction
                # opening_qty = 0
                # opening_qty += y.qty_after_transaction / y.cartoon_cf
                # warehouses = frappe.db.sql(
                #     """select name as name from `tabWarehouse` where disabled = 0 and warehouse_type = 'مخزون سلعي' """,
                #     as_dict=1,
                # )
                # data['opening_carton'] = opening_qty
                itemo = item_dict.item_code
                # for x in warehouses:

                # warehouseo = x.name
                # opening = frappe.db.sql(
                #     """
                #                             select
                #                                  ifnull(qty_after_transaction, 0) as qty_after_transaction,
                #                                  (select ifnull(conversion_factor, 1) from `tabUOM Conversion Detail` where uom = 'كرتونه' and parent = '{itemo}') as cartoon_cf
                #                             from `tabStock Ledger Entry` join `tabItem` on `tabStock Ledger Entry`.item_code = '{itemo}'
                #                             where
                #                                 `tabStock Ledger Entry`.item_code = '{itemo}'
                #                                  and `tabStock Ledger Entry`.posting_date <= '{from_date}'
                #                                  and `tabStock Ledger Entry`.warehouse = '{warehouseo}'
                #                                  and `tabStock Ledger Entry`.is_cancelled = 0
                #                             ORDER BY `tabStock Ledger Entry`.posting_date DESC, `tabStock Ledger Entry`.posting_time DESC, `tabStock Ledger Entry`.creation DESC LIMIT 1
                #                         """.format(
                #         itemo=itemo, from_date=from_date, warehouseo=warehouseo
                #     ),
                #     as_dict=1,
                # )
                # for y in opening:

                pinv = frappe.db.sql(
                    """ select 
                                            ifnull(sum(`tabPurchase Invoice Item`.stock_qty), 0) as stock_qty,
                                            ifnull(sum(`tabPurchase Invoice Item`.base_amount), 0) as amount
                                       from 
                                            `tabPurchase Invoice Item` join `tabPurchase Invoice` on `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                                       where 
                                           `tabPurchase Invoice`.docstatus = 1
                                           and `tabPurchase Invoice Item`.item_code = '{itemo}'
                                           and `tabPurchase Invoice`.posting_date between '{from_date}' and '{to_date}'
                                   """.format(
                        itemo=itemo, from_date=from_date, to_date=to_date
                    ),
                    as_dict=0,
                )
                pinv1 = frappe.db.sql(
                    """ select 
                                            ifnull(sum(`tabPurchase Invoice Item`.stock_qty), 0) as stock_qty
                                       from 
                                            `tabPurchase Invoice Item` join `tabPurchase Invoice` on `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                                       where 
                                           `tabPurchase Invoice`.docstatus = 1
                                           and `tabPurchase Invoice Item`.stock_qty >0
                                           and `tabPurchase Invoice Item`.rate >0
                                   """,
                    as_dict=0,
                )
                pinv2 = frappe.db.sql(
                    """ select 
                                            ifnull(sum(`tabPurchase Invoice Item`.stock_qty), 0) as stock_qty
                                       from 
                                            `tabPurchase Invoice Item` join `tabPurchase Invoice` on `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                                       where 
                                           `tabPurchase Invoice`.docstatus = 1
                                           and `tabPurchase Invoice Item`.stock_qty >0
                                           and `tabPurchase Invoice Item`.rate =0
                                           and `tabPurchase Invoice Item`.item_code = '{itemo}'
                                           and `tabPurchase Invoice`.posting_date between '{from_date}' and '{to_date}'
                                   """.format(
                        itemo=itemo, from_date=from_date, to_date=to_date
                    ),
                    as_dict=0,
                )

                data["pinv_carton"] = (
                    pinv[0][0] / item_dict.carton_cf
                    if item_dict.carton_cf
                    else pinv[0][0]
                )
                data["pinv_carton1"] = (
                    pinv1[0][0] / item_dict.carton_cf
                    if item_dict.carton_cf
                    else pinv1[0][0]
                )
                data["pinv_carton2"] = (
                    pinv2[0][0] / item_dict.carton_cf
                    if item_dict.carton_cf
                    else pinv2[0][0]
                )
                data["pinv_return"] = data["pinv_carton1"] - data["pinv_carton"]
                data["amount"] = pinv[0][1]
                data["avg_rate"] = (
                    pinv[0][1] * item_dict.carton_cf / pinv[0][0] if pinv[0][0] else 0
                )

                so = frappe.db.sql(
                    """ select 
                                                        ifnull(`tabSales Order Item`.stock_qty, 0) as stock_qty
                                                   from 
                                                        `tabSales Order Item` join `tabSales Order` on `tabSales Order`.name = `tabSales Order Item`.parent
                                                   where 
                                                       `tabSales Order`.docstatus = 1
                                                       and `tabSales Order Item`.item_code = '{itemo}'
                                                       and `tabSales Order`.transaction_date between '{from_date}' and '{to_date}'
                                               """.format(
                        itemo=itemo, from_date=from_date, to_date=to_date
                    ),
                    as_dict=0,
                )

                # data["so_carton"] = (
                #     so[0][0] / item_dict.carton_cf if item_dict.carton_cf else so[0][0]
                # )

                sinv = frappe.db.sql(
                    """ select 
                                            ifnull(sum(`tabSales Invoice Item`.stock_qty), 0) as stock_qty
                                       from 
                                            `tabSales Invoice Item` join `tabSales Invoice` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent
                                       where 
                                           `tabSales Invoice`.docstatus = 1
                                           and `tabSales Invoice Item`.item_code = '{itemo}'
                                           and `tabSales Invoice`.posting_date between '{from_date}' and '{to_date}'
                                   """.format(
                        itemo=itemo, from_date=from_date, to_date=to_date
                    ),
                    as_dict=0,
                )
                data["sinv_carton"] = (
                    sinv[0][0] / item_dict.carton_cf
                    if item_dict.carton_cf
                    else sinv[0][0]
                )
                data["closing_carton"] = (
                    (opening_qty + pinv[0][0] - sinv[0][0]) / item_dict.carton_cf
                    if item_dict.carton_cf
                    else (opening_qty + pinv[0][0] - sinv[0][0])
                )
                # data["p_percent"] = (
                #     100 * (pinv1[0][0] / po[0][0]) if po[0][0] else pinv[0][0]
                # )

                data["p_percent"] = 0
                # data["s_percent"] = (
                #     100 * (sinv[0][0] / so[0][0]) if so[0][0] else sinv[0][0]
                # )

                result.append(data)

    if filters.get("group_by_item_group"):
        conditions = ""
        if filters.get("item_group"):
            conditions = " and `tabItem`.item_group = %(item_group)s "
        item_group_list = frappe.db.sql(
            """
                        SELECT
                            `tabItem`.item_group as item_group,
                            `tabItem`.item_code as item_code,
                            (select ifnull(conversion_factor, 1) from `tabUOM Conversion Detail` where uom = 'كرتونه' and parent = `tabItem`.item_code) as carton_cf
                        FROM
                            `tabItem`
                        WHERE
                            `tabItem`.disabled = 0
                            and `tabItem`.is_sales_item = 1
                            {conditions}
                            
                            
                        GROUP BY `tabItem`.item_group
                        ORDER BY `tabItem`.item_group
                        """.format(
                conditions=conditions
            ),
            filters,
            as_dict=1,
        )

        for y in item_group_list:
            data = {
                "item_group": y.item_group,
            }

            warehouses = frappe.db.sql(
                """select name as name from `tabWarehouse` where disabled = 0 and warehouse_type = 'مخزون سلعي' """,
                as_dict=1,
            )
            opening_qty = 0
            item_groupo = y.item_group
            itemz = y.item_code
            for x in warehouses:
                warehouseo = x.name
                opening = frappe.db.sql(
                    """
                                        select
                                             ifnull(sum(qty_after_transaction), 0) as qty_after_transaction
                                        from `tabStock Ledger Entry` join `tabItem` on `tabStock Ledger Entry`.item_code = '{itemz}'
                                        where
                                            `tabStock Ledger Entry`.item_code = '{itemz}'
                                             and `tabItem`.item_group = '{item_groupo}'
                                             and `tabStock Ledger Entry`.posting_date <= '{from_date}'
                                             and `tabStock Ledger Entry`.warehouse = '{warehouseo}'
                                             and `tabStock Ledger Entry`.is_cancelled = 0
                                        ORDER BY `tabStock Ledger Entry`.posting_date DESC, `tabStock Ledger Entry`.posting_time DESC, `tabStock Ledger Entry`.creation DESC LIMIT 1
                                    """.format(
                        itemz=itemz,
                        item_groupo=item_groupo,
                        from_date=from_date,
                        warehouseo=warehouseo,
                    ),
                    as_dict=1,
                )
                for y in opening:
                    opening_qty += y.qty_after_transaction
            data["opening_carton"] = (
                opening_qty / y.carton_cf if y.carton_cf else opening_qty
            )

            po = frappe.db.sql(
                """ select 
                                                        ifnull(sum(`tabPurchase Order Item`.qty), 0) as stock_qty
                                                   from 
                                                        `tabPurchase Order Item` join `tabPurchase Order` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
                                                   where 
                                                       `tabPurchase Order`.docstatus = 1
                                                       and `tabPurchase Order Item`.item_group = '{item_groupo}'
                                                       and `tabPurchase Order`.transaction_date between '{from_date}' and '{to_date}'
                                               """.format(
                    item_groupo=item_groupo, from_date=from_date, to_date=to_date
                ),
                as_dict=0,
            )

            data["po_carton"] = po[0][0]

            pinv = frappe.db.sql(
                """ select 
                                                        ifnull(sum(`tabPurchase Invoice Item`.qty), 0) as stock_qty,
                                                        ifnull(sum(`tabPurchase Invoice Item`.base_amount), 0) as amount
                                                   from 
                                                        `tabPurchase Invoice Item` join `tabPurchase Invoice` on `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                                                   where 
                                                       `tabPurchase Invoice`.docstatus = 1
                                                       and `tabPurchase Invoice Item`.item_group = '{item_groupo}'
                                                       and `tabPurchase Invoice`.posting_date between '{from_date}' and '{to_date}'
                                               """.format(
                    item_groupo=item_groupo, from_date=from_date, to_date=to_date
                ),
                as_dict=0,
            )
            pinv1 = frappe.db.sql(
                """ select 
                                                        ifnull(sum(`tabPurchase Invoice Item`.qty), 0) as stock_qty
                                                   from 
                                                        `tabPurchase Invoice Item` join `tabPurchase Invoice` on `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                                                   where 
                                                       `tabPurchase Invoice`.docstatus = 1
                                                       and `tabPurchase Invoice Item`.qty >0
                                                       and `tabPurchase Invoice Item`.rate >0
                                                       and `tabPurchase Invoice Item`.item_group = '{item_groupo}'
                                                       and `tabPurchase Invoice`.posting_date between '{from_date}' and '{to_date}'
                                               """.format(
                    item_groupo=item_groupo, from_date=from_date, to_date=to_date
                ),
                as_dict=0,
            )
            pinv2 = frappe.db.sql(
                """ select 
                                                        ifnull(sum(`tabPurchase Invoice Item`.qty), 0) as stock_qty
                                                   from 
                                                        `tabPurchase Invoice Item` join `tabPurchase Invoice` on `tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent
                                                   where 
                                                       `tabPurchase Invoice`.docstatus = 1
                                                       and `tabPurchase Invoice Item`.qty >0
                                                       and `tabPurchase Invoice Item`.rate =0
                                                       and `tabPurchase Invoice Item`.item_group = '{item_groupo}'
                                                       and `tabPurchase Invoice`.posting_date between '{from_date}' and '{to_date}'
                                               """.format(
                    item_groupo=item_groupo, from_date=from_date, to_date=to_date
                ),
                as_dict=0,
            )

            data["pinv_carton"] = pinv[0][0]
            data["pinv_carton1"] = pinv1[0][0]
            data["pinv_carton2"] = pinv2[0][0]
            data["pinv_return"] = data["pinv_carton1"] - data["pinv_carton"]
            data["amount"] = pinv[0][1]
            # data['avg_rate'] = pinv[0][1] * y.carton_cf / pinv[0][0] if pinv[0][0] else 0

            so_cartoon = 0
            so = frappe.db.sql(
                """ select 
                                                                    ifnull(sum(`tabSales Order Item`.qty), 0) as stock_qty,
                                                                    (select ifnull(conversion_factor, 1) from `tabUOM Conversion Detail` where uom = 'كرتونه' and parent = `tabSales Order Item`.item_code) as cartoon_cf
                                                               from 
                                                                    `tabSales Order Item` join `tabSales Order` on `tabSales Order`.name = `tabSales Order Item`.parent
                                                               where 
                                                                   `tabSales Order`.docstatus = 1
                                                                   and `tabSales Order Item`.item_group = '{item_groupo}'
                                                                   and `tabSales Order`.transaction_date between '{from_date}' and '{to_date}'
                                                           """.format(
                    item_groupo=item_groupo, from_date=from_date, to_date=to_date
                ),
                as_dict=0,
            )

            # so_cartoon += so[0][0] / so[0][1]
            # data["so_carton"] = so_cartoon
            # data['so_carton'] = so[0][0] / y.carton_cf if y.carton_cf else so[0][0]

            sinv = frappe.db.sql(
                """ select 
                                                        ifnull(sum(`tabSales Invoice Item`.qty), 0) as stock_qty
                                                   from 
                                                        `tabSales Invoice Item` join `tabSales Invoice` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent
                                                   where 
                                                       `tabSales Invoice`.docstatus = 1
                                                       and `tabSales Invoice Item`.item_group = '{item_groupo}'
                                                       and `tabSales Invoice`.posting_date between '{from_date}' and '{to_date}'
                                               """.format(
                    item_groupo=item_groupo, from_date=from_date, to_date=to_date
                ),
                as_dict=0,
            )

            data["sinv_carton"] = sinv[0][0]
            data["closing_carton"] = opening_qty + pinv[0][0] - sinv[0][0]
            data["p_percent"] = (
                100 * (pinv1[0][0] / po[0][0]) if po[0][0] else pinv[0][0]
            )
            # data["s_percent"] = (
            #     100 * (sinv[0][0] / so[0][0]) if so[0][0] else sinv[0][0]
            # )

            result.append(data)

    return result

