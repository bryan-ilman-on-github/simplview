"""
Agent 2: The Executor

Uses PandasAI + Gemini to execute plans and retrieve answers.
"""
import json
import re
import google.generativeai as genai
from typing import Dict, List, Any, Optional
import pandas as pd

from app.config import settings
from app.agents.prompts import EXECUTOR_SYSTEM_PROMPT


class ExecutorAgent:
    """
    The Executor Agent executes plans and analyzes data.

    This is Agent 2 in the multi-agent workflow.
    Uses Gemini for code generation and pandas for execution.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Executor Agent with Gemini API.

        Args:
            api_key: Google Gemini API key. If None, uses settings.
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format conversation context for the prompt."""
        if not context:
            return "No previous conversation."

        lines = ["Previous Conversation:"]
        for i, item in enumerate(context[-5:], 1):
            lines.append(f"  Q{i}: {item.get('question', '')}")
            lines.append(f"  A{i}: {item.get('answer', '')[:200]}...")
        return "\n".join(lines)

    def _extract_json(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response."""
        # Try to find JSON in code blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        if matches:
            return json.loads(matches[0])

        # Try to find JSON object directly
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)

        if matches:
            return json.loads(max(matches, key=len))

        # Fallback
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "answer": response_text,
                "data": None,
                "chart_type": "none",
                "insights": []
            }

    def _execute_with_pandas(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """
        Execute analysis using pandas directly.

        This provides a fallback when JSON parsing fails.
        """
        response = self.model.generate_content(
            f"You are a data analyst. Analyze this data and answer the question. "
            f"Return ONLY a valid JSON response with 'answer' and 'insights' keys.\n\n"
            f"Question: {question}\n"
            f"Data has {len(df)} rows and columns: {', '.join(df.columns.tolist())}"
        )

        try:
            return self._extract_json(response.text)
        except:
            return {
                "answer": response.text,
                "data": None,
                "chart_type": "none",
                "insights": []
            }

    def execute(
        self,
        df: pd.DataFrame,
        plan: Dict[str, Any],
        question: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Execute the plan and return results.

        Args:
            df: The dataset to analyze
            plan: Execution plan from the Planner
            question: Original user question
            context: Previous Q&A for follow-up context

        Returns:
            Result dictionary with answer, chart data, and insights
        """
        context_str = self._format_context(context or [])

        prompt = EXECUTOR_SYSTEM_PROMPT.format(
            plan=json.dumps(plan, indent=2),
            n_rows=len(df),
            context=context_str
        )

        # Add the actual question to the prompt
        full_prompt = f"{prompt}\n\nUser Question: {question}"

        try:
            response = self.model.generate_content(full_prompt)
            result = self._extract_json(response.text)

            # If chart is expected but not in result, try to extract it
            if plan.get("visualization") != "none" and not result.get("data"):
                result["data"] = self._generate_chart_data(df, plan)

            return result

        except Exception as e:
            return {
                "answer": f"Error executing analysis: {str(e)}",
                "data": None,
                "chart_type": "none",
                "insights": []
            }

    def _generate_chart_data(
        self,
        df: pd.DataFrame,
        plan: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate chart data from DataFrame based on plan.

        Args:
            df: The dataset
            plan: Execution plan with visualization config

        Returns:
            Chart data dict or None
        """
        viz_config = plan.get("visualization_config", {})
        viz_type = plan.get("visualization", "none")

        if viz_type == "none" or not viz_config:
            return None

        try:
            x_axis = viz_config.get("x_axis")
            y_axis = viz_config.get("y_axis")

            if not x_axis or not y_axis:
                return None

            # Handle multiple y axes (for grouped charts)
            if isinstance(y_axis, str):
                y_axis = [y_axis]

            # Group by x_axis and aggregate
            if len(y_axis) == 1:
                grouped = df.groupby(x_axis, as_index=False)[y_axis[0]].sum()
                labels = grouped[x_axis].tolist()
                values = grouped[y_axis[0]].tolist()

                return {
                    "labels": labels,
                    "values": values
                }
            else:
                # Multiple series
                grouped = df.groupby(x_axis, as_index=False)[y_axis].sum()
                labels = grouped[x_axis].tolist()

                additional_series = []
                for col in y_axis:
                    additional_series.append({
                        "name": col,
                        "data": grouped[col].tolist()
                    })

                return {
                    "labels": labels,
                    "values": grouped[y_axis[0]].tolist(),
                    "additional_series": additional_series
                }

        except Exception as e:
            print(f"Error generating chart data: {e}")
            return None

    def answer_simple_question(
        self,
        df: pd.DataFrame,
        question: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Answer a simple question without a formal plan.

        Useful for quick queries.

        Args:
            df: The dataset
            question: User's question
            context: Previous Q&A

        Returns:
            Answer as string
        """
        context_str = self._format_context(context or [])

        prompt = f"""You are a data analyst. Answer the user's question about their data.

Data Info:
- Rows: {len(df)}
- Columns: {', '.join(df.columns.tolist())}

{context_str}

Question: {question}

Provide a clear, concise answer. If calculations are needed, explain your reasoning.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
