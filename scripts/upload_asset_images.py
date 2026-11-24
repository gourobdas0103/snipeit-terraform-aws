#!/usr/bin/env python3
"""
Uploads high-quality hardware images to Snipe-IT Assets and Models.
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

ASSETS_IMAGES = [
    {
        "hardware_id": 1,
        "model_id": 1,
        "name": "Dell Latitude 5440",
        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f2/Dell_Latitude_D630.jpg",
        "mime": "image/jpeg"
    },
    {
        "hardware_id": 2,
        "model_id": 2,
        "name": "HP EliteBook 840 G10",
        "url": "https://upload.wikimedia.org/wikipedia/commons/5/5e/HP_Laptop_Notebook.png",
        "mime": "image/png"
    },
    {
        "hardware_id": 3,
        "model_id": 3,
        "name": "Lenovo ThinkPad T14 Gen 4",
        "url": "https://upload.wikimedia.org/wikipedia/commons/d/d9/Lenovo_ThinkPad_T460.png",
        "mime": "image/png"
    },
    {
        "hardware_id": 4,
        "model_id": 4,
        "name": "Dell OptiPlex 7010 Micro",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Dell_OptiPlex_9020_Desktop_%2814246675643%29.png",
        "mime": "image/png"
    },
    {
        "hardware_id": 5,
        "model_id": 5,
        "name": "Dell PowerEdge R660",
        "url": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Dell_PowerEdge_2950.jpg",
        "mime": "image/jpeg"
    }
]

CONSUMABLE_IMAGE = {
    "consumable_id": 1,
    "name": "Logitech MX Master 3S Wireless Mouse",
    "url": "https://upload.wikimedia.org/wikipedia/commons/8/8a/2023_Mysz_komputerowa_Logitech_M705.jpg",
    "mime": "image/jpeg"
}

def download_and_b64(url, mime):
    r = requests.get(url, headers={"User-Agent": "SnipeITBot/1.0 (contact@acme.internal)"}, timeout=30)
    if r.status_code == 200:
        b64 = base64.b64encode(r.content).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    else:
        print(f"[-] Failed downloading {url}: status {r.status_code}")
        return None

def main():
    print("====================================================================")
    print("           Uploading Hardware & Model Images to Snipe-IT           ")
    print("====================================================================")

    for item in ASSETS_IMAGES:
        print(f"\n--> Fetching image for: {item['name']}...")
        data_uri = download_and_b64(item["url"], item["mime"])
        if not data_uri:
            continue

        # 1. Update Asset Model
        payload = {"image_source": data_uri}
        res_m = requests.put(f"{BASE_URL}/api/v1/models/{item['model_id']}", json=payload, headers=HEADERS)
        print(f"    [+] Model {item['model_id']} updated: {res_m.json().get('status')}")

        # 2. Update Hardware Asset
        res_h = requests.put(f"{BASE_URL}/api/v1/hardware/{item['hardware_id']}", json=payload, headers=HEADERS)
        print(f"    [+] Hardware {item['hardware_id']} updated: {res_h.json().get('status')}")

    # Update Consumable
    print(f"\n--> Fetching image for Consumable: {CONSUMABLE_IMAGE['name']}...")
    c_data_uri = download_and_b64(CONSUMABLE_IMAGE["url"], CONSUMABLE_IMAGE["mime"])
    if c_data_uri:
        res_c = requests.put(f"{BASE_URL}/api/v1/consumables/{CONSUMABLE_IMAGE['consumable_id']}", json={"image_source": c_data_uri}, headers=HEADERS)
        print(f"    [+] Consumable {CONSUMABLE_IMAGE['consumable_id']} updated: {res_c.json().get('status')}")

    print("\n====================================================================")
    print(" [✓] All images successfully uploaded and attached to assets!       ")
    print("====================================================================")

if __name__ == "__main__":
    main()
