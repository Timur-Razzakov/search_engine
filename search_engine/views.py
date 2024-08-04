import os

from django.shortcuts import render, redirect

from .fields import handle_uploaded_file, delete_all_files, extract_info_from_pdf, extract_info_from_excel
from .forms import FileUploadForm, SearchForm


def upload_files(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('files')
            for f in files:
                handle_uploaded_file(f)
            return redirect('search_product_by_files')
    else:
        form = FileUploadForm()

    return render(request, 'upload.html', {'form': form})

def search_product_by_files(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            barcode = form.cleaned_data['barcode']
            results = {}
            uploads_dir = 'uploads'
            files = os.listdir(uploads_dir)

            if not files:
                return render(request, 'search.html', {'form': form, 'error': 'Нет загруженных файлов.'})

            pdf_searched = False  # Флаг для поиска в PDF
            xlsx_searched = False  # Флаг для поиска в Excel

            for file_name in files:
                file_path = os.path.join(uploads_dir, file_name)
                product_info = None

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
    delete_all_files()
    return redirect('upload_files')
