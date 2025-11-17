from bs4 import BeautifulSoup
import requests
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import xml.etree.ElementTree as ET
import os


class ParserApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.root.title('Universal Parser - HTML/XML/JSON')
        self.root.geometry('1200x800')

        # Переменные для RadioButton
        self.data_type = tk.StringVar(value="html")
        self.source_type = tk.StringVar(value="url")

        # Основной фрейм
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Выбор типа данных
        type_frame = tk.LabelFrame(main_frame, text="Тип данных", padx=10, pady=10)
        type_frame.pack(fill=tk.X, pady=5)

        tk.Radiobutton(type_frame, text="HTML", variable=self.data_type,
                       value="html", command=self.on_data_type_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="XML", variable=self.data_type,
                       value="xml", command=self.on_data_type_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(type_frame, text="JSON", variable=self.data_type,
                       value="json", command=self.on_data_type_change).pack(side=tk.LEFT, padx=10)

        # Выбор источника
        source_frame = tk.LabelFrame(main_frame, text="Источник данных", padx=10, pady=10)
        source_frame.pack(fill=tk.X, pady=5)

        tk.Radiobutton(source_frame, text="URL (ссылка)", variable=self.source_type,
                       value="url", command=self.on_source_type_change).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(source_frame, text="Файл", variable=self.source_type,
                       value="file", command=self.on_source_type_change).pack(side=tk.LEFT, padx=10)

        # Фрейм для ввода URL/файла
        self.input_frame = tk.Frame(main_frame)
        self.input_frame.pack(fill=tk.X, pady=5)

        self.setup_input_widgets()

        # Фрейм для запроса
        query_frame = tk.LabelFrame(main_frame, text="Параметры парсинга", padx=10, pady=10)
        query_frame.pack(fill=tk.X, pady=5)

        tk.Label(query_frame, text="Запрос (тег/ключ/путь):").pack(anchor=tk.W)
        self.query_entry = tk.Entry(query_frame, width=80)
        self.query_entry.pack(fill=tk.X, pady=5)
        self.query_entry.insert(0, "a")

        # Подсказка для запроса
        self.query_hint = tk.Label(query_frame, text="Примеры: div.header, //item, data.users",
                                   fg="gray", font=("Arial", 9))
        self.query_hint.pack(anchor=tk.W)

        # Фрейм для кнопок
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text='Парсить', command=self.parse_data,
                  bg='lightblue', font=('Arial', 12), width=15).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text='Очистить', command=self.clear_output,
                  bg='lightyellow', font=('Arial', 12), width=15).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text='Показать примеры', command=self.show_examples,
                  bg='lightgreen', font=('Arial', 12), width=15).pack(side=tk.LEFT, padx=5)

        # Текстовое поле для вывода
        output_frame = tk.LabelFrame(main_frame, text="Результаты", padx=10, pady=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.text = tk.Text(output_frame, wrap=tk.WORD)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)

        self.update_query_hint()

    def setup_input_widgets(self):
        """Создает виджеты для ввода в зависимости от выбранного источника"""
        # Очищаем фрейм
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        if self.source_type.get() == "url":
            tk.Label(self.input_frame, text="URL:").pack(anchor=tk.W)
            self.url_entry = tk.Entry(self.input_frame, width=80)
            self.url_entry.pack(fill=tk.X, pady=5)
            self.url_entry.insert(0, "https://example.com")

        else:  # file
            tk.Label(self.input_frame, text="Файл:").pack(anchor=tk.W)
            file_frame = tk.Frame(self.input_frame)
            file_frame.pack(fill=tk.X, pady=5)

            self.file_entry = tk.Entry(file_frame, width=70)
            self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Button(file_frame, text="Обзор", command=self.browse_file).pack(side=tk.RIGHT, padx=5)

    def on_data_type_change(self):
        """Обновляет интерфейс при изменении типа данных"""
        self.update_query_hint()

    def on_source_type_change(self):
        """Обновляет интерфейс при изменении источника"""
        self.setup_input_widgets()

    def update_query_hint(self):
        """Обновляет подсказку для запроса в зависимости от типа данных"""
        data_type = self.data_type.get()
        hints = {
            "html": "Примеры: a, div.header, p.text, div.id=main",
            "xml": "Примеры: //item, //book/title, //div[@class='header']",
            "json": "Примеры: data.users, items[0].name, *.title"
        }
        self.query_hint.config(text=hints.get(data_type, ""))

    def browse_file(self):
        """Открывает диалог выбора файла"""
        filetypes = {
            "html": [("HTML files", "*.html;*.htm")],
            "xml": [("XML files", "*.xml")],
            "json": [("JSON files", "*.json")]
        }

        filename = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=filetypes.get(self.data_type.get(), [("All files", "*.*")])
        )

        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def get_data_content(self):
        """Получает содержимое данных из URL или файла"""
        source_type = self.source_type.get()
        data_type = self.data_type.get()

        try:
            if source_type == "url":
                url = self.url_entry.get().strip()
                if not url:
                    raise ValueError("Введите URL")

                response = requests.get(url)
                response.raise_for_status()

                if data_type == "html":
                    return response.content
                else:
                    return response.text

            else:  # file
                filepath = self.file_entry.get().strip()
                if not filepath:
                    raise ValueError("Выберите файл")

                if not os.path.exists(filepath):
                    raise ValueError("Файл не существует")

                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()

        except Exception as e:
            raise Exception(f"Ошибка загрузки данных: {e}")

    def parse_html(self, content, query):
        """Парсит HTML данные"""
        soup = BeautifulSoup(content, 'html.parser')

        # Разбираем запрос на тег и атрибуты
        parts = query.split('.')
        base_tag = parts[0].strip()
        attrs = {}

        for part in parts[1:]:
            if '=' in part:
                key_value = part.split('=', 1)
                key = key_value[0].strip()
                value = key_value[1].strip()
                attrs[key] = value
            else:
                if 'class' in attrs:
                    attrs['class'].append(part.strip())
                else:
                    attrs['class'] = [part.strip()]

        # Ищем элементы
        if attrs:
            elements = soup.find_all(base_tag, attrs=attrs)
        else:
            elements = soup.find_all(base_tag)

        return elements, soup

    def parse_xml(self, content, query):
        """Парсит XML данные"""
        try:
            root = ET.fromstring(content)
        except ET.ParseError as e:
            raise Exception(f"Ошибка парсинга XML: {e}")

        # Простой XPath-like поиск
        if query.startswith('//'):
            elements = root.findall('.')  # Получаем все элементы для поиска
            results = []
            for elem in elements.iter():
                if self.match_xml_path(elem, query):
                    results.append(elem)
            return results, root
        else:
            # Простой поиск по тегу
            return root.findall(f'.//{query}'), root

    def match_xml_path(self, element, query):
        """Проверяет соответствие элемента XML запросу"""
        # Простая реализация для демонстрации
        query = query[2:]  # Убираем '//'
        if '[' in query and ']' in query:
            tag_part = query.split('[')[0]
            attr_part = query.split('[')[1].split(']')[0]

            if element.tag == tag_part:
                if '@' in attr_part:
                    attr_name, attr_value = attr_part.split('=')
                    attr_name = attr_name.replace('@', '').strip()
                    attr_value = attr_value.strip("'\"")
                    return element.get(attr_name) == attr_value
        else:
            return element.tag == query

        return False

    def parse_json(self, content, query):
        """Парсит JSON данные"""
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка парсинга JSON: {e}")

        # Простой поиск по ключам
        def find_in_json(obj, path):
            results = []

            if isinstance(obj, dict):
                for key, value in obj.items():
                    if path == '*' or key == path:
                        results.append((key, value))
                    if isinstance(value, (dict, list)):
                        results.extend(find_in_json(value, path))
            elif isinstance(obj, list):
                for item in obj:
                    results.extend(find_in_json(item, path))

            return results

        return find_in_json(data, query), data

    def format_html_result(self, elements):
        """Форматирует результат для HTML"""
        if not elements:
            return "Элементы не найдены\n"

        result = f"Найдено элементов: {len(elements)}\n\n"

        for i, element in enumerate(elements, 1):
            result += f"--- Элемент {i} ---\n"

            element_text = element.get_text(strip=True)
            if element_text:
                if len(element_text) > 200:
                    element_text = element_text[:200] + "..."
                result += f"Текст: {element_text}\n"

            element_attrs = element.attrs
            if element_attrs:
                result += "Атрибуты:\n"
                for attr, value in element_attrs.items():
                    result += f"  {attr}: {value}\n"

            if element.name == 'a':
                href = element.get('href', 'нет ссылки')
                result += f"Ссылка: {href}\n"
            elif element.name == 'img':
                src = element.get('src', 'нет источника')
                alt = element.get('alt', 'нет описания')
                result += f"Источник: {src}\n"
                result += f"Описание: {alt}\n"

            result += "\n"

        return result

    def format_xml_result(self, elements):
        """Форматирует результат для XML"""
        if not elements:
            return "Элементы не найдены\n"

        result = f"Найдено элементов: {len(elements)}\n\n"

        for i, element in enumerate(elements, 1):
            result += f"--- Элемент {i} ---\n"
            result += f"Тег: {element.tag}\n"

            if element.attrib:
                result += "Атрибуты:\n"
                for attr, value in element.attrib.items():
                    result += f"  {attr}: {value}\n"

            if element.text and element.text.strip():
                text = element.text.strip()
                if len(text) > 200:
                    text = text[:200] + "..."
                result += f"Текст: {text}\n"

            result += "\n"

        return result

    def format_json_result(self, elements):
        """Форматирует результат для JSON"""
        if not elements:
            return "Элементы не найдены\n"

        result = f"Найдено элементов: {len(elements)}\n\n"

        for i, (key, value) in enumerate(elements, 1):
            result += f"--- Элемент {i} ---\n"
            result += f"Ключ: {key}\n"
            result += f"Тип: {type(value).__name__}\n"
            result += f"Значение: {json.dumps(value, ensure_ascii=False, indent=2)}\n\n"

        return result

    def parse_data(self):
        """Основная функция парсинга"""
        try:
            content = self.get_data_content()
            query = self.query_entry.get().strip()
            data_type = self.data_type.get()

            self.text.delete(1.0, tk.END)

            if not query:
                self.text.insert(tk.END, "Введите запрос для поиска")
                return

            # Парсим в зависимости от типа данных
            if data_type == "html":
                elements, _ = self.parse_html(content, query)
                result = self.format_html_result(elements)

            elif data_type == "xml":
                elements, _ = self.parse_xml(content, query)
                result = self.format_xml_result(elements)

            elif data_type == "json":
                elements, _ = self.parse_json(content, query)
                result = self.format_json_result(elements)

            self.text.insert(tk.END, result)

        except Exception as e:
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, f"Ошибка: {e}")

    def clear_output(self):
        """Очищает поле вывода"""
        self.text.delete(1.0, tk.END)

    def show_examples(self):
        """Показывает примеры использования"""
        examples = {
            "html": """
HTML ПРИМЕРЫ:
• a - все ссылки
• div.header - div с классом header
• p.text - параграфы с классом text
• div.id=main - div с id=main
• img.avatar - изображения с классом avatar
            """,
            "xml": """
XML ПРИМЕРЫ:
• //item - все элементы item
• //book/title - все title внутри book
• //div[@class='header'] - div с атрибутом class='header'
• //item[1] - первый элемент item
            """,
            "json": """
JSON ПРИМЕРЫ:
• users - все ключи 'users'
• name - все ключи 'name'
• *.title - все ключи 'title' на любом уровне
• data - ключ 'data'
• items - ключ 'items'
            """
        }

        examples_window = tk.Toplevel(self.root)
        examples_window.title("Примеры использования")
        examples_window.geometry("500x400")

        text_widget = tk.Text(examples_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)

        current_type = self.data_type.get()
        text_widget.insert(tk.END, examples.get(current_type, "Примеры не найдены"))
        text_widget.config(state=tk.DISABLED)


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ParserApp(root)
    root.mainloop()
