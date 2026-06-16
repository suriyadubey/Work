import os
import json
import hashlib

STATE_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/.process_state.json"))

def load_state() -> dict:
    """Loads the process state from data/.process_state.json."""
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Failed to load process state: {e}")
    return {}

def save_state(state: dict):
    """Saves the process state to data/.process_state.json."""
    try:
        os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)
        with open(STATE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Warning: Failed to save process state: {e}")

def get_row_hash(row_dict: dict) -> str:
    """Computes a unique sha256 hash for a row dictionary."""
    canonical = json.dumps(row_dict, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
