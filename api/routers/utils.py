from typing import List, Optional

from sqlalchemy import asc, desc


def generate_ordering_dict(param: str, valid_params: Optional[List[str]] = None):
    if not param:
        return {}

    params = param.split(",")
    return {
        p.strip("- "): desc if p.startswith("-") else asc
        for p in params
        if valid_params is None or p.strip("- ") in valid_params
    }
