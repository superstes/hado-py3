

def value_exists(data: dict, key: str) -> bool:
    if key not in data or not data[key]:
        return False

    return True
