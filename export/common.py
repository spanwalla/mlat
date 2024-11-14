import csv
from pathlib import Path
from config import DEFAULT_EXPORT_DIRECTORY


def create_dir_and_file(filename: str, extra_directory: str | None = None) -> Path:
    directory = Path(DEFAULT_EXPORT_DIRECTORY)
    if extra_directory is not None:
        directory = directory / extra_directory

    directory.mkdir(parents=True, exist_ok=True)  # Создаём директорию и всю структуру, если их не существовало ранее
    return directory / filename


def from_dict_to_csv(data: list[dict[str, any]], filename: str, extra_directory: str | None = None):
    file_path = create_dir_and_file(filename, extra_directory)
    with file_path.open('w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
