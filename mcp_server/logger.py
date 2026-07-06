import json
import time
import os
from datetime import datetime, timezone

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "tool_calls.jsonl")

def log_tool_call(tool_name: str, input_data: dict, output_summary: str, success: bool):
    """Writes a structured JSON log line for an MCP tool call."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "input": input_data,
        "output_summary": output_summary,
        "success": success
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
