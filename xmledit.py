# -*- coding: utf-8 -*-
"""
XMLedit — редактор XML-файлов электронных документов.
Все реквизиты документа отображаются разом на одной прокручиваемой форме,
сгруппированные по разделам. Интерфейс в стиле онлайн-валидатора Диадок.
"""

import os
import re
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

COLOR = {
    "brand": "#0B6BCB",
    "brand_dark": "#00529B",
    "brand_light": "#EAF3FB",
    "bg": "#FFFFFF",
    "panel": "#F4F6F9",
    "border": "#D9E0E8",
    "text": "#1F2A37",
    "muted": "#6B7A90",
    "error": "#C8202A",
    "warn": "#A96A00",
    "success": "#00875A",
    "white": "#FFFFFF",
}

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

TAG_LABELS = {
    "Файл": "Файл",
    "Документ": "Документ",
    "СодИнфКлнт": "Содержание информации клиента",
    "ОбщОбъявлСтГруз": "Общая объявленная стоимость груза",
    "СвГруз": "Сведения о грузе",
    "СвГП": "Грузополучатель",
    "СвГО": "Грузоотправитель",
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

HIDDEN_ATTRS = {"ИдФайл", "ВерсПрог", "ВерсФорм", "КНД", "УИД_ПорЭксп", "ИдентПартГруз"}

ABBREV = {

    "ИНН": "ИНН", "КПП": "КПП", "КНД": "КНД", "ОКВ": "ОКВ", "ОКВЭД": "ОКВЭД",
    "ОКПО": "ОКПО", "ОГРН": "ОГРН", "ОГРНИП": "ОГРНИП", "УИД": "УИД",
    "Св": "Сведения", "Ид": "Идентификатор", "ИдСв": "Идентификационные сведения",
    "ФИО": "ФИО", "ТС": "транспортное средство", "ГП": "грузополучатель",
    "ГО": "грузоотправитель", "Клнт": "клиент", "Эксп": "экспедитор",
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
    "СвГП": "Грузополучатель", "СвГО": "Грузоотправитель",
    "СвТС": "Транспортное средство", "СвКлнт": "Клиент", "СвЭксп": "Экспедитор",
    "СвИП": "Индивидуальный предприниматель", "СвЮЛУч": "Юридическое лицо",
    "СвГруз": "Сведения о грузе", "СвСтрПроисх": "Страна происхождения",
}


def _split_camel(name):
    """Разбивает CamelCase-имя на отдельные слова."""
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


class XMLeditApp:

    def __init__(self, root):
        self.root = root
        self.root.title("XMLedit — все реквизиты документа")
        self.root.geometry("1000x760")
        self.root.minsize(820, 600)
        self.root.configure(bg=COLOR["bg"])

        self.file_path = None
        self.tree_root = None
        self.entries = []   # список (element, key, StringVar)

        self._setup_style()
        self._build_ui()

    # ---------- Стили ----------
    def _setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Diadoc.TButton",
                        background=COLOR["brand"],
                        foreground=COLOR["white"],
                        font=("Segoe UI", 10, "bold"),
                        padding=(16, 8),
                        borderwidth=0,
                        focusthickness=0)
        style.map("Diadoc.TButton",
                  background=[("active", COLOR["brand_dark"]),
                              ("pressed", COLOR["brand_dark"])])

        style.configure("DiadocSecondary.TButton",
                        background="#E7EDF4",
                        foreground=COLOR["brand_dark"],
                        font=("Segoe UI", 10),
                        padding=(12, 6),
                        borderwidth=0,
                        focusthickness=0)
        style.map("DiadocSecondary.TButton",
                  background=[("active", "#D5E2EE"),
                              ("pressed", "#D5E2EE")])

        style.configure("Diadoc.TEntry",
                        fieldbackground=COLOR["bg"],
                        foreground=COLOR["text"],
                        bordercolor=COLOR["border"],
                        lightcolor=COLOR["border"],
                        darkcolor=COLOR["border"],
                        font=("Segoe UI", 10),
                        padding=5)
        style.configure("Diadoc.Vertical.TScrollbar",
                        background="#D9E0E8",
                        troughcolor=COLOR["panel"],
                        borderwidth=0)

    # ---------- Интерфейс ----------
    def _build_ui(self):
        # Хедер в стиле Диадок
        header = tk.Frame(self.root, bg=COLOR["brand"], height=72)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        badge = tk.Label(header, text="XML", bg=COLOR["white"],
                         fg=COLOR["brand"], font=("Segoe UI", 16, "bold"),
                         padx=12, pady=2)
        badge.place(x=16, y=18)

        tk.Label(header, text="XMLedit — реквизиты документа",
                 bg=COLOR["brand"], fg=COLOR["white"],
                 font=("Segoe UI", 16, "bold")).place(x=82, y=10)
        tk.Label(header, text="Все значения видны разом · интерфейс в стиле Диадок",
                 bg=COLOR["brand"], fg="#B9D7F2",
                 font=("Segoe UI", 9)).place(x=83, y=42)

        # Панель инструментов
        toolbar = tk.Frame(self.root, bg=COLOR["bg"])
        toolbar.pack(fill=tk.X, padx=12, pady=(10, 6))

        ttk.Button(toolbar, text="Загрузить файл...",
                   style="Diadoc.TButton",
                   command=self.open_file).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="Сохранить",
                   style="DiadocSecondary.TButton",
                   command=self.save_file).pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Сохранить как...",
                   style="DiadocSecondary.TButton",
                   command=self.save_file_as).pack(side=tk.LEFT, padx=6)

        self.file_label = tk.Label(toolbar, text="Файл не выбран",
                                   bg=COLOR["bg"], fg=COLOR["muted"],
                                   font=("Segoe UI", 9))
        self.file_label.pack(side=tk.RIGHT)

        # Основная область: одна прокручиваемая форма
        wrap = tk.Frame(self.root, bg=COLOR["bg"])
        wrap.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        self.form_canvas = tk.Canvas(wrap, bg=COLOR["bg"], highlightthickness=0)
        ysb = ttk.Scrollbar(wrap, orient=tk.VERTICAL,
                            command=self.form_canvas.yview,
                            style="Diadoc.Vertical.TScrollbar")
        self.form_canvas.configure(yscrollcommand=ysb.set)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.form_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.form_frame = tk.Frame(self.form_canvas, bg=COLOR["bg"])
        self._form_window = self.form_canvas.create_window(
            (0, 0), window=self.form_frame, anchor="nw")

        self.form_frame.bind(
            "<Configure>",
            lambda e: self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all")))
        self.form_canvas.bind(
            "<Configure>",
            lambda e: self.form_canvas.itemconfigure(self._form_window, width=e.width))

        # Мышь прокручивает форму (колесо над любым местом формы)
        self.form_canvas.bind(
            "<MouseWheel>",
            lambda e: self._scroll_form(e))
        self._bind_mousewheel(self.form_frame)

        # Статусная панель
        self.status_frame = tk.Frame(self.root, bg=COLOR["panel"],
                                     highlightbackground=COLOR["border"],
                                     highlightthickness=1)
        self.status_frame.pack(fill=tk.X, padx=12, pady=(6, 10))
        self.status_icon = tk.Label(self.status_frame, text="i",
                                    bg=COLOR["panel"], fg=COLOR["muted"],
                                    font=("Segoe UI", 14, "bold"))
        self.status_icon.pack(side=tk.LEFT, padx=(10, 4), pady=6)
        self.status_text = tk.Label(self.status_frame,
                                    text="Загрузите XML-файл — все реквизиты появятся в форме.",
                                    bg=COLOR["panel"], fg=COLOR["muted"],
                                    font=("Segoe UI", 10),
                                    justify=tk.LEFT, anchor="w", wraplength=780)
        self.status_text.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=6)


    # ---------- Прокрутка колёсиком мыши ----------
    def _scroll_form(self, event):
        """Прокручивает форму на delta колеса мыши."""
        self.form_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def _bind_mousewheel(self, widget):
        """Рекурсивно привязывает колесо мыши ко всем дочерним виджетам."""
        try:
            widget.bind("<MouseWheel>", self._scroll_form)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            self._bind_mousewheel(child)


    # ---------- Загрузка ----------
    def open_file(self):
        initialdir = os.path.dirname(self.file_path) if self.file_path else os.path.expanduser("~")
        path = filedialog.askopenfilename(
            title="Загрузить XML-файл",
            filetypes=[("XML файлы", "*.xml"), ("Все файлы", "*.*")],
            initialdir=initialdir)
        if not path:
            return
        self.load_file(path)

    def load_file(self, path):
        self._set_status("loading", "Загрузка...")
        self.root.update_idletasks()
        try:
            self.tree_root = ET.parse(path).getroot()
        except ET.ParseError:
            self._set_status(
                "error",
                "Файл поврежден или ФНС не регламентирует этот формат.\n"
                "Неверный формат файла. Загрузите файл в формате XML.")
            messagebox.showerror("Ошибка", "Неверный формат файла.\nЗагрузите файл в формате XML.")
            return
        except Exception as e:
            self._set_status("error", f"Ошибка при загрузке: {e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return

        self.file_path = path
        self.file_label.config(text=os.path.basename(path), fg=COLOR["brand_dark"])
        self._render_form()
        self._validate_document()

    # ---------- Отрисовка всех реквизитов разом ----------
    def _render_form(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.entries = []

        if self.tree_root is None:
            return

        # Инфо-карточка файла
        card = self._make_card(self.form_frame)
        self._card_add_header(card, "Документ", first=True)
        self._card_add_info(card, f"Файл: {os.path.basename(self.file_path) if self.file_path else ''}")
        root = self.tree_root
        doc = root.find("Документ") or root
        knd = root.get("КНД") or doc.get("КНД")
        if knd:
            self._card_add_info(card, f"КНД: {knd}")
        if doc.get("НаимДок"):
            self._card_add_info(card, f"Тип: {doc.get('НаимДок')}")

        # Рекурсивно рисуем все блоки с полями
        self._render_node(self.form_frame, root, depth=0)

        # Повторная привязка колеса мыши к новым виджетам
        self._bind_mousewheel(self.form_frame)

    def _render_node(self, parent, element, depth):
        """Рекурсивно рисует блок для элемента: заголовок + все его поля."""
        visible_attrs = [(k, v) for k, v in element.attrib.items()
                         if k not in HIDDEN_ATTRS]
        has_text = bool(element.text and element.text.strip())
        label = _tag_label(element.tag)

        has_fields = bool(visible_attrs or has_text)

        # Структурный узел с заголовком, но без собственных полей
        if not has_fields:
            if element.tag in TAG_LABELS:
                ttk.Separator(parent, orient="horizontal").pack(
                    fill=tk.X, padx=(16 + depth * 12, 16), pady=(6, 2))
                tk.Label(parent, text=label,
                         bg=COLOR["bg"], fg=COLOR["brand_dark"],
                         font=("Segoe UI", 11, "bold"),
                         anchor="w").pack(fill=tk.X, padx=(16 + depth * 12, 10), pady=(4, 0))
            for child in element:
                self._render_node(parent, child, depth + (0 if not element.tag in TAG_LABELS else 1))
            return

        # Блок с полями
        card = self._make_card(parent, depth)
        self._card_add_header(card, label)

        row = 0
        if has_text:
            row = self._add_field(card, row, "Значение", element, "__text__",
                                  element.text.strip())
        for key, value in visible_attrs:
            row = self._add_field(card, row, _attr_label(key), element, key, value)

        for child in element:
            self._render_node(card, child, 1)

    def _make_card(self, parent, depth=0):
        card = tk.Frame(parent, bg=COLOR["panel"],
                        highlightbackground=COLOR["border"], highlightthickness=1)
        card.pack(fill=tk.X, padx=(12 + depth * 16, 12), pady=4)
        return card

    def _card_add_header(self, card, text, first=False):
        inner = tk.Frame(card, bg=COLOR["panel"])
        inner.pack(fill=tk.X, pady=(8 if not first else 6, 0))
        tk.Frame(inner, bg=COLOR["brand"], width=4, height=16).pack(
            side=tk.LEFT, padx=(10, 6))
        tk.Label(inner, text=text, bg=COLOR["panel"],
                 fg=COLOR["brand_dark"],
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

    def _card_add_info(self, card, text):
        tk.Label(card, text=text, bg=COLOR["panel"], fg=COLOR["muted"],
                 font=("Segoe UI", 9)).pack(anchor=tk.W, padx=20, pady=(0, 2))

    def _add_field(self, card, row, label, element, key, value):
        """Добавляет строку «подпись → поле ввода» в карточку."""
        line = tk.Frame(card, bg=COLOR["panel"])
        line.pack(fill=tk.X, padx=10, pady=1)
        tk.Label(line, text=label + ":",
                 bg=COLOR["panel"], fg=COLOR["text"],
                 font=("Segoe UI", 10), width=32, anchor="w",
                 wraplength=260).pack(side=tk.LEFT, padx=(12, 6))
        var = tk.StringVar(value=value)
        entry = ttk.Entry(line, textvariable=var, style="Diadoc.TEntry")
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        self.entries.append((element, key, var))
        return row + 1

    # ---------- Статус ----------
    def _set_status(self, kind, text):
        icons = {"success": "✓", "error": "✗", "warn": "!", "info": "i", "loading": "…"}
        colors = {"success": COLOR["success"], "error": COLOR["error"],
                  "warn": COLOR["warn"], "info": COLOR["muted"],
                  "loading": COLOR["brand"]}
        self.status_icon.config(text=icons.get(kind, "i"),
                                fg=colors.get(kind, COLOR["muted"]))
        self.status_text.config(text=text, fg=colors.get(kind, COLOR["muted"]))

    # ---------- Проверка в стиле Диадок ----------
    def _validate_document(self):
        root = self.tree_root
        doc = root.find("Документ") or root
        knd = root.get("КНД") or doc.get("КНД")
        name = doc.get("НаимДок")
        enc = self._detect_encoding()

        if not knd:
            self._set_status(
                "warn",
                "Невозможно определить тип файла. Добавьте в файл атрибут КНД.")
            return

        base = f"Файл успешно распознан (КНД {knd})"
        if name:
            base += f". Тип: «{name}»"
        base += f". Кодировка: {enc}."

        if enc.lower() != "windows-1251":
            self._set_status(
                "warn",
                f"{base} Валидатор Диадок ожидает windows-1251 — это не мешает редактированию.")
        else:
            self._set_status("success", base)

    def _detect_encoding(self):
        try:
            with open(self.file_path, "rb") as f:
                head = f.read(3)
            if head.startswith(b"\xef\xbb\xbf"):
                return "UTF-8 (BOM)"
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    f.read()
                return "UTF-8"
            except (UnicodeDecodeError, ValueError):
                return "windows-1251"
        except OSError:
            return "windows-1251"

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
            initialfile=os.path.basename(self.file_path) if self.file_path else "document.xml")
        if not path:
            return
        self.file_path = path
        self.file_label.config(text=os.path.basename(path), fg=COLOR["brand_dark"])
        self._write_xml(path)

    def _write_xml(self, path):
        try:
            # Применяем все значения из полей к дереву
            for element, key, var in self.entries:
                if key == "__text__":
                    element.text = var.get()
                else:
                    element.set(key, var.get())
            xml_str = ET.tostring(self.tree_root, encoding="unicode")
            with open(path, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write(xml_str)
            self._set_status("success",
                             f"Файл успешно сохранён: {os.path.basename(path)}")
            messagebox.showinfo("Готово", "Файл успешно сохранён.")
        except Exception as e:
            self._set_status("error", f"Ошибка при сохранении: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


def main():
    root = tk.Tk()
    app = XMLeditApp(root)
    default = r"d:\Users\andrnl\Downloads\81-70342.xml"
    if os.path.exists(default):
        app.load_file(default)
    root.mainloop()


if __name__ == "__main__":
    main()

