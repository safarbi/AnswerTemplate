import json

def calculate_sum_of_products(json_data):
    total_sum = sum(item['score'] * item['weight'] for item in json_data)
    return round(total_sum, 3)

json_example = """
[
    {"score": 0.0009456152645028281, "weight": 1},
    {"score": 0.5, "weight": 2},
    {"score": 0.2, "weight": 3},
    {"score": 0.01, "weight": 10}
]
"""

json_data = json.loads(json_example)
sum_of_products = calculate_sum_of_products(json_data)

print(sum_of_products)
