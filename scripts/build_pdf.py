"""
build_pdf.py — единый скрипт генерации PDF-памяток Туроператора

Что делает:
  1. Читает pages/memos/*.html
  2. BeautifulSoup вырезает лишнее (навигация, картинки, форма, кнопки)
  3. Сохраняет чистый HTML в tmp/pdf_ready/memos/
  4. Запускает node scripts/generate_pdf.js

Запуск:
  python scripts/build_pdf.py
"""

import os
import subprocess
import sys
from bs4 import BeautifulSoup

# --- Пути ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, 'pages', 'memos')
OUTPUT_DIR = os.path.join(ROOT, 'tmp', 'pdf_ready', 'memos')
GENERATE_PDF_JS = os.path.join(ROOT, 'scripts', 'generate_pdf.js')

# Список памяток для генерации
FILES = [
    'egypt.html',
    'maldives.html',
    'turkey.html',
    'vietnam.html',
    'china.html',
    'mauritius.html',
    'thailand.html',
    'seychelles.html',
    'indonesia.html',
    'sri-lanka.html',
    'tanzania.html',
    'tunisia.html',
]


def clean_memo(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    # 1. Удаляем верхнюю навигацию (фиксированный header/nav)
    for tag in soup.find_all('nav'):
        # Оставляем только nav внутри print-header (там нет nav, но на всякий случай)
        if not tag.find_parent(class_='print-header'):
            tag.decompose()

    # 2. Удаляем aside (боковая навигация) и footer сайта
    for tag in soup.find_all('aside'):
        tag.decompose()
    for tag in soup.find_all('footer'):
        if not tag.find_parent(class_='print-footer'):
            tag.decompose()

    # 3. Удаляем кнопки (мобильное меню, скачать и т.д.)
    for tag in soup.find_all('button'):
        tag.decompose()

    # 4. Удаляем мобильный drawer (overlay + drawer)
    for el_id in ('drawer-overlay', 'mobile-drawer'):
        tag = soup.find(id=el_id)
        if tag:
            tag.decompose()

    # 5. Удаляем все <img> кроме тех, что внутри .print-header / .print-only
    #    У оставшихся (логотип) исправляем путь: ../../ → ../../../
    #    (файлы лежат на уровень глубже: tmp/pdf_ready/memos/ вместо pages/memos/)
    for img in soup.find_all('img'):
        parent_print = img.find_parent(class_='print-header') or \
                       img.find_parent(class_='print-only')
        if not parent_print:
            img.decompose()
        else:
            src = img.get('src', '')
            if src.startswith('../../'):
                img['src'] = '../' + src  # ../../ → ../../../
            # Убираем no-print с логотипа и фиксируем размер инлайном
            classes = img.get('class', [])
            if isinstance(classes, list):
                img['class'] = [c for c in classes if c != 'no-print']
            elif isinstance(classes, str):
                img['class'] = classes.replace('no-print', '').strip()
            img['style'] = 'height: 40pt; width: auto; display: block;'

    # 6. Удаляем ссылки-кнопки "О стране", "Хочу туда", "Скачать PDF"
    #    (это <a class="no-print ..."> прямо в начале контентной зоны)
    for a in soup.find_all('a', class_=lambda c: c and 'no-print' in c):
        a.decompose()

    # 7. Удаляем секцию с формой (#section-form) и разделитель перед ней
    form_section = soup.find(id='section-form')
    if form_section:
        # BS4 может засунуть полезные секции внутрь form_section из-за кривого HTML — спасаем их
        for rescued in form_section.find_all('section', recursive=False):
            form_section.insert_before(rescued.extract())

        # Ищем разделитель <div class="h-px ..."> прямо перед формой
        prev = form_section.find_previous_sibling()
        while prev and prev.name is None:
            prev = prev.find_previous_sibling()
        if prev and prev.name == 'div' and prev.get('class'):
            if any('h-px' in c for c in prev.get('class', [])):
                prev.decompose()
        form_section.decompose()

    # 8. Убираем pt-24 у <main> — он нужен только для веб (отступ под фиксированную шапку)
    main = soup.find('main')
    if main and main.get('class'):
        new_classes = [c for c in main['class'] if c != 'pt-24']
        main['class'] = new_classes if new_classes else None

    return str(soup)


def build():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    processed = 0
    for filename in FILES:
        src_path = os.path.join(SOURCE_DIR, filename)
        if not os.path.exists(src_path):
            print(f'  Пропускаем {filename}: файл не найден')
            continue

        with open(src_path, 'r', encoding='utf-8') as f:
            html = f.read()

        clean_html = clean_memo(html)

        dst_path = os.path.join(OUTPUT_DIR, filename)
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(clean_html)

        print(f'  OK {filename}')
        processed += 1

    print(f'\nПодготовлено файлов: {processed}/{len(FILES)}')
    return processed > 0


def generate_pdfs():
    print('\n--- Запускаем генерацию PDF ---')
    result = subprocess.run(
        ['node', GENERATE_PDF_JS],
        cwd=ROOT,
        capture_output=False,
    )
    if result.returncode != 0:
        print('Ошибка при генерации PDF')
        sys.exit(result.returncode)


if __name__ == '__main__':
    print('--- Туроператора: подготовка HTML для PDF ---')
    ok = build()
    if ok:
        generate_pdfs()
