import boto3

TARGET_ROLE_ARN = "arn:aws:iam::482497020602:role/aws-reserved/sso.amazonaws.com/ap-southeast-2/AWSReservedSSO_SOC-Senior-Developer_865e5c7a0ae4c163"

REGIONS = [
    "sa-east-1",       # South America (São Paulo)
    "ca-central-1",    # Canada (Central)
    "us-west-2",       # US West (Oregon)
    "us-east-2",       # US East (Ohio)
    "us-east-1",       # US East (N. Virginia)
    "us-west-1",       # US West (N. California)
    "eu-west-3",       # Europe (Paris)
    "eu-west-1",       # Europe (Ireland)
    "eu-west-2",       # Europe (London)
    "eu-north-1",      # Europe (Stockholm)
    "eu-central-1",    # Europe (Frankfurt)
    "ap-south-1",      # Asia Pacific (Mumbai)
    "ap-northeast-1",  # Asia Pacific (Tokyo)
    "ap-northeast-2",  # Asia Pacific (Seoul)
    "ap-southeast-2",  # Asia Pacific (Sydney)
    "ap-northeast-3",  # Asia Pacific (Osaka)
]

def ensure_data_lake_admin(region, role_arn):
    client = boto3.client("lakeformation", region_name=region)

    settings = client.get_data_lake_settings()
    admins = settings["DataLakeSettings"].get("DataLakeAdmins", [])

    if any(a.get("DataLakePrincipalIdentifier") == role_arn for a in admins):
        print(f"[{region}] already configured")
        return

    admins.append({
        "DataLakePrincipalIdentifier": role_arn
    })

    client.put_data_lake_settings(
        DataLakeSettings={
            **settings["DataLakeSettings"],
            "DataLakeAdmins": admins
        }
    )

    print(f"[{region}] role added as Data Lake Admin")

if __name__ == "__main__":
    for region in REGIONS:
        ensure_data_lake_admin(region, TARGET_ROLE_ARN)
