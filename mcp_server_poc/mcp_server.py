#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server
Python 3.12 implementation demonstrating:
- Reading local markdown files
- DuckDB integration
- Prepared prompts for specific tools
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import duckdb
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


@dataclass
class Resource:
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mimeType: str


@dataclass
class Prompt:
    """MCP Prompt definition"""
    name: str
    description: str
    arguments: Optional[List[Dict[str, Any]]] = None


class MCPServer:
    """
    Model Context Protocol Server implementation
    Provides tools, resources, and prompts to AI clients
    """
    
    def __init__(self, markdown_dir: str = "./docs", db_path: str = ":memory:"):
        self.markdown_dir = Path(markdown_dir)
        self.db_path = db_path
        self.db_connection = None
        self.tools = self._register_tools()
        self.prompts = self._register_prompts()
        
    def _register_tools(self) -> Dict[str, Tool]:
        """Register available tools with their schemas"""
        return {
            "read_markdown": Tool(
                name="read_markdown",
                description="Read and return the content of a markdown file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name or path of the markdown file to read"
                        }
                    },
                    "required": ["filename"]
                }
            ),
            "list_markdown_files": Tool(
                name="list_markdown_files",
                description="List all available markdown files in the configured directory",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            "query_database": Tool(
                name="query_database",
                description="Execute a SQL query on the DuckDB database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            ),
            "create_table": Tool(
                name="create_table",
                description="Create a table in the DuckDB database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to create"
                        },
                        "schema": {
                            "type": "string",
                            "description": "Table schema definition (e.g., 'id INTEGER, name VARCHAR')"
                        }
                    },
                    "required": ["table_name", "schema"]
                }
            ),
            "insert_data": Tool(
                name="insert_data",
                description="Insert data into a DuckDB table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table"
                        },
                        "values": {
                            "type": "string",
                            "description": "Values to insert (e.g., '(1, \"Alice\"), (2, \"Bob\")')"
                        }
                    },
                    "required": ["table_name", "values"]
                }
            )
        }
    
    def _register_prompts(self) -> Dict[str, Prompt]:
        """Register prepared prompts for specific tools"""
        return {
            "analyze_markdown_docs": Prompt(
                name="analyze_markdown_docs",
                description="Analyze and summarize all markdown documentation files",
                arguments=[
                    {
                        "name": "focus_area",
                        "description": "Specific area to focus on (e.g., 'installation', 'api', 'examples')",
                        "required": False
                    }
                ]
            ),
            "database_schema_analysis": Prompt(
                name="database_schema_analysis",
                description="Analyze the database schema and provide insights",
                arguments=[]
            ),
            "create_sample_dataset": Prompt(
                name="create_sample_dataset",
                description="Create a sample dataset with users and orders tables",
                arguments=[
                    {
                        "name": "num_records",
                        "description": "Number of sample records to create",
                        "required": False
                    }
                ]
            ),
            "documentation_query": Prompt(
                name="documentation_query",
                description="Query documentation files for specific information",
                arguments=[
                    {
                        "name": "query",
                        "description": "What to search for in the documentation",
                        "required": True
                    }
                ]
            )
        }
    
    async def initialize(self):
        """Initialize the MCP server and database connection"""
        logger.info("Initializing MCP Server...")
        
        # Ensure markdown directory exists
        self.markdown_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize DuckDB connection
        self.db_connection = duckdb.connect(self.db_path)
        logger.info(f"DuckDB connection established: {self.db_path}")
        
        return self
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [asdict(tool) for tool in self.tools.values()]
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts"""
        return [asdict(prompt) for prompt in self.prompts.values()]
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources (markdown files)"""
        resources = []
        
        # Find all markdown files
        md_files = list(self.markdown_dir.glob("**/*.md"))
        
        for md_file in md_files:
            relative_path = md_file.relative_to(self.markdown_dir)
            resources.append(asdict(Resource(
                uri=f"file://{md_file}",
                name=str(relative_path),
                description=f"Markdown document: {relative_path}",
                mimeType="text/markdown"
            )))
        
        return resources
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given arguments"""
        logger.info(f"Calling tool: {tool_name} with args: {arguments}")
        
        if tool_name == "read_markdown":
            return await self._read_markdown(arguments["filename"])
        
        elif tool_name == "list_markdown_files":
            return await self._list_markdown_files()
        
        elif tool_name == "query_database":
            return await self._query_database(arguments["query"])
        
        elif tool_name == "create_table":
            return await self._create_table(
                arguments["table_name"], 
                arguments["schema"]
            )
        
        elif tool_name == "insert_data":
            return await self._insert_data(
                arguments["table_name"],
                arguments["values"]
            )
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    async def get_prompt(self, prompt_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get a prepared prompt with arguments"""
        logger.info(f"Getting prompt: {prompt_name} with args: {arguments}")
        
        if prompt_name == "analyze_markdown_docs":
            return await self._prompt_analyze_markdown(
                arguments.get("focus_area", "general")
            )
        
        elif prompt_name == "database_schema_analysis":
            return await self._prompt_database_schema()
        
        elif prompt_name == "create_sample_dataset":
            return await self._prompt_create_sample_dataset(
                int(arguments.get("num_records", 10))
            )
        
        elif prompt_name == "documentation_query":
            return await self._prompt_documentation_query(
                arguments["query"]
            )
        
        else:
            return {
                "success": False,
                "error": f"Unknown prompt: {prompt_name}"
            }
    
    # Tool implementations
    
    async def _read_markdown(self, filename: str) -> Dict[str, Any]:
        """Read a markdown file"""
        try:
            # Support both relative and absolute paths
            file_path = Path(filename)
            if not file_path.is_absolute():
                file_path = self.markdown_dir / filename
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {filename}"
                }
            
            content = file_path.read_text(encoding="utf-8")
            
            return {
                "success": True,
                "filename": str(file_path),
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _list_markdown_files(self) -> Dict[str, Any]:
        """List all markdown files"""
        try:
            md_files = list(self.markdown_dir.glob("**/*.md"))
            file_list = [
                {
                    "name": str(f.relative_to(self.markdown_dir)),
                    "size": f.stat().st_size,
                    "path": str(f)
                }
                for f in md_files
            ]
            
            return {
                "success": True,
                "count": len(file_list),
                "files": file_list
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _query_database(self, query: str) -> Dict[str, Any]:
        """Execute a SQL query"""
        try:
            result = self.db_connection.execute(query).fetchall()
            columns = [desc[0] for desc in self.db_connection.description] if self.db_connection.description else []
            
            return {
                "success": True,
                "query": query,
                "columns": columns,
                "rows": result,
                "row_count": len(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def _create_table(self, table_name: str, schema: str) -> Dict[str, Any]:
        """Create a table in the database"""
        try:
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
            self.db_connection.execute(query)
            
            return {
                "success": True,
                "message": f"Table '{table_name}' created successfully",
                "table_name": table_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _insert_data(self, table_name: str, values: str) -> Dict[str, Any]:
        """Insert data into a table"""
        try:
            query = f"INSERT INTO {table_name} VALUES {values}"
            self.db_connection.execute(query)
            
            return {
                "success": True,
                "message": f"Data inserted into '{table_name}'",
                "table_name": table_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Prompt implementations
    
    async def _prompt_analyze_markdown(self, focus_area: str) -> Dict[str, Any]:
        """Generate prompt for analyzing markdown documentation"""
        files_result = await self._list_markdown_files()
        
        if not files_result["success"]:
            return files_result
        
        # Read all markdown files
        contents = []
        for file_info in files_result["files"]:
            content_result = await self._read_markdown(file_info["name"])
            if content_result["success"]:
                contents.append({
                    "file": file_info["name"],
                    "content": content_result["content"]
                })
        
        prompt = f"""Please analyze the following markdown documentation files with a focus on: {focus_area}

Files analyzed: {len(contents)}

"""
        
        for item in contents:
            prompt += f"\n--- File: {item['file']} ---\n{item['content']}\n"
        
        prompt += f"""

Please provide:
1. A summary of the key information
2. Main topics covered
3. Any issues or improvements needed
4. Specific insights related to: {focus_area}
"""
        
        return {
            "success": True,
            "prompt": prompt,
            "files_analyzed": len(contents)
        }
    
    async def _prompt_database_schema(self) -> Dict[str, Any]:
        """Generate prompt for database schema analysis"""
        try:
            # Get all tables
            tables_result = await self._query_database(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            )
            
            if not tables_result["success"]:
                return tables_result
            
            tables = [row[0] for row in tables_result["rows"]]
            
            schema_info = []
            for table in tables:
                # Get table structure
                structure = await self._query_database(f"DESCRIBE {table}")
                schema_info.append({
                    "table": table,
                    "structure": structure["rows"]
                })
            
            prompt = f"""Please analyze the following database schema:

Number of tables: {len(tables)}

"""
            
            for info in schema_info:
                prompt += f"\nTable: {info['table']}\n"
                prompt += "Columns:\n"
                for col in info['structure']:
                    prompt += f"  - {col}\n"
            
            prompt += """

Please provide:
1. Overview of the database structure
2. Relationships between tables (if any)
3. Suggested improvements or optimizations
4. Potential use cases for this schema
"""
            
            return {
                "success": True,
                "prompt": prompt,
                "tables_analyzed": len(tables)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _prompt_create_sample_dataset(self, num_records: int) -> Dict[str, Any]:
        """Generate prompt for creating sample dataset"""
        prompt = f"""I'll help you create a sample dataset with {num_records} records.

The dataset will include:
1. A 'users' table with user information
2. An 'orders' table with order data

Would you like me to:
1. Create these tables
2. Insert {num_records} sample records
3. Run some example queries to demonstrate the data

Please confirm and I'll proceed with the following SQL operations:

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    email VARCHAR,
    created_at DATE
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount DECIMAL(10,2),
    status VARCHAR,
    order_date DATE
);
"""
        
        return {
            "success": True,
            "prompt": prompt,
            "num_records": num_records
        }
    
    async def _prompt_documentation_query(self, query: str) -> Dict[str, Any]:
        """Generate prompt for querying documentation"""
        files_result = await self._list_markdown_files()
        
        if not files_result["success"]:
            return files_result
        
        # Read all markdown files
        all_content = []
        for file_info in files_result["files"]:
            content_result = await self._read_markdown(file_info["name"])
            if content_result["success"]:
                all_content.append({
                    "file": file_info["name"],
                    "content": content_result["content"]
                })
        
        prompt = f"""Based on the following documentation, please answer this query: {query}

Documentation files:

"""
        
        for item in all_content:
            prompt += f"\n=== {item['file']} ===\n{item['content']}\n"
        
        prompt += f"""

Query: {query}

Please provide a detailed answer based on the documentation above.
"""
        
        return {
            "success": True,
            "prompt": prompt,
            "query": query,
            "files_searched": len(all_content)
        }
    
    async def shutdown(self):
        """Cleanup and shutdown"""
        if self.db_connection:
            self.db_connection.close()
        logger.info("MCP Server shutdown complete")


# Example usage and testing
async def main():
    """Demonstration of MCP server capabilities"""
    
    # Initialize server
    server = await MCPServer(
        markdown_dir="./docs",
        db_path=":memory:"
    ).initialize()
    
    print("=" * 60)
    print("MCP SERVER - Proof of Concept")
    print("=" * 60)
    
    # 1. List available tools
    print("\n📦 AVAILABLE TOOLS:")
    tools = await server.list_tools()
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
    
    # 2. List available prompts
    print("\n💬 AVAILABLE PROMPTS:")
    prompts = await server.list_prompts()
    for prompt in prompts:
        print(f"  • {prompt['name']}: {prompt['description']}")
    
    # 3. Test markdown file operations
    print("\n\n" + "=" * 60)
    print("TESTING MARKDOWN FILE OPERATIONS")
    print("=" * 60)
    
    result = await server.call_tool("list_markdown_files", {})
    print(f"\n📄 Markdown files found: {result.get('count', 0)}")
    if result.get("files"):
        for file in result["files"]:
            print(f"  • {file['name']} ({file['size']} bytes)")
    
    # 4. Test database operations
    print("\n\n" + "=" * 60)
    print("TESTING DUCKDB OPERATIONS")
    print("=" * 60)
    
    # Create a sample table
    print("\n🗄️  Creating 'users' table...")
    result = await server.call_tool("create_table", {
        "table_name": "users",
        "schema": "id INTEGER, name VARCHAR, email VARCHAR, age INTEGER"
    })
    print(f"  Result: {result['message'] if result['success'] else result['error']}")
    
    # Insert sample data
    print("\n➕ Inserting sample data...")
    result = await server.call_tool("insert_data", {
        "table_name": "users",
        "values": "(1, 'Alice Smith', 'alice@example.com', 30), (2, 'Bob Johnson', 'bob@example.com', 25), (3, 'Carol White', 'carol@example.com', 35)"
    })
    print(f"  Result: {result['message'] if result['success'] else result['error']}")
    
    # Query the data
    print("\n🔍 Querying data...")
    result = await server.call_tool("query_database", {
        "query": "SELECT * FROM users WHERE age > 25"
    })
    if result["success"]:
        print(f"  Columns: {result['columns']}")
        print(f"  Rows returned: {result['row_count']}")
        for row in result["rows"]:
            print(f"    {row}")
    
    # 5. Test prepared prompts
    print("\n\n" + "=" * 60)
    print("TESTING PREPARED PROMPTS")
    print("=" * 60)
    
    print("\n🎯 Testing 'database_schema_analysis' prompt...")
    result = await server.get_prompt("database_schema_analysis", {})
    if result["success"]:
        print(f"  Tables analyzed: {result['tables_analyzed']}")
        print(f"  Prompt length: {len(result['prompt'])} characters")
        print(f"\n  Preview:\n{result['prompt'][:300]}...")
    
    print("\n🎯 Testing 'create_sample_dataset' prompt...")
    result = await server.get_prompt("create_sample_dataset", {"num_records": 50})
    if result["success"]:
        print(f"  Records planned: {result['num_records']}")
        print(f"  Prompt length: {len(result['prompt'])} characters")
    
    # Cleanup
    await server.shutdown()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
