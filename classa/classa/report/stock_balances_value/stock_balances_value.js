// Copyright (c) 2022, ERPCloud.Systems and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Balances Value"] = {
		"filters": [
       {
			fieldname: "parent_item_group",
			label: __("Parent Item Group"),
			fieldtype: "Select",
			options: ["","سلع مستوردة", "سلع محلية"],
		},

	]
}