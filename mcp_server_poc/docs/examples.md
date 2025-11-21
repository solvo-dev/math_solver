# Examples

## Example 1: Reading Documentation

```python
# List all markdown files
result = await server.call_tool("list_markdown_files", {})
print(f"Found {result['count']} files")

# Read a specific file
content = await server.call_tool("read_markdown", {
    "filename": "getting_started.md"
})
print(content['content'])
```

## Example 2: Database Operations

```python
# Create a users table
await server.call_tool("create_table", {
    "table_name": "users",
    "schema": "id INTEGER, name VARCHAR, email VARCHAR"
})

# Insert data
await server.call_tool("insert_data", {
    "table_name": "users",
    "values": "(1, 'Alice', 'alice@example.com'), (2, 'Bob', 'bob@example.com')"
})

# Query data
result = await server.call_tool("query_database", {
    "query": "SELECT * FROM users WHERE id = 1"
})
print(result['rows'])
```

## Example 3: Using Prepared Prompts

```python
# Get a documentation analysis prompt
prompt_result = await server.get_prompt("analyze_markdown_docs", {
    "focus_area": "api"
})

# The prompt is ready to be sent to an LLM
llm_response = send_to_llm(prompt_result['prompt'])

# Database schema analysis
schema_prompt = await server.get_prompt("database_schema_analysis", {})
print(schema_prompt['prompt'])
```

## Example 4: Creating Sample Datasets

```python
# Get instructions for creating a sample dataset
result = await server.get_prompt("create_sample_dataset", {
    "num_records": 100
})
print(result['prompt'])

# Follow the generated SQL commands to create tables
```

## Example 5: Advanced Queries

```python
# Complex SQL query with DuckDB
result = await server.call_tool("query_database", {
    "query": """
        SELECT 
            u.name,
            COUNT(o.id) as order_count,
            SUM(o.amount) as total_amount
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.name
        HAVING COUNT(o.id) > 0
    """
})

for row in result['rows']:
    print(f"{row[0]}: {row[1]} orders, ${row[2]:.2f} total")
```

## Example 6: Documentation Search

```python
# Query documentation for specific information
result = await server.get_prompt("documentation_query", {
    "query": "How do I install the dependencies?"
})

# The prompt includes all relevant documentation
print(result['prompt'])
```
