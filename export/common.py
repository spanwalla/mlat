import csv
from pathlib import Path
from config import DEFAULT_EXPORT_DIRECTORY


def from_dict_to_csv(data: list[dict[str, any]], filename: str, extra_directory: str | None = None):
    directory = Path(DEFAULT_EXPORT_DIRECTORY)
    if extra_directory is not None:
        directory = directory / extra_directory

    directory.mkdir(parents=True, exist_ok=True)  # Создаём директорию и всю структуру, если их не существовало ранее
    file_path = directory / filename

    with file_path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
