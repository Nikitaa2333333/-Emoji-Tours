import os
import glob
import re

def fix_html_layout(file_path):
    print(f"Лечим {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Исправляем баг с бесконечными px-5 md:px...
    # Удаляем все повторения и ставим чистый px-5 md:px-8
    content = re.sub(r'px-5(?:\s+md:px-5)*\s+md:px-8', 'px-5 md:px-8', content)
    # На случай если px-8 уже размножился
    content = re.sub(r'px-5(?:\s+md:px-5|\s+md:px-8)+', 'px-5 md:px-8', content)

    # 2. ВОЗВРАЩАЕМ ФОРМУ НА МЕСТО (Разлепляем ПК вид)
    # Нам нужно убедиться, что перед секцией #journey закрыты ВСЕ открытые ранее дивы сетки.
    # В норме их должно быть 2 (закрыть контент-зону <div class="flex-1"> и закрыть flex-сетку <div class="max-w-7xl">)
    if 'id="journey"' in content:
        # Убираем любые скопления </div> перед формой и вставляем строго 2 штуки
        # Ищем <!-- ═══ ФОРМА или <section id="journey"
        content = re.sub(r'(?:\s*</div>\s*)*\s*<!-- ═══ ФОРМА', '\n            </div>\n        </div>\n    </div>\n\n    <!-- ═══ ФОРМА', content)
        # Если коммента нет, ищем по id
        content = re.sub(r'(?:\s*</div>\s*)*\s*<section id="journey"', '\n            </div>\n        </div>\n    </div>\n\n    <section id="journey"', content)

    # 3. Исправляем заголовок (leading и отступы)
    # Делаем адаптивно: на ПК как было, на мобиле с запасом
    # Сначала сбросим то, что натворили раньше
    content = content.replace('leading-[1.1] pt-6 mb-10', 'leading-[1.1] md:leading-none pt-4 md:pt-0 mb-8 md:mb-10')
    content = content.replace('leading-[1.1] pt-4 md:pt-0 mb-8 md:mb-10', 'leading-[1.1] md:leading-none pt-4 md:pt-0 mb-8 md:mb-10')
    
    # 4. Проверяем памятки (вертикальные дыры)
    content = content.replace('space-y-16" id="memo-content-area"', 'space-y-8 md:space-y-12" id="memo-content-area"')
    content = content.replace('space-y-8" id="memo-content-area"', 'space-y-8 md:space-y-12" id="memo-content-area"')

    # 5. Исправляем заголовки секций H2
    content = content.replace('class="text-6xl font-black mb-8 tracking-tight"', 'class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none"')
    content = content.replace('class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1]"', 'class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none"')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Список всех файлов
html_files = glob.glob("*.html")
for file in html_files:
    if file != "index.html":
        fix_html_layout(file)

print("\n🚀 Успех! Форма уехала вниз, поля расширились, ПК-версия снова в порядке.")
