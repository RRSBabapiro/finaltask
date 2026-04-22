import os, yaml, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_URL = os.getenv('QRADAR_URL')
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_DIR = 'qradarrules/'

headers = {
    'SEC': QRADAR_TOKEN,
    'Content-Type': 'application/json'
}

def deploy_qradar(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if not config: return

    payload = {
        "name": config['name'],
        "aql": config['expression']
    }

    # Bu endpoint ən stabil olanıdır
    url = f"{QRADAR_URL}/api/ariel/saved_searches"
    
    print(f"Göndərilir: {config['name']}...")
    res = requests.post(url, json=payload, headers=headers, verify=False)

    if res.status_code in [200, 201]:
        print(f"UĞURLU: {config['name']} QRadar-a oturdu.")
    elif res.status_code == 409:
        print(f"Məlumat: {config['name']} artıq mövcuddur.")
    else:
        print(f"XƏTA: {res.status_code} - {res.text}")

if __name__ == "__main__":
    if os.path.exists(RULES_DIR):
        for filename in os.listdir(RULES_DIR):
            if filename.endswith(".yaml"): deploy_qradar(os.path.join(RULES_DIR, filename))
