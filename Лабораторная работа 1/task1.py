"""Задание 1. Приветствие по имени."""


def greet(name: str) -> str:
    """Вернуть строку приветствия для переданного имени."""
    return f"Привет, {name}!"


if __name__ == "__main__":
    user_name = input("Как вас зовут? ").strip() or "студент"
    print(greet(user_name))
