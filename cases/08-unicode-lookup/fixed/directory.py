"""Name lookup for a contacts directory."""
import unicodedata


def _key(name: str) -> str:
    # NFC makes "e" + combining accent and the precomposed letter identical.
    # casefold() is the Unicode-aware comparison form of lower() ("STRASSE" == "straße").
    return unicodedata.normalize("NFC", name.strip()).casefold()


class Directory:
    def __init__(self) -> None:
        self._by_name: dict[str, str] = {}

    def add(self, name: str, user_id: str) -> None:
        self._by_name[_key(name)] = user_id

    def find(self, query: str) -> str | None:
        return self._by_name.get(_key(query))
