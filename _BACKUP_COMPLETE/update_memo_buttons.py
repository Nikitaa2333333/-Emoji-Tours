import os
import re

def update_memo_buttons():
    # 1. Update template_memo.html
    template_path = 'template_memo.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace buttons block in template
        # Was: Памятка туристу -> Now: О стране (link to country page)
        new_buttons = '''                <div class="flex flex-wrap gap-4 mb-10">
                    <a href="#journey" class="inline-block bg-primary text-black px-10 py-4 rounded-full text-lg font-bold shadow-lg hover:scale-105 active:scale-95 transition-all">Хочу туда</a>
                    <a href="██slug██.html" class="inline-block bg-black text-white px-10 py-4 rounded-full text-lg font-bold shadow-lg hover:scale-105 active:scale-95 transition-all">О стране</a>
                </div>'''
        
        content = re.sub(r'<div class="flex flex-wrap gap-4 mb-10">.*?</div>', new_buttons, content, flags=re.DOTALL)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Обновлен шаблон: {template_path}")

    # 2. Update all existing memo-*.html files
    for filename in os.listdir('.'):
        if filename.startswith('memo-') and filename.endswith('.html'):
            # Extract country slug (e.g., memo-egypt.html -> egypt)
            # Remove "memo-" prefix and ".html" suffix
            country_slug = filename[5:-5]
            country_link = f"{country_slug}.html"
            
            # Special case for Sri Lanka if needed, but the slug is usually the country name
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Button block for specific file
            updated_buttons = f'''                <div class="flex flex-wrap gap-4 mb-10">
                    <a href="#journey" class="inline-block bg-primary text-black px-10 py-4 rounded-full text-lg font-bold shadow-lg hover:scale-105 active:scale-95 transition-all">Хочу туда</a>
                    <a href="{country_link}" class="inline-block bg-black text-white px-10 py-4 rounded-full text-lg font-bold shadow-lg hover:scale-105 active:scale-95 transition-all">О стране</a>
                </div>'''
            
            # Replace old buttons block
            new_content = re.sub(r'<div class="flex flex-wrap gap-4 mb-10">.*?</div>', updated_buttons, content, flags=re.DOTALL)
            
            if new_content != content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Обновлены кнопки в: {filename} (ссылка на {country_link})")
            else:
                print(f"Кнопки в {filename} уже обновлены или не найдены.")

if __name__ == "__main__":
    update_memo_buttons()
