import os, yaml, requests, urllib3, json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_URL = os.getenv('QRADAR_URL')
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_DIR = 'qradarrules/'

headers = {
    'SEC': QRADAR_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def deploy_custom_rule(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if not config: return

    # QRadar Custom Rule JSON strukturu
    payload = {
        "name": config['name'],
        "type": "EVENT", # Hadisə əsaslı qayda
        "enabled": True,
        "base_capacity": 100,
        "origin": "USER",
        "description": config.get('description', ''),
        "content": {
            "aql_expression": config['expression']
        },
        # Bu hissə OFFENSE yaradan hissədir
        "responses": {
            "ensure_offense": config.get('offense_response', True),
            "offense_column": "sourceip", # Offense-i nəyə görə qruplaşdırsın
            "severity": config.get('severity', 5),
            "credibility": config.get('credibility', 5)
        }
    }

    url = f"{QRADAR_URL}/api/analytics/rules"
    
    print(f"Custom Rule yüklənir: {config['name']}...")
    res = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

    if res.status_code in [200, 201]:
        print(f"UĞURLU: '{config['name']}' Offense qaydası yaradıldı.")
    else:
        # Əgər yenə 404 verərsə, bu o deməkdir ki, API ilə birbaşa qayda yaratmaq 
        # sənin versiyanda bağlıdır. Bu halda "ariel/saved_searches" istifadə etməliyik.
        print(f"XƏTA: {res.status_code} - {res.text}")

if __name__ == "__main__":
    if os.path.exists(RULES_DIR):
        for filename in os.listdir(RULES_DIR):
            if filename.endswith(".yaml"):
                deploy_custom_rule(os.path.join(RULES_DIR, filename))
