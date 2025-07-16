import argparse
from rainbow_table import RainbowTable
from settings import settings
from storage import ChainStorage
from logger import log


def main():
    storage = ChainStorage(settings.data_path / "rainbow_table.db")

    rt = RainbowTable(storage)

    try:
        # rt.build(rows=10000, length=5)

        hashed_password = "1e65cf1485fa6b43f090a448feb1cd8931378e4c96daf245a6d96c264e55579b59ca80519d020cb394b7e501c71386d8aeaf503206de439c9d92558c8884812d"
        while hashed_password:
            password = rt.check(hashed_password, 5)

            if password:
                log.status(f"Password: {password}")

            print("\n----\n")

            hashed_password = str(
                input("Digite o hash da senha (ou pressione Enter para sair): ")
            ).strip()
            print()
            if not hashed_password:
                break
    finally:
        storage.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A RainbowTable built in python for a bonus college assignment."
    )

    args = parser.parse_args()

    main()
