# Math Solver

A simple local math solver that helps with mathematical problems. Uses Ollama for explanations and SymPy/mpmath for accurate computation. Everything runs locally with no external services.

## Features

- 🧮 **Math Solving**: Clear, step-by-step solutions
- 🛠️ **Tool Integration**: Automatic evaluation using SymPy and mpmath
- 💬 **Simple Chat**: Clean interface for asking math questions
- 🔒 **Privacy**: Everything runs locally, no data sent to external services

## Quick Start

### 1. Install Dependencies

```bash
cd Version_3
pip install -r requirements.txt
```

### 2. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai).

### 3. Pull a Model

```bash
ollama pull llama3.2:latest
```

Or any math-capable model you prefer.

### 4. Launch the Solver

```bash
python main.py
```

The web interface will open at http://localhost:7860

## Usage

### Basic Usage

1. Open the web interface
2. Type your math question (e.g., "Solve 2x + 3 = 7")
3. The solver will respond with step-by-step solutions

### Tool Integration

The solver automatically detects mathematical expressions and uses appropriate tools:

- **Basic Arithmetic**: For simple calculations (+, -, *, /)
  - Example: "What is 5 + 3?" → Result: 8
  - Example: "Calculate 10 * 7" → Result: 70
- **SymPy Tool**: For symbolic math (equations, calculus, algebra)
  - Example: "Solve x² - 5x + 6 = 0"
- **Numeric Tool**: For high-precision calculations
  - Example: "Calculate √2 with high precision"

## Security Notes

- All computation happens locally
- No external API calls (except to local Ollama)
- Conversation data stays on your machine

## Troubleshooting

- **Model not found**: Run `ollama pull llama3.2:latest`
- **Connection refused**: Ensure Ollama is running (`ollama serve`)
- **Slow responses**: Try a smaller model or reduce `MAX_TOKENS`

---

*Built with Gradio, Ollama, and SymPy*
