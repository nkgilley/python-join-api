"""Cache helpers for Join API."""
import hashlib
import os
import tempfile

def _get_cache_path(api_key):
    """Generate a safe cache file path based on a hashed API key."""
    try:
        hashed_key = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
    except Exception:
        return None

    # Try standard user cache directory first, fall back to system temp
    for base in [
        os.path.join(os.path.expanduser("~"), ".cache", "pyjoin"),
        os.path.join(tempfile.gettempdir(), "pyjoin")
    ]:
        try:
            os.makedirs(base, exist_ok=True)
            # Verify write permissions
            test_path = os.path.join(base, ".write_test")
            with open(test_path, "w") as f:
                f.write("")
            os.remove(test_path)
            return os.path.join(base, f"{hashed_key}.json")
        except Exception:
            continue
    return None
