# -*- coding: utf-8 -*-
"""
Программа для просмотра и редактирования электронного поручения экспедитору
(формат Diadoc XML). Универсальный редактор, отображающий любую структуру XML.
"""

import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re

# Словарь русских подписей для атрибутов
ATTR_LABELS = {
    "ИдФайл": "Идентификатор файла",
    "ВерсПрог": "Версия программы",
    "ВерсФорм": "Версия формы",
    "КНД": "КНД",
    "НаимДок": "Наименование документа",
    "ДатИнфКлнт": "Дата информации клиента",
    "ВрИнфКлнт": "Время информации клиента",
    "СодОпер": "Содержание операции",
    "НомДок": "Номер документа",
    "ДатаДок": "Дата документа",
    "ДокГруз": "Док груз",
    "УИД_ПорЭксп": "УИД поручения экспедитору",
    "КодОКВ": "Код валюты (ОКВ)",
    "НаимОКВ": "Наименование валюты",
    "СтГр": "Стоимость груза",
    "ПрУведСторон": "Признак уведомления сторон",
    "ДатОтгрС": "Дата отгрузки с",
    "ДатОтгрПо": "Дата отгрузки по",
    "ПрзПрвз": "Признак перевозки",
    "ИдентПартГруз": "Идентификатор партии груза",
    "ИННФЛ": "ИНН физического лица",
    "Фамилия": "Фамилия",
    "Имя": "Имя",
    "Отчество": "Отчество",
    "ВидТС": "Вид транспортного средства",
    "НаимГруз": "Наименование груза",
    "КолМестГр": "Количество мест груза",
    "ПрзОпаснГруз": "Признак опасного груза",
    "ПрзИзъятВещ": "Признак изъятых вещей",
    "УказОбъем": "Указан объём",
    "УчГосСист": "Учёт в гос. системе",
    "НалУпак": "Наличие упаковки",
    "НалКодТовНом": "Наличие кода товара",
    "Объем": "Объём (м³)",
    "Марк": "Маркировка",
    "КодСтр": "Код страны",
    "НаимСтран": "Наименование страны",
    "ВесНетто": "Вес нетто (кг)",
    "ВесБрутто": "Вес брутто (кг)",
    "АдрТекст": "Адрес",
    "НаимОрг": "Наименование организации",
    "ИННЮЛ": "ИНН организации",
    "КПП": "КПП",
    "РеквНаимДок": "Наименование документа (договор)",
    "РеквНомерДок": "Номер документа (договор)",
    "РеквДатаДок": "Дата документа (договор)",
    "СпосПодтПолном": "Способ подтверждения полномочий",
}

# Словарь русских подписей для тегов (разделов)
TAG_LABELS = {
    "Файл": "Файл",
    "Документ": "Документ",
    "СодИнфКлнт": "Содержание информации клиента",
    "ОбщОбъявлСтГруз": "Общая объявленная стоимость груза",
    "СвГруз": "Сведения о грузе",
    "СвГП": "Грузоотправитель",
    "СвГО": "Грузополучатель",
    "СвТС": "Транспортное средство",
    "ОбъявлСтГрузПарт": "Объявленная стоимость груза (партия)",
    "ОпГруз": "Описание груза",
    "Марк": "Маркировка",
    "СвСтрПроисх": "Страна происхождения",
    "ВесГруз": "Вес груза",
    "АдрГруз": "Адрес груза",
    "АдрПриемГруз": "Адрес приёма груза",
    "АдрПунктНазн": "Адрес пункта назначения",
    "АдрВыдГруз": "Адрес выдачи груза",
    "Адрес": "Адрес",
    "АдрИнф": "Адресная информация",
    "СвКлнт": "Клиент",
    "СвЭксп": "Экспедитор",
    "ДогТрЭксп": "Договор транспортной экспедиции",
    "ПодпИнфКлнт": "Подпись информации клиента",
    "ИдСв": "Идентификационные сведения",
    "СвИП": "Индивидуальный предприниматель",
    "СвЮЛУч": "Юридическое лицо",
    "ФИО": "ФИО",
}

# Атрибуты, которые не стоит показывать как редактируемые (служебные)
HIDDEN_ATTRS = {"ИдФайл", "ВерсПрог", "ВерсФорм", "КНД", "УИД_ПорЭксп", "ИдентПартГруз"}

# Словарь сокращений для автоматического перевода неизвестных тегов/атрибутов
ABBREV = {
    "ИНН": "ИНН", "КПП": "КПП", "КНД": "КНД", "ОКВ": "ОКВ", "ОКВЭД": "ОКВЭД",
    "ОКПО": "ОКПО", "ОГРН": "ОГРН", "ОГРНИП": "ОГРНИП", "УИД": "УИД",
    "Св": "Сведения", "Ид": "Идентификатор", "ИдСв": "Идентификационные сведения",
    "ФИО": "ФИО", "ТС": "транспортное средство", "ГП": "грузоотправитель",
    "ГО": "грузополучатель", "Клнт": "клиент", "Эксп": "экспедитор",
    "Груз": "груз", "Док": "документ", "Инф": "информация", "Наим": "наименование",
    "Ном": "номер", "Дат": "дата", "Вр": "время", "Ст": "стоимость",
    "Вес": "вес", "Объем": "объём", "Адр": "адрес", "Стр": "страна",
    "Код": "код", "Прз": "признак", "Указ": "указан", "Уч": "учёт",
    "Нал": "наличие", "Кол": "количество", "Мест": "мест", "Опасн": "опасный",
    "Изъят": "изъятые", "Вещ": "вещи", "Гос": "государственная", "Сист": "система",
    "Упак": "упаковка", "Тов": "товар", "Происх": "происхождение",
    "Нетто": "нетто", "Брутто": "брутто", "Прием": "приём", "Выд": "выдача",
    "Пункт": "пункт", "Назн": "назначения", "Отгр": "отгрузка",
    "Увед": "уведомление", "Сторон": "сторон", "Првз": "перевозка",
    "Парт": "партия", "Рекв": "реквизит", "Подт": "подтверждение",
    "Полном": "полномочия", "Спос": "способ", "Опер": "операция",
    "Общ": "общая", "Объявл": "объявленная", "ЮЛ": "юридическое лицо",
    "ИП": "индивидуальный предприниматель", "Орг": "организация",
    "Фам": "фамилия", "Отч": "отчество", "Вид": "вид", "Марк": "маркировка",
    "Текст": "текст", "Верс": "версия", "Форм": "форма", "Прог": "программа",
    "Идент": "идентификатор", "Пор": "поручение", "Дог": "договор",
    "Тр": "транспортная", "Экспед": "экспедиция", "Сод": "содержание",
    "Подп": "подпись", "Файл": "файл", "Документ": "документ",
    "СвГП": "Грузоотправитель", "СвГО": "Грузополучатель",
    "СвТС": "Транспортное средство", "СвКлнт": "Клиент", "СвЭксп": "Экспедитор",
    "СвИП": "Индивидуальный предприниматель", "СвЮЛУч": "Юридическое лицо",
    "СвГруз": "Сведения о грузе", "СвСтрПроисх": "Страна происхождения",
}


def _split_camel(name):
    """Разбивает CamelCase-имя на отдельные слова."""
    # Сначала ищем известные аббревиатуры в начале строки
    for abbr in sorted(ABBREV.keys(), key=len, reverse=True):
        if name.startswith(abbr) and len(abbr) > 1:
            rest = name[len(abbr):]
            if rest:
                return [abbr] + _split_camel(rest)
            return [abbr]
    return re.findall(
        r"[А-ЯЁA-Z]+(?=[А-ЯЁA-Z][а-яёa-z])|[А-ЯЁA-Z]?[а-яёa-z]+|[А-ЯЁA-Z]+|\d+",
        name,
    )


def _translate_name(name):
    """Переводит имя тега/атрибута в понятную подпись."""
    if name in ABBREV:
        return ABBREV[name]
    parts = _split_camel(name)
    translated = [ABBREV.get(p, p) for p in parts]
    if not translated:
        return name
    result = " ".join(translated)
    return result[0].upper() + result[1:]



def _tag_label(tag):
    """Возвращает подпись для тега."""
    return TAG_LABELS.get(tag, _translate_name(tag))


def _attr_label(attr):
    """Возвращает подпись для атрибута."""
    return ATTR_LABELS.get(attr, _translate_name(attr))


class PoruchenieEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор поручения экспедитору")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)

        self.tree = None
        self.file_path = None
        self.entries = {}  # (element, key) -> StringVar
        self._node_map = {}

        self._build_ui()

    def _build_ui(self):
        # Верхняя панель с кнопками
        top = ttk.Frame(self.root, padding=5)
        top.pack(fill=tk.X)

        ttk.Button(top, text="Открыть файл…", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Сохранить", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="Сохранить как…", command=self.save_file_as).pack(side=tk.LEFT, padx=2)

        self.file_label = ttk.Label(top, text="Файл не выбран", foreground="gray")
        self.file_label.pack(side=tk.LEFT, padx=10)

        # Основная область: слева дерево, справа поля
        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Левая панель - дерево разделов
        left = ttk.Frame(main)
        main.add(left, weight=1)

        ttk.Label(left, text="Разделы документа:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        self.tree = ttk.Treeview(left, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Правая панель - поля редактирования
        right = ttk.Frame(main)
        main.add(right, weight=2)

        self.header_label = ttk.Label(right, text="Выберите раздел слева", font=("Segoe UI", 12, "bold"))
        self.header_label.pack(anchor=tk.W, padx=10, pady=5)

        # Контейнер с прокруткой для полей
        canvas = tk.Canvas(right, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=canvas.yview)
        self.fields_frame = ttk.Frame(canvas)
        self.fields_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Нижняя панель - подсказка
        bottom = ttk.Label(
            self.root,
            text="Изменяйте значения в полях справа и нажимайте «Сохранить».",
            foreground="gray",
            padding=5,
        )
        bottom.pack(fill=tk.X)

    # ---------- Загрузка файла ----------
    def open_file(self):
        path = filedialog.askopenfilename(
            title="Выберите XML-файл",
            filetypes=[("XML файлы", "*.xml"), ("Все файлы", "*.*")],
            initialdir=os.path.dirname(self.file_path) if self.file_path else os.path.expanduser("~"),
        )
        if not path:
            return
        self.load_file(path)

    def load_file(self, path):
        try:
            self.tree_root = ET.parse(path).getroot()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return
        self.file_path = path
        self.file_label.config(text=os.path.basename(path), foreground="black")
        self._populate_tree()
        self._clear_fields()

    # ---------- Дерево ----------
    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        self._node_map = {}
        self._add_node("", self.tree_root)

    def _add_node(self, parent, element, count=0):
        label = _tag_label(element.tag)
        if count > 1:
            label = f"{label} ({count})"
        node_id = self.tree.insert(parent, "end", text=label, open=True)
        self._node_map[node_id] = element
        # Подсчитываем повторяющиеся дочерние элементы
        child_counts = {}
        for child in element:
            child_counts[child.tag] = child_counts.get(child.tag, 0) + 1
        for child in element:
            self._add_node(node_id, child, child_counts[child.tag])

    # ---------- Поля ----------
    def on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        node_id = selection[0]
        element = self._node_map.get(node_id)
        if element is None:
            return
        self._show_fields(element)

    def _clear_fields(self):
        for w in self.fields_frame.winfo_children():
            w.destroy()
        self.entries.clear()
        self.header_label.config(text="Выберите раздел слева")

    def _show_fields(self, element):
        for w in self.fields_frame.winfo_children():
            w.destroy()
        self.entries.clear()

        header = _tag_label(element.tag)
        self.header_label.config(text=header)

        row = 0

        # Если у элемента есть текстовое содержимое - показываем его
        if element.text and element.text.strip():
            ttk.Label(self.fields_frame, text="Значение:", font=("Segoe UI", 10)).grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=3
            )
            var = tk.StringVar(value=element.text.strip())
            entry = ttk.Entry(self.fields_frame, textvariable=var, width=50)
            entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=3)
            self.entries[(element, "__text__")] = var
            row += 1

        # Атрибуты
        for key, value in element.attrib.items():
            if key in HIDDEN_ATTRS:
                continue
            label = _attr_label(key)
            ttk.Label(self.fields_frame, text=label + ":", font=("Segoe UI", 10)).grid(
                row=row, column=0, sticky=tk.W, padx=10, pady=3
            )
            var = tk.StringVar(value=value)
            entry = ttk.Entry(self.fields_frame, textvariable=var, width=50)
            entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=3)
            self.entries[(element, key)] = var
            row += 1

        if row == 0:
            ttk.Label(
                self.fields_frame,
                text="В этом разделе нет редактируемых полей.",
                foreground="gray",
            ).pack(anchor=tk.W, padx=10, pady=10)
            return

        # Кнопка сохранения изменений этого раздела
        ttk.Button(
            self.fields_frame,
            text="Применить изменения раздела",
            command=lambda: self.apply_section(element),
        ).grid(row=row, column=0, columnspan=2, pady=10)

    def apply_section(self, element):
        for (el, key), var in self.entries.items():
            if el is element:
                if key == "__text__":
                    el.text = var.get()
                else:
                    el.set(key, var.get())
        messagebox.showinfo("Готово", "Изменения раздела применены.")

    # ---------- Сохранение ----------
    def save_file(self):
        if not self.file_path:
            self.save_file_as()
            return
        self._write_xml(self.file_path)

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".xml",
            filetypes=[("XML файлы", "*.xml"), ("Все файлы", "*.*")],
            initialfile=os.path.basename(self.file_path) if self.file_path else "document.xml",
        )
        if not path:
            return
        self.file_path = path
        self.file_label.config(text=os.path.basename(path), foreground="black")
        self._write_xml(path)

    def _write_xml(self, path):
        try:
            # Применяем все незакоммиченные изменения
            for (el, key), var in self.entries.items():
                if key == "__text__":
                    el.text = var.get()
                else:
                    el.set(key, var.get())
            # Сохраняем с объявлением XML
            xml_str = ET.tostring(self.tree_root, encoding="unicode")
            with open(path, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write(xml_str)
            messagebox.showinfo("Готово", "Файл успешно сохранён.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


def main():
    root = tk.Tk()
    app = PoruchenieEditor(root)
    # Попробуем открыть файл по умолчанию, если он существует
    default = r"d:\Users\andrnl\Downloads\81-70342.xml"
    if os.path.exists(default):
        app.load_file(default)
    root.mainloop()


if __name__ == "__main__":
    main()
