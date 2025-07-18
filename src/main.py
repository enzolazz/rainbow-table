import argparse
from rainbow_table import RainbowTable
from settings import settings
from storage import ChainStorage
from logger import log


def main(rows, length):
    storage = ChainStorage(settings.data_path / "rainbow_table.db")

    rt = RainbowTable(storage)

    try:
        if rows and length:
            rt.build(rows=rows, length=length)

        log.info("Counting row length...")
        storage.count_row_length()

        hashed_password = "1e65cf1485fa6b43f090a448feb1cd8931378e4c96daf245a6d96c264e55579b59ca80519d020cb394b7e501c71386d8aeaf503206de439c9d92558c8884812d"
        while hashed_password:

            password = rt.check(hashed_password)

            if password:
                log.status(f"Password found: {password}")

            print("\n----\n")

            hashed_password = str(
                input("Digite o hash da senha (ou pressione Enter para sair): ")
            ).strip()
            print()
    finally:
        storage.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A RainbowTable built in python for a bonus college assignment."
    )

    parser.add_argument("--rows", type=int, help="Rows to add to the table.")
    parser.add_argument(
        "--length", type=int, help="Required length to build passwords with."
    )

    args = parser.parse_args()

    main(args.rows, args.length)
