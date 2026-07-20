#!/usr/bin/env python
import frappe
import random

def create_demo_suppliers():
    """Create 100 demo suppliers for pharmaceutical distribution"""
    
    # Local Egyptian Suppliers
    local_suppliers = [
        "Eva Pharma", "Amoun", "EIPICO", "MUP", "CID", "Pharco", "UPM",
        "Global Napi", "Rameda", "Kahira Pharma", "Egyptian International Pharmaceutical Industries",
        "Arab Drug Company", "Chemipharm", "Pharco B", "Pharco C", "Pharco D",
        "Nile Pharmaceuticals", "Alexandria Pharmaceuticals", "Delta Pharmaceuticals",
        "Giza Pharmaceuticals", "Cairo Pharmaceuticals", "Misr Pharmaceuticals",
        "El-Nile Pharmaceuticals", "El-Kahera Pharmaceuticals", "El-Arab Pharmaceuticals"
    ]
    
    # International Suppliers
    international_suppliers = [
        "Pfizer", "Novartis", "Sanofi", "AstraZeneca", "GSK", "Julphar", "Hikma",
        "Bayer", "Roche", "Merck", "Johnson & Johnson", "Abbott", "Teva",
        "Boehringer Ingelheim", "Bristol-Myers Squibb", "Eli Lilly", "GlaxoSmithKline",
        "Novo Nordisk", "Astellas", "Takeda", "Daiichi Sankyo", "Otsuka",
        "Mitsubishi Tanabe", "Eisai", "Shionogi", "Ono Pharmaceutical", "Sumitomo Pharma"
    ]
    
    # Additional suppliers to reach 100
    additional_suppliers = []
    for i in range(1, 51):
        additional_suppliers.append(f"International Pharma Supplier {i}")
    
    all_suppliers = local_suppliers + international_suppliers + additional_suppliers
    
    created_count = 0
    for i, supplier_name in enumerate(all_suppliers, 1):
        try:
            if frappe.db.exists("Supplier", supplier_name):
                print(f"Supplier already exists: {supplier_name}")
                continue
                
            supplier = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": supplier_name,
                "supplier_type": "International" if i > 30 else "Local",
                "country": "Egypt" if i <= 30 else random.choice(["USA", "Germany", "Switzerland", "UK", "France", "Japan", "India", "UAE"]),
                "supplier_group": "Pharmaceutical Manufacturers",
                "credit_limit": random.randint(1000000, 10000000),
                "payment_terms": "Net 30" if random.random() > 0.5 else "Net 60",
                "tax_id": f"EG{random.randint(100000000, 999999999)}" if i <= 30 else f"INT{random.randint(100000000, 999999999)}",
                "is_internal_supplier": 0
            })
            supplier.insert()
            created_count += 1
            print(f"Created supplier {i}: {supplier_name}")
        except Exception as e:
            print(f"Error creating supplier {supplier_name}: {e}")
    
    print(f"Total suppliers created: {created_count}")
    return created_count

def create_demo_customers():
    """Create 250 demo customers"""
    
    customer_types = {
        "Pharmacy": 150,
        "Drug Store": 50,
        "Hospital": 20,
        "Clinic": 15,
        "Medical Center": 10,
        "Company": 3,
        "Wholesaler": 2
    }
    
    cities = ["Cairo", "Alexandria", "Giza", "Mansoura", "Tanta", "Assiut", "Luxor", "Aswan", "Port Said", "Ismailia"]
    
    # Get the next available customer code sequence
    last_customer = frappe.db.sql("SELECT customer_code FROM tabCustomer WHERE customer_code LIKE 'CUST-%' ORDER BY customer_code DESC LIMIT 1", as_dict=True)
    if last_customer:
        last_seq = int(last_customer[0].customer_code.split('-')[1])
        customer_seq = last_seq + 1
    else:
        customer_seq = 1
    
    customer_count = 0
    
    for customer_type, count in customer_types.items():
        for i in range(1, count + 1):
            try:
                customer_name = f"{customer_type} {i} - {random.choice(cities)} - {random.randint(1000, 9999)}"
                
                if frappe.db.exists("Customer", customer_name):
                    print(f"Customer already exists: {customer_name}")
                    customer_seq += 1
                    continue
                
                customer = frappe.get_doc({
                    "doctype": "Customer",
                    "customer_name": customer_name,
                    "customer_type": "Individual" if customer_type in ["Pharmacy", "Drug Store", "Clinic"] else "Company",
                    "customer_group": customer_type,
                    "territory": random.choice(["Egypt - North", "Egypt - South", "Egypt - East", "Egypt - West"]),
                    "credit_limit": random.randint(50000, 500000),
                    "payment_terms": "Net 30" if random.random() > 0.5 else "Net 45",
                    "tax_id": f"CUST{random.randint(100000000, 999999999)}",
                    "is_internal_customer": 0,
                    "customer_code": f"CUST-{customer_seq:05d
	}"
                })
                customer.insert()
                customer_count += 1
                customer_seq += 1
                print(f"Created customer {customer_count}: {customer_name}")
            except Exception as e:
                print(f"Error creating customer {customer_name}: {e}")
                customer_seq += 1
    
    print(f"Total customers created: {customer_count}")
    return customer_count

def create_demo_warehouses():
    """Create specialized warehouses"""
    
    # Get the first company in the system
    company = frappe.db.get_value("Company", {}, "name")
    if not company:
        print("No company found in the system. Please create a company first.")
        return 0
    
    warehouses = [
        {"warehouse_name": "Main Warehouse - Cairo", "warehouse_type": "Main"
	},
        {"warehouse_name": "Cold Warehouse - Cairo", "warehouse_type": "Sub"
	},
        {"warehouse_name": "Controlled Drugs Warehouse", "warehouse_type": "Sub"
	},
        {"warehouse_name": "Returns Warehouse", "warehouse_type": "Sub"
	},
        {"warehouse_name": "Damaged Warehouse", "warehouse_type": "Sub"
	},
        {"warehouse_name": "Quarantine Warehouse", "warehouse_type": "Sub"
	},
        {"warehouse_name": "Branch Warehouse - Alexandria", "warehouse_type": "Sub"
	},
        {"warehouse_name": "Branch Warehouse - Giza", "warehouse_type": "Sub"
	},
        {"warehouse_name": "Pharmacy Warehouse - Downtown", "warehouse_type": "POS"
	},
        {"warehouse_name": "Pharmacy Warehouse - Maadi", "warehouse_type": "POS"
	}
    ]
    
    created_count = 0
    existing_count = 0
    for warehouse in warehouses:
        try:
            if frappe.db.exists("Warehouse", warehouse["warehouse_name"]):
                print(f"Warehouse already exists: {warehouse['warehouse_name']}")
                existing_count += 1
                continue
                
            # Find the next available warehouse code
            last_wh = frappe.db.sql("SELECT warehouse_code FROM tabWarehouse WHERE warehouse_code LIKE 'WH-%' ORDER BY warehouse_code DESC LIMIT 1", as_dict=True)
            if last_wh:
                last_seq = int(last_wh[0].warehouse_code.split('-')[1])
                warehouse_seq = last_seq + 1
            else:
                warehouse_seq = 1
                
            wh = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": warehouse["warehouse_name"],
                "warehouse_type": warehouse["warehouse_type"],
                "is_group": 0,
                "company": company,
                "warehouse_code": f"WH-{warehouse_seq:03d
	}"
            })
            wh.insert()
            created_count += 1
            print(f"Created warehouse: {warehouse['warehouse_name']}")
        except Exception as e:
            print(f"Error creating warehouse {warehouse['warehouse_name']}: {e}")
    
    print(f"Total warehouses created: {created_count}")
    print(f"Total warehouses already existing: {existing_count}")
    return created_count

def create_demo_item_groups():
    """Create pharmaceutical item groups"""
    
    # Check if All Item Groups exists
    parent_group = "All Item Groups"
    if not frappe.db.exists("Item Group", parent_group):
        print(f"Parent item group '{parent_group}' does not exist. Creating without parent.")
        parent_group = None
    
    groups = [
        "Antibiotics",
        "Analgesics",
        "Antihypertensives",
        "Antidiabetics",
        "Cardiovascular",
        "Respiratory",
        "Gastrointestinal",
        "Dermatological",
        "Vitamins & Supplements",
        "Vaccines",
        "Oncology",
        "Psychiatric",
        "Neurological",
        "Hormonal",
        "Antiviral"
    ]
    
    created_count = 0
    for group_name in groups:
        try:
            if frappe.db.exists("Item Group", group_name):
                print(f"Item Group already exists: {group_name}")
                continue
                
            group_data = {
                "doctype": "Item Group",
                "item_group_name": group_name,
                "is_group": 0
            }
            if parent_group:
                group_data["parent_item_group"] = parent_group
                
            group = frappe.get_doc(group_data)
            group.insert()
            created_count += 1
            print(f"Created item group: {group_name}")
        except Exception as e:
            print(f"Error creating item group {group_name}: {e}")
    
    print(f"Total item groups created: {created_count}")
    return created_count

def run_demo_data_creation():
    """Run all demo data creation functions"""
    print("=" * 50)
    print("Creating Demo Data for Omnexa Trading")
    print("=" * 50)
    
    print("\n1. Creating item groups...")
    item_groups = create_demo_item_groups()
    
    print("\n2. Creating demo suppliers...")
    suppliers = create_demo_suppliers()
    
    print("\n3. Creating demo customers...")
    customers = create_demo_customers()
    
    print("\n4. Creating specialized warehouses...")
    warehouses = create_demo_warehouses()
    
    print("\n" + "=" * 50)
    print("Demo Data Creation Summary")
    print("=" * 50)
    print(f"Item Groups: {item_groups}")
    print(f"Suppliers: {suppliers}")
    print(f"Customers: {customers}")
    print(f"Warehouses: {warehouses}")
    print("=" * 50)
