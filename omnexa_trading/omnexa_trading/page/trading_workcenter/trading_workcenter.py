import frappe
from frappe import _

def get_context(context):
    """
    Build context for Commerce/Trading Workcenter
    Includes all role-based portals with dynamic addition capability
    """
    # Get all commerce roles
    commerce_roles = get_commerce_roles()
    
    # Build portal cards for each role
    portal_cards = []
    for role in commerce_roles:
        portal_card = {
            "role": role["role_id"],
            "role_name": role["role_name"],
            "portal_name": role["portal_name"],
            "portal_url": role["portal_url"],
            "icon": role["icon"],
            "description": role["description"],
            "color": role.get("color", "#9C27B0")
        }
        portal_cards.append(portal_card)
    
    # Get dynamic roles (custom added roles)
    dynamic_roles = get_dynamic_commerce_roles()
    
    # Add dynamic role cards
    for role in dynamic_roles:
        portal_card = {
            "role": role["role_id"],
            "role_name": role["role_name"],
            "portal_name": role["portal_name"],
            "portal_url": role["portal_url"],
            "icon": role.get("icon", "dashboard"),
            "description": role.get("description", ""),
            "color": role.get("color", "#9C27B0"),
            "is_dynamic": True
        }
        portal_cards.append(portal_card)
    
    context.portal_cards = portal_cards
    context.show_add_portal = True
    context.application_name = "Commerce"
    context.application_color = "#9C27B0"
    context.total_portals = len(portal_cards)
    
    return context


def get_commerce_roles():
    """
    Get all standard commerce roles with their portal information
    """
    return [
        {
            "role_id": "commerce_sales",
            "role_name": "Sales",
            "portal_name": "Sales Portal",
            "portal_url": "/app/trading-operations-desk",
            "icon": "trending_up",
            "description": "Manage sales orders, quotations, and customer relationships",
            "color": "#2196F3"
        },
        {
            "role_id": "commerce_pos_cashier",
            "role_name": "POS Cashier",
            "portal_name": "POS Portal",
            "portal_url": "/app/trading-van-sales-pwa",
            "icon": "point_of_sale",
            "description": "Manage point of sale transactions and customer checkout",
            "color": "#4CAF50"
        },
        {
            "role_id": "commerce_warehouse",
            "role_name": "Warehouse",
            "portal_name": "Warehouse Portal",
            "portal_url": "/app/trading-operations-desk",
            "icon": "warehouse",
            "description": "Manage warehouse operations, stock, and inventory",
            "color": "#FF9800"
        },
        {
            "role_id": "commerce_purchasing",
            "role_name": "Purchasing",
            "portal_name": "Purchasing Portal",
            "portal_url": "/app/trading-operations-desk",
            "icon": "shopping_cart",
            "description": "Manage purchase orders, suppliers, and procurement",
            "color": "#9C27B0"
        },
        {
            "role_id": "commerce_inventory",
            "role_name": "Inventory",
            "portal_name": "Inventory Portal",
            "portal_url": "/app/trading-operations-desk",
            "icon": "inventory_2",
            "description": "Manage inventory items, stock levels, and movements",
            "color": "#F44336"
        },
        {
            "role_id": "commerce_customer_service",
            "role_name": "Customer Service",
            "portal_name": "Customer Service Portal",
            "portal_url": "/app/trading-customer-portal",
            "icon": "support_agent",
            "description": "Manage customer support, tickets, and returns",
            "color": "#FF5722"
        },
        {
            "role_id": "commerce_finance",
            "role_name": "Finance",
            "portal_name": "Finance Portal",
            "portal_url": "/app/trading-finance-desk",
            "icon": "account_balance",
            "description": "Manage financial records, accounting, and payments",
            "color": "#3F51B5"
        },
        {
            "role_id": "commerce_hr",
            "role_name": "HR",
            "portal_name": "HR Portal",
            "portal_url": "/app/trading-executive-dashboard",
            "icon": "people",
            "description": "Manage staff, leaves, recruitment, and HR operations",
            "color": "#E91E63"
        },
        {
            "role_id": "commerce_branch_manager",
            "role_name": "Branch Manager",
            "portal_name": "Branch Manager Portal",
            "portal_url": "/app/trading-executive-dashboard",
            "icon": "store",
            "description": "Manage branch operations, staff, and local administration",
            "color": "#795548"
        },
        {
            "role_id": "commerce_general_manager",
            "role_name": "General Manager",
            "portal_name": "General Manager Portal",
            "portal_url": "/app/trading-executive-dashboard",
            "icon": "business",
            "description": "Manage company operations, branches, and overall administration",
            "color": "#607D8B"
        },
        {
            "role_id": "commerce_system_administrator",
            "role_name": "System Administrator",
            "portal_name": "System Administrator Portal",
            "portal_url": "/app/trading-workcenter",
            "icon": "admin_panel_settings",
            "description": "Manage system settings, users, and technical administration",
            "color": "#424242"
        }
    ]


def get_dynamic_commerce_roles():
    """
    Get dynamically added commerce roles from database
    """
    try:
        # Get custom roles that start with commerce_
        dynamic_roles = frappe.db.sql("""
            SELECT 
                role_name,
                role_id,
                portal_name,
                portal_url,
                icon,
                description,
                color
            FROM `tabCommerce Dynamic Role`
            WHERE is_active = 1
            ORDER BY creation
        """, as_dict=True)
        
        return dynamic_roles
    except Exception as e:
        frappe.log_error(f"Error fetching dynamic commerce roles: {e}")
        return []


@frappe.whitelist()
def add_dynamic_commerce_role(role_data):
    """
    Add a new dynamic commerce role and portal
    """
    try:
        # Create new dynamic role
        dynamic_role = frappe.get_doc({
            "doctype": "Commerce Dynamic Role",
            "role_id": role_data.get("role_id"),
            "role_name": role_data.get("role_name"),
            "portal_name": role_data.get("portal_name"),
            "portal_url": role_data.get("portal_url"),
            "icon": role_data.get("icon", "dashboard"),
            "description": role_data.get("description", ""),
            "color": role_data.get("color", "#9C27B0"),
            "is_active": 1
        })
        
        dynamic_role.insert()
        
        # Create corresponding role in Frappe if it doesn't exist
        if not frappe.db.exists("Role", role_data.get("role_id")):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": role_data.get("role_id"),
                "desk_access": 1
            }).insert()
        
        return {
            "success": True,
            "message": "Dynamic role added successfully",
            "role": dynamic_role.role_id
        }
    except Exception as e:
        frappe.log_error(f"Error adding dynamic commerce role: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def remove_dynamic_commerce_role(role_id):
    """
    Remove a dynamic commerce role
    """
    try:
        # Get the dynamic role
        dynamic_role = frappe.get_doc("Commerce Dynamic Role", {"role_id": role_id})
        
        if dynamic_role:
            # Mark as inactive instead of deleting
            dynamic_role.is_active = 0
            dynamic_role.save()
            
            return {
                "success": True,
                "message": "Dynamic role removed successfully"
            }
        else:
            return {
                "success": False,
                "message": "Role not found"
            }
    except Exception as e:
        frappe.log_error(f"Error removing dynamic commerce role: {e}")
        return {
            "success": False,
            "message": str(e)
        }


@frappe.whitelist()
def get_commerce_workcenter_stats():
    """
    Get statistics for commerce workcenter
    """
    try:
        stats = {
            "total_portals": len(get_commerce_roles()) + len(get_dynamic_commerce_roles()),
            "active_users": frappe.db.count("User", {"enabled": 1}),
            "today_sales": frappe.db.count("Sales Order", {"transaction_date": frappe.utils.today()}),
            "active_customers": frappe.db.count("Customer", {"status": "Active"})
        }
        
        return stats
    except Exception as e:
        frappe.log_error(f"Error fetching commerce workcenter stats: {e}")
        return {}
