size = 1.44 * 1024 * 1024
pages = 100
strings = 50
symbols = 25
bytes_per_symbol = 4

books = size // (pages*strings*symbols*bytes_per_symbol)
print(f"На дискету поместится {int(books)} книг")