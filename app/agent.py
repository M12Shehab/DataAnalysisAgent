# app/agent.py
from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Correct imports using langchain-classic
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent

# ---- Tool functions (pure Python) ----
from app.tools.dataframe import (
    dataset_summary,
    sample_rows,
    find_columns,
)
from app.tools.stats import (
    describe_columns,
    missing_values,
    value_counts,
    correlation_matrix,
)
from app.tools.visualization import plot

# -----------------------------------------------------------------------------
# Environment / OpenRouter configuration
# -----------------------------------------------------------------------------

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4o-mini"  # safe default; change freely
)

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")


# -----------------------------------------------------------------------------
# Tool registration
# -----------------------------------------------------------------------------

def build_tools() -> List[StructuredTool]:
    """
    Wrap pure Python functions as LangChain tools.

    Returns:
        list[StructuredTool]: Tools exposed to the agent.
    """
    return [
        StructuredTool.from_function(
            func=dataset_summary,
            name="dataset_summary",
            description=dataset_summary.__doc__,
        ),
        StructuredTool.from_function(
            func=sample_rows,
            name="sample_rows",
            description=sample_rows.__doc__,
        ),
        StructuredTool.from_function(
            func=find_columns,
            name="find_columns",
            description=find_columns.__doc__,
        ),
        StructuredTool.from_function(
            func=describe_columns,
            name="describe_columns",
            description=describe_columns.__doc__,
        ),
        StructuredTool.from_function(
            func=missing_values,
            name="missing_values",
            description=missing_values.__doc__,
        ),
        StructuredTool.from_function(
            func=value_counts,
            name="value_counts",
            description=value_counts.__doc__,
        ),
        StructuredTool.from_function(
            func=correlation_matrix,
            name="correlation_matrix",
            description=correlation_matrix.__doc__,
        ),
        StructuredTool.from_function(
            func=plot,
            name="plot",
            description=plot.__doc__,
        ),
    ]


# -----------------------------------------------------------------------------
# Prompt (this is critical)
# -----------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are a data analysis assistant with access to tools for analyzing datasets.

CRITICAL RULES:
1. ALWAYS use the dataset_summary tool FIRST when a user asks ANY question about their data
2. You MUST use tools to answer questions - you cannot answer from memory
3. You do NOT write or execute Python code yourself
4. When asked about columns, use find_columns tool
5. When asked about statistics, use describe_columns or missing_values tools
6. When asked to create visualizations, use the plot tool
7. ALWAYS call tools to get information - never assume the dataset structure

Available tools:
- dataset_summary: Get overview (shape, columns, types) - USE THIS FIRST
- sample_rows: View sample data rows
- find_columns: Search for columns by keyword
- describe_columns: Get statistical summaries
- missing_values: Check for missing data
- value_counts: Count unique values in a column
- correlation_matrix: Compute correlations between numeric columns
- plot: Create visualizations (hist, box, scatter, bar)

Your workflow:
1. User asks a question
2. Call dataset_summary to understand the dataset
3. Use appropriate tools to gather the needed information
4. Present findings clearly and concisely

Be helpful, precise, and always rely on the tools provided.
""".strip()


def build_prompt() -> ChatPromptTemplate:
    """
    Build the chat prompt for the agent.

    Returns:
        ChatPromptTemplate
    """
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )


# -----------------------------------------------------------------------------
# Agent factory
# -----------------------------------------------------------------------------

def build_agent() -> AgentExecutor:
    """
    Create and return a fully configured AgentExecutor.

    Returns:
        AgentExecutor: Ready-to-use LangChain agent.
    """
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        model=OPENROUTER_MODEL,
        temperature=0.0,  # deterministic, analytical behavior
    )

    tools = build_tools()
    prompt = build_prompt()

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # Enable verbose mode for debugging
        handle_parsing_errors=True,
        max_iterations=10,  # Increase from 5 to allow more tool calls
        return_intermediate_steps=False,
    )


# -----------------------------------------------------------------------------
# Convenience entry point (used by Gradio)
# -----------------------------------------------------------------------------

def run_agent(
    agent: AgentExecutor,
    user_input: str,
    chat_history: list | None = None,
) -> str:
    """
    Run the agent on a single user message.

    Args:
        agent (AgentExecutor): The agent instance.
        user_input (str): User's message.
        chat_history (list, optional): Prior chat messages (LangChain format).

    Returns:
        str: Agent's final response text.
    """
    chat_history = chat_history or []

    result = agent.invoke(
        {
            "input": user_input,
            "chat_history": chat_history,
        }
    )

    return result["output"]