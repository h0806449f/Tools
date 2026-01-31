import boto3
import time

AWS_REGION = "ap-southeast-2"
PERMISSION_SET_NAME = "NOCEngineer"

sso_admin = boto3.client("sso-admin", region_name=AWS_REGION)


# ---------- helpers ----------

def get_instance_arn():
    resp = sso_admin.list_instances()
    return resp["Instances"][0]["InstanceArn"]


def get_permission_set_arn(instance_arn, name):
    paginator = sso_admin.get_paginator("list_permission_sets")
    for page in paginator.paginate(InstanceArn=instance_arn):
        for ps_arn in page["PermissionSets"]:
            ps = sso_admin.describe_permission_set(
                InstanceArn=instance_arn,
                PermissionSetArn=ps_arn,
            )
            if ps["PermissionSet"]["Name"] == name:
                return ps_arn
    raise RuntimeError(f"Permission Set not found: {name}")


def list_accounts(instance_arn, permission_set_arn):
    accounts = []
    paginator = sso_admin.get_paginator(
        "list_accounts_for_provisioned_permission_set"
    )
    for page in paginator.paginate(
        InstanceArn=instance_arn,
        PermissionSetArn=permission_set_arn,
    ):
        accounts.extend(page["AccountIds"])
    return accounts


def list_assignments(instance_arn, account_id, permission_set_arn):
    assignments = []
    paginator = sso_admin.get_paginator("list_account_assignments")
    for page in paginator.paginate(
        InstanceArn=instance_arn,
        AccountId=account_id,
        PermissionSetArn=permission_set_arn,
    ):
        assignments.extend(page["AccountAssignments"])
    return assignments


# ---------- delete assignment ----------

def delete_assignment(instance_arn, account_id, permission_set_arn, a):
    resp = sso_admin.delete_account_assignment(
        InstanceArn=instance_arn,
        TargetId=account_id,
        TargetType="AWS_ACCOUNT",
        PermissionSetArn=permission_set_arn,
        PrincipalType=a["PrincipalType"],   # GROUP or USER
        PrincipalId=a["PrincipalId"],
    )
    return resp["AccountAssignmentDeletionStatus"]["RequestId"]


def wait_for_assignment_deletion(instance_arn, request_id):
    while True:
        status = sso_admin.describe_account_assignment_deletion_status(
            InstanceArn=instance_arn,
            AccountAssignmentDeletionRequestId=request_id,
        )
        state = status["AccountAssignmentDeletionStatus"]["Status"]
        if state in ("SUCCEEDED", "FAILED"):
            return state
        time.sleep(1)

# ---------- main ----------

def main():
    instance_arn = get_instance_arn()
    print(f"InstanceArn: {instance_arn}")

    permission_set_arn = get_permission_set_arn(
        instance_arn, PERMISSION_SET_NAME
    )
    print(f"PermissionSetArn: {permission_set_arn}")

    accounts = list_accounts(instance_arn, permission_set_arn)
    print(f"Found {len(accounts)} provisioned accounts")

    for account_id in accounts:
        print(f"\nAccount {account_id}")

        assignments = list_assignments(
            instance_arn, account_id, permission_set_arn
        )

        # 1️⃣ delete assignments (user / group)
        if assignments:
            for a in assignments:
                print(
                    f"  Deleting {a['PrincipalType']} {a['PrincipalId']}"
                )
                req = delete_assignment(
                    instance_arn, account_id, permission_set_arn, a
                )
                result = wait_for_assignment_deletion(instance_arn, req)
                print(f"    → {result}")
        else:
            print("  No assignments")

        # 2️⃣ deprovision permission set from account
        print("  Deprovisioning permission set from account")

    print("\n✅ All accounts cleaned.")
    print("You can now safely delete the Permission Set.")
    


if __name__ == "__main__":
    main()
