# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

import boto3
from openai import OpenAI


def generate(model, **kwargs):
    if "gpt" in model:
        return generate_openai(model, **kwargs)
    elif "claude" in model or "anthropic" in model:
        return generate_bedrock(model, **kwargs)
    else:
        raise ValueError(
            f"Unsupported model: {model}. Supported models: OpenAI (gpt-*) and AWS Bedrock (claude-*, anthropic.*)."
        )


# openai
def generate_openai(model: str, prompt: str, json_mode: bool = True, **kwargs):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response_format = {"type": "text"}
    if json_mode:
        response_format = {"type": "json_object"}
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        response_format=response_format,
        model=model,
    )

    txt = response.choices[0].message.content
    return txt


# aws bedrock
def generate_bedrock(model: str, prompt: str, json_mode: bool = True, **kwargs):
    """Generates text using AWS Bedrock with Claude models."""
    # Create Bedrock Runtime client
    # AWS credentials should be configured via environment variables or AWS config
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )

    # Prepare the request body for Claude models
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }

    # Invoke the model
    response = bedrock_runtime.invoke_model(
        modelId=model,
        body=json.dumps(request_body),
    )

    # Parse the response
    response_body = json.loads(response["body"].read())

    # Extract text from the response
    # Claude models return content as a list of content blocks
    if "content" in response_body and len(response_body["content"]) > 0:
        return response_body["content"][0]["text"]

    return ""
