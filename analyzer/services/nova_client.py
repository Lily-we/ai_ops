import json
import os
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError


class NovaClientError(RuntimeError):
    pass


class NovaClient:
    """
    Thin wrapper over Bedrock Runtime invoke_model for Nova 2.
    """

    def __init__(
        self,
        region: Optional[str] = None,
        model_id: Optional[str] = None,
        timeout_seconds: int = 15,
    ):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        # Nova 2 Lite modelId options include:
        #   us.amazon.nova-2-lite-v1:0
        #   global.amazon.nova-2-lite-v1:0
        # (docs list both) :contentReference[oaicite:2]{index=2}
        self.model_id = model_id or os.getenv("NOVA_MODEL_ID", "amazon.nova-2-lite-v1:0")

        cfg = Config(
            connect_timeout=5,
            read_timeout=timeout_seconds,
            retries={"max_attempts": 1},
        )
        self.client = boto3.client("bedrock-runtime", region_name=self.region, config=cfg)

    def invoke_text(self, system_prompt: str, user_prompt: str, max_tokens: int = 900, temperature: float = 0.2) -> str:
        try:
            resp = self.client.converse(
                modelId=self.model_id,
                system=[{"text": system_prompt}],
                messages=[{"role": "user", "content": [{"text": user_prompt}]}],
                inferenceConfig={"maxTokens": max_tokens, "temperature": temperature},
        )

            content_list = resp["output"]["message"]["content"]
            text_block = next((item for item in content_list if "text" in item), None)
            if not text_block:
                 raise NovaClientError("Nova returned no text block.")
            return text_block["text"]

        except (ClientError, BotoCoreError, KeyError, ValueError) as e:
            raise NovaClientError(str(e)) from e
