def count_letters(text):
    letter_counts = {}
    for char in text.lower():
        if char.isalpha():
            letter_counts[char] = letter_counts.get(char, 0) + 1
    return letter_counts

def calculate_frequency(letter_counts):
    total_letters = sum(letter_counts.values())
    frequency = {letter: round(count / total_letters, 2) for letter, count in letter_counts.items()}
    return frequency

text = "Пример текста 123123 текст АААААааааа"

letter_counts = count_letters(text)
frequency = calculate_frequency(letter_counts)

for letter, freq in frequency.items():
    print(f"{letter}: {freq}")
