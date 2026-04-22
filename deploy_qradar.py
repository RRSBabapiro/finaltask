import os, yaml, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_URL = os.getenv('QRADAR_URL') # https://1.2.3.4
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_DIR = 'qradarrules/'

# QRadar-da başlıq (header) fərqlidir: 'SEC' istifadə olunur
headers = {
    'SEC': QRADAR_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def deploy_qradar_rule(file_path):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # QRadar qayda strukturu
    payload = {
        "name": config['name'],
        "type": "AQL", # AQL əsaslı qayda
        "base_capacity": 100,
        "enabled": config.get('enabled', True),
        "content": {
            "aql_expression": config['expression']
        }
    }

    url = f"{QRADAR_URL}/api/analytics/rules"
    
    print(f"QRadar-a yüklənir: {config['name']}...")
    res = requests.post(url, json=payload, headers=headers, verify=False)

    if res.status_code in [200, 201]:
        print(f"UĞURLU: QRadar qaydası yaradıldı.")
    else:
        print(f"XƏTA: {res.status_code} - {res.text}")

if __name__ == "__main__":
    if os.path.exists(RULES_DIR):
        for filename in os.listdir(RULES_DIR):
            if filename.endswith(".yaml"):
                deploy_qradar_rule(os.path.join(RULES_DIR, filename))
