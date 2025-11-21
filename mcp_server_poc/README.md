# Model Context Protocol (MCP) Server - Proof of Concept

## Overview

This is a **proof-of-concept implementation** of a Model Context Protocol server in **Python 3.12** that demonstrates:

✅ **Reading local markdown files** - Access and process documentation  
✅ **DuckDB integration** - SQL database operations  
✅ **Prepared prompts** - Pre-configured prompts for specific tools  

## What is MCP?

The Model Context Protocol (MCP) is a standardized way for AI assistants to access tools, resources, and context. This server implements:

- **Tools**: Callable functions with defined schemas
- **Resources**: Available data sources (files, databases)
- **Prompts**: Pre-configured prompt templates for common tasks

## Features

### 1. Markdown File Operations 📄

```python
# List all markdown files
await server.call_tool("list_markdown_files", {})

# Read a specific file
await server.call_tool("read_markdown", {
    "filename": "getting_started.md"
})
```

### 2. DuckDB Database Integration 🗄️

```python
# Create tables
await server.call_tool("create_table", {
    "table_name": "users",
    "schema": "id INTEGER, name VARCHAR, email VARCHAR"
})

# Query data
await server.call_tool("query_database", {
    "query": "SELECT * FROM users"
})

# Insert data
await server.call_tool("insert_data", {
    "table_name": "users",
    "values": "(1, 'Alice', 'alice@example.com')"
})
```

### 3. Prepared Prompts 💬

```python
# Analyze documentation
await server.get_prompt("analyze_markdown_docs", {
    "focus_area": "installation"
})

# Database schema analysis
await server.get_prompt("database_schema_analysis", {})

# Documentation queries
await server.get_prompt("documentation_query", {
    "query": "How do I get started?"
})
```

## Installation

### Requirements
- Python 3.12 or higher
- DuckDB

### Setup

```bash
# Clone or navigate to the directory
cd mcp_server_poc

# Install dependencies
pip install -r requirements.txt

# Or using uv
uv pip install -r requirements.txt

# Run the demonstration
python mcp_server.py
```

## Project Structure

```
mcp_server_poc/
├── mcp_server.py          # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
├── README.md             # This file
└── docs/                 # Markdown documentation
    ├── getting_started.md
    ├── api_reference.md
    └── examples.md
```

## Usage Examples

### Basic Usage

```python
import asyncio
from mcp_server import MCPServer

async def main():
    # Initialize the server
    server = await MCPServer(
        markdown_dir="./docs",
        db_path=":memory:"
    ).initialize()
    
    # List available tools
    tools = await server.list_tools()
    print(f"Available tools: {[t['name'] for t in tools]}")
    
    # Use a tool
    result = await server.call_tool("list_markdown_files", {})
    print(f"Found {result['count']} markdown files")
    
    # Get a prepared prompt
    prompt = await server.get_prompt("analyze_markdown_docs", {
        "focus_area": "api"
    })
    print(prompt['prompt'])
    
    # Cleanup
    await server.shutdown()

asyncio.run(main())
```

### Running the Demo

```bash
python mcp_server.py
```

This will demonstrate:
- Listing available tools and prompts
- Reading markdown files
- Creating and querying a DuckDB database
- Using prepared prompts

## Available Tools

| Tool | Description |
|------|-------------|
| `read_markdown` | Read content of a markdown file |
| `list_markdown_files` | List all available markdown files |
| `query_database` | Execute SQL queries on DuckDB |
| `create_table` | Create a new database table |
| `insert_data` | Insert data into a table |

## Available Prompts

| Prompt | Description |
|--------|-------------|
| `analyze_markdown_docs` | Analyze and summarize documentation |
| `database_schema_analysis` | Analyze database schema |
| `create_sample_dataset` | Generate sample dataset instructions |
| `documentation_query` | Query documentation for information |

## Key Capabilities Demonstrated

### ✅ Python 3.12 Compatibility
- Uses modern Python 3.12 features
- Async/await for efficient operations
- Type hints with dataclasses

### ✅ Markdown File Reading
- Recursively finds markdown files
- Reads and processes content
- Lists available documentation

### ✅ DuckDB Integration
- In-memory or file-based database
- Full SQL query support
- Schema introspection
- CRUD operations

### ✅ Prepared Prompts
- Context-aware prompt generation
- Combines data from multiple sources
- Parameterized prompts
- Ready-to-use with LLMs

## Architecture

The server follows the MCP specification with three main components:

1. **Tools** - Executable functions with JSON schemas
2. **Resources** - Discoverable data sources
3. **Prompts** - Pre-configured prompt templates

```
┌─────────────────┐
│   AI Assistant  │
└────────┬────────┘
         │
         ├─ list_tools()
         ├─ call_tool(name, args)
         ├─ list_prompts()
         ├─ get_prompt(name, args)
         └─ list_resources()
         │
┌────────▼────────┐
│   MCP Server    │
├─────────────────┤
│ • Markdown      │
│ • DuckDB        │
│ • Prompts       │
└─────────────────┘
```

## Extending the Server

### Adding a New Tool

```python
# In _register_tools()
"my_tool": Tool(
    name="my_tool",
    description="Description of what it does",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param"]
    }
)

# Add implementation
async def _my_tool(self, param: str) -> Dict[str, Any]:
    # Implementation here
    return {"success": True, "result": "..."}
```

### Adding a New Prompt

```python
# In _register_prompts()
"my_prompt": Prompt(
    name="my_prompt",
    description="What this prompt does",
    arguments=[{"name": "arg", "description": "Argument description", "required": True}]
)

# Add implementation
async def _prompt_my_prompt(self, arg: str) -> Dict[str, Any]:
    prompt_text = f"Generated prompt using {arg}"
    return {"success": True, "prompt": prompt_text}
```

## Limitations & Future Enhancements

### Current Limitations
- In-memory database (data lost on restart)
- No authentication/authorization
- No streaming responses
- Single-threaded execution

### Potential Enhancements
- [ ] Add persistent database support
- [ ] Implement streaming for large results
- [ ] Add authentication layer
- [ ] Support more file formats (JSON, CSV, etc.)
- [ ] Add caching for frequently accessed resources
- [ ] Implement rate limiting
- [ ] Add logging and monitoring
- [ ] Create HTTP/WebSocket API
- [ ] Support for remote markdown repositories
- [ ] Advanced query optimization

## Testing

Run the built-in demonstration:

```bash
python mcp_server.py
```

Expected output:
```
==========================================
MCP SERVER - Proof of Concept
==========================================

📦 AVAILABLE TOOLS:
  • read_markdown: Read and return the content of a markdown file
  • list_markdown_files: List all available markdown files
  ...

💬 AVAILABLE PROMPTS:
  • analyze_markdown_docs: Analyze and summarize all markdown documentation files
  ...

==========================================
TESTING MARKDOWN FILE OPERATIONS
==========================================
...
```

## Contributing

This is a proof-of-concept. Feel free to:
- Add more tools and prompts
- Improve error handling
- Add tests
- Extend documentation

## License

This is demonstration code for educational purposes.

## References

- [DuckDB Documentation](https://duckdb.org/docs/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- Model Context Protocol specification

## Questions?

Check the documentation in the `docs/` folder:
- `getting_started.md` - Quick start guide
- `api_reference.md` - Complete API documentation
- `examples.md` - Usage examples

---

**Status**: ✅ Proof of Concept Complete

All requested features implemented:
- ✅ Python 3.12 compatibility
- ✅ Read local markdown files
- ✅ DuckDB integration
- ✅ Prepared prompts for tools
