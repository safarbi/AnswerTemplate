import csv
import json
from io import StringIO

def csv_to_json(csv_text, delimiter=',', line_terminator='\n'):
    csv_text = csv_text.strip()
    csv_file = StringIO(csv_text)
    csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
    data = list(csv_reader)
    json_data = json.dumps(data, indent=4)

    return json_data

csv_example = """
name,age,city
Alice,30,New York
Bob,25,Los Angeles
Alex,44,London
"""

json_result = csv_to_json(csv_example)
print(json_result)
