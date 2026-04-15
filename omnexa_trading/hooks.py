app_name = "omnexa_trading"
app_title = "ErpGenEx — Trading"
app_publisher = "Omnexa"
app_description = "Trading and POS vertical"
app_email = "dev@omnexa.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core", "omnexa_accounting", "omnexa_customer_core"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "omnexa_trading",
		"logo": "/assets/omnexa_trading/trading.svg",
		"title": "Trading",
		"route": "/app/trading",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/omnexa_trading/css/omnexa_trading.css"
# app_include_js = "/assets/omnexa_trading/js/omnexa_trading.js"

# include js, css files in header of web template
# web_include_css = "/assets/omnexa_trading/css/omnexa_trading.css"
# web_include_js = "/assets/omnexa_trading/js/omnexa_trading.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omnexa_trading/public/scss/website"

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

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "omnexa_trading/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "omnexa_trading.utils.jinja_methods",
# 	"filters": "omnexa_trading.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "omnexa_trading.install.before_install"
# after_install = "omnexa_trading.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "omnexa_trading.uninstall.before_uninstall"
# after_uninstall = "omnexa_trading.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "omnexa_trading.utils.before_app_install"
# after_app_install = "omnexa_trading.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "omnexa_trading.utils.before_app_uninstall"
# after_app_uninstall = "omnexa_trading.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "omnexa_trading.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Trading Sales Representative": "omnexa_trading.permissions.trading_sales_representative_query_conditions",
	"Trading Vehicle": "omnexa_trading.permissions.trading_vehicle_query_conditions",
	"Distribution Zone": "omnexa_trading.permissions.distribution_zone_query_conditions",
	"Trading Route Plan": "omnexa_trading.permissions.trading_route_plan_query_conditions",
	"Trading Commission Rule": "omnexa_trading.permissions.trading_commission_rule_query_conditions",
	"Trading Distribution Order": "omnexa_trading.permissions.trading_distribution_order_query_conditions",
	"Trading Vehicle Stock Transfer": "omnexa_trading.permissions.trading_vehicle_stock_transfer_query_conditions",
	"Trading Van Sales Invoice": "omnexa_trading.permissions.trading_van_sales_invoice_query_conditions",
	"Trading Commission Settlement": "omnexa_trading.permissions.trading_commission_settlement_query_conditions",
	"Trading Tender": "omnexa_trading.permissions.trading_tender_query_conditions",
	"Trading Installment Contract": "omnexa_trading.permissions.trading_installment_contract_query_conditions",
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Trading Sales Representative": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Vehicle": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Distribution Zone": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Route Plan": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Commission Rule": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Distribution Order": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Vehicle Stock Transfer": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Van Sales Invoice": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Commission Settlement": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Tender": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
	"Trading Installment Contract": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"omnexa_trading.tasks.all"
# 	],
# 	"daily": [
# 		"omnexa_trading.tasks.daily"
# 	],
# 	"hourly": [
# 		"omnexa_trading.tasks.hourly"
# 	],
# 	"weekly": [
# 		"omnexa_trading.tasks.weekly"
# 	],
# 	"monthly": [
# 		"omnexa_trading.tasks.monthly"
# 	],
# }
scheduler_events = {
	"daily": [
		"omnexa_trading.tasks.process_installment_overdue_penalties",
	]
}

# Testing
# -------

# before_tests = "omnexa_trading.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omnexa_trading.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omnexa_trading.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["omnexa_trading.license_gate.before_request"]
# after_request = ["omnexa_trading.utils.after_request"]

# Job Events
# ----------
# before_job = ["omnexa_trading.utils.before_job"]
# after_job = ["omnexa_trading.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"omnexa_trading.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

