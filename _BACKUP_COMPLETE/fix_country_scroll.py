import os

def fix_scroll_links():
    # Директория с файлами
    directory = "."
    
    # Список файлов в директории
    files = [f for f in os.listdir(directory) if f.endswith(".html")]
    
    print("Начинаю исправление ссылок для скролла...")
    
    fixed_count = 0
    # Исправляем страницы стран
    for filename in files:
        # Пропускаем главную, шаблон и памятки по правилам USER_GLOBAL
        if filename in ["index.html", "template.html"] or filename.startswith("memo-"):
            continue
            
        filepath = os.path.join(directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем некорректный якорь #booking-form на правильный #journey
            # Это активирует встроенный скрипт плавного скролла
            new_content = content.replace('href="#booking-form"', 'href="#journey"')
            
            if content != new_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Исправлен скролл в файле: {filename}")
                fixed_count += 1
        except Exception as e:
            print(f"❌ Ошибка при обработке {filename}: {e}")

    # Также обновим template.html, чтобы новые страницы создавались правильно
    template_path = "template.html"
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            t_content = f.read()
        new_t_content = t_content.replace('href="#booking-form"', 'href="#journey"')
        if t_content != new_t_content:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(new_t_content)
            print(f"⭐ Обновлен мастер-шаблон: template.html")

    print(f"\nГотово! Исправлено файлов: {fixed_count}")

if __name__ == "__main__":
    fix_scroll_links()
