import hashlib
import random
import time
import sys
from collections import defaultdict

from tqdm import tqdm

from settings import settings
from storage import JSONStorage
from logger import log


class RainbowTable:
    def __init__(self, steps=settings.default_steps):
        self.alphabet = list(settings.alphabet)
        self.storage = JSONStorage(settings.data_path / "table.json")
        self.steps = steps

        self.tables = {}
        self.rows = {}

        completion = self.__load()
        if completion:
            log.success(
                f"Rainbow Table {completion} successfully. Current lengths: {list(self.rows.keys())}"
            )

    def __load(self):
        """Loads all tables from the JSON file."""

        data = self.storage.load()
        loaded_steps = data.get("steps", self.steps)

        if loaded_steps != self.steps:
            log.warning(
                f"Steps in storage ({loaded_steps}) do not match given steps ({self.steps})."
            )

            confirm = (
                input("Do you want to continue with the given steps? (y/n): ")
                .strip()
                .lower()
            )

            if confirm != "y":
                sys.exit("Exiting due to mismatch in steps.")

            return "created"

        loaded_tables = data.get("tables", {})
        for length_str, table_dict in loaded_tables.items():
            try:
                length = int(length_str)
                if not isinstance(table_dict, dict):
                    log.warning(f"Data for length '{length}' is malformed. Skipping.")
                    continue

                processed_dict = {
                    key: set(values) for key, values in table_dict.items()
                }

                self.tables[length] = defaultdict(set, processed_dict)
                self.rows[length] = len(self.tables[length])

            except (ValueError, TypeError) as e:
                log.warning(
                    f"Could not load table for key '{length_str}': {e}. Skipping."
                )
                continue

        return "loaded" if self.tables else "created"

    def __save(self):
        tables_to_save = {
            length: {
                end_point: list(start_points)
                for end_point, start_points in inner_table.items()
            }
            for length, inner_table in self.tables.items()
        }

        data = {"steps": self.steps, "tables": tables_to_save}
        self.storage.save(data)
        log.success("Tables saved!")

    def __random_password(self, length):
        return "".join(random.choices(self.alphabet, k=length))

    def __sha512_hash(self, plaintext):
        return hashlib.sha512(plaintext.encode()).hexdigest()

    def __reduce(self, hash_val, step, length):
        seed = hashlib.sha512((hash_val + str(step)).encode()).hexdigest()
        rng = random.Random(seed)
        return "".join(rng.choices(self.alphabet, k=length))

    def build(self, rows, length):
        log.info(f"Building table for length {length} with {rows} rows...")
        start_time = time.perf_counter()

        self.tables.setdefault(length, defaultdict(set))

        for i in tqdm(range(rows), desc=f"==> Building (len={length})", unit="row"):
            start = self.__random_password(length)
            end = start
            for step in range(self.steps):
                h = self.__sha512_hash(end)
                end = self.__reduce(h, step, length)

            self.tables[length][end].add(start)

        self.rows[length] = len(self.tables[length])
        self.__save()

        end_time = time.perf_counter()
        log.info(
            f"Time: {end_time - start_time:.2f}s. Total rows for length {length}: {self.rows[length]}"
        )

    def __regenerate(self, start, target_hash, length):
        password = start
        for step in range(self.steps):
            hashed_password = self.__sha512_hash(password)
            if hashed_password == target_hash:
                return password
            password = self.__reduce(hashed_password, step, length)
        return None

    def check(self, hashed_password, length):
        table_for_length = self.tables.get(length)
        if not table_for_length:
            log.warning(f"No table found for password length {length}.")
            return None

        for step in range(self.steps - 1, -1, -1):
            candidate = self.__reduce(hashed_password, step, length)
            for k in range(step + 1, self.steps):
                candidate = self.__reduce(self.__sha512_hash(candidate), k, length)

            for start in table_for_length.get(candidate, []):
                password = self.__regenerate(start, hashed_password, length)
                if password:
                    return password
        return None
