import json
import asyncio
from pathlib import Path
from typing import List
from datetime import datetime
from models import Outage, User
import os
import sys

# Detectar si se ejecuta como ejecutable (PyInstaller)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)  # Asegura que la carpeta data exista
OUTAGES_FILE = DATA_DIR / 'outages.json'
USERS_FILE = DATA_DIR / 'users.json'

async def load_outages() -> List[Outage]:
    if not OUTAGES_FILE.exists():
        return []
    text = await asyncio.to_thread(OUTAGES_FILE.read_text)
    try:
        raw_data = json.loads(text)
    except json.JSONDecodeError:
        return []
    return [Outage.from_dict(item) for item in raw_data]

async def save_outages(outages: List[Outage]):
    data = [outage.to_dict() for outage in outages]
    await asyncio.to_thread(lambda: OUTAGES_FILE.write_text(json.dumps(data, indent=2)))

async def send_notification(user: User, message: str):
    await asyncio.sleep(0.1)  # Simulate delay
    print(f"[Notification to {user.contact}]: {message}")
