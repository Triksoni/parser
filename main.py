import requests
import tkinter as tk
from tkinter import scrolledtext


def parse_json():
    # Очищаем поле вывода
    output_text.delete(1.0, tk.END)

    url = input_link.get()
    attributes = input_attribute.get()

    # Проверяем заполнение полей
    if not url or not attributes:
        output_text.insert(tk.END, "Заполните все поля!\n")
        return

    try:
        # Получаем данные
        response = requests.get(url)
        data = response.json()

        # Разделяем атрибуты
        attrs = [attr.strip() for attr in attributes.split(',')]

        # Ищем значения
        output_text.insert(tk.END, f"Результаты поиска:\n{'=' * 40}\n")

        for attr in attrs:
            output_text.insert(tk.END, f"\nАтрибут: {attr}\n")
            values = search_in_json(data, attr)

            if values:
                for val in values[:5]:  # Показываем первые 5 значений
                    output_text.insert(tk.END, f"  ✓ {val}\n")
            else:
                output_text.insert(tk.END, "  ✗ Не найдено\n")

    except Exception as e:
        output_text.insert(tk.END, f"Ошибка: {e}\n")


def search_in_json(obj, path):
    """Простой поиск значений в JSON"""
    results = []

    # Разбиваем путь на части
    keys = path.split('.')

    if isinstance(obj, dict):
        # Если это словарь, ищем ключ
        if keys[0] in obj:
            if len(keys) == 1:
                results.append(obj[keys[0]])
            else:
                # Ищем дальше по вложенному пути
                nested_results = search_in_json(obj[keys[0]], '.'.join(keys[1:]))
                results.extend(nested_results)

        # Ищем во всех значениях словаря
        for value in obj.values():
            if isinstance(value, (dict, list)):
                results.extend(search_in_json(value, path))

    elif isinstance(obj, list):
        # Если это список, ищем в каждом элементе
        for item in obj:
            if isinstance(item, (dict, list)):
                results.extend(search_in_json(item, path))

    return results


def add_example():
    """Добавляем пример для теста"""
    input_link.delete(0, tk.END)
    input_link.insert(0, "https://jsonplaceholder.typicode.com/users")
    input_attribute.delete(0, tk.END)
    input_attribute.insert(0, "name, email, phone, address.city")


# Создаем главное окно
root = tk.Tk()
root.title("Простой JSON Парсер")
root.geometry("500x400")

# Элементы интерфейса
tk.Label(root, text="URL с JSON данными:").pack(pady=5)
input_link = tk.Entry(root, width=60)
input_link.pack(pady=5)

tk.Label(root, text="Атрибуты (через запятую):").pack(pady=5)
input_attribute = tk.Entry(root, width=60)
input_attribute.pack(pady=5)

# Кнопки
tk.Button(root, text="Парсить", command=parse_json, bg="lightblue").pack(pady=5)
tk.Button(root, text="Пример", command=add_example, bg="lightgreen").pack(pady=5)

# Поле для вывода
output_text = scrolledtext.ScrolledText(root, width=60, height=15)
output_text.pack(pady=10)

# Запускаем приложение
root.mainloop()