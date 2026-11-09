"""Hinglish translation service using Sarvam AI API."""

import re
import httpx
from app.core.config import settings


class SarvamTranslator:
    """Translator for Hinglish (Hindi + English) using Sarvam AI."""

    def __init__(self):
        self.api_key = settings.sarvam_api_key
        self.chat_model = settings.sarvam_chat_model
        self.translate_model = settings.sarvam_translate_model
        self.enabled = settings.hinglish_translation_enabled
        self.base_url = "https://api.sarvam.ai"

    async def translate_hinglish_to_english(self, text: str) -> str:
        """Normalize Hinglish text to English using chat completion API."""
        if not self.enabled or not self.api_key:
            return text

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "api-subscription-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.chat_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a language normalizer. Convert Hinglish (Hindi written in English script) to standard English. Only return the normalized English text, nothing else."
                            },
                            {
                                "role": "user",
                                "content": text
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 200
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    translated = result.get("choices", [{}])[0].get("message", {}).get("content", text)
                    return translated.strip()
                else:
                    print(f"Sarvam API error: {response.status_code} - {response.text}")
                    return text
        except Exception as e:
            print(f"Sarvam translation error: {e}")
            return text

    async def translate_english_to_hinglish(self, text: str) -> str:
        """Translate English text to Hindi using Sarvam translate API."""
        if not self.enabled or not self.api_key:
            return text

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/translate",
                    headers={
                        "api-subscription-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "input": text,
                        "source_language_code": "en-IN",
                        "target_language_code": "hi-IN",
                        "model": self.translate_model,
                        "numerals_format": "international",
                        "mode": "formal"
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    translated = result.get("translated_text", text)
                    return translated.strip()
                else:
                    print(f"Sarvam API error: {response.status_code} - {response.text}")
                    return text
        except Exception as e:
            print(f"Sarvam translation error: {e}")
            return text

    def is_hinglish(self, text: str) -> bool:
        """Detect if text contains Hinglish (Hindi written in Latin script)."""
        if not text or len(text.strip()) < 3:
            return False

        # Words that are purely Hindi written in Roman script
        distinctive_hinglish_words = {
            "kya", "hai", "hain", "kaise", "kaisa", "kaisi", "kahan", "kab", "kyun", "kaun",
            "mera", "mere", "meri", "mujhe", "mujho", "tum", "tumhara", "tumhari",
            "aap", "aapka", "aapki", "hum", "hamara", "hamari", "hoga", "hogi", "hoge",
            "tha", "thi", "the", "chahiye", "karna", "karo", "karne", "karunga", "karungi",
            "batao", "bataye", "batayiye", "dikhaye", "dikhao", "nahi", "nahin", "mat",
            "bhi", "toh", "lekin", "magar", "aur", "ya", "sath", "saath", "liye"
        }

        # Extract words from text
        words = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
        
        # Check if any distinctive Hinglish word is present
        matching_words = words.intersection(distinctive_hinglish_words)
        return len(matching_words) > 0
