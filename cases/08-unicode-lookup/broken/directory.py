"""Name lookup for a contacts directory."""


class Directory:
    def __init__(self) -> None:
        self._by_name: dict[str, str] = {}

    def add(self, name: str, user_id: str) -> None:
        self._by_name[name.strip().lower()] = user_id

    def find(self, query: str) -> str | None:
        return self._by_name.get(query.strip().lower())
