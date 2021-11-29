from . import __version__ as app_version

app_name = "classa"
app_title = "Classa"
app_publisher = "ERPCloud.Systems"
app_description = "classa Customizations "
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "info@erpcloud.systems"
app_license = "MIT"



doc_events = {
"Quotation": {
	"validate": "classa.functions.quotation_validate",
	"before_submit": "classa.functions.quotation_submit"
},
"Sales Order": {
	"before_submit": "classa.functions.sales_order_validate"
},
"Material Request": {
	"after_insert": "classa.permission.share_mr"
}
}


# Includes in <head>
# ------------------
# include js, css files in header of desk.html
# app_include_css = "/assets/classa/css/classa.css"
# app_include_js = "/assets/classa/js/classa.js"

# include js, css files in header of web template
# web_include_css = "/assets/classa/css/classa.css"
# web_include_js = "/assets/classa/js/classa.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "classa/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "classa.install.before_install"
# after_install = "classa.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "classa.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"classa.tasks.all"
# 	],
# 	"daily": [
# 		"classa.tasks.daily"
# 	],
# 	"hourly": [
# 		"classa.tasks.hourly"
# 	],
# 	"weekly": [
# 		"classa.tasks.weekly"
# 	]
# 	"monthly": [
# 		"classa.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "classa.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "classa.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "classa.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"classa.auth.validate"
# ]

