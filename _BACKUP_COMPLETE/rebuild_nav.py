import os
import re

def rebuild_memo_nav(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Находим область контента
    content_area_regex = re.compile(r'<!-- ═══ CONTENT AREA ═══ -->.*?<div id="memo-content-area">', re.DOTALL)
    if not content_area_regex.search(content):
        # Если нет специальной метки, ищем просто начало main
        content_parts = content.split('<main>')
        if len(content_parts) < 2:
            return False
        content_to_scan = content_parts[1]
    else:
        # Берем все от начала контента до футера
        content_to_scan = content.split('<div id="memo-content-area">')[1].split('</main>')[0]

    # 2. Находим все <h2 id="X">Текст</h2>
    headings = re.findall(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', content_to_scan, re.DOTALL)
    
    if not headings:
        print(f"  - В {filename} не найдено заголовков H2 с ID.")
        return False

    # 3. Формируем новый список ссылок для десктопа
    nav_links_html = ""
    for anchor_id, title in headings:
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        # Стандартный стиль: nav-link (совпадает с CSS в файлах)
        nav_links_html += f'                        <a href="#{anchor_id}" class="nav-link">{clean_title}</a>\n'

    # 4. Глобальная чистка и замена блока навигации
    # Ищем aside и заменяем весь блок внутри
    aside_pattern = re.compile(r'(<aside[^>]*>.*?<p[^>]*>Содержание</p>\s*)\s*(<nav[^>]*>.*?</nav>|.*?)(?=\s*</div>\s*</div>\s*</aside>)', re.DOTALL)
    
    new_nav = f'<nav id="quick-links" class="flex flex-col border-l border-black/5">\n{nav_links_html}                        </nav>'
    
    if aside_pattern.search(content):
        content = aside_pattern.sub(r'\1' + new_nav, content)
        print(f"✅ Навигация в {filename} обновлена ({len(headings)} пунктов).")
    else:
        print(f"⚠️  Не удалось найти структуру Aside в {filename}")
        return False

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

# Запуск по всем файлам памяткам
files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
for f in files:
    try:
        rebuild_memo_nav(f)
    except Exception as e:
        print(f"❌ Ошибка в {f}: {e}")
