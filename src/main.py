import argparse
from rainbow_table import RainbowTable
from settings import settings


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A RainbowTable built in python for a bonus college assignment."
    )

    parser.add_argument(
        "--rows",
        type=int,
        help="Rows to add to the table; If a table does not exist, creates this amount of rows.",
        default=None,
    )
    parser.add_argument(
        "--steps",
        type=int,
        help="How many steps (cols) the table should have.",
        default=None,
    )

    args = parser.parse_args()

    if args.steps and not args.rows:
        parser.error("--rows is required when --steps is specified.")

    rt = RainbowTable(rows=args.rows, steps=args.steps or settings.default_steps)

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
