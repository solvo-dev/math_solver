#!/usr/bin/env python3
"""
Example: Integrating MCP Server with an LLM
Demonstrates how to use the MCP server with Ollama or other LLMs
"""

import asyncio
import json
from mcp_server import MCPServer


async def demonstrate_llm_integration():
    """
    This demonstrates how an LLM would interact with the MCP server.
    In a real integration:
    1. LLM receives tool/prompt definitions
    2. LLM decides which tools to call
    3. Results are passed back to LLM for interpretation
    """
    
    # Initialize MCP Server
    server = await MCPServer(
        markdown_dir="./docs",
        db_path=":memory:"
    ).initialize()
    
    print("=" * 70)
    print("MCP SERVER + LLM INTEGRATION EXAMPLE")
    print("=" * 70)
    
    # ============================================================
    # SCENARIO 1: Documentation Analysis
    # ============================================================
    print("\n📚 SCENARIO 1: Analyzing Documentation")
    print("-" * 70)
    
    # Step 1: LLM gets available prompts
    prompts = await server.list_prompts()
    print(f"✓ LLM discovers {len(prompts)} available prompts")
    
    # Step 2: LLM chooses to use documentation analysis prompt
    print("✓ LLM chooses: 'analyze_markdown_docs'")
    
    # Step 3: Generate the prompt with context
    prompt_result = await server.get_prompt("analyze_markdown_docs", {
        "focus_area": "getting started"
    })
    
    print(f"✓ Generated prompt with {prompt_result['files_analyzed']} files")
    print(f"✓ Prompt length: {len(prompt_result['prompt'])} characters")
    
    # In real use: send prompt_result['prompt'] to LLM
    print("\n→ This prompt would be sent to Ollama/OpenAI/Claude for analysis")
    
    # ============================================================
    # SCENARIO 2: Interactive Data Exploration
    # ============================================================
    print("\n\n📊 SCENARIO 2: Interactive Data Exploration")
    print("-" * 70)
    
    # User asks: "Can you analyze some sample customer data?"
    print("User: 'Can you analyze some sample customer data?'")
    
    # Step 1: LLM creates a database and sample data
    print("\n✓ LLM creates database schema...")
    await server.call_tool("create_table", {
        "table_name": "customers",
        "schema": "id INTEGER, name VARCHAR, country VARCHAR, revenue DECIMAL(10,2)"
    })
    
    await server.call_tool("insert_data", {
        "table_name": "customers",
        "values": """
            (1, 'Acme Corp', 'USA', 150000.00),
            (2, 'TechStart GmbH', 'Germany', 95000.00),
            (3, 'Global Solutions', 'UK', 200000.00),
            (4, 'Innovation Inc', 'USA', 180000.00),
            (5, 'Future Systems', 'France', 120000.00)
        """
    })
    print("✓ Sample data inserted")
    
    # Step 2: LLM queries the data
    print("\n✓ LLM analyzes the data...")
    result = await server.call_tool("query_database", {
        "query": """
            SELECT 
                country,
                COUNT(*) as customer_count,
                SUM(revenue) as total_revenue,
                AVG(revenue) as avg_revenue
            FROM customers
            GROUP BY country
            ORDER BY total_revenue DESC
        """
    })
    
    print(f"✓ Query returned {result['row_count']} rows")
    print("\nResults:")
    for row in result['rows']:
        print(f"  {row[0]}: {row[1]} customers, ${row[2]:,.2f} total, ${row[3]:,.2f} avg")
    
    # Step 3: LLM can now respond to user with insights
    print("\n→ LLM would respond: 'I've analyzed the customer data. The USA has the")
    print("   highest total revenue with 2 customers generating $330,000...'")
    
    # ============================================================
    # SCENARIO 3: Multi-Step Workflow
    # ============================================================
    print("\n\n🔄 SCENARIO 3: Multi-Step Documentation Query")
    print("-" * 70)
    
    # User asks: "How do I get started with this project?"
    print("User: 'How do I get started with this project?'")
    
    # Step 1: LLM uses documentation query prompt
    print("\n✓ LLM searches documentation...")
    doc_query = await server.get_prompt("documentation_query", {
        "query": "installation and getting started"
    })
    
    print(f"✓ Searched {doc_query['files_searched']} documentation files")
    
    # In real use: LLM would process the prompt and respond
    print("\n→ LLM would analyze the docs and provide a clear answer")
    
    # ============================================================
    # SCENARIO 4: Schema Introspection
    # ============================================================
    print("\n\n🔍 SCENARIO 4: Database Schema Discovery")
    print("-" * 70)
    
    # User asks: "What data do we have?"
    print("User: 'What data do we have?'")
    
    print("\n✓ LLM uses database_schema_analysis prompt...")
    schema_prompt = await server.get_prompt("database_schema_analysis", {})
    
    if schema_prompt['success']:
        print(f"✓ Analyzed {schema_prompt['tables_analyzed']} table(s)")
        print("\n→ LLM would explain: 'You have a customers table with columns for")
        print("   id, name, country, and revenue. This appears to be customer data")
        print("   with 5 records from various countries...'")
    
    # ============================================================
    # INTEGRATION PATTERNS
    # ============================================================
    print("\n\n🔌 INTEGRATION PATTERNS")
    print("=" * 70)
    
    print("""
    Pattern 1: Tool Discovery
    -------------------------
    1. LLM calls: list_tools()
    2. LLM receives tool definitions with schemas
    3. LLM can intelligently choose tools based on user request
    
    Pattern 2: Prepared Prompts
    ---------------------------
    1. LLM calls: list_prompts()
    2. LLM sees available prompt templates
    3. LLM calls: get_prompt(name, args)
    4. LLM receives fully-formed prompt with context
    5. LLM processes and responds
    
    Pattern 3: Resource Discovery
    -----------------------------
    1. LLM calls: list_resources()
    2. LLM sees available markdown files
    3. LLM calls: read_markdown(filename)
    4. LLM has context to answer questions
    
    Pattern 4: Dynamic Tool Chaining
    --------------------------------
    1. User: "Show me customers from USA"
    2. LLM calls: query_database(SELECT...)
    3. LLM analyzes results
    4. LLM calls: create_table() to store analysis
    5. LLM responds with insights
    """)
    
    # ============================================================
    # EXAMPLE OLLAMA INTEGRATION
    # ============================================================
    print("\n\n🦙 OLLAMA INTEGRATION EXAMPLE")
    print("=" * 70)
    
    print("""
    # Example using Ollama API
    import requests
    
    async def chat_with_context():
        # Get documentation context
        docs = await server.get_prompt("analyze_markdown_docs", {
            "focus_area": "api"
        })
        
        # Send to Ollama with context
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'llama3.1',
            'prompt': docs['prompt'],
            'system': 'You are a helpful assistant with access to documentation.'
        })
        
        return response.json()
    
    # Example: Using tools with Ollama function calling
    tools_schema = await server.list_tools()
    
    # Send user query + tools to Ollama
    ollama_response = requests.post('http://localhost:11434/api/chat', json={
        'model': 'llama3.1',
        'messages': [{'role': 'user', 'content': 'List markdown files'}],
        'tools': tools_schema
    })
    
    # Ollama returns which tool to call
    tool_call = ollama_response.json()['message']['tool_calls'][0]
    
    # Execute the tool
    result = await server.call_tool(
        tool_call['function']['name'],
        tool_call['function']['arguments']
    )
    
    # Send results back to Ollama for final response
    final_response = requests.post('http://localhost:11434/api/chat', json={
        'model': 'llama3.1',
        'messages': [
            {'role': 'user', 'content': 'List markdown files'},
            {'role': 'assistant', 'content': '', 'tool_calls': [tool_call]},
            {'role': 'tool', 'content': json.dumps(result)}
        ]
    })
    """)
    
    # Cleanup
    await server.shutdown()
    
    print("\n" + "=" * 70)
    print("✅ INTEGRATION EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("• MCP server provides structured access to tools and data")
    print("• LLMs can discover and call tools dynamically")
    print("• Prepared prompts reduce token usage and improve consistency")
    print("• Works with any LLM that supports function calling or tool use")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demonstrate_llm_integration())
