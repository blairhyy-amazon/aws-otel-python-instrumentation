# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import boto3
from flask import Flask, request

# Let's use Amazon S3
s3 = boto3.resource("s3")

app = Flask(__name__)


@app.route("/server_request")
def server_request():
    print(request.args.get("param"))
    for bucket in s3.buckets.all():
        print(bucket.name)
    return "served"


# Initialize Kinesis client
kinesis = boto3.client("kinesis")


@app.route("/get_stream")
def get_kinesis_stream(stream_arn):
    # Extract stream name from ARN
    stream_name = stream_arn.split("/")[-1]

    try:
        # Get stream description
        response = kinesis.describe_stream(StreamARN=stream_arn)
        return response["StreamDescription"]
    except kinesis.exceptions.ResourceNotFoundException:
        print(f"Stream {stream_name} not found")
        return None
    except Exception as e:
        print(f"Error getting stream: {str(e)}")
        return None

@app.route("/get_s3_bucket")
def get_s3_bucket():
    # Create an STS client to assume role
    sts_client = boto3.client("sts")

    role_arn = ""
    # Assume the specified role
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn, 
        RoleSessionName="CrossAccountAccess"
    )

    # Get temporary credentials from assumed role
    credentials = assumed_role["Credentials"]

    # Create S3 client with the assumed role credentials
    s3 = boto3.client(
        "s3",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    bucket_name = "cross-account-test-blairhyy"

    try:
        # Get bucket information
        s3.head_bucket(Bucket=bucket_name)
        
        return {
            "bucket_exists": True,
            "bucket_name": bucket_name,
        }
    except s3.exceptions.NoSuchBucket:
        return {"error": f"Bucket {bucket_name} not found"}
    except Exception as e:
        return {"error": f"Error accessing bucket: {str(e)}"}
    
@app.route("/get_table")
def get_dynamodb_table(role_arn):
    # Create an STS client to assume role
    sts_client = boto3.client("sts")

    # Assume the specified role
    assumed_role = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="CrossAccountAccess")

    # Get temporary credentials from assumed role
    credentials = assumed_role["Credentials"]

    # Create DynamoDB client with the assumed role credentials
    dynamodb = boto3.client(
        "dynamodb",
        region_name="us-east-2",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    # Use the specified table name
    table_name = "cross-account-test"

    try:
        # Get table description
        response = dynamodb.describe_table(TableName=table_name)
        return response["Table"]
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"Table {table_name} not found")
        return None
    except Exception as e:
        print(f"Error getting table: {str(e)}")
        return None


if __name__ == "__main__":
    app.run(port=8082)
