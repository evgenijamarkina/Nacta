import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("1000x1000")

        # Инициализируем историю как пустой список ДО загрузки из файла
        self.history = []

        # Файл для сохранения истории
        self.history_file = "history.json"
        self.load_history()

        # Список валют
        self.currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD","CNY", "INR", "BRL", "MXN", "ZAR", "TRY", "RUB", "KRW", "SGD","SEK", "NOK", "DKK", "PLN", "CZK", "HUF",
            "AED", "SAR", "EGP", "ILS", "QAR", "KWD","THB", "IDR", "MYR", "PHP", "VND", "HKD","ARS", "CLP", "COP", "PEN",]

        # Выбор валют
        ttk.Label(root, text="Из валюты:").grid(row=0, column=0, padx=10, pady=10)
        self.from_currency = ttk.Combobox(root, values=self.currencies)
        self.from_currency.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(root, text="В валюту:").grid(row=1, column=0, padx=10, pady=10)
        self.to_currency = ttk.Combobox(root, values=self.currencies)
        self.to_currency.grid(row=1, column=1, padx=10, pady=10)

        # Поле ввода суммы
        ttk.Label(root, text="Сумма:").grid(row=2, column=0, padx=10, pady=10)
        self.amount_entry = ttk.Entry(root)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=10)

        # Кнопка конвертации
        self.convert_button = ttk.Button(root, text="Конвертировать", command=self.convert)
        self.convert_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Таблица истории
        self.history_tree = ttk.Treeview(root, columns=("From", "To", "Amount", "Result"), show="headings")
        self.history_tree.heading("From", text="Из валюты")
        self.history_tree.heading("To", text="В валюту")
        self.history_tree.heading("Amount", text="Сумма")
        self.history_tree.heading("Result", text="Результат")
        self.history_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Обновляем таблицу истории при запуске
        self.update_history_table()

    def get_exchange_rate(self, from_currency, to_currency):
        api_key = "YOUR_API_KEY"
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"

        try:
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                return data["rates"].get(to_currency)
            else:
                raise Exception(f"Ошибка API: {data.get('error', 'Неизвестная ошибка')}")
        except Exception as e:
            raise Exception(f"Ошибка подключения к API: {str(e)}")

    def convert(self):
        try:
            # Проверка и преобразование суммы
            amount_str = self.amount_entry.get().strip()
            if not amount_str:
                messagebox.showerror("Ошибка", "Введите сумму для конвертации")
                return

            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return

            # Получение выбранных валют
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()

            if not from_curr or not to_curr:
                messagebox.showerror("Ошибка", "Выберите валюты для конвертации")
                return

            # Получение курса и расчёт
            rate = self.get_exchange_rate(from_curr, to_curr)
            if rate is None:
                raise Exception("Не удалось получить курс для выбранной пары валют")

            result = amount * rate

            # Добавление в историю
            self.add_to_history(from_curr, to_curr, amount, result)

            # Показ результата
            messagebox.showinfo(
                "Результат конвертации",
                f"{amount:.2f} {from_curr} = {result:.2f} {to_curr}\n"
                f"Курс: 1 {from_curr} = {rate:.4f} {to_curr}"
            )

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму (число)")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def add_to_history(self, from_curr, to_curr, amount, result):
        entry = {
            "From": from_curr,
            "To": to_curr,
            "Amount": amount,
            "Result": result
        }
        self.history.append(entry)
        self.save_history()
        self.update_history_table()

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось сохранить историю: {str(e)}")

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    loaded_history = json.load(f)
                    if isinstance(loaded_history, list):
                        self.history = loaded_history
                    else:
                        messagebox.showwarning("Предупреждение", "Файл истории повреждён, создаётся новый")
                        self.history = []
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Ошибка загрузки истории: {str(e)}")
                self.history = []
        else:
            self.history = []

    def update_history_table(self):
        # Очищаем таблицу
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Заполняем таблицу данными из истории (последние 10 записей)
        recent_entries = self.history[-10:] if len(self.history) > 10 else self.history
        for entry in recent_entries:
            self.history_tree.insert("", "end", values=(
                entry["From"],
                entry["To"],
                f"{entry['Amount']:.2f}",
                f"{entry['Result']:.2f}"
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
