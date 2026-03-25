import pandas as pd
import requests
import time
import os
from openpyxl import load_workbook
from tqdm import tqdm 


github_token = 'Your GitHub Personal Access Token'
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': f'token {github_token}'
}

INPUT_FILE = 'output_with_readme_status.xlsx'
OUTPUT_FILE = 'output_with_content_status.xlsx'

def check_repository_content(repo, retries=10):
    backoff_factor = 1
    
    try:
        owner, repo_name = repo.split('/')
        
        url = f"https://api.github.com/repos/{owner}/{repo_name}/contents/"
    except ValueError:
        print(f"error: {repo}, pass")
        return 0

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 404:
                print(f"repository {repo} not found (404), pass")
                return 0
            
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                sleep_time = max(reset_time - time.time(), 60)
                print(f"speed limit, wait {sleep_time:.0f} seconds, and retry.")
                time.sleep(sleep_time)
                continue 
            
            elif response.status_code >= 400:
                print(f"try {attempt+1}/{retries}: accept {repo}'s HTTP {response.status_code} error")
                response.raise_for_status()

            content_list = response.json()
        
            if isinstance(content_list, list) and len(content_list) > 1:
                return 1  
            else:
                return 0

        except requests.exceptions.HTTPError as errh:
            print(f"HTTP error: {errh}, try {attempt+1}/{retries}")
            time.sleep(backoff_factor * (2 ** attempt))
            
        except Exception as err:
            print(f"other errors: {err}, try {attempt+1}/{retries}")
            time.sleep(backoff_factor * (2 ** attempt))
            
   
    print(f"repository {repo} failure, label 0")
    return 0

def process_content_check():
    try:
        from tqdm import tqdm
    except ImportError:
        print("please install dependencies:")
        print("pip install pandas openpyxl requests tqdm")
        return

    if 'ghp_...' in github_token:
        print("="*50)
        print("error!")
        print("="*50)
        return

    if not os.path.exists(INPUT_FILE):
        print(f"error: not found the file {INPUT_FILE}.")
        return

    
    df = pd.read_excel(INPUT_FILE)
    
    
    df['Has_content'] = 0
    
    total = len(df)
    
    repos_to_check = df[df['Has_README'] == 1]
    
    print(f"a total {total} repository, where {len(repos_to_check)} repositories need to check the content.")

    
    with tqdm(total=len(repos_to_check), desc="Checking repo content") as pbar:
        for index, row in repos_to_check.iterrows():
            repo = row['repository_name']
            
            
            content_status = check_repository_content(repo)
            
           
            df.at[index, 'Has_content'] = content_status
            
           
            if pbar.n % 50 == 0 and pbar.n > 0:
                df.to_excel(OUTPUT_FILE, index=False)
            
            pbar.update(1)
            time.sleep(0.5)  

   
    df.to_excel(OUTPUT_FILE, index=False)
    
    final_count = df[df['Has_content'] == 1].shape[0]
    print(f"{len(repos_to_check)} repositories with english README, and there are {final_count} repositories with other content.")

if __name__ == "__main__":
    process_content_check()