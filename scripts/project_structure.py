from pathlib import Path


IGNORED_NAMES = {
    ".venv",
    "__pycache__",
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def print_tree(path: Path, prefix: str = "") -> None:
    items = sorted(
        [item for item in path.iterdir() if item.name not in IGNORED_NAMES],
        key=lambda item: (item.is_file(), item.name.lower()),
    )

    for item in items:
        print(f"{prefix}- {item.name}")

        if item.is_dir():
            print_tree(item, prefix + "  ")


if __name__ == "__main__":
    print_tree(Path("."))
