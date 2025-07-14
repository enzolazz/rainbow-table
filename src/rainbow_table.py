import hashlib
import random
import time
import sys
from collections import defaultdict

from tqdm import tqdm

from settings import settings
from storage import JSONStorage


class RainbowTable:
    def __init__(self, steps=settings.default_steps, rows=None):
        self.alphabet = list(settings.alphabet)
        self.storage = JSONStorage(settings.data_path / "table.json")
        self.steps = steps
        self.rows = 0
        self.table = defaultdict(list)

        self.__load()

        if rows:
            self.__build_table(rows)

    def __load(self):
        data = self.storage.load()

        table_dict = data.get("table", {})
        steps = data.get("steps", self.steps)

        if steps != self.steps:
            print(
                f"Warning: Steps in storage ({steps}) do not match given steps ({self.steps})."
            )

            confirm = (
                input("Do you want to continue with the given steps? (y/n): ")
                .strip()
                .lower()
            )

            if confirm != "y":
                sys.exit("Exiting due to mismatch in steps.")

            table_dict = {}
            self.steps = steps

        self.table = defaultdict(list, table_dict)
        self.rows = len(self.table)

    def __save(self):
        data = {"steps": self.steps, "table": dict(self.table)}

        self.storage.save(data)

    def __random_password(self):
        password = ""

        while True:
            probability = random.uniform(0, 1)

            if (
                len(password) >= settings.min_password_length
                and probability < settings.stop_probability
            ):
                break

            password += random.choice(self.alphabet)

        return password

    def __sha512_hash(self, plaintext):
        return hashlib.sha512(plaintext.encode()).hexdigest()

    def __reduce(self, hash, step):
        seed = hashlib.sha512((hash + str(step)).encode()).hexdigest()
        rng = random.Random(seed)

        reduced = ""
        while True:
            stop_probability = rng.uniform(0, 1)
            if (
                len(reduced) >= settings.min_password_length
                and stop_probability < settings.stop_probability
            ):
                break

            idx = rng.randint(0, settings.alphabet_size - 1)
            reduced += self.alphabet[idx]

        return reduced

    def __build_table(self, row_count):
        print("==> BUILDING TABLE...")
        start_time = time.perf_counter()
        for i in tqdm(range(row_count), desc="Building rows", unit="row"):
            start = self.__random_password()

            end = start
            for step in range(self.steps):
                h = self.__sha512_hash(end)
                end = self.__reduce(h, step)

            self.table[end].append(start)

        self.rows = len(self.table)
        self.__save()

        end_time = time.perf_counter()
        print(f"\r==> TABLE BUILT{' ' * 20}", flush=True)
        print(f"==> Time: {end_time - start_time:.2f}s")

        end = random.choice(list(self.table.keys()))
        start_list = ",".join(self.table[end])
        print(f"==> Random row: ({start_list}) -> {end}")

    def __regenerate(self, start, target_hash):
        password = start

        for step in range(self.steps):
            hashed_password = self.__sha512_hash(password)
            if hashed_password == target_hash:
                return password

            password = self.__reduce(hashed_password, step)

        return None

    def check_password(self, hashed_password):
        for step in range(self.steps - 1, -1, -1):
            candidate = self.__reduce(hashed_password, step)

            for k in range(step + 1, self.steps):
                candidate = self.__reduce(self.__sha512_hash(candidate), k)

            if candidate in self.table:
                for start in self.table[candidate]:
                    password = self.__regenerate(start, hashed_password)
                    if password:
                        return password
        return None
