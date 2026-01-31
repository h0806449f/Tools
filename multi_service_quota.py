import subprocess
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
"""
用於跨帳號申請 AWS Service Quota 上限提高
"""


PROFILES = [
    "ai_genai_prod",
    "ai_genaipoc_dev",
    "app_alpha",
    "app_au",
    "app_mo",
    "app_ops",
    "app_pu",
    "app_sandbox",
    "app_sharedservice",
    "app_stage",
    "app_star",
    "app_um",
    "app_vjp",
    "app_vt",
    "audit",
    "bit_bybit",
    "bit_cashier",
    "bit_finance",
    "bit_pub",
    "bit_service",
    "bit_shared_service",
    "bit_uat",
    "bit_vts",
    "cis",
    "cis_noc",
    "create_gold_technology_limited",
    "crm_alpha01",
    "crm_at",
    "crm_au",
    "crm_mo",
    "crm_ops",
    "crm_pu",
    "crm_pub",
    "crm_sandbox",
    "crm_star",
    "crm_um",
    "crm_vjp",
    "crm_vt",
    "finance_datalake",
    "gbis",
    "gbis_datawind",
    "ha_cps",
    "ha_cps_dev",
    "ha_cps_sandbox",
    "hr",
    "log_archive",
    "mts_business",
    "network_account",
    "network_staging",
    "payment_datalake",
    "risk_antifraud_prod",
    "risk_antifraud_test",
    "risk_datalake",
    "risk_datalake_dev",
    "risk_hs",
    "risk_infra",
    "risk_infra_dev",
    "risk_insight",
    "risk_pe",
    "risk_pe_dev",
    "risk_rc",
    "risk_rnd",
    "risk_saas",
    "risk_taipei_data",
    "risk_wt",
    "shared_service_account",
    "star_bi",
    "unicorn",
    "vantage_international_group_limited",
    "webteam_officialsite",
    "data_governance"
]


REGION = "us-east-1"
SERVICE_CODE = "iam"
QUOTA_CODE = "L-0DA4ABF3"
DESIRED = 25
MAX_WORKERS = 10


def run_aws_vault(cmd, profile):
    full_cmd = f"aws-vault exec {profile} -- {cmd}"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def check_current(profile):
    cmd = f"aws service-quotas get-service-quota " \
          f"--service-code {SERVICE_CODE} --quota-code {QUOTA_CODE} " \
          f"--region {REGION} --query 'Quota.Value' --output text"
    out, err, rc = run_aws_vault(cmd, profile)
    
    if rc == 0:
        try:
            value = out.strip().replace('.0', '')
            return float(value) if value.isdigit() else None
        except:
            return None
    elif "NoSuchResourceException" in err:
        return None
    else:
        print(f"\n[{profile}] 檢查失敗: {err.splitlines()[-1]}")
        return "CHECK_ERROR"

def request_increase(profile):
    cmd = f"aws service-quotas request-service-quota-increase " \
          f"--service-code {SERVICE_CODE} --quota-code {QUOTA_CODE} " \
          f"--desired-value {DESIRED} --region {REGION} --output json"
    out, err, rc = run_aws_vault(cmd, profile)
    
    if rc == 0:
        try:
            data = json.loads(out)
            case_id = data['RequestedQuota']['Id']
            return True, f"成功 (Case ID: {case_id})"
        except:
            return False, "解析回傳失敗"
    elif "ResourceAlreadyExistsException" in err:
        return False, "已有申請進行中"
    elif "AccessDenied" in err:
        return False, "權限不足 (缺少 servicequotas:RequestServiceQuotaIncrease)"
    else:
        error_msg = err.splitlines()[-1] if err else "未知錯誤"
        return False, f"失敗: {error_msg[:100]}"

def process(profile):
    print(f"[{profile}] 檢查配額中...", end=" ")
    
    current = check_current(profile)
    
    if isinstance(current, float):
        if current >= 20:
            print(f"已達 {current}，無需申請")
            return profile, f"已達上限 ({current})"
        else:
            print(f"目前 {current} → 申請 {DESIRED}...", end=" ")
    elif current is None:
        print("配額不存在或未初始化，嘗試申請...")
    else:
        return profile, f"檢查失敗 ({current})"

    # 送出申請
    success, msg = request_increase(profile)
    if success:
        print(msg)
        return profile, msg
    else:
        print(msg)
        return profile, msg


def main():
    if not PROFILES:
        print("錯誤：PROFILES 列表為空！請填入 aws-vault profile 名稱")
        sys.exit(1)
        
    print(f"\n開始處理 {len(PROFILES)} 個帳戶 → IAM Role Managed Policy 上限 10 → 20")
    print(f"Quota Code: {QUOTA_CODE} ({REGION})\n")

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process, p): p for p in PROFILES}
        for future in as_completed(futures):
            profile, status = future.result()
            results.append((profile, status))

    print("\n" + "="*70)
    print("執行結果總覽")
    print("="*70)
    
    success = [r for r in results if "Case ID" in r[1]]
    already = [r for r in results if "已達上限" in r[1]]
    pending = [r for r in results if "已有申請" in r[1]]
    failed  = [r for r in results if r not in success + already + pending]

    print(f"成功送出申請    : {len(success)} 個")
    for p, s in success:
        print(f"   → {p:20} {s}")

    print(f"\n已達 20 上限     : {len(already)} 個")
    for p, s in already:
        print(f"   → {p:20} {s}")

    print(f"\n已有申請中       : {len(pending)} 個")
    for p, s in pending:
        print(f"   → {p:20} {s}")

    if failed:
        print(f"\n其他狀態（失敗/錯誤）: {len(failed)} 個")
        for p, s in failed:
            print(f"   → {p:20} {s}")

    print(f"\n全部完成！總共處理 {len(PROFILES)} 個帳戶。")

if __name__ == "__main__":
    main()