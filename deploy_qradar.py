import os, yaml, requests, urllib3, sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# GitHub Secrets-dən məlumatları oxuyur
QRADAR_URL = os.getenv('QRADAR_URL').rstrip('/')
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_DIR = 'qradarrules/'

headers = {
    'SEC': QRADAR_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def deploy_to_qradar_cre(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if not config: return True

    # QRadar Custom Rule (CRE) üçün ən doğru endpoint
    url = f"{QRADAR_URL}/api/analytics/rules"
    
    # QRadar-ın tələb etdiyi Custom Rule strukturu
    payload = {
        "name": config['name'],
        "type": "EVENT", # Hadisə əsaslı qayda
        "enabled": config.get('enabled', True),
        "description": config.get('description', ''),
        "content": {
            "aql_expression": config['expression']
        },
        "responses": {
            "ensure_offense": True, # BU HİSSƏ OFFENSE YARADIR
            "offense_column": "sourceip",
            "severity": config.get('severity', 5),
            "credibility": config.get('credibility', 5)
        }
    }

    print(f"Custom Rule göndərilir: {config['name']}...")
    res = requests.post(url, json=payload, headers=headers, verify=False)

    if res.status_code in [200, 201]:
        print(f"UĞURLU: '{config['name']}' Custom Rule olaraq yaradıldı.")
        return True
    elif res.status_code == 409:
        print(f"Məlumat: '{config['name']}' artıq Custom Rule-lar siyahısında var.")
        return True
    else:
        print(f"XƏTA: {res.status_code} - {res.text}")
        return False

if __name__ == "__main__":
    all_success = True
    if os.path.exists(RULES_DIR):
        for filename in os.listdir(RULES_DIR):
            if filename.endswith(".yaml"):
                if not deploy_to_qradar_cre(os.path.join(RULES_DIR, filename)):
                    all_success = False
    
    if not all_success:
        sys.exit(1)
