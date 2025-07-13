import hashlib
import random
import string
import time

from tqdm import tqdm

MIN_LENGTH = 5
SPECIAL_CHARS = "!@#%&*()"
PROBABILITY = 0.125


class RainbowTable:
    def __init__(self, rows=8000, steps=600):
        self.rows = rows
        self.steps = steps
        self.alphabet = list(string.ascii_letters + string.digits + SPECIAL_CHARS)
        self.alphabet_size = len(self.alphabet)
        self.table = self.__build_table()

    def __random_password(self):
        password = ""

        while True:
            stop_probability = random.uniform(0, 1)

            if len(password) >= MIN_LENGTH and stop_probability < PROBABILITY:
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
            if len(reduced) >= MIN_LENGTH and stop_probability < PROBABILITY:
                break

            idx = rng.randint(0, len(self.alphabet) - 1)
            reduced += self.alphabet[idx]

        return reduced

    def __build_table(self):
        table = {}
        print("==> BUILDING TABLE...")
        start_time = time.perf_counter()
        for _ in tqdm(range(self.rows), desc="Building rows", unit="row"):
            start = self.__random_password()

            end = start
            for step in range(self.steps):
                h = self.__sha512_hash(end)
                end = self.__reduce(h, step)

            if end not in table:
                table[end] = []

            table[end].append(start)

        end_time = time.perf_counter()
        print(f"\r==> TABLE BUILT{' ' * 20}", flush=True)
        print(f"==> Time: {end_time - start_time:.2f}s")
        
        end = random.choice(list(table.keys()))
        lista = table[end]
        print(f"==> Random rows:")
        for row in lista:
            print(f"start: {row} -> end: {end}")

        return table

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
