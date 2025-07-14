import argparse
from collections import defaultdict
import json

from rainbow_table import RainbowTable


def load_table():
    try:
        with open("table.json") as f:
            loaded = json.load(f)

        return defaultdict(list, loaded)
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A RainbowTable built in python for a bonus college assignment."
    )

    parser.add_argument("--rows", type=int, help="Table row size.", default=20000)
    parser.add_argument(
        "--steps",
        type=int,
        help="How many steps (cols) the table should have.",
        default=2000,
    )
    parser.add_argument(
        "--build", type=bool, help="Build a new table from scratch.", default=False
    )

    args = parser.parse_args()

    table = None
    if not args.build:
        table = load_table()

    rt = RainbowTable(rows=args.rows, steps=args.steps, table=table)

    hashed_password = "1e65cf1485fa6b43f090a448feb1cd8931378e4c96daf245a6d96c264e55579b59ca80519d020cb394b7e501c71386d8aeaf503206de439c9d92558c8884812d"
    while hashed_password:
        password = rt.check_password(hashed_password)

        if password:
            print("Achou senha: ", password)
        else:
            print("Nao achou!")
        print("\n----\n")

        hashed_password = str(
            input("Digite o hash da senha (ou pressione Enter para sair): ")
        ).strip()
        print()
        if not hashed_password:
            break
