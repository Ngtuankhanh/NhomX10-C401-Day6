"""Medical tools for the ReAct agent.

VD: stock_tools.py
"""

from langchain_core.tools import tool


@tool
def get_specialty_info(specialty_name: str) -> str:
    """Get information about a medical specialty."""
    # Placeholder implementation
    return f"Thông tin về chuyên khoa {specialty_name}: ..."
