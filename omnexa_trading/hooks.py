app_name = "omnexa_trading"
app_title = "ErpGenEx — Trading"
app_publisher = "ErpGenEx"
app_description = "Trading and POS vertical"
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_core", "omnexa_accounting", "omnexa_customer_core"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "omnexa_trading",
		"logo": "/assets/omnexa_trading/logo.png",
		"title": "Trading",
		"route": "/app/trading-workcenter"
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
	"/assets/omnexa_trading/css/omnexa-journey.css",
]
app_include_js = [
	"/assets/omnexa_trading/js/omnexa-journey.js",
	"/assets/omnexa_trading/js/trading-journey-kit.js",
]

page_js = {
	"trading-workcenter": "public/js/trading-journey-kit.js",
	"trading-executive-dashboard": "public/js/trading-journey-kit.js",
	"trading-operations-desk": "public/js/trading-journey-kit.js",
	"trading-finance-desk": "public/js/trading-journey-kit.js",
	"trading-analytics-dashboard": "public/js/trading-journey-kit.js",
	"trading-customer-portal": "public/js/trading-journey-kit.js",
	"trading-van-sales-pwa": "public/js/trading-journey-kit.js",
	"trading-general-manager": "public/js/trading-journey-kit.js",
	"trading-commercial-director": "public/js/trading-journey-kit.js",
	"trading-warehouse-manager": "public/js/trading-journey-kit.js",
	"trading-purchase-manager": "public/js/trading-journey-kit.js",
	"trading-import-manager": "public/js/trading-journey-kit.js",
	"trading-export-manager": "public/js/trading-journey-kit.js",
	"trading-quality-manager": "public/js/trading-journey-kit.js",
	"trading-cold-chain-manager": "public/js/trading-journey-kit.js",
	"trading-regulatory-officer": "public/js/trading-journey-kit.js",
	"trading-inventory-controller": "public/js/trading-journey-kit.js",
	"trading-sales-director": "public/js/trading-journey-kit.js",
	"trading-auditor": "public/js/trading-journey-kit.js"
	}

# include js, css files in header of web template
web_include_css = "/assets/omnexa_trading/css/trading_website.css"
web_include_js = "/assets/omnexa_trading/js/trading_website.js"

# Public website routes
website_route_rules = [
	{"from_route": "/trading", "to_route": "trading/index"}
]

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

before_install = "omnexa_trading.install.enforce_supported_frappe_version"
before_migrate = "omnexa_trading.install.enforce_supported_frappe_version"
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
	"Trading Installment Contract": "omnexa_trading.permissions.trading_installment_contract_query_conditions"
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
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Vehicle": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Distribution Zone": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Route Plan": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Commission Rule": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Distribution Order": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Vehicle Stock Transfer": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Van Sales Invoice": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Commission Settlement": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Tender": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Trading Installment Contract": {
		"before_validate": "omnexa_trading.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_trading.permissions.enforce_branch_access_for_doc",
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Pharma Batch": {
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"
	},
	"Pharma Quality Inspection": {
		"after_insert": "omnexa_trading.audit_events.log_document_create",
		"on_update": "omnexa_trading.audit_events.log_document_update",
		"on_trash": "omnexa_trading.audit_events.log_document_delete",
		"on_submit": "omnexa_trading.audit_events.log_document_submit",
		"on_cancel": "omnexa_trading.audit_events.log_document_cancel"}
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
		"omnexa_trading.tasks.process_expired_batches",
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
# 		"doctype": "{}",
# 		"filter_by": "{}",
# 		"redact_fields": ["{}", "{}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{}",
# 		"filter_by": "{}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{}"
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

