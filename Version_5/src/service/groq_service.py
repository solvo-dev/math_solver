"""Groq service for solving math problems using Groq API."""

from __future__ import annotations

import os
import requests
from pathlib import Path
from typing import Optional


class GroqService:
    """Service to interact with Groq API for math problem solving."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.groq.com/openai/v1/",
        model: str = "llama-3.3-70b-versatile",
        prompt_template_path: Optional[Path] = None,
        timeout: int = 60,
    ):
        """Initialize Groq service.

        Args:
            api_key: Groq API key (defaults to env GROQ_API_KEY)
            base_url: Groq API base URL
            model: Model name to use (e.g., 'llama-3.3-70b-versatile')
            prompt_template_path: Path to prompt template file
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.prompt_template_path = prompt_template_path
        self.timeout = timeout
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Missing Groq API key. Set GROQ_API_KEY or pass api_key.")

        self._test_connection()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _test_connection(self) -> bool:
        """Test if Groq API is reachable."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self._headers(),
                timeout=10,
            )
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Groq API not reachable at {self.base_url}: {e}")
            return False

    def load_prompt_template(self) -> str:
        """Load prompt template from file.

        Returns:
            Template content as string
        """
        if not self.prompt_template_path or not self.prompt_template_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {self.prompt_template_path}")

        with open(self.prompt_template_path, "r", encoding="utf-8") as f:
            return f.read()

    def create_prompt(
        self,
        problem: str,
        rationale: str,
        correct: str,
        user_input: str,
    ) -> str:
        """Create prompt by replacing template placeholders.

        Args:
            problem: Example problem
            rationale: Example rationale/solution approach
            correct: Example correct answer
            user_input: User's current question

        Returns:
            Filled prompt template
        """
        template = self.load_prompt_template()

        prompt = template.replace("{Problem}", problem)
        prompt = prompt.replace("{rational}", rationale)
        prompt = prompt.replace("{correct}", correct)
        prompt = prompt.replace("{input}", user_input)

        return prompt

    def solve(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 500,
    ) -> str:
        """Send prompt to Groq API and get solution.

        Args:
            prompt: The prompt to send
            temperature: Controls randomness (0-1)
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate

        Returns:
            Generated solution text
        """
        try:
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
                "stream": False,
            }

            response = requests.post(
                url,
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()

            result = response.json()
            choices = result.get("choices", [])
            if not choices:
                return ""
            message = choices[0].get("message", {})
            return (message.get("content") or "").strip()

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Groq API at {self.base_url}."
            )
        except Exception as e:
            raise RuntimeError(f"Error calling Groq API: {e}")

    def solve_math_problem(
        self,
        user_input: str,
        problem: str,
        rationale: str,
        correct: str,
        **kwargs,
    ) -> str:
        """Complete workflow: create prompt and solve.

        Args:
            user_input: User's math problem
            problem: Example problem from similar search
            rationale: Example rationale
            correct: Example correct answer
            **kwargs: Additional parameters for solve()

        Returns:
            Solution text
        """
        try:
            prompt = self.create_prompt(problem, rationale, correct, user_input)
            solution = self.solve(prompt, **kwargs)
            return solution
        except Exception as e:
            return f"⚠️ Fehler bei der Problemlösung: {e}"
