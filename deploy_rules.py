import os
import yaml
import requests

# GitHub Secrets-dən gələn məlumatlar
SPLUNK_URL = os.getenv('SPLUNK_URL') # https://stack.splunkcloud.com:8089
SPLUNK_TOKEN = os.getenv('SPLUNK_TOKEN')
RULES_DIR = 'splunkrules/'

headers = {
    'Authorization': f'Bearer {SPLUNK_TOKEN}'
}

def deploy_rule(file_path):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Splunk API üçün məlumatları hazırla
    data = {
        'name': config['name'],
        'search': config['search'],
        'dispatch.earliest_time': config.get('earliest_time', '0'),
        'dispatch.latest_time': config.get('latest_time', 'now'),
        'description': config.get('description', 'GitHub-dan avtomatik yüklənib'),
        'is_scheduled': 0,
        'request.ui_dispatch_app': 'search'
    }

    # API ünvanı (Saved Searches)
    url = f"{SPLUNK_URL}/servicesNS/admin/search/saved/searches"
    
    print(f"Yüklənir: {config['name']}...")
    response = requests.post(url, data=data, headers=headers, verify=False)
    
    if response.status_code == 201:
        print(f"Uğurlu: {config['name']} yaradıldı.")
    elif response.status_code == 409:
        print(f"Xəbərdarlıq: {config['name']} artıq mövcuddur. Yeniləmə lazımdırsa köhnəni silin və ya API-ni UPDATE rejimində işlədin.")
    else:
        print(f"Xəta: {response.status_code} - {response.text}")

# Qovluqdakı bütün .yaml fayllarını dövrə sal
if __name__ == "__main__":
    for filename in os.listdir(RULES_DIR):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            deploy_rule(os.path.join(RULES_DIR, filename))
