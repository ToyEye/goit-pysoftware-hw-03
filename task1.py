import os
import shutil
import argparse
from threading import Thread, Condition


class FileCopyThread(Thread):
    def __init__(self, source_file, destination_dir, condition):
        super().__init__()
        self.source_file = source_file
        self.destination_dir = destination_dir
        self.condition = condition

    def run(self):
        try:
            shutil.copy(self.source_file, self.destination_dir)
            print(f"Copied {self.source_file} to {self.destination_dir}")
        except Exception as e:
            print(f"Error copying {self.source_file}: {e}")
        finally:
            with self.condition:
                self.condition.notify()  # Повідомляємо про завершення копіювання


def process_directory(source_dir, destination_dir, condition):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_file = os.path.join(root, file)
            extension = os.path.splitext(file)[1][1:]  # Отримуємо розширення файлу
            destination_subdir = os.path.join(destination_dir, extension)
            if not os.path.exists(destination_subdir):
                os.makedirs(destination_subdir)
            thread = FileCopyThread(source_file, destination_subdir, condition)
            thread.start()  # Запускаємо потік для копіювання файлу


def main(source_dir, destination_dir):
    condition = Condition()
    process_directory(source_dir, destination_dir, condition)
    # Чекаємо, поки всі потоки завершаться
    with condition:
        condition.wait()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sort files by extension from a source directory to a destination directory."
    )
    parser.add_argument("source_dir", help="Path to the source directory")
    parser.add_argument(
        "destination_dir",
        nargs="?",
        default="dist",
        help="Path to the destination directory. Default is 'dist'",
    )
    args = parser.parse_args()

    main(args.source_dir, args.destination_dir)
