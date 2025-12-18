"""
LLM Client for uAgents Hiring System
===================================

This file contains the shared LLM client that all uAgents use to communicate with Google Gemini.
"""

import aiohttp
import ssl
import json
import re
import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API configuration from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = os.getenv("GEMINI_API_URL")


class SimpleLLMAgent:
    """Base class for LLM-powered agents"""

    def __init__(self, name: str):
        self.name = name
        self.api_key = GEMINI_API_KEY
        self.api_url = GEMINI_API_URL

    async def query_llm(self, prompt: str) -> dict:
        """Query Gemini API with a prompt and get response"""
        headers = {
            "Content-Type": "application/json",
        }

        # Gemini API uses contents format and combines system + user prompts
        full_prompt = "You are a specialized AI agent for hiring analysis. Provide clear, structured responses in valid JSON format.\n\n" + prompt

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1700,
            }
        }

        # Gemini API key goes in the URL
        api_url_with_key = f"{self.api_url}?key={self.api_key}"

        try:
            print(f"🔗 {self.name}: Querying Gemini API")

            # Create SSL context to bypass certificate verification
            # SSL is encrption from the server to the client
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    api_url_with_key, headers=headers, json=payload, timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Gemini response format: candidates[0].content.parts[0].text
                        content = result["candidates"][0]["content"]["parts"][0]["text"]
                        return {
                            "success": True,
                            "content": content,
                        }
                    else:
                        error_text = await response.text()
                        print(
                            f"❌ {self.name}: API Error {response.status}: {error_text}"
                        )
                        return {
                            "success": False,
                            "content": f"API Error {response.status}: {error_text}",
                        }
        except Exception as e:
            print(f"💥 {self.name}: Error querying Gemini: {e}")
            return {"success": False, "content": f"Request Error: {str(e)}"}

    def parse_json_response(self, content: str) -> Dict:
        """Parse JSON response from LLM, handling markdown formatting"""
        try:
            # Remove markdown code blocks if present
            content = re.sub(
                r"^```json\s*|```$", "", content.strip(), flags=re.MULTILINE
            )
            content = content.strip()
            return json.loads(content)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ {self.name}: JSON parsing error: {e}")
            return {}
