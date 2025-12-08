"""Test script to verify classifier UI formatting works correctly."""

from src.math_solver.ui.formatters import MessageFormatter

# Test classifier tool result formatting
test_chunks = [
    {
        "type": "tool_result",
        "tool": "classifier",
        "content": "Category: algebra (confidence: 0.92)"
    },
    {
        "type": "tool_result",
        "tool": "classifier",
        "content": "Category: calculus (confidence: 0.87)"
    },
    {
        "type": "tool_result",
        "tool": "classifier",
        "content": "Category: geometry (confidence: 0.75)"
    },
    {
        "type": "tool_result",
        "tool": "classifier",
        "content": "Category: number_theory (confidence: 0.95)"
    },
    {
        "type": "tool_result",
        "tool": "sympy",
        "content": "Result: x = 5"
    },
    {
        "type": "chunk",
        "content": "This is a regular assistant response."
    }
]

print("=" * 70)
print("Classifier UI Formatting Test")
print("=" * 70)
print()

for i, chunk in enumerate(test_chunks, 1):
    print(f"Test {i}: {chunk.get('tool', chunk.get('type'))}")
    print("-" * 70)
    formatted = MessageFormatter.format_message_chunk(chunk)
    print(formatted)
    print()

print("=" * 70)
print("✓ All formatting tests completed!")
print("=" * 70)
