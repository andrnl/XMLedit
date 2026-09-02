# -*- coding: utf-8 -*-
"""
Программа для просмотра и редактирования XML-файлов электронных документов.
Интерфейс выполнен в стиле онлайн-валидатора XML Диадок (CheckXML):
https://www.diadoc.ru/docs/forms/validation-xml
"""

import os
import re
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------------------------------------------------------------------------
# Фирменная цветовая схема в стиле СКБ Контур / Диадок
# ---------------------------------------------------------------------------
COLOR = {
    "brand": "#0B6BCB",        # фирменный синий Диадок
    "brand_dark": "#00529B",   # тёмно-синий (наведение)
    "brand_light": "#EAF3FB",  # светло-голубой (выделение)
    "bg": "#FFFFFF",           # основной фон
    "panel": "#F4F6F9",        # фон панелей
    "border": "#D9E0E8",       # границы
    "text": "#1F2A37",         # основной текст
    "muted": "#6B7A90",        # приглушённый текст
    "error": "#C8202A",        # красный (ошибки)
    "warn": "#A96A00",         # оранжевый (предупреждения)
    "success": "#00875A",      # зелёный (успех)
    "white": "#FFFFFF",
}

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
        self.root.title("Проверка XML-файла")
        self.root.geometry("1000x720")
        self.root.minsize(800, 560)
        self.root.configure(bg=COLOR["bg"])

        self.tree = None
        self.file_path = None
        self.entries = {}   # (element, key) -> StringVar
        self._node_map = {}
        self.btn_other = None
        self.btn_other_packed = False

        self._setup_style()
        self._build_ui()

    # ---------- Стили в духе Диадок ----------
    def _setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Главная кнопка (синяя, как «Загрузить файл»)
        style.configure(
            "Diadoc.TButton",
            background=COLOR["brand"],
            foreground=COLOR["white"],
            font=("Segoe UI", 10, "bold"),
            padding=(16, 8),
            borderwidth=0,
            focusthickness=0,
        )
        style.map("Diadoc.TButton",
                  background=[("active", COLOR["brand_dark"]),
                              ("pressed", COLOR["brand_dark"])])

        # Вторичная кнопка (светло-голубая)
        style.configure(
            "DiadocSecondary.TButton",
            background="#E7EDF4",
            foreground=COLOR["brand_dark"],
            font=("Segoe UI", 10),
            padding=(12, 6),
            borderwidth=0,
            focusthickness=0,
        )
        style.map("DiadocSecondary.TButton",
                  background=[("active", "#D5E2EE"),
                              ("pressed", "#D5E2EE")])

        # Дерево разделов
        style.configure(
            "Diadoc.Treeview",
            background=COLOR["bg"],
            fieldbackground=COLOR["bg"],
            foreground=COLOR["text"],
            borderwidth=1,
            relief="solid",
            rowheight=28,
            font=("Segoe UI", 10),
        )
        style.map("Diadoc.Treeview",
                  background=[("selected", COLOR["brand_light"])],
                  foreground=[("selected", COLOR["brand_dark"])])

        # Скроллбары
        style.configure("Diadoc.Vertical.TScrollbar",
                        background="#D9E0E8",
                        troughcolor=COLOR["panel"],
                        borderwidth=0)

        # Поля ввода
        style.configure(
            "Diadoc.TEntry",
            fieldbackground=COLOR["bg"],
            foreground=COLOR["text"],
            bordercolor=COLOR["border"],
            lightcolor=COLOR["border"],
            darkcolor=COLOR["border"],
            font=("Segoe UI", 10),
            padding=5,
        )

        # Секционные заголовки
        style.configure(
            "Diadoc.Treeview.Heading",
            background=COLOR["panel"],
            foreground=COLOR["text"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )


    # ---------- Построение интерфейса ----------
    def _build_ui(self):
        # ---- Синий хедер как на сайте Диадок ----
        header = tk.Frame(self.root, bg=COLOR["brand"], height=72)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        badge = tk.Label(header, text="XML",
                         bg=COLOR["white"], fg=COLOR["brand"],
                         font=("Segoe UI", 16, "bold"),
                         padx=12, pady=2)
        badge.place(x=16, y=18)

        title = tk.Label(header, text="Проверка XML-файла",
                         bg=COLOR["brand"], fg=COLOR["white"],
                         font=("Segoe UI", 16, "bold"))
        title.place(x=82, y=10)

        subtitle = tk.Label(header, text="Электронные документы и форматы · в стиле Диадок",
                            bg=COLOR["brand"], fg="#B9D7F2",
                            font=("Segoe UI", 9))
        subtitle.place(x=83, y=42)

        # ---- Панель инструментов ----
        toolbar = tk.Frame(self.root, bg=COLOR["bg"])
        toolbar.pack(fill=tk.X, padx=12, pady=(10, 6))

        self.btn_upload = ttk.Button(toolbar, text="Загрузить файл...",
                                     style="Diadoc.TButton",
                                     command=self.open_file)
        self.btn_upload.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_save = ttk.Button(toolbar, text="Сохранить",
                                   style="DiadocSecondary.TButton",
                                   command=self.save_file)
        self.btn_save_as = ttk.Button(toolbar, text="Сохранить как...",
                                      style="DiadocSecondary.TButton",
                                      command=self.save_file_as)
        self.btn_save.pack(side=tk.LEFT, padx=6)
        self.btn_save_as.pack(side=tk.LEFT, padx=6)

        self.file_label = tk.Label(toolbar, text="Файл не выбран",
                                   bg=COLOR["bg"], fg=COLOR["muted"],
                                   font=("Segoe UI", 9))
        self.file_label.pack(side=tk.RIGHT)


        # ---- Основная область ----
        main = tk.Frame(self.root, bg=COLOR["bg"])
        main.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # Левая панель: дерево
        left = tk.Frame(main, bg=COLOR["panel"],
                        highlightbackground=COLOR["border"], highlightthickness=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        tk.Label(left, text="Разделы документа",
                 bg=COLOR["panel"], fg=COLOR["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(8, 4))

        tree_wrap = tk.Frame(left, bg=COLOR["panel"])
        tree_wrap.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.tree = ttk.Treeview(tree_wrap, show="tree", style="Diadoc.Treeview")
        ysb = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL,
                            command=self.tree.yview,
                            style="Diadoc.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=ysb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ysb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Правая панель: поля
        right = tk.Frame(main, bg=COLOR["panel"],
                         highlightbackground=COLOR["border"], highlightthickness=1)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        self.header_label = tk.Label(right, text="Выберите раздел слева",
                                     bg=COLOR["panel"], fg=COLOR["brand_dark"],
                                     font=("Segoe UI", 13, "bold"))
        self.header_label.pack(anchor=tk.W, padx=12, pady=(8, 4))

        canvas = tk.Canvas(right, bg=COLOR["panel"], highlightthickness=0)
        ysb2 = ttk.Scrollbar(right, orient=tk.VERTICAL, command=canvas.yview,
                             style="Diadoc.Vertical.TScrollbar")
        self.fields_frame = tk.Frame(canvas, bg=COLOR["panel"])
        self.fields_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.fields_frame, anchor="nw")
        canvas.configure(yscrollcommand=ysb2.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ysb2.pack(side=tk.RIGHT, fill=tk.Y)


        # ---- Нижняя статусная панель (результат «проверки») ----
        self.status_frame = tk.Frame(self.root, bg=COLOR["panel"],
                                     highlightbackground=COLOR["border"],
                                     highlightthickness=1)
        self.status_frame.pack(fill=tk.X, padx=12, pady=(6, 10))

        self.status_icon = tk.Label(self.status_frame, text="i",
                                    bg=COLOR["panel"], fg=COLOR["muted"],
                                    font=("Segoe UI", 14, "bold"))
        self.status_icon.pack(side=tk.LEFT, padx=(10, 4), pady=6)

        self.status_text = tk.Label(self.status_frame,
                                    text="Загрузите XML-файл для проверки.",
                                    bg=COLOR["panel"], fg=COLOR["muted"],
                                    font=("Segoe UI", 10),
                                    justify=tk.LEFT, anchor="w", wraplength=760)
        self.status_text.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=6)

    # ---------- Установка статуса ----------
    def _set_status(self, kind, text):
        icons = {"success": "✓", "error": "✗", "warn": "!", "info": "i", "loading": "…"}
        colors = {"success": COLOR["success"], "error": COLOR["error"],
                  "warn": COLOR["warn"], "info": COLOR["muted"],
                  "loading": COLOR["brand"]}
        self.status_icon.config(text=icons.get(kind, "i"),
                                fg=colors.get(kind, COLOR["muted"]))
        self.status_text.config(text=text, fg=colors.get(kind, COLOR["muted"]))


    # ---------- Загрузка файла ----------
    def open_file(self):
        initialdir = os.path.dirname(self.file_path) if self.file_path else os.path.expanduser("~")
        path = filedialog.askopenfilename(
            title="Загрузить XML-файл",
            filetypes=[("XML файлы", "*.xml"), ("Все файлы", "*.*")],
            initialdir=initialdir,
        )
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
                "Мы не можем распознать и проверить этот файл. Неверный формат файла. "
                "Загрузите файл в формате XML.",
            )
            messagebox.showerror("Ошибка", "Неверный формат файла.\nЗагрузите файл в формате XML.")
            return
        except Exception as e:
            self._set_status("error", f"Ошибка на странице.\n{e}")
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")
            return

        self.file_path = path
        self.file_label.config(text=os.path.basename(path), fg=COLOR["brand_dark"])
        self._populate_tree()
        self._clear_fields()

        # Показываем кнопку «Загрузить другой файл...»
        if not self.btn_other_packed:
            self.btn_other = ttk.Button(self.btn_upload.master,
                                        text="Загрузить другой файл...",
                                        style="DiadocSecondary.TButton",
                                        command=self.open_file)
            self.btn_other.pack(side=tk.LEFT, after=self.btn_upload, padx=6)
            self.btn_other_packed = True

        self._validate_document()

    # ---------- Проверка документа (как в валидаторе Диадок) ----------
    def _validate_document(self):
        root = self.tree_root
        doc = root.find("Документ")
        if doc is None:
            doc = root

        # Ищем КНД на корне или Документе
        knd = root.get("КНД") or (doc.get("КНД") if doc is not None else None)
        name = doc.get("НаимДок") if doc is not None else None
        enc = self._detect_encoding()

        if not knd:
            self._set_status(
                "warn",
                "Невозможно определить тип файла. Добавьте в файл атрибут КНД. "
                "КНД указан в приказе ФНС к документу и в примере XML-документа.",
            )
            return

        if name:
            base = (f"Файл успешно распознан. Тип документа: «{name}» (КНД {knd}). "
                    f"Кодировка: {enc}.")
        else:
            base = f"Файл успешно распознан. КНД {knd}. Кодировка: {enc}."

        # Если кодировка не windows-1251 — предупреждение как у Диадок
        if enc.lower() != "windows-1251":
            self._set_status(
                "warn",
                f"Файл успешно распознан (КНД {knd}), но кодировка {enc}, "
                "а валидатор Диадок ожидает windows-1251. Это не мешает редактированию.",
            )
        else:
            self._set_status("success", base)

    def _detect_encoding(self):
        """Определяет кодировку файла по BOM и попытке декодировать."""
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
        element = self._node_map.get(selection[0])
        if element is not None:
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

        self.header_label.config(text=_tag_label(element.tag))
        row = 0

        # Текстовое содержимое элемента
        if element.text and element.text.strip():
            self._add_row(row, "Значение:", element, "__text__",
                          element.text.strip())
            row += 1

        # Атрибуты
        for key, value in element.attrib.items():
            if key in HIDDEN_ATTRS:
                continue
            self._add_row(row, _attr_label(key), element, key, value)
            row += 1

        if row == 0:
            tk.Label(self.fields_frame, text="В этом разделе нет редактируемых полей.",
                     bg=COLOR["panel"], fg=COLOR["muted"],
                     font=("Segoe UI", 10)).pack(anchor=tk.W, padx=12, pady=10)
            return

        ttk.Button(self.fields_frame, text="Применить изменения раздела",
                   style="DiadocSecondary.TButton",
                   command=lambda: self.apply_section(element)
                   ).grid(row=row, column=0, columnspan=2, sticky=tk.W,
                          padx=12, pady=12)

    def _add_row(self, row, label, element, key, value):
        tk.Label(self.fields_frame, text=label + ":",
                 bg=COLOR["panel"], fg=COLOR["text"],
                 font=("Segoe UI", 10)).grid(row=row, column=0,
                                            sticky=tk.W, padx=(12, 6), pady=3)
        var = tk.StringVar(value=value)
        entry = ttk.Entry(self.fields_frame, textvariable=var,
                          style="Diadoc.TEntry", width=52)
        entry.grid(row=row, column=1, sticky=tk.W, padx=(6, 12), pady=3)
        self.entries[(element, key)] = var


    # ---------- Сохранение ----------
    def apply_section(self, element):
        for (el, key), var in self.entries.items():
            if el is element:
                if key == "__text__":
                    el.text = var.get()
                else:
                    el.set(key, var.get())
        messagebox.showinfo("Готово", "Изменения раздела применены.")

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
        self.file_label.config(text=os.path.basename(path), fg=COLOR["brand_dark"])
        self._write_xml(path)

    def _write_xml(self, path):
        try:
            for (el, key), var in self.entries.items():
                if key == "__text__":
                    el.text = var.get()
                else:
                    el.set(key, var.get())
            xml_str = ET.tostring(self.tree_root, encoding="unicode")
            with open(path, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write(xml_str)
            self._set_status("success", f"Файл успешно сохранён: {os.path.basename(path)}")
            messagebox.showinfo("Готово", "Файл успешно сохранён.")
        except Exception as e:
            self._set_status("error", f"Ошибка при сохранении: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


def main():
    root = tk.Tk()
    app = PoruchenieEditor(root)
    default = r"d:\Users\andrnl\Downloads\81-70342.xml"
    if os.path.exists(default):
        app.load_file(default)
    root.mainloop()


if __name__ == "__main__":
    main()

