import os, yaml, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPLUNK_URL = os.getenv('SPLUNK_URL') 
SPLUNK_TOKEN = os.getenv('SPLUNK_TOKEN')
RULES_DIR = 'splunkrules/'

headers = {'Authorization': f'Bearer {SPLUNK_TOKEN}'}

def deploy_rule(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    rule_name = config['name']
    # 'nobody' və 'search' istifadə edirik ki, hər kəs üçün əlçatan olsun
    base_url = f"{SPLUNK_URL}/servicesNS/nobody/search/saved/searches"
    entry_url = f"{base_url}/{rule_name}"

    payload = {
        'name': rule_name,
        'search': config['search'],
        'dispatch.earliest_time': config.get('earliest_time', '0'),
        'dispatch.latest_time': config.get('latest_time', 'now'),
        'is_scheduled': 0,
        'action.email.reportServerEnabled': 0,
        'ui_collect_mode': 'simple'
    }

    print(f"Yoxlanılır: {rule_name}...")
    # Əvvəlcə yoxlayırıq varmı
    check = requests.get(entry_url + "?output_mode=json", headers=headers, verify=False)

    if check.status_code == 200:
        print(f"Yenilənir: {rule_name}...")
        payload.pop('name')
        res = requests.post(entry_url, data=payload, headers=headers, verify=False)
    else:
        print(f"Yeni yaradılır: {rule_name}...")
        res = requests.post(base_url, data=payload, headers=headers, verify=False)

    if res.status_code in [200, 201]:
        print(f"UĞURLU: {rule_name} yükləndi.")
    else:
        print(f"XƏTA: {res.status_code} - {res.text}")

if __name__ == "__main__":
    for filename in os.listdir(RULES_DIR):
        if filename.endswith(".yaml"): deploy_rule(os.path.join(RULES_DIR, filename))
