from rainbow_table import RainbowTable

if __name__ == "__main__":
    rt = RainbowTable()

    password = rt.check_password(
        "1e65cf1485fa6b43f090a448feb1cd8931378e4c96daf245a6d96c264e55579b59ca80519d020cb394b7e501c71386d8aeaf503206de439c9d92558c8884812d"
    )

    if not password:
        print("Achou senha: ", password)
    else:
        print("Nao achou!")
