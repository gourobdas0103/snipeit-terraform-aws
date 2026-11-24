#!/usr/bin/env python3
"""
Snipe-IT REST API Automation Script
Populates foundational ITAM data and sample assets in Snipe-IT.

Requirements:
    pip install requests

Usage:
    python populate_assets_api.py --url "http://<EC2_PUBLIC_IP>:8000" --token "<API_BEARER_TOKEN>"
"""

import argparse
import sys
import requests

def create_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def post_resource(base_url: str, endpoint: str, payload: dict, headers: dict) -> dict:
    url = f"{base_url.rstrip('/')}/api/v1/{endpoint}"
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code in [200, 201]:
        data = resp.json()
        if data.get("status") == "success":
            return data.get("payload", {})
        else:
            print(f"[!] Warning on {endpoint}: {data.get('messages')}")
            # Try to get existing resource if already created
            return {}
    else:
        print(f"[-] Failed {endpoint} ({resp.status_code}): {resp.text}")
        return {}

def get_or_create(base_url: str, endpoint: str, search_name: str, payload: dict, headers: dict) -> int:
    # First search if exists
    search_url = f"{base_url.rstrip('/')}/api/v1/{endpoint}?search={search_name}&limit=1"
    res = requests.get(search_url, headers=headers)
    if res.status_code == 200:
        rows = res.json().get("rows", [])
        for row in rows:
            if row.get("name", "").lower() == search_name.lower():
                print(f"[+] Found existing {endpoint}: {search_name} (ID: {row.get('id')})")
                return row.get("id")

    # If not found, create it
    created = post_resource(base_url, endpoint, payload, headers)
    item_id = created.get("id")
    print(f"[+] Created {endpoint}: {search_name} (ID: {item_id})")
    return item_id

def main():
    parser = argparse.ArgumentParser(description="Populate Snipe-IT IT Assets via REST API")
    parser.add_argument("--url", required=True, help="Snipe-IT base URL (e.g. http://54.x.x.x:8000)")
    parser.add_argument("--token", required=True, help="Personal Access API Token")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    headers = create_headers(args.token)

    print("====================================================================")
    print("           Snipe-IT IT Asset Management Population Script           ")
    print("====================================================================")
    print(f"Target URL: {base_url}\n")

    # 1. Company
    print("--> 1. Creating Company...")
    company_id = get_or_create(base_url, "companies", "Acme Global Technologies", {
        "name": "Acme Global Technologies"
    }, headers)

    # 2. Locations
    print("\n--> 2. Creating Locations...")
    loc_head_id = get_or_create(base_url, "locations", "Head Office", {
        "name": "Head Office",
        "city": "Bengaluru",
        "country": "India"
    }, headers)

    loc_branch_id = get_or_create(base_url, "locations", "Branch Office", {
        "name": "Branch Office",
        "city": "Mumbai",
        "country": "India"
    }, headers)

    # 3. Department
    print("\n--> 3. Creating Department...")
    dept_id = get_or_create(base_url, "departments", "IT Operations", {
        "name": "IT Operations",
        "company_id": company_id,
        "location_id": loc_head_id
    }, headers)

    # 4. Suppliers
    print("\n--> 4. Creating Suppliers...")
    sup_dell_id = get_or_create(base_url, "suppliers", "Dell Technologies Direct", {
        "name": "Dell Technologies Direct",
        "contact": "Corporate Sales",
        "email": "enterprise-sales@dell.com"
    }, headers)

    sup_insight_id = get_or_create(base_url, "suppliers", "Insight Enterprises", {
        "name": "Insight Enterprises",
        "contact": "Account Management",
        "email": "orders@insight.com"
    }, headers)

    # 5. Manufacturers
    print("\n--> 5. Creating Manufacturers...")
    mfg_dell_id = get_or_create(base_url, "manufacturers", "Dell", {"name": "Dell"}, headers)
    mfg_hp_id   = get_or_create(base_url, "manufacturers", "HP", {"name": "HP"}, headers)
    mfg_len_id  = get_or_create(base_url, "manufacturers", "Lenovo", {"name": "Lenovo"}, headers)
    mfg_log_id  = get_or_create(base_url, "manufacturers", "Logitech", {"name": "Logitech"}, headers)

    # 6. Categories
    print("\n--> 6. Creating Categories...")
    cat_laptops_id  = get_or_create(base_url, "categories", "Laptops", {
        "name": "Laptops",
        "category_type": "asset"
    }, headers)

    cat_desktops_id = get_or_create(base_url, "categories", "Desktops", {
        "name": "Desktops",
        "category_type": "asset"
    }, headers)

    cat_servers_id  = get_or_create(base_url, "categories", "Servers", {
        "name": "Servers",
        "category_type": "asset"
    }, headers)

    cat_access_id   = get_or_create(base_url, "categories", "Accessories", {
        "name": "Accessories",
        "category_type": "consumable"
    }, headers)

    # 7. Custom Fields and Fieldset
    print("\n--> 7. Configuring Custom Fields & 'Hardware Specs' Fieldset...")
    field_cpu_id = get_or_create(base_url, "fields", "CPU", {
        "name": "CPU",
        "element": "text",
        "format": "ANY"
    }, headers)

    field_ram_id = get_or_create(base_url, "fields", "RAM", {
        "name": "RAM",
        "element": "text",
        "format": "ANY"
    }, headers)

    field_storage_id = get_or_create(base_url, "fields", "Storage", {
        "name": "Storage",
        "element": "text",
        "format": "ANY"
    }, headers)

    fieldset_id = get_or_create(base_url, "fieldsets", "Hardware Specs", {
        "name": "Hardware Specs"
    }, headers)

    # 8. Status Label (Ready to Deploy)
    print("\n--> 8. Checking Status Label...")
    res_status = requests.get(f"{base_url}/api/v1/statuslabels?search=Ready%20to%20Deploy", headers=headers)
    status_rtd_id = 1
    if res_status.status_code == 200 and res_status.json().get("rows"):
        status_rtd_id = res_status.json()["rows"][0]["id"]

    # 9. Asset Models
    print("\n--> 9. Creating Asset Models...")
    model_lat_id = get_or_create(base_url, "models", "Latitude 5440", {
        "name": "Latitude 5440",
        "model_number": "LAT-5440-01",
        "manufacturer_id": mfg_dell_id,
        "category_id": cat_laptops_id,
        "fieldset_id": fieldset_id
    }, headers)

    model_hp_id = get_or_create(base_url, "models", "EliteBook 840 G10", {
        "name": "EliteBook 840 G10",
        "model_number": "EB-840-G10",
        "manufacturer_id": mfg_hp_id,
        "category_id": cat_laptops_id,
        "fieldset_id": fieldset_id
    }, headers)

    model_think_id = get_or_create(base_url, "models", "ThinkPad T14 Gen 4", {
        "name": "ThinkPad T14 Gen 4",
        "model_number": "TP-T14-G4",
        "manufacturer_id": mfg_len_id,
        "category_id": cat_laptops_id,
        "fieldset_id": fieldset_id
    }, headers)

    model_opti_id = get_or_create(base_url, "models", "OptiPlex 7010 Micro", {
        "name": "OptiPlex 7010 Micro",
        "model_number": "OPT-7010-MFF",
        "manufacturer_id": mfg_dell_id,
        "category_id": cat_desktops_id,
        "fieldset_id": fieldset_id
    }, headers)

    model_r660_id = get_or_create(base_url, "models", "PowerEdge R660", {
        "name": "PowerEdge R660",
        "model_number": "PE-R660-1U",
        "manufacturer_id": mfg_dell_id,
        "category_id": cat_servers_id,
        "fieldset_id": fieldset_id
    }, headers)

    # 10. Create 5 Sample Hardware Assets
    print("\n--> 10. Populating 5 Sample Assets...")
    assets_data = [
        {
            "name": "Dell Latitude 5440",
            "asset_tag": "IT-00001",
            "model_id": model_lat_id,
            "status_id": status_rtd_id,
            "serial": "8XK29M1",
            "company_id": company_id,
            "rtd_location_id": loc_head_id,
            "supplier_id": sup_dell_id,
            "purchase_cost": "1250.00",
            "warranty_months": 36,
            "purchase_date": "2024-01-15",
            "notes": "Specs: Intel Core i7-1365U, 32GB DDR5, 1TB NVMe SSD"
        },
        {
            "name": "HP EliteBook 840 G10",
            "asset_tag": "IT-00002",
            "model_id": model_hp_id,
            "status_id": status_rtd_id,
            "serial": "5CD3419K7X",
            "company_id": company_id,
            "rtd_location_id": loc_branch_id,
            "supplier_id": sup_insight_id,
            "purchase_cost": "1320.00",
            "warranty_months": 36,
            "purchase_date": "2024-02-10",
            "notes": "Specs: Intel Core i7-1370P, 32GB DDR5, 512GB NVMe SSD"
        },
        {
            "name": "Lenovo ThinkPad T14 Gen 4",
            "asset_tag": "IT-00003",
            "model_id": model_think_id,
            "status_id": status_rtd_id,
            "serial": "PF489KL2",
            "company_id": company_id,
            "rtd_location_id": loc_head_id,
            "supplier_id": sup_insight_id,
            "purchase_cost": "1180.00",
            "warranty_months": 36,
            "purchase_date": "2024-03-01",
            "notes": "Specs: AMD Ryzen 7 PRO 7840U, 16GB LPDDR5x, 512GB SSD"
        },
        {
            "name": "Dell OptiPlex 7010 Micro",
            "asset_tag": "IT-00004",
            "model_id": model_opti_id,
            "status_id": status_rtd_id,
            "serial": "3NQ78P2",
            "company_id": company_id,
            "rtd_location_id": loc_head_id,
            "supplier_id": sup_dell_id,
            "purchase_cost": "890.00",
            "warranty_months": 24,
            "purchase_date": "2024-03-15",
            "notes": "Specs: Intel Core i5-13500, 16GB DDR5, 512GB SSD"
        },
        {
            "name": "Dell PowerEdge R660",
            "asset_tag": "IT-00005",
            "model_id": model_r660_id,
            "status_id": status_rtd_id,
            "serial": "9PL44R1",
            "company_id": company_id,
            "rtd_location_id": loc_head_id,
            "supplier_id": sup_dell_id,
            "purchase_cost": "6500.00",
            "warranty_months": 60,
            "purchase_date": "2024-04-01",
            "notes": "Specs: 2x Intel Xeon Silver 4410Y, 128GB DDR5 ECC, 4x 1.92TB NVMe RAID-10"
        }
    ]

    for item in assets_data:
        get_or_create(base_url, "hardware", item["name"], item, headers)

    # 11. Create 1 Consumable
    print("\n--> 11. Creating 1 Sample Consumable...")
    get_or_create(base_url, "consumables", "Logitech MX Master 3S Wireless Mouse", {
        "name": "Logitech MX Master 3S Wireless Mouse",
        "category_id": cat_access_id,
        "manufacturer_id": mfg_log_id,
        "supplier_id": sup_insight_id,
        "item_no": "910-006557",
        "qty": 25,
        "min_amt": 5,
        "company_id": company_id,
        "location_id": loc_head_id,
        "purchase_cost": "99.99"
    }, headers)

    print("\n====================================================================")
    print(" [✓] Successfully populated all foundational records & IT assets!   ")
    print("====================================================================")

if __name__ == "__main__":
    main()
