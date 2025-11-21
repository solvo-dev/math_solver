# Getting Started with MCP Server

## Introduction

This Model Context Protocol (MCP) server provides tools and resources for AI assistants to interact with:
- Local markdown documentation files
- DuckDB databases
- Pre-configured prompts for common tasks

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or using uv
uv pip install -r requirements.txt
```

## Quick Start

1. Place your markdown files in the `docs/` directory
2. Run the server:

```bash
python mcp_server.py
```

## Features

### 1. Markdown File Operations
- Read markdown files
- List all available documentation
- Search and query documentation

### 2. Database Operations
- Create tables in DuckDB
- Insert and query data
- Analyze database schemas

### 3. Prepared Prompts
- Pre-configured prompts for common tasks
- Context-aware documentation analysis
- Database schema insights

## Example Usage

```python
# Initialize the server
server = await MCPServer(
    markdown_dir="./docs",
    db_path=":memory:"
).initialize()

# List available tools
tools = await server.list_tools()

# Call a tool
result = await server.call_tool("read_markdown", {
    "filename": "getting_started.md"
})

# Use a prepared prompt
prompt = await server.get_prompt("analyze_markdown_docs", {
    "focus_area": "installation"
})
```

## Next Steps

- Explore the available tools and prompts
- Customize prompts for your use case
- Integrate with your AI assistant
