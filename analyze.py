import re

def analyze_all():
    try:
        with open('content/тильда.txt', 'r', encoding='utf-8') as f:
            html = f.read()
        
        print("--- ГЛУБОКИЙ АНАЛИЗ НАВИГАЦИИ ТИЛЬДЫ ---")
        
        # Находим все ссылки с решеткой (якоря)
        # Ищем их названия (текст внутри тега <a>)
        all_links = re.findall(r'href="(#[^"]+)"[^>]*>(.*?)</a>', html)
        
        # Находим все хуки для субменю
        hooks = re.findall(r'data-submenu-hook="([^"]+)"', html)
        
        print(f"Всего ссылок-якорей найдено: {len(all_links)}")
        print(f"Найдено групп (субменю): {len(hooks)}")
        print("\nПОЛНЫЙ СПИСОК ССЫЛОК:")
        
        seen = set()
        for href, text in all_links:
            clean_text = re.sub(r'<[^>]*>', '', text).strip()
            if not clean_text: clean_text = "[Нет текста]"
            
            # Чтобы не дублировать
            if (href, clean_text) not in seen:
                print(f"{href} -> {clean_text}")
                seen.add((href, clean_text))
        
        print("\n--- ГРУППЫ СУБМЕНЮ (которые нужно связать) ---")
        for h in hooks:
            print(f"Группа: {h}")

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    analyze_all()
