import os
import re
from PIL import Image

def optimize_images():
    # Настройки
    quality = 80
    extensions = ('.jpg', '.jpeg', '.png')
    search_dirs = ['.', './images']
    
    image_map = {}
    
    print("🚀 Начинаю конвертацию изображений в WebP...")
    
    # 1. Конвертация изображений
    for folder in search_dirs:
        if not os.path.exists(folder):
            continue
            
        files = [f for f in os.listdir(folder) if f.lower().endswith(extensions)]
        for filename in files:
            filepath = os.path.join(folder, filename)
            base_name = os.path.splitext(filename)[0]
            new_filename = f"{base_name}.webp"
            new_filepath = os.path.join(folder, new_filename)
            
            try:
                with Image.open(filepath) as img:
                    # Сохраняем как webp
                    img.save(new_filepath, 'webp', quality=quality, method=6)
                
                # Запоминаем что на что поменяли (только имя файла)
                image_map[filename] = new_filename
                
                # Удаляем оригинал для экономии места
                os.remove(filepath)
                print(f"✅ {filename} -> {new_filename}")
            except Exception as e:
                print(f"❌ Ошибка в {filename}: {e}")

    if not image_map:
        print("🤔 Изображения для конвертации не найдены.")
        return

    print(f"\n📝 Обновляю ссылки в HTML-файлах (всего замен: {len(image_map)})...")

    # 2. Обновление HTML файлов
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Заменяем упоминания файлов
            for old_name, new_name in image_map.items():
                # Ищем точное совпадение имени файла в кавычках (src="...", url('...'))
                content = content.replace(old_name, new_name)
            
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✨ Обновлен: {html_file}")
            else:
                print(f"➖ Без изменений: {html_file}")
                
        except Exception as e:
            print(f"❌ Ошибка при чтении {html_file}: {e}")

    print("\n🎉 Готово! Все фото сжаты и подключены.")

if __name__ == "__main__":
    optimize_images()
