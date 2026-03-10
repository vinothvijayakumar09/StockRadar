"""Simple logger"""
from datetime import datetime

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "ERROR": "❌", "WARN": "⚠️"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] {icon}  {message}")
