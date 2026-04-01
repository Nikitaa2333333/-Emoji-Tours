import os
import re

def slugify(text):
    # Простая очистка текста для ID
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def fix_caps(text):
    # Убирает капс, оставляя первую букву заглавной
    text = text.strip()
    if not text: return text
    if text.isupper():
        return text.capitalize()
    return text

def process_html(filepath):
    print(f"Обработка: {os.path.basename(filepath)}")
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Удаляем пустые блоки фото и текст-заглушки типа "Фото: tild..."
    html = re.sub(r'<p[^>]*>Фото:\s*tild[^<]*</p>', '', html, flags=re.IGNORECASE)
    
    # 2. Исправляем Капс в H1 и H2
    def replace_h(match):
        tag = match.group(1)
        attrs = match.group(2)
        content = match.group(3)
        # Убираем капс из контента
        if content.isupper() or (len(content) > 5 and content == content.upper()):
            content = content.capitalize()
        return f'<{tag}{attrs}>{content}</{tag}>'
    
    html = re.sub(r'<(h[12])([^>]*)>(.*?)</\1>', replace_h, html, flags=re.DOTALL)

    # 3. Собираем H2 для содержания (кроме формы)
    h2_matches = re.findall(r'<h2([^>]*)>(.*?)</h2>', html, flags=re.DOTALL)
    quick_links = []
    
    # Очищаем старые ID и добавляем новые для тех H2, которые не в форме
    sections_found = 0
    
    def replace_h2_with_id(match):
        nonlocal sections_found
        attrs = match.group(1)
        content = match.group(2).strip()
        
        # Пропускаем заголовок формы
        if "Заполните анкету" in content:
            return match.group(0)
            
        clean_content = re.sub(r'<[^>]+>', '', content) # Текст без тегов
        section_id = f"section-{slugify(clean_content)}" if clean_content else f"section-{sections_found}"
        
        # Добавляем в список для сайдбара
        quick_links.append(f'<a href="#{section_id}" class="nav-link">{clean_content}</a>')
        
        # Перезаписываем тег с новым ID
        sections_found += 1
        return f'<h2 id="{section_id}"{attrs}>{content}</h2>'

    # Сначала удалим существующие id у h2 в контенте, чтобы не дублировать
    html = re.sub(r'<h2 id="[^"]+"', '<h2', html)
    # Теперь расставим новые
    html = re.sub(r'<h2([^>]*)>(.*?)</h2>', replace_h2_with_id, html, flags=re.DOTALL)

    # 4. Вставляем ссылки в сайдбар
    links_html = "\n".join(quick_links)
    sidebar_nav_pattern = r'(<nav id="quick-links"[^>]*>).*?(</nav>)'
    if re.search(sidebar_nav_pattern, html, flags=re.DOTALL):
        html = re.sub(sidebar_nav_pattern, rf'\1\n{links_html}\n\2', html, flags=re.DOTALL)

    # 5. Чистим "каскад пустых дивов" (часто бывает после сбоев шаблона)
    # Ищем последовательности </div> </div> </div> и схлопываем лишние, 
    # но это опасно. Лучше просто уберем пустые секции.
    html = re.sub(r'<section[^>]*>\s*<div[^>]*>\s*</div>\s*</section>', '', html)
    html = re.sub(r'<div[^>]*>\s*</div>', '', html)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

# Список файлов для обработки
exclude = ['index.html', 'template.html', 'template_memo.html']
html_files = [f for f in os.listdir('.') if f.endswith('.html') and f not in exclude]

for f in html_files:
    try:
        process_html(f)
    except Exception as e:
        print(f"Ошибка в файле {f}: {e}")

print("\n--- ВСЕ ПОЧИНЕНО ---")
print(f"Обработано файлов: {len(html_files)}")
