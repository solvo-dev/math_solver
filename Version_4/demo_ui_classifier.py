"""
Integration demo: Classifier results in chatbot UI

This script demonstrates how classifier results appear in the chat interface.
Enable the classifier to see category badges before the assistant response.
"""

import asyncio
from pathlib import Path
from src.math_solver.services.chatbot_service import ChatbotService
from src.math_solver.config import ChatConfig
from src.math_solver.ui.formatters import MessageFormatter

async def demo():
    print("=" * 70)
    print("Classifier UI Integration Demo")
    print("=" * 70)
    print()
    
    # Create config with classifier enabled
    config = ChatConfig(
        enable_classifier=True,
        classifier_model_path="models/classifier",
        classifier_confidence_threshold=0.5
    )
    
    print(f"✓ Classifier enabled: {config.enable_classifier}")
    print(f"✓ Model path: {config.classifier_model_path}")
    print(f"✓ Confidence threshold: {config.classifier_confidence_threshold}")
    print()
    
    # Initialize chatbot service
    print("Initializing chatbot service...")
    service = ChatbotService(config=config)
    chatbot = service.get_chatbot()
    print("✓ Chatbot initialized")
    print()
    
    # Test problems
    test_problems = [
        "Solve the equation: 3x + 7 = 22",
        "Find the derivative of x^2 + 3x",
        "Calculate the area of a circle with radius 5"
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print("-" * 70)
        print(f"Test {i}: {problem}")
        print("-" * 70)
        
        # Simulate chat history
        history = []
        
        # Get response with classifier
        full_response = ""
        try:
            async for chunk in chatbot.generate_response_with_tools(problem):
                formatted = MessageFormatter.format_message_chunk(chunk)
                full_response += formatted
                
                # Print classifier results immediately
                if chunk.get("type") == "tool_result" and chunk.get("tool") == "classifier":
                    print(formatted.strip())
            
            print("\nAssistant Response Preview:")
            preview = full_response[:200] + "..." if len(full_response) > 200 else full_response
            print(preview)
            
        except Exception as e:
            print(f"Error: {e}")
        
        print()
    
    print("=" * 70)
    print("Demo completed!")
    print("=" * 70)
    print()
    print("💡 How it appears in the UI:")
    print("   User asks a question")
    print("   → Classifier badge appears first (e.g., 🏷️ Kategorie: 📐 Calculus)")
    print("   → Then the full assistant explanation follows")
    print()
    
    # Cleanup
    await service.close()

if __name__ == "__main__":
    asyncio.run(demo())
