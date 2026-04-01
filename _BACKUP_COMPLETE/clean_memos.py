import os
import re

def clean_memo_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Список ключевых слов для удаления
    garbage_patterns = [
        r'Телефон: \+7 \(916\) 649-18-52',
        r'Соцсети: вконтакте.*',
        r'Индивидуальный предприниматель трохин евгений альбертович',
        r'^\s*/\s*$'
    ]

    # 1. Удаление из сайдбара
    # <a href="#section-..." class="nav-link">...</a>
    for pattern in garbage_patterns:
        content = re.sub(
            rf'<a href="#section-[^"]*" class="nav-link">{pattern}</a>\n?',
            '', 
            content, 
            flags=re.IGNORECASE | re.MULTILINE
        )

    # 2. Удаление из контента
    # <section class="pt-24 border-t border-black/5"><h2 id="section-..." class="text-6xl font-black mb-16 tracking-tight">...</h2></section>
    for pattern in garbage_patterns:
        # Учитываем возможные вариации внутри тегов
        content = re.sub(
            rf'<section class="pt-24 border-t border-black/5"><h2 id="section-[^"]*" class="text-6xl font-black mb-16 tracking-tight">{pattern}</h2></section>\n?',
            '',
            content,
            flags=re.IGNORECASE | re.MULTILINE
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Очищен файл: {filepath}")

# Проходим по всем файлам memo-*.html
directory = '.'
for filename in os.listdir(directory):
    if filename.startswith('memo-') and filename.endswith('.html'):
        clean_memo_file(os.path.join(directory, filename))
