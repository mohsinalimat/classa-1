// Copyright (c) 2022, ERPCloud.Systems and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Balances Per Warehouse"] = {
		"filters": [

        {
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group",
		
		},
	{
			fieldname: "uom",
			label: __("UOM"),
			fieldtype: "Select",
			options: ["قطعه", "كرتونه","علبه"],
			default: "قطعه",
		},

	]
}