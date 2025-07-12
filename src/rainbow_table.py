import hashlib
import string
import random
import time

MIN_LENGTH = 5
ALPHABET_LENGTH = 62
SPECIAL_CHARS = "!@#%&*()"


class RainbowTable:
    def __init__(self, rows=8000, steps=600):
        self.rows = rows
        self.steps = steps
        self.alphabet = list(string.ascii_letters + string.digits)
        self.table = self.__build_table()

    def __random_password(self):
        password = ""

        while True:
            stop_probability = random.uniform(0, 1)

            if len(password) >= MIN_LENGTH and stop_probability < 0.125:
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
            if len(reduced) >= MIN_LENGTH and stop_probability < 0.125:
                break

            idx = rng.randint(0, ALPHABET_LENGTH - 1)
            reduced += self.alphabet[idx]

        return reduced

    def __build_table(self):
        table = []
        print("==> BUILDING TABLE...")
        start_time = time.perf_counter()
        for row in range(self.rows):
            print(f"\rBuilding row: {row+1}/{self.rows}", end="", flush=True)
            start = self.__random_password()

            end = start
            for step in range(self.steps):
                h = self.__sha512_hash(end)
                end = self.__reduce(h, step)

            table.append((start, end))
        end_time = time.perf_counter()
        print(f"\r==> TABLE BUILT{" "* 20}", flush=True)
        print(f"==> Time: {end_time - start_time:.2f}s")
        print(f"==> Random row: { table[random.randint(0, self.rows) ]}")

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
        max = 0
        for step in range(self.steps - 1, -1, -1):
            candidate = hashed_password

            for k in range(step, self.steps):
                candidate = self.__reduce(self.__sha512_hash(candidate), k)
                size_str = len(candidate)
                if size_str > max:
                    max = size_str

                print(
                    f"\r==> {k}:{candidate}{" " * (max-size_str)}",
                    end="",
                    flush=True,
                )

            for start, end in self.table:
                if candidate == end:
                    return self.__regenerate(start, hashed_password)

        print()
        return None
