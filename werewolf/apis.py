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
from typing import Any, Optional

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
from openai import OpenAI

# Module-level client cache to avoid recreating clients on every call
_bedrock_client: Optional[Any] = None
_openai_client: Optional[OpenAI] = None
_ollama_base_url: str = "http://localhost:11434"


def _get_bedrock_client() -> Any:
    """Returns a cached Bedrock Runtime client."""
    global _bedrock_client
    if _bedrock_client is None:
        region = os.environ.get("AWS_REGION", "us-east-1")
        try:
            _bedrock_client = boto3.client(
                service_name="bedrock-runtime",
                region_name=region,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to create AWS Bedrock client. Ensure AWS credentials are configured. Error: {e}",
            ) from e
    return _bedrock_client


def _get_openai_client() -> OpenAI:
    """Returns a cached OpenAI client."""
    global _openai_client
    if _openai_client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY environment variable is not set. Please configure your OpenAI API key.",
            )
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def generate(model: str, **kwargs: Any) -> str:
    """Routes model generation requests to the appropriate provider.

    Args:
        model: Model identifier (e.g., 'gpt-4', 'claude-3-sonnet', 'deepseek-r1')
        **kwargs: Additional arguments passed to the provider function

    Returns:
        Generated text response

    Raises:
        ValueError: If model is not supported
    """
    if not model:
        raise ValueError("Model parameter cannot be empty")

    if "gpt" in model:
        return generate_openai(model, **kwargs)
    if "claude" in model or "anthropic" in model:
        return generate_bedrock(model, **kwargs)
    if model.startswith("ollama:"):
        # Ollama models are prefixed with "ollama:"
        ollama_model = model.replace("ollama:", "")
        return generate_ollama(ollama_model, **kwargs)
    raise ValueError(
        f"Unsupported model: {model}. Supported models: OpenAI (gpt-*), AWS Bedrock (claude-*, anthropic.*), and Ollama (ollama:*).",
    )


# openai
def generate_openai(
    model: str,
    prompt: str,
    json_mode: bool = True,
    **_kwargs: Any,
) -> str:
    """Generates text using OpenAI API.

    Args:
        model: OpenAI model identifier (e.g., 'gpt-4', 'gpt-4o')
        prompt: Input prompt text
        json_mode: If True, request JSON-formatted response
        **kwargs: Additional arguments (unused, for compatibility)

    Returns:
        Generated text response

    Raises:
        RuntimeError: If API key is not configured or API call fails
        ValueError: If response is invalid
    """
    if not prompt:
        raise ValueError("Prompt parameter cannot be empty")

    try:
        client = _get_openai_client()

        response_format = {"type": "text"}
        if json_mode:
            response_format = {"type": "json_object"}

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format,
            model=model,
        )

        if not response.choices or not response.choices[0].message.content:
            raise ValueError(
                f"OpenAI API returned invalid response for model {model}",
            )

        return response.choices[0].message.content

    except Exception as e:
        if isinstance(e, (RuntimeError, ValueError)):
            raise
        raise RuntimeError(f"OpenAI API call failed for model {model}: {e}") from e


# aws bedrock
def generate_bedrock(
    model: str,
    prompt: str,
    _json_mode: bool = True,
    **kwargs: Any,
) -> str:
    """Generates text using AWS Bedrock with Claude models.

    Args:
        model: Bedrock model identifier (e.g., 'anthropic.claude-3-sonnet-20240229-v1:0')
        prompt: Input prompt text
        json_mode: Reserved for future use (currently ignored for Bedrock compatibility)
        **kwargs: Additional arguments:
            - max_tokens: Maximum tokens to generate (default: 4096)
            - temperature: Sampling temperature (default: not set, uses model default)

    Returns:
        Generated text response

    Raises:
        RuntimeError: If AWS credentials are not configured or API call fails
        ValueError: If prompt is empty or response is invalid
    """
    if not prompt:
        raise ValueError("Prompt parameter cannot be empty")

    try:
        bedrock_runtime = _get_bedrock_client()

        # Extract optional parameters
        max_tokens = kwargs.get("max_tokens", 4096)
        temperature = kwargs.get("temperature")

        # Prepare the request body for Claude models
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Add temperature if specified
        if temperature is not None:
            request_body["temperature"] = temperature

        # Invoke the model
        response = bedrock_runtime.invoke_model(
            modelId=model,
            body=json.dumps(request_body),
        )

        # Parse the response
        response_body = json.loads(response["body"].read())

        # Extract text from the response
        # Claude models return content as a list of content blocks
        if "content" not in response_body:
            raise ValueError(
                f"AWS Bedrock returned response without 'content' field for model {model}",
            )

        if not response_body["content"] or len(response_body["content"]) == 0:
            raise ValueError(
                f"AWS Bedrock returned empty content for model {model}",
            )

        return response_body["content"][0]["text"]

    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(
            f"AWS Bedrock API call failed for model {model}. "
            f"Ensure AWS credentials are configured and the model is accessible. Error: {e}",
        ) from e
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse AWS Bedrock response for model {model}: {e}",
        ) from e
    except Exception as e:
        if isinstance(e, (RuntimeError, ValueError)):
            raise
        raise RuntimeError(
            f"Unexpected error calling AWS Bedrock for model {model}: {e}",
        ) from e


# ollama
def generate_ollama(model: str, prompt: str, json_mode: bool = True, **kwargs: Any) -> str:
    """Generates text using Ollama API with local models.

    Args:
        model: Ollama model identifier (e.g., 'deepseek-r1:latest', 'llama2')
        prompt: Input prompt text
        json_mode: If True, request JSON-formatted response
        **kwargs: Additional arguments:
            - max_tokens: Maximum tokens to generate (default: 4096)
            - temperature: Sampling temperature (default: 0.7)

    Returns:
        Generated text response

    Raises:
        RuntimeError: If Ollama server is not running or API call fails
        ValueError: If prompt is empty or response is invalid
    """
    if not prompt:
        raise ValueError("Prompt parameter cannot be empty")

    try:
        # Override base URL if provided via environment variable
        base_url = os.environ.get("OLLAMA_BASE_URL", _ollama_base_url)

        # Extract optional parameters
        max_tokens = kwargs.get("max_tokens", 4096)
        temperature = kwargs.get("temperature", 0.7)

        # Prepare the request body
        request_body = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        # Add format parameter for JSON mode
        if json_mode:
            request_body["format"] = "json"

        # Make the API call to Ollama
        response = requests.post(
            f"{base_url}/api/generate",
            json=request_body,
            timeout=300,  # 5 minute timeout for generation
        )

        response.raise_for_status()

        # Parse the response
        response_data = response.json()

        if "response" not in response_data:
            raise ValueError(
                f"Ollama API returned response without 'response' field for model {model}",
            )

        return response_data["response"]

    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Could not connect to Ollama server at {base_url}. "
            f"Ensure Ollama is running (try 'ollama serve'). Error: {e}",
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Ollama API call timed out for model {model}. "
            f"The model may be too slow or the prompt too complex. Error: {e}",
        ) from e
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Ollama API returned HTTP error for model {model}. "
            f"The model may not be available. Try 'ollama pull {model}'. Error: {e}",
        ) from e
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse Ollama response for model {model}: {e}",
        ) from e
    except Exception as e:
        if isinstance(e, (RuntimeError, ValueError)):
            raise
        raise RuntimeError(
            f"Unexpected error calling Ollama for model {model}: {e}",
        ) from e
