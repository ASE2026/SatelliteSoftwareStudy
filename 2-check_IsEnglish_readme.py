import pandas as pd
import requests
import base64
import os
import time
from openpyxl import load_workbook
from tqdm import tqdm 
import langdetect


github_token = 'Your GitHub Personal Access Token'
headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}



def detect_language(text):
    try:
        return langdetect.detect(text)
    except langdetect.lang_detect_exception.LangDetectException:
        return 'unknown'

def get_repository_readme(repo, retries=10):
    
    backoff_factor = 1  
    for attempt in range(retries):
        try:
            owner, repo_name = repo.split('/')
            url = f"https://api.github.com/repos/{owner}/{repo_name}/readme"
            response = requests.get(url, headers=headers, timeout=10)
            
            
            if response.status_code == 404:
                return 0
            elif response.status_code >= 400:
                print(f"try {attempt+1}/{retries}: accept {repo}'s HTTP {response.status_code} error")
                response.raise_for_status()


            readme_data = response.json()
            content = readme_data.get('content', '')
            decoded_content = base64.b64decode(content).decode('utf-8')

            language = detect_language(decoded_content)
            if language != 'en':
                print(f"repository {repo} 's README is not English, pass.")
                return 0
            
            return 1 if decoded_content.strip() else 0
            
        except requests.exceptions.HTTPError as errh:
            
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                sleep_time = max(reset_time - time.time(), 60)
                time.sleep(sleep_time)
                continue

            time.sleep(backoff_factor * (2 ** attempt))  
            
        except Exception as err:
            time.sleep(backoff_factor * (2 ** attempt))
            
    
    return 0

def process_repositories():
    df = pd.read_csv('satellite_repositories.csv')
    # df = pd.read_excel('satellite_test.xlsx')
    total = len(df)
    has_readme_list = []
    log_entries = []
    
    df['Has_README'] = 0
    
    with tqdm(total=total, desc="Processing repositories") as pbar:
        for index, row in df.iterrows():
            repo = row['repository_name']
            has_readme = get_repository_readme(repo)
            
            df.at[index, 'Has_README'] = has_readme
            if has_readme:
                log_entries.append(repo)
                
            
            if index % 100 == 0:
                df.to_excel('output_with_readme_status.xlsx', index=False)
                with open('log.txt', 'w') as f:
                    f.write('\n'.join(log_entries))
                    f.write(f"\n\nTotal repositories with README: {len(log_entries)}")
            
            pbar.update(1)
            time.sleep(0.5) 

    df.to_excel('output_with_readme_status.xlsx', index=False)
    with open('log.txt', 'w') as f:
        f.write('\n'.join(log_entries))
        f.write(f"\n\nTotal repositories with README: {len(log_entries)}")
    
    print(f"\nfinish! A total of {len(log_entries)} repositories with English README!")

if __name__ == "__main__":
    
    try:
        from tqdm import tqdm
    except ImportError:
        print("pip install pandas openpyxl requests tqdm")
        exit()

    process_repositories()