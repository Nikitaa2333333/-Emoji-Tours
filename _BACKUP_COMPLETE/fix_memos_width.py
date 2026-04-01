import os
import glob

def fix_memos_width():
    path = "c:/Users/User/Downloads/tilda dododo/"
    # Находим все файлы памяток и шаблон
    files = glob.glob(os.path.join(path, "memo-*.html"))
    template = os.path.join(path, "template_memo.html")
    if os.path.exists(template):
        files.append(template)
    
    for file_path in files:
        print(f"Обработка {os.path.basename(file_path)}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Увеличиваем ширину основного контейнера (с 1280px до 1440px)
        # Это затронет шапку, основной контент и футер
        new_content = content.replace('max-w-7xl', 'max-w-[1440px]')
        
        # 2. Увеличиваем ширину контейнера формы (с 896px до 1152px)
        new_content = new_content.replace('max-w-4xl', 'max-w-6xl')
        
        # 3. Делаем секции контента более свободными, если есть ограничения
        # В предоставленных файлах ограничений на секции внутри flex-1 не было, 
        # но на всякий случай проверяем стандартные лимиты tailwind
        # new_content = new_content.replace('max-w-2xl', 'max-w-none')
        # new_content = new_content.replace('max-w-3xl', 'max-w-none')

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Файл {os.path.basename(file_path)} обновлен.")
        else:
            print(f"ℹ️ Изменений в {os.path.basename(file_path)} не потребовалось.")

if __name__ == "__main__":
    fix_memos_width()
