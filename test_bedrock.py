import json
import boto3
from config import credential

client = boto3.client("bedrock-runtime",region_name=credential.region)

native_request = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": "Hello, how are you?"
                }
            ]
        }
    ]
}

# Invoke the model+
response = client.invoke_model(
    modelId=credential.model_id,
    body=json.dumps(native_request),
    contentType="application/json",
    accept="application/json"
)

# Parse and extract the response text
response_body = json.loads(response["body"].read())
response_text = response_body["content"][0]["text"]

print(response_text)
