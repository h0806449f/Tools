import boto3
import re
import os

def list_aws_accounts():
    client = boto3.client('organizations')

    accounts = []
    paginator = client.get_paginator('list_accounts')
    
    for page in paginator.paginate():
        for acct in page['Accounts']:
            cleaned_name = clean_account_name(acct['Name'])
            accounts.append(cleaned_name)
    
    return accounts

def clean_account_name(name):
    """
    將 account name 統一格式:
    1. 全部小寫
    2. 將 '-' 或空格 ' ' 換成 '_'
    3. 多個連續的 '_' 也合併成一個
    """
    name = name.lower()
    name = re.sub(r'[-\s]+', '_', name)
    name = name.strip('_')
    return name

def create_folders(account_names, base_path='.'):
    """
    在 base_path 下為每個 account name 建立資料夾
    """
    for name in account_names:
        folder_path = os.path.join(base_path, name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")

if __name__ == "__main__":
    account_names = list_aws_accounts()
    create_folders(account_names)
