import os
import re

def repair_image_links():
    # Расширения, которые мы ищем
    old_exts = ('.jpg', '.jpeg', '.png')
    
    # 1. Собираем список всех существующих webp файлов для сверки
    print("🔍 Сканирую имеющиеся WebP файлы...")
    existing_webp = set()
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.lower().endswith('.webp'):
                # Сохраняем имя без расширения и с путем, если нужно
                rel_path = os.path.join(os.path.relpath(root, '.'), f)
                if rel_path.startswith('.' + os.sep):
                    rel_path = rel_path[2:]
                existing_webp.add(rel_path.replace(os.sep, '/'))

    # 2. Ищем все HTML файлы
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    print(f"📝 Проверяю {len(html_files)} HTML-файлов на наличие битых ссылок...")
    
    total_fixed = 0
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Регулярка для поиска путей к картинкам в src="" или url()
            # Ищем все строки, заканчивающиеся на .jpg, .jpeg, .png
            found_links = re.findall(r'([^"\'\s()]+\.(?:jpg|jpeg|png))', content, re.IGNORECASE)
            
            unique_links = set(found_links)
            file_fixed_count = 0
            
            for link in unique_links:
                # Если файла по ссылке НЕ существует
                if not os.path.exists(link.replace('/', os.sep)):
                    # Проверяем, есть ли такой же файл, но с .webp
                    base = os.path.splitext(link)[0]
                    webp_link = base + ".webp"
                    
                    if os.path.exists(webp_link.replace('/', os.sep)):
                        # Заменяем в контенте
                        content = content.replace(link, webp_link)
                        file_fixed_count += 1
                        total_fixed += 1
            
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Исправлено {file_fixed_count} ссылок в: {html_file}")
            
        except Exception as e:
            print(f"❌ Ошибка в файле {html_file}: {e}")

    print(f"\n🎉 Готово! Всего восстановлено ссылок: {total_fixed}")
    print("Теперь все картинки, которые успели сжаться, должны отображаться.")

if __name__ == "__main__":
    repair_image_links()
