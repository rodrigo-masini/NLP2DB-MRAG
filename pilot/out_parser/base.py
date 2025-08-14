from __future__ import annotations
import json
import re
from abc import ABC
from typing import Any, TypeVar
from pilot.utils import build_logger

T = TypeVar("T")
logger = build_logger("OutputParser", "output_parser.log")

class BaseOutputParser(ABC):
    """Base class to parse the output of an LLM call."""

    def __init__(self, sep: str, is_stream_out: bool):
        self.sep = sep
        self.is_stream_out = is_stream_out

    def _extract_json(self, text: str) -> str:
        """Extracts a JSON object from a string."""
        # Use a non-greedy regex to find the first valid JSON object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                # Verify it's valid JSON
                json.loads(match.group(0))
                return match.group(0)
            except json.JSONDecodeError:
                logger.warning("Found a JSON-like structure that failed to parse.")
        
        logger.warning("Could not find a valid JSON object in the output.")
        return text # Return original text if no JSON is found

    def parse_prompt_response(self, model_out_text: str) -> Any:
        """
        Parses the model output text to extract a structured response.
        This implementation now robustly finds and parses JSON.
        """
        cleaned_output = model_out_text.strip()
        if "```json" in cleaned_output:
            cleaned_output = cleaned_output.split("```json")[1]
        if "```" in cleaned_output:
            cleaned_output = cleaned_output.split("```")[0]
        
        json_str = self._extract_json(cleaned_output)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}\nOriginal text: {model_out_text}")
            # Fallback: return the raw text if JSON parsing fails
            return {"error": "Failed to parse JSON", "raw_text": model_out_text}

    def parse_view_response(self, ai_text: str, data: Any) -> str:
        """
        Default implementation to format the AI's thoughts and data for the user.
        Scenes can override this for custom formatting.
        """
        response = f"**Thought:** {ai_text}\n\n"
        if isinstance(data, list) and data:
            try:
                import pandas as pd
                df = pd.DataFrame(data[1:], columns=data[0])
                response += "**Result:**\n"
                response += df.to_markdown(index=False)
            except Exception:
                response += f"**Result:**\n```json\n{json.dumps(data, indent=2)}\n```"
        elif data:
            response += f"**Result:**\n```\n{data}\n```"
        
        return response
