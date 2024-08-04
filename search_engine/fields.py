import os

import pandas as pd
import pdfplumber
from django import forms

from service import settings
from .widgets import MultipleFileInput


def extract_info_from_pdf(pdf_path, doc_number):
    headers = None  # Переменная для хранения заголовков таблицы
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            table = page.extract_table()
            if table:
                if headers is None:
                    # Извлекаем и сохраняем заголовки с первой страницы
                    headers = [h.replace('\n', ' ').strip() if h else '' for h in table[0]]
                # Проверяем, что заголовки были извлечены
                if headers:
                    # Создаем индекс для данных на основе заголовков
                    data_index = {header: index for index, header in enumerate(headers)}
                    doc_index = data_index.get('Номер коммерческого документа')

                    if doc_index is not None:
                        # Определяем начальную строку для обработки данных
                        start_row = 1 if page_number == 0 else 0
                        for row in table[start_row:]:
                            if row[doc_index] == doc_number:
                                # Собираем данные по найденному документу
                                required_fields = ["Адрес получателя", "Вес брутто (кг)", "Стоимость товара"]
                                if all(field in data_index for field in required_fields):
                                    row_data = {field: row[data_index[field]].replace('\n', ' ').strip() for
                                                field in required_fields}
                                    return row_data
    return None


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


def handle_uploaded_file(f):
    upload_dir = 'uploads/'
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f.name)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path


def delete_file(file_path):
    """ Удаление файла по указанному пути """
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.isfile(full_path):
        os.remove(full_path)
        return True
    return False


def delete_all_files():
    """ Удаление всех файлов в директории uploads """
    upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Удален файл: {filename}")



def extract_info_from_excel(file_path, barcode):
    # Загружаем Excel файл, пропуская первые 4 строки, если они не содержат данных
    try:
        df = pd.read_excel(file_path, skiprows=4)
    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        return None
    df['ШК'] = df['ШК'].astype(str)
    # Определение необходимых столбцов
    required_columns = ['ШК', 'п/п', 'Наименование товара', 'ФИО получателя физ. лица', 'Номер паспорта', 'Пинфл', 'Контактный номер']

    # Проверяем наличие всех необходимых столбцов в DataFrame
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Отсутствующие столбцы: {', '.join(missing_columns)}")
        return None
    # Поиск всех строк с заданным ШК
    matched_rows = df[df['ШК'] == barcode]

    if matched_rows.empty:
        print("ШК не найден в файле.")
        return None

    # Сбор данных из всех подходящих строк
    results = []
    for _, row in matched_rows.iterrows():
        result = {
            'НАИМЕНОВАНИЕ': row['Наименование товара'],
            'ФИО получателя': row['ФИО получателя физ. лица'],
            'Номер паспорта': row['Номер паспорта'],
            'ПИНФЛ': row['Пинфл'],
            'Контактный номер': row['Контактный номер']
        }

        # Обработка возможных NaN значений
        result = {k: (v if not pd.isna(v) else None) for k, v in result.items()}
        results.append(result)

    return results