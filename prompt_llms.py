import os
import boto3
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))

# Nova Lite model ID for Bedrock
MODEL_ID = "amazon.nova-lite-v1:0"

# Function to call AWS Bedrock Nova Lite
def prompt_nova_lite(text):
    body = {
        "messages": [
            {"role": "user", "content": text}
        ],
        "max_tokens": 10000
    }
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json"
    )
    result = json.loads(response["body"].read())
    # Extract the model's reply
    return result["content"][0]["text"] if "content" in result and result["content"] else result

if __name__ == "__main__":
    text = "What is the capital of France?"
    response = prompt_nova_lite(text)
    print(f"Response from Nova Lite: {response}")
