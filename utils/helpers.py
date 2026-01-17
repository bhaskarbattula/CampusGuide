import os
import hashlib
from typing import Dict, Any, List
from datetime import datetime


def get_file_hash(file_path: str) -> str:
    """
    Calculate SHA256 hash of a file.

    Args:
        file_path: Path to the file

    Returns:
        SHA256 hash as hex string
    """
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def format_timestamp(timestamp: float) -> str:
    """
    Format a timestamp as a readable string.

    Args:
        timestamp: Unix timestamp

    Returns:
        Formatted timestamp string
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def safe_get_nested_value(data: Dict[str, Any], keys: List[str], default=None):
    """
    Safely get a nested value from a dictionary.

    Args:
        data: Dictionary to search
        keys: List of keys to traverse
        default: Default value if not found

    Returns:
        Value or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def extract_document_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract basic metadata from a file.

    Args:
        file_path: Path to the file

    Returns:
        Metadata dictionary
    """
    if not os.path.exists(file_path):
        return {}

    stat = os.stat(file_path)
    return {
        "filename": os.path.basename(file_path),
        "file_path": file_path,
        "file_size": stat.st_size,
        "created_time": stat.st_ctime,
        "modified_time": stat.st_mtime,
        "file_hash": get_file_hash(file_path),
    }


def validate_role(role: str, allowed_roles: List[str]) -> bool:
    """
    Validate if a role is allowed.

    Args:
        role: Role to validate
        allowed_roles: List of allowed roles

    Returns:
        True if role is allowed
    """
    return role in allowed_roles


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.

    Args:
        dict1: First dictionary
        dict2: Second dictionary

    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
