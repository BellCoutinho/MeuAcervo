from uuid import UUID


def is_uuid(identifier: str) -> bool:
    try:
        uuid_result = UUID(identifier, version=4)
    except ValueError:
        return False
    return str(uuid_result) == identifier
