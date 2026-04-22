import os, yaml, requests, urllib3, sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. URL-i təmizləyirik (Sonundakı / və ya /api hissələrini silirik ki, dublikat olmasın)
raw_url = os.getenv('QRADAR_URL', '').rstrip('/')
if raw_url.endswith('/api'):
    raw_url = raw_url[:-4]
QRADAR_URL = raw_url

QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')
RULES_DIR = 'qradarrules/'

# QRadar-da mütləq Version header-i istifadə etməliyik
headers = {
    'SEC': QRADAR_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Version': '12.0' # QRadar API versiyasını məcburi edirik
}

def deploy_to_qradar(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    if not config: return True

    # Tam və dəqiq API ünvanı
    url = f"{QRADAR_URL}/api/analytics/rules"
    
    # QRadar-ın ən çox bəyəndiyi Custom Rule strukturu
    payload = {
        "name": config['name'],
        "type": "EVENT",
        "enabled": True,
        "content": {
            "aql_expression": config['expression']
        },
        "responses": {
            "ensure_offense": True,
            "offense_column": "sourceip", # 'Username' yerinə daha stabil olan 'sourceip' yoxlayaq
            "severity": int(config.get('severity', 7)),
            "credibility": int(config.get('credibility', 5))
        }
    }

    print(f"Müraciət edilir: POST {url}")
    res = requests.post(url, json=payload, headers=headers, verify=False)

    if res.status_code in [200, 201]:
        print(f"UĞURLU: '{config['name']}' Custom Rule yaradıldı.")
        return True
    elif res.status_code == 409:
        print(f"Məlumat: '{config['name']}' artıq var.")
        return True
    else:
        print(f"XƏTA: {res.status_code} - {res.text}")
        return False

if __name__ == "__main__":
    success = True
    if os.path.exists(RULES_DIR):
        for filename in os.listdir(RULES_DIR):
            if filename.endswith(".yaml"):
                if not deploy_to_qradar(os.path.join(RULES_DIR, filename)):
                    success = False
    
    if not success:
        sys.exit(1)
