"""
UI component builders for the Gradio interface.
"""

import gradio as gr
from typing import List

from math_solver.services import ConfigService
from math_solver.ui.handlers import MessageHandler


class UIComponents:
    """Builds and manages UI components for the application."""

    def __init__(self, message_handler: MessageHandler, config_service: ConfigService) -> None:
        """Initialize with dependencies."""
        self.message_handler = message_handler
        self.config_service = config_service

    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface."""

        async def handle_message(message: str, history: List[List[str]]) -> str:
            """Wrapper for message handling."""
            return await self.message_handler.handle_message(message, history)

        with gr.Blocks(title="Mathe-Löser", theme=gr.themes.Soft()) as interface:
            gr.Markdown("# 🧮 Mathe-Löser")
            gr.Markdown("*Stelle mir mathematische Aufgaben oder Fragen — ich antworte auf Deutsch.*")

            with gr.Row():
                with gr.Column(scale=2):
                    # Chat interface (auf Deutsch)
                    # Note: gr.ChatInterface does not accept placeholder/submit_text kwargs
                    gr.ChatInterface(
                        fn=handle_message,
                        theme=gr.themes.Soft()
                    )

                with gr.Column(scale=1):
                    # Configuration display
                    gr.Markdown("### Aktuelle Einstellungen")
                    config_display = gr.Markdown(value=self.config_service.get_config_display())

                    # Refresh button
                    refresh_btn = gr.Button("🔄 Einstellungen aktualisieren", size="sm")

            # Update config display when refresh is clicked
            refresh_btn.click(
                fn=self.config_service.get_config_display,
                outputs=config_display
            )

        return interface
