import json
import os

from django.shortcuts import render, redirect

from .fields import handle_uploaded_file, delete_all_files, extract_info_from_pdf, extract_info_from_excel
from .forms import FileUploadForm, SearchForm


def upload_files(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            file_names = [f.name for f in files]  # Получаем имена файлов

            for f in files:
                handle_uploaded_file(f)

            response = redirect('search_product_by_files')
            response.set_cookie('file_names', json.dumps(file_names))

            return response
    else:
        form = FileUploadForm()

    return render(request, 'upload.html', {'form': form})


def search_product_by_files(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            barcode = form.cleaned_data['barcode']
            results = {}
            # Получаем список имен файлов из cookie
            file_names = json.loads(request.COOKIES.get('file_names', '[]'))

            if not file_names:
                return render(request, 'search.html', {'form': form, 'error': 'Нет загруженных файлов.'})

            uploads_dir = 'uploads'
            pdf_searched = False  # Флаг для поиска в PDF
            xlsx_searched = False  # Флаг для поиска в Excel

            for file_name in file_names:
                file_path = os.path.join(uploads_dir, file_name)

                # Поиск в PDF только если не найдено ранее
                if not pdf_searched and file_name.endswith('.pdf'):
                    product_info = extract_info_from_pdf(file_path, barcode)
                    if product_info:
                        pdf_searched = True  # Устанавливаем флаг поиска в PDF
                        if barcode not in results:
                            results[barcode] = {}
                        results[barcode].update(product_info)  # Обновляем словарь с новыми данными

                # Поиск в Excel только если не найдено ранее
                if not xlsx_searched and file_name.endswith('.xlsx'):
                    product_info = extract_info_from_excel(file_path, barcode)
                    if product_info:
                        xlsx_searched = True  # Устанавливаем флаг поиска в Excel
                        if barcode not in results:
                            results[barcode] = {}
                        # Объединяем данные, добавляем ключи
                        for item in product_info:
                            results[barcode].update(item)
            print(34534, results)
            if not results:
                return render(request, 'search.html', {'form': form, 'error': 'Штрих-код не найден в файлах.'})
            else:
                # Распаковываем словарь для передачи в шаблон
                return render(request, 'search.html', {'form': form, 'results': results[barcode]})

    # Перемещаем render для GET и невалидной формы сюда
    form = SearchForm()
    return render(request, 'search.html', {'form': form})


def finish_search(request):
    # Получаем имена файлов из cookie
    file_names = json.loads(request.COOKIES.get('file_names', '[]'))

    # Удаляем все файлы
    delete_all_files(file_names)

    # Перенаправляем пользователя
    response = redirect('upload_files')

    # Удаляем куки, установив его значение в пустую строку и срок действия на прошлую дату
    response.delete_cookie('file_names')

    return response
