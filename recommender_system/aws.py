'''
https://realpython.com/python-boto3-aws-s3/#uploading-a-file
'''
import boto3

def get_client():
    client_s3 = boto3.client('s3')
    return client_s3

def upload_s3_object(file_object, bucket, key):
    client = get_client()
    client.put_object(Body = file_object.getvalue(), Bucket=bucket, Key=key)
    

def download_s3_object(bucket, key):
    client = get_client()
    response = client.get_object(Bucket=bucket, Key=key)
    data = response.get('Body').read()
    return data
