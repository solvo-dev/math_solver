"""Ollama service for solving math problems using LLM."""

from __future__ import annotations

import json
import requests
from pathlib import Path
from typing import Optional


class OllamaService:
    """Service to interact with Ollama LLM for math problem solving."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        prompt_template_path: Optional[Path] = None,
    ):
        """Initialize Ollama service.
        
        Args:
            base_url: Ollama server URL
            model: Model name to use (e.g., 'llama2', 'neural-chat', 'mistral')
            prompt_template_path: Path to prompt template file
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.prompt_template_path = prompt_template_path
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️ Ollama server not reachable at {self.base_url}: {e}")
            return False
    
    def load_prompt_template(self) -> str:
        """Load prompt template from file.
        
        Returns:
            Template content as string
        """
        if not self.prompt_template_path or not self.prompt_template_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {self.prompt_template_path}")
        
        with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
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
        top_k: int = 40,
        num_predict: int = 500,
    ) -> str:
        """Send prompt to Ollama and get solution.
        
        Args:
            prompt: The prompt to send
            temperature: Controls randomness (0-1)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            num_predict: Maximum tokens to generate
            
        Returns:
            Generated solution text
        """
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "num_predict": num_predict,
            }
            
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
        
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )
        except Exception as e:
            raise RuntimeError(f"Error calling Ollama: {e}")
    
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
            Complete response with prompt and solution
        """
        try:
            # Create filled prompt
            prompt = self.create_prompt(problem, rationale, correct, user_input)
            
            # Get solution from Ollama
            solution = self.solve(prompt, **kwargs)
            
            # Combine prompt and solution
            # response = f"**Erstellter Prompt:**\n\n{prompt}\n\n"
            # response += f"---\n\n**Lösung vom LLM:**\n\n{solution}"
            
            return solution
        
        except Exception as e:
            return f"⚠️ Fehler bei der Problemlösung: {e}"
