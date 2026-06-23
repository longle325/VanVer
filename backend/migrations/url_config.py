from __future__ import annotations


def escape_configparser_value(value: str) -> str:
    """Escape percent signs before storing dynamic values in ConfigParser."""
    return value.replace("%", "%%")
