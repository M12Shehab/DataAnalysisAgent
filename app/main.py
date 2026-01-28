# app/main.py

"""
Data Analysis Agent - AI-Powered CSV Data Explorer
Copyright (c) 2026 Mohammed Shehab. All rights reserved.

Author: Mohammed Shehab
Email: shihab@live.cn
GitHub: https://github.com/M12Shehab/DataAnalysisAgent
LinkedIn: https://linkedin.com/in/mohammed-shehab

Description:
    Main application entry point for the Data Analysis Agent.

License:
    MIT License - see LICENSE file for details

Created: January 2026
Last Modified: January 2026
"""

from __future__ import annotations

import pandas as pd
import gradio as gr
import os
import re

from app.state import STATE
from app.agent import build_agent, run_agent
from app.config import CONFIG


# -----------------------------------------------------------------------------
# Agent (single instance)
# -----------------------------------------------------------------------------

AGENT = build_agent()


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def load_csv(file):
    """
    Load a CSV file into the global application state.

    Returns:
        tuple[str, list]: Status message and cleared chat history.
    """
    if file is None:
        return "No file uploaded.", []

    try:
        # Handle different Gradio file object types
        if hasattr(file, 'name'):
            filepath = file.name
        else:
            filepath = file
        
        df = pd.read_csv(filepath)
        
    except Exception as e:
        return f"Failed to read CSV: {e}", []

    STATE.df = df
    STATE.dataset_name = os.path.basename(filepath)

    return (
        f"Loaded dataset '{STATE.dataset_name}' "
        f"with {df.shape[0]} rows and {df.shape[1]} columns.",
        [],
    )


def chat_handler(message: str, chat_history: list):
    """
    Handle a single chat turn.

    Returns:
        tuple[list, None | str]:
            - Updated chat history
            - Optional plot path
    """
    if not message.strip():
        return chat_history, None

    # Convert chat_history to LangChain format
    langchain_history = []
    
    # Handle both old tuple format and new dict format
    for item in chat_history:
        if isinstance(item, dict):
            # New format: {"role": "user"/"assistant", "content": "..."}
            role = "human" if item["role"] == "user" else "ai"
            langchain_history.append((role, item["content"]))
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            # Old format: (user_msg, bot_msg) or [user_msg, bot_msg]
            langchain_history.append(("human", item[0]))
            if item[1]:  # only add if bot message exists
                langchain_history.append(("ai", item[1]))

    try:
        response = run_agent(
            agent=AGENT,
            user_input=message,
            chat_history=langchain_history,
        )
    except Exception as e:
        response = f"Error: {str(e)}"

    # Extract plot path from response
    plot_path = None
    display_response = response
    
    # Check if response contains a file path (either direct or in markdown)
    # Pattern 1: Direct path like /tmp/plot_xxx.png
    # Pattern 2: Markdown image like ![...](...) or sandbox:/tmp/...
    path_patterns = [
        r'/tmp/plot_[a-f0-9]+\.png',
        r'sandbox:(/tmp/plot_[a-f0-9]+\.png)',
    ]
    
    for pattern in path_patterns:
        matches = re.findall(pattern, response)
        if matches:
            # Get the actual path (handle capture groups)
            plot_path = matches[0] if not isinstance(matches[0], tuple) else matches[0]
            # Remove sandbox: prefix if present
            plot_path = plot_path.replace('sandbox:', '')
            
            # Clean up the response - remove the image markdown
            display_response = re.sub(r'!\[.*?\]\(sandbox:/tmp/.*?\)', '', response)
            display_response = re.sub(r'sandbox:/tmp/plot_[a-f0-9]+\.png', '', display_response)
            display_response = display_response.strip()
            
            if not display_response:
                display_response = "I generated a plot for you. See below."
            break

    # Return in new Gradio messages format (dict with role/content)
    updated_history = chat_history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": display_response}
    ]

    return updated_history, plot_path


# -----------------------------------------------------------------------------
# Gradio UI
# -----------------------------------------------------------------------------

with gr.Blocks(title=CONFIG.APP_TITLE) as demo:
    gr.Markdown(f"# {CONFIG.APP_TITLE}")
    gr.Markdown(CONFIG.APP_DESCRIPTION)
    gr.Markdown(f"*Built by {CONFIG.AUTHOR} © {CONFIG.COPYRIGHT_YEAR}*")  # Add this line


    with gr.Row():
        with gr.Column(scale=1):
            file_upload = gr.File(
                label="Upload CSV",
                file_types=[".csv"],
                type="filepath",
            )
            upload_status = gr.Textbox(
                label="Dataset status",
                interactive=False,
            )

        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="Data Agent",
                height=400,
            )
            user_input = gr.Textbox(
                label="Ask a question about your data",
                placeholder="e.g. Show missing values, plot age distribution, etc.",
            )

    plot_output = gr.Image(
        label="Generated Plot",
        visible=True,
    )

    # ---- Events ----

    file_upload.upload(
        fn=load_csv,
        inputs=file_upload,
        outputs=[upload_status, chatbot],
    )

    user_input.submit(
        fn=chat_handler,
        inputs=[user_input, chatbot],
        outputs=[chatbot, plot_output],
    )

    user_input.submit(
        fn=lambda: "",
        inputs=None,
        outputs=user_input,
    )


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    demo.launch(
        server_name=CONFIG.GRADIO_HOST,
        server_port=CONFIG.GRADIO_PORT,
        share=CONFIG.GRADIO_SHARE,
    )