products = ["яблоки", "бананы", "апельсины", "груши", "бананы"]
item_to_find = "бананы"

try:
    print(products.index(item_to_find))
except ValueError:
    print("None")

