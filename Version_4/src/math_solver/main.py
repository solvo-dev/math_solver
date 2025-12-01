#!/usr/bin/env python3
"""
Math Solver - Web Interface

Main entry point for the math solver application.
"""

import asyncio
import logging


from math_solver.services import ChatbotService, ConfigService
from math_solver.ui import MessageHandler, UIComponents

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main application entry point."""
    # Initialize services with dependency injection
    chatbot_service = ChatbotService()
    config_service = ConfigService(chatbot_service)

    # Initialize UI components
    message_handler = MessageHandler(chatbot_service)
    ui_components = UIComponents(message_handler, config_service)

    # Create and launch UI
    interface = ui_components.create_interface()

    logger.info("Math Solver application starting...")

    try:
        # Launch interface
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            show_api=False,
            share=False
        )
    finally:
        # Clean up resources
        logger.info("Shutting down Math Solver application...")
        await chatbot_service.close()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
