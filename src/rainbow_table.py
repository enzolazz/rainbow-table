import hashlib
import random
import time

from tqdm import tqdm

from logger import log
from settings import settings
from concurrent.futures import ThreadPoolExecutor


class RainbowTable:
    def __init__(self, storage):
        self.alphabet = list(settings.alphabet)
        self.steps = settings.default_steps
        self.storage = storage

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

        batch_size = int(rows * 0.1)

        start_time = time.perf_counter()

        with tqdm(total=rows, desc=f"==> Building (len={length})", unit="row") as pbar:
            batch = []
            for _ in range(rows):
                start = self.__random_password(length)
                end = start
                for step in range(self.steps):
                    h = self.__sha512_hash(end)
                    end = self.__reduce(h, step, length)

                batch.append((start, end, length))

                if len(batch) >= batch_size:
                    self.storage.add_chains(batch)
                    batch = []

                pbar.update(1)

            if batch:
                self.storage.add_chains(batch)

        end_time = time.perf_counter()
        log.success(
            f"Build complete for length {length}. Time: {end_time - start_time:.2f}s"
        )

    def __regenerate(self, start, target_hash, length):
        password = start
        for step in range(self.steps + 1):
            hashed_password = self.__sha512_hash(password)
            if hashed_password == target_hash:
                return password

            password = self.__reduce(hashed_password, step, length)

        return None

    def check(self, hashed_password):
        available_lengths = self.storage.get_available_lengths()

        if not available_lengths:
            log.warning("No rainbow tables available.")
            return None

        log.info(f"Checking hash against {len(available_lengths)} lengths...")

        def try_lengths(length):
            storage = self.storage.__class__(self.storage.db_path)

            if length not in storage.get_available_lengths():
                log.warning(f"[Thread] No table for length {length}")
                return None

            log.status(f"[Thread] Checking length {length}")

            for step in range(self.steps - 1, -1, -1):
                candidate = self.__reduce(hashed_password, step, length)
                for k in range(step + 1, self.steps):
                    candidate = self.__reduce(self.__sha512_hash(candidate), k, length)

                start_candidates = storage.get_start_candidates(candidate, length)

                for start in start_candidates:
                    password = self.__regenerate(start, hashed_password, length)
                    if password:
                        log.success(f"Password found with length {length}!")
                        return password

            log.info(f"Password not found for length: {length}")

            return None

        with ThreadPoolExecutor(max_workers=len(available_lengths)) as executor:
            results = list(executor.map(try_lengths, available_lengths))

        for result in results:
            if result:
                return result

        return None
