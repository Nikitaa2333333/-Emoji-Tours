import os
import re

# Настройки
TARGET_DIR = r"c:\Users\User\Downloads\tilda dododo"

HEADER_CODE = """
    <!-- ═══ ФИКСИРОВАННАЯ ШАПКА ═══ -->
    <nav id="main-nav"
        class="fixed top-0 w-full z-50 bg-[#fffcf5]/90 backdrop-blur-md border-b border-black/5 py-4 transition-all duration-300">
        <div class="max-w-7xl mx-auto flex justify-between md:justify-center items-center px-4 md:px-8 relative">
            <a href="index.html"
                class="flex md:absolute md:left-8 text-xs md:text-sm font-bold items-center gap-1 md:gap-2 hover:opacity-70 transition-opacity whitespace-nowrap bg-black/5 px-3 py-2 rounded-full md:bg-transparent md:px-0 md:py-0">
                <span class="material-symbols-outlined text-[18px] md:text-[24px]">arrow_back</span>
                Все страны
            </a>
            <a href="index.html" class="flex-shrink-0 mx-auto md:mx-0">
                <img src="LogoB_300x.png" alt="Emoji Tours" class="h-8 md:h-10">
            </a>
            <div class="w-24 md:hidden"></div>
        </div>
    </nav>
"""

def process_file(filepath, filename):
    if filename == 'index.html':
        return False
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Ищем место, где должен быть хедер. 
    # Обычно это сразу после <div id="scroll-progress"></div> или после <body>
    
    # Паттерн сломанного хедера (пустота и закрывающий тег)
    broken_pattern = re.compile(r'<!-- Premium Mobile Elements [^>]+ -->\s*<div id="scroll-progress"></div>\s*</nav>', re.DOTALL)
    
    if broken_pattern.search(content):
        # Заменяем сломанный кусок на нормальный
        new_fragment = '<!-- Premium Mobile Elements (Pro Max) -->\n    <div id="scroll-progress"></div>' + HEADER_CODE
        content = broken_pattern.sub(new_fragment, content)
    else:
        # Если паттерн не совсем такой, но логотипа нет в хедере
        if '<nav' not in content or 'LogoB_300x.png' not in content:
             # Попробуем вставить после scroll-progress
             if '<div id="scroll-progress"></div>' in content:
                 content = content.replace('<div id="scroll-progress"></div>', '<div id="scroll-progress"></div>' + HEADER_CODE)
             elif '<body>' in content:
                 content = content.replace('<body>', '<body>' + HEADER_CODE)
             elif '<body' in content:
                 # Ищем конец открывающего тега body
                 content = re.sub(r'(<body[^>]*>)', r'\1' + HEADER_CODE, content)

    if content != original_content:
        # Убираем возможные дубликаты </nav> если они возникли при кривой замене
        content = content.replace('</nav>\s*</nav>', '</nav>', 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🛠 Восстановление пропавшей шапки (Header Restore)...")
    html_files = [f for f in os.listdir(TARGET_DIR) if f.endswith('.html')]
    
    updated = 0
    for filename in html_files:
        filepath = os.path.join(TARGET_DIR, filename)
        if process_file(filepath, filename):
            updated += 1
            print(f"✅ Восстановлено: {filename}")
        else:
            print(f"➖ Шапка на месте: {filename}")

    print(f"\n🎉 Готово! Шапка возвращена в {updated} файлах.")

if __name__ == "__main__":
    main()
