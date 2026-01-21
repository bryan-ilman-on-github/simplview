"""
Agent 1: The Planner

Analyzes user questions and data schema to create execution plans.
"""
import json
import re
import google.generativeai as genai
from typing import Dict, List, Any
import pandas as pd

from app.config import settings
from app.agents.prompts import PLANNER_SYSTEM_PROMPT


class PlannerAgent:
    """
    The Planner Agent analyzes user questions and creates execution plans.

    This is Agent 1 in the multi-agent workflow.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the Planner Agent with Gemini API.

        Args:
            api_key: Google Gemini API key. If None, uses settings.
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def _get_schema_description(self, df: pd.DataFrame) -> str:
        """
        Generate a human-readable schema description from a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            String description of the schema
        """
        schema_lines = ["Available Columns:"]
        for col in df.columns:
            dtype = str(df[col].dtype)
            # Get sample non-null values
            samples = df[col].dropna().head(3).tolist()
            samples_str = ", ".join(str(s) for s in samples)
            schema_lines.append(f"  - {col} ({dtype}): examples [{samples_str}]")

        schema_lines.append(f"\nTotal Rows: {len(df)}")
        return "\n".join(schema_lines)

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """
        Format conversation context for the prompt.

        Args:
            context: List of previous Q&A pairs

        Returns:
            Formatted context string
        """
        if not context:
            return "No previous conversation."

        lines = ["Previous Conversation:"]
        for i, item in enumerate(context[-5:], 1):  # Last 5 messages
            lines.append(f"  Q{i}: {item.get('question', '')}")
            lines.append(f"  A{i}: {item.get('answer', '')[:200]}...")  # Truncate long answers
        return "\n".join(lines)

    def _extract_json(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from Gemini response.

        Gemini sometimes wraps JSON in markdown code blocks.

        Args:
            response_text: Raw response text

        Returns:
            Parsed JSON dict
        """
        # Try to find JSON in code blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        if matches:
            return json.loads(matches[0])

        # Try to find JSON object directly
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        if matches:
            # Return the largest match (most complete JSON)
            return json.loads(max(matches, key=len))

        # Fallback: try parsing the whole response
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Return a default plan if all parsing fails
            return {
                "analysis": "Could not parse plan. Please try rephrasing your question.",
                "steps": ["Analyze the data manually"],
                "visualization": "none",
                "visualization_config": {},
                "expected_output": "Please try again with a clearer question."
            }

    def create_plan(
        self,
        df: pd.DataFrame,
        question: str,
        context: List[Dict[str, Any]] | None = None
    ) -> Dict[str, Any]:
        """
        Create an execution plan for the user's question.

        Args:
            df: The dataset to analyze
            question: User's natural language question
            context: Previous Q&A for follow-up questions

        Returns:
            Execution plan as a dictionary
        """
        schema = self._get_schema_description(df)
        context_str = self._format_context(context or [])

        prompt = PLANNER_SYSTEM_PROMPT.format(
            schema=schema,
            context=context_str,
            question=question
        )

        try:
            response = self.model.generate_content(prompt)
            plan = self._extract_json(response.text)
            return plan

        except Exception as e:
            # Return error plan
            return {
                "analysis": f"Error creating plan: {str(e)}",
                "steps": [],
                "visualization": "none",
                "visualization_config": {},
                "expected_output": "Please try again."
            }
