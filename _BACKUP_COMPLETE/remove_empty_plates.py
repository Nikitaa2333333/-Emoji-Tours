import os
import re

def fix_embassy_layouts():
    pattern = re.compile(
        r'(<div class="grid grid-cols-1 md:grid-cols-2 gap-8">)\s*(<div[^>]*class="[^"]*rounded-\[2\.5rem\][^"]*">.*?</div>)\s*(<div[^>]*class="relative overflow-hidden rounded-\[2\.5rem\] bg-primary/10 flex items-center justify-center group">.*?account_balance.*?</div>)',
        re.DOTALL
    )
    
    files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
    
    for filename in files:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        
        # Находим все такие сетки
        matches = list(pattern.finditer(content))
        if not matches:
            continue
            
        for match in reversed(matches):
            full_match = match.group(0)
            grid_start = match.group(1)
            text_block = match.group(2)
            # icon_block = match.group(3) # Мы его удаляем
            
            # 1. Меняем сетку на 1 колонку
            new_grid = '<div class="grid grid-cols-1 gap-8">'
            
            # 2. Убираем my-8 у внутреннего блока, чтобы не было лишних отступов, раз теперь это одна колонка
            # и растягиваем его (хотя он и так w-full обычно)
            fixed_text_block = text_block.replace('my-8', 'mt-4 mb-8')
            
            replacement = f"{new_grid}\n                            {fixed_text_block}\n                        </div>"
            
            new_content = new_content[:match.start()] + replacement + new_content[match.end():]
            
        if new_content != content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Исправлено в {filename}")

if __name__ == '__main__':
    fix_embassy_layouts()
