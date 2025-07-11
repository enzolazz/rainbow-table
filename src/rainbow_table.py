import hashlib
import string
import random

MIN_LENGTH = 5
ALPHABET_LENGTH = 70


class RainbowTable:
    def __init__(self, rows=8000, steps=600):
        self.rows = rows
        self.steps = steps
        self.alphabet = list(string.ascii_letters + string.digits + "!@#%&*()")
        self.table = self.__build_table()

    def __random_password(self):
        password = ""

        while True:
            stop_probability = random.uniform(0, 1)

            if len(password) >= MIN_LENGTH and stop_probability < 0.125:
                break

            password += random.choice(self.alphabet)

        return password

    def __hash(self, plaintext):
        return hashlib.sha512(plaintext.encode()).hexdigest()

    def __reduce(self, hash, step):
        data = hash + str(step)
        reduced = ""

        while True:
            stop_probability = random.uniform(0, 1)
            i = len(reduced)

            if i >= MIN_LENGTH and stop_probability < 0.125:
                break

            idx = (int(data[i * 4 : i * 4 + 4], 16) + step) % ALPHABET_LENGTH
            reduced += self.alphabet[idx]

        return reduced

    def __build_table(self):
        table = []
        for _ in range(self.rows):
            start = self.__random_password()

            end = start
            for step in range(self.steps):
                hash = self.__hash(end)
                end = self.__reduce(hash, step)

            table.append((start, end))

        return table
