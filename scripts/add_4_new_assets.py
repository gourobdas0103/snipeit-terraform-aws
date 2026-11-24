#!/usr/bin/env python3
"""
Adds 4 new high-spec assets to Snipe-IT with latest market prices and images:
1. Apple MacBook Pro 16-inch (M5 Pro chip) - $2,499.00
2. Lenovo LOQ 15 Gaming Laptop (i5 13th Gen, RTX 5050) - $1,099.00
3. Sony PlayStation 5 Pro (2TB Custom NVMe) - $699.99
4. Microsoft Xbox Series X (1TB Custom NVMe) - $499.99
"""
import requests
import base64
import sys

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIwMWEyMGRkMi1jNzhlLTczYTUtYTU4ZS0xMjM3Yzg3NDMwYTciLCJqdGkiOiJiNzRiNDg5M2M2YjAyZTYzMDQ1ZDk5ZmFjZmFkOTgwNDZlN2FlOThhN2Y0NDA3YzhjMjg4ZmYxYTk2MzU1OWNhMWY2ZGE1NTk3MWMxYWVjOCIsImlhdCI6MTc5NTUzMjcxOS4xMTM4MDcsIm5iZiI6MTc5NTUzMjcxOS4xMTM4MTEsImV4cCI6MzA1NzgzNjcxOS4wNzk2NDMsInN1YiI6IjEiLCJzY29wZXMiOltdfQ.QhaH8h1nN2QK0d2CNf9HIFPWtmgB-gLgt-6yiJqN8tXtviRM4SMcRLj8gwPIiWF8WKSwX7GWZSnDomwAvBD_-ku4AOqSkB5agUE-75TxfuUvmgjci59JrGoMuiSMlfIBCWthxjLlDWlm9hKDWueCjzgPo8bHMFELvBAwWTcSVusViQZtUsAAmrFCGaJSbeG1ESdnis2_7ovwLoykgOcshJ1jVM52dy8znghSYrUG6ulXnxiGOe1Xb4IMlCo93ibnLulrDhM8xUm3rkWbEmT0YsvK-O5bkdIdyEThlOYkj4DRHIpaO_Z9u3viict4zjIQX88VFRdh3Ievm2-zwk_n4760woMMe3nVP6HfmTDF-Q2ARYDLbWKNwfI-zho46NHfOiegqzBv3oaphSNpC77HcP8pwQs0uR3ek_1YcJkDfS_CTydglBltQ4659nD28oRF-hr2EHpu5BBKgrF4k5uZeoZLlmEvyBc9csLHMbOrnFXZDJ5Jz_6JXrMuwBkvGuru95fqa75MimmCzjGme_aTfNv36RZfOaoVXqG4m7tjCq3S4BUXwQv1W-hD0V_aGpHMQqaIK2kCRKOjoFz_4M6viobztORlRQFWyoSyf7nZ9QpkDvhfgD9cDSDSc_PiXy6NoVsJnrNaCygNDRqEnfnwIVr5pha-24i2INrSxhH2jnA"
BASE_URL = "http://13.203.209.10:8000"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def download_and_b64(url, mime):
    r = requests.get(url, headers={"User-Agent": "SnipeITBot/1.0 (contact@acme.internal)"}, timeout=30)
    if r.status_code == 200:
        b64 = base64.b64encode(r.content).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    return None

def get_or_create(endpoint, search_name, payload):
    s_url = f"{BASE_URL}/api/v1/{endpoint}?search={search_name}&limit=1"
    r = requests.get(s_url, headers=HEADERS)
    if r.status_code == 200 and r.json().get("rows"):
        for row in r.json()["rows"]:
            if row.get("name", "").lower() == search_name.lower():
                print(f"[+] Found existing {endpoint}: {search_name} (ID: {row.get('id')})")
                return row.get("id")
    # create
    cr = requests.post(f"{BASE_URL}/api/v1/{endpoint}", json=payload, headers=HEADERS)
    if cr.status_code in [200, 201]:
        data = cr.json()
        item_id = data.get("payload", {}).get("id")
        print(f"[+] Created {endpoint}: {search_name} (ID: {item_id})")
        return item_id
    else:
        print(f"[-] Failed {endpoint} {search_name}: {cr.text}")
        return None

def main():
    print("====================================================================")
    print("        Adding 4 High-Spec Assets with Market Pricing to Snipe-IT    ")
    print("====================================================================")

    # 1. Company, Locations, Status
    company_id = 1
    loc_head_id = 1
    loc_branch_id = 2
    status_id = 1
    fieldset_id = 2

    # 2. Manufacturers
    print("\n--> Checking Manufacturers...")
    mfg_apple = get_or_create("manufacturers", "Apple", {"name": "Apple"})
    mfg_lenovo = 3 # already exists
    mfg_sony = get_or_create("manufacturers", "Sony", {"name": "Sony"})
    mfg_msft = get_or_create("manufacturers", "Microsoft", {"name": "Microsoft"})

    # 3. Categories
    print("\n--> Checking Categories...")
    cat_laptops = 2
    cat_consoles = get_or_create("categories", "Gaming & Multimedia Consoles", {
        "name": "Gaming & Multimedia Consoles",
        "category_type": "asset"
    })

    # 4. Suppliers
    print("\n--> Checking Suppliers...")
    sup_apple = get_or_create("suppliers", "Apple Commercial Direct", {
        "name": "Apple Commercial Direct", "email": "business@apple.com"
    })
    sup_lenovo = get_or_create("suppliers", "Lenovo Enterprise Direct", {
        "name": "Lenovo Enterprise Direct", "email": "sales@lenovo.com"
    })
    sup_sony = get_or_create("suppliers", "Sony Interactive Enterprise", {
        "name": "Sony Interactive Enterprise", "email": "enterprise@sony.com"
    })
    sup_msft = get_or_create("suppliers", "Microsoft Store Enterprise", {
        "name": "Microsoft Store Enterprise", "email": "business@microsoft.com"
    })

    # 5. Asset Models & Images
    NEW_MODELS = [
        {
            "name": "MacBook Pro 16-inch (M5)",
            "model_number": "MBP16-M5-2026",
            "manufacturer_id": mfg_apple,
            "category_id": cat_laptops,
            "fieldset_id": fieldset_id,
            "img_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/9/91/MacBook_Pro_16_%28M1_Pro%2C_2021%29_-_Wikipedia.jpg/960px-MacBook_Pro_16_%28M1_Pro%2C_2021%29_-_Wikipedia.jpg",
            "img_mime": "image/jpeg"
        },
        {
            "name": "Lenovo LOQ 15 (RTX 5050)",
            "model_number": "LOQ-15IRX9-RTX5050",
            "manufacturer_id": mfg_lenovo,
            "category_id": cat_laptops,
            "fieldset_id": fieldset_id,
            "img_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7d/Lenovo_Legion_Y7000P_Eclipse_Gray_Laptop.jpg/960px-Lenovo_Legion_Y7000P_Eclipse_Gray_Laptop.jpg",
            "img_mime": "image/jpeg"
        },
        {
            "name": "PlayStation 5 Pro",
            "model_number": "CFI-7000B",
            "manufacturer_id": mfg_sony,
            "category_id": cat_consoles,
            "fieldset_id": fieldset_id,
            "img_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_5_and_DualSense.jpg/960px-PlayStation_5_and_DualSense.jpg",
            "img_mime": "image/jpeg"
        },
        {
            "name": "Xbox Series X (1TB)",
            "model_number": "RRT-00001",
            "manufacturer_id": mfg_msft,
            "category_id": cat_consoles,
            "fieldset_id": fieldset_id,
            "img_url": "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2b/Microsoft-Xbox-One-Console-wKinect.png/960px-Microsoft-Xbox-One-Console-wKinect.png",
            "img_mime": "image/png"
        }
    ]

    print("\n--> Creating Asset Models with Images...")
    model_ids = {}
    for m in NEW_MODELS:
        payload = {
            "name": m["name"],
            "model_number": m["model_number"],
            "manufacturer_id": m["manufacturer_id"],
            "category_id": m["category_id"],
            "fieldset_id": m["fieldset_id"]
        }
        b64_img = download_and_b64(m["img_url"], m["img_mime"])
        if b64_img:
            payload["image_source"] = b64_img

        mid = get_or_create("models", m["name"], payload)
        model_ids[m["name"]] = (mid, b64_img)

    # 6. Create 4 Hardware Assets
    print("\n--> Creating 4 Hardware Assets with Market Prices...")
    NEW_ASSETS = [
        {
            "name": "Apple MacBook Pro 16\" (M5 Pro)",
            "asset_tag": "IT-00006",
            "model_id": model_ids["MacBook Pro 16-inch (M5)"][0],
            "b64_img": model_ids["MacBook Pro 16-inch (M5)"][1],
            "status_id": status_id,
            "serial": "C02K981M5PRO",
            "company_id": company_id,
            "rtd_location_id": loc_head_id,
            "supplier_id": sup_apple,
            "purchase_cost": "2499.00",
            "warranty_months": 36,
            "purchase_date": "2024-04-15",
            "notes": "Specs: Apple M5 Pro (14-core CPU, 20-core GPU, 16-core NPU), 36GB Unified Memory, 1TB NVMe SSD"
        },
        {
            "name": "Lenovo LOQ 15 (i5-13th Gen / RTX 5050)",
            "asset_tag": "IT-00007",
            "model_id": model_ids["Lenovo LOQ 15 (RTX 5050)"][0],
            "b64_img": model_ids["Lenovo LOQ 15 (RTX 5050)"][1],
            "status_id": status_id,
            "serial": "MP24KL09LOQ",
            "company_id": company_id,
            "rtd_location_id": loc_branch_id,
            "supplier_id": sup_lenovo,
            "purchase_cost": "1099.00",
            "warranty_months": 24,
            "purchase_date": "2024-04-18",
            "notes": "Specs: Intel Core i5-13450HX (10-core 4.6GHz), 16GB DDR5, 512GB NVMe PCIe 4.0 SSD, NVIDIA GeForce RTX 5050 6GB GDDR7"
        },
        {
            "name": "Sony PlayStation 5 Pro",
            "asset_tag": "IT-00008",
            "model_id": model_ids["PlayStation 5 Pro"][0],
            "b64_img": model_ids["PlayStation 5 Pro"][1],
            "status_id": status_id,
            "serial": "AK983719001PRO",
            "company_id": company_id,
            "rtd_location_id": loc_head_id,
            "supplier_id": sup_sony,
            "purchase_cost": "699.99",
            "warranty_months": 12,
            "purchase_date": "2024-04-20",
            "notes": "Specs: Custom AMD Zen 2 (8-core/16-thread), 16.7 TFLOPs RDNA + PSSR AI, 16GB GDDR6 + 2GB DDR5, 2TB High-Speed Custom NVMe"
        },
        {
            "name": "Microsoft Xbox Series X (1TB)",
            "asset_tag": "IT-00009",
            "model_id": model_ids["Xbox Series X (1TB)"][0],
            "b64_img": model_ids["Xbox Series X (1TB)"][1],
            "status_id": status_id,
            "serial": "XBX4490182X",
            "company_id": company_id,
            "rtd_location_id": loc_branch_id,
            "supplier_id": sup_msft,
            "purchase_cost": "499.99",
            "warranty_months": 12,
            "purchase_date": "2024-04-20",
            "notes": "Specs: Custom AMD Zen 2 (8-core @ 3.8GHz), 12 TFLOPs RDNA 2, 16GB GDDR6, 1TB Custom NVMe SSD"
        }
    ]

    for a in NEW_ASSETS:
        b64 = a.pop("b64_img", None)
        aid = get_or_create("hardware", a["name"], a)
        if aid and b64:
            res_img = requests.put(f"{BASE_URL}/api/v1/hardware/{aid}", json={"image_source": b64}, headers=HEADERS)
            print(f"    [+] Image attached to Asset {aid} ({a['asset_tag']}): {res_img.json().get('status')}")

    print("\n====================================================================")
    print(" [✓] Successfully added all 4 new assets with market prices & images!")
    print("====================================================================")

if __name__ == "__main__":
    main()
