import boto3
"""
用於確認 AWS IAM Identity Center 中的 user-id 對應人名
"""

client = boto3.client("identitystore")

identity_store_id = "d-97677ae164"
user_ids = [
    "192e3478-6071-70f2-238a-7f56837dc552",
    "59fe84d8-d031-7030-f503-58b6e58fd1b5",
    "693e3498-6021-7076-42be-238e65afdb7e",
    "f90ec498-e0c1-706b-f34f-a4784bb1d2d1",
    "d9eee488-6021-7014-64bc-0332912eb529",
    "693e84a8-40d1-7045-3b8b-3adbc71c24ab",
    "096e2428-f081-70df-b068-ab641f8e3e64",
    "b90e9468-80d1-70fc-3f93-6f9212ec3e0b",
    "29ae14a8-90e1-7028-a2eb-0de0dd269c22",
    "e96e5438-9041-7058-f94b-0ce47ca61b42",
    "59fe5428-30f1-705d-f680-ff21701234af",
    "49de44b8-50d1-70f6-1b48-a744c4f7cece",
    "593ee4b8-1061-7016-3913-f3042f062cad",
    "695e14d8-c061-707f-d04e-8a5dc844bf43",
    "d92e74b8-2031-70fb-bf6b-fe36b7c6b717",
]

for uid in user_ids:
    try:
        response = client.describe_user(
            IdentityStoreId=identity_store_id,
            UserId=uid,
        )
        username = response.get("UserName")
        print(f"UserId: {uid} | UserName: {username}")
        print("-" * 50)
    except client.exceptions.ResourceNotFoundException:
        print(f"UserId {uid} not found.")
