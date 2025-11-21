# API Reference

## Tools

### read_markdown
Read the content of a markdown file.

**Parameters:**
- `filename` (string, required): Name or path of the markdown file

**Returns:**
```json
{
  "success": true,
  "filename": "path/to/file.md",
  "content": "file content...",
  "size": 1234
}
```

### list_markdown_files
List all available markdown files.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "count": 3,
  "files": [
    {
      "name": "getting_started.md",
      "size": 1234,
      "path": "/full/path/to/file.md"
    }
  ]
}
```

### query_database
Execute a SQL query on the DuckDB database.

**Parameters:**
- `query` (string, required): SQL query to execute

**Returns:**
```json
{
  "success": true,
  "query": "SELECT * FROM users",
  "columns": ["id", "name", "email"],
  "rows": [[1, "Alice", "alice@example.com"]],
  "row_count": 1
}
```

### create_table
Create a table in the database.

**Parameters:**
- `table_name` (string, required): Name of the table
- `schema` (string, required): Table schema definition

**Returns:**
```json
{
  "success": true,
  "message": "Table 'users' created successfully",
  "table_name": "users"
}
```

### insert_data
Insert data into a table.

**Parameters:**
- `table_name` (string, required): Name of the table
- `values` (string, required): Values to insert

**Returns:**
```json
{
  "success": true,
  "message": "Data inserted into 'users'",
  "table_name": "users"
}
```

## Prompts

### analyze_markdown_docs
Analyze and summarize markdown documentation.

**Arguments:**
- `focus_area` (string, optional): Specific area to focus on

### database_schema_analysis
Analyze the database schema and provide insights.

**Arguments:** None

### create_sample_dataset
Create a sample dataset with tables.

**Arguments:**
- `num_records` (integer, optional): Number of records to create

### documentation_query
Query documentation for specific information.

**Arguments:**
- `query` (string, required): What to search for

## Error Handling

All responses include a `success` boolean field. On failure:

```json
{
  "success": false,
  "error": "Error message description"
}
```
