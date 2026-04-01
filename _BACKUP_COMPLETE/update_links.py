import os
import re

target_dir = "."

# Регулярное выражение для поиска блока с иконками соцсетей в подвале.
# Будет искать текст после абзаца "Позвольте нам стать..." до конца блока <div class="flex gap-...">...</div>
footer_socials_pattern = re.compile(
    r'(Позвольте нам стать\s*вашим проводником в мир ярких эмоций\.\s*</p>\s*)<div class="flex gap-[46]">\s*<a href=.*?</div>',
    re.DOTALL
)

new_footer_socials = r'''<div class="flex gap-6">
                        <a href="https://max.ru/join/0haRr-rt5CMasX93mYrj_DuaLtUNy7gLfKyjXIdKFys" target="_blank"
                            class="w-8 h-8 flex items-center justify-center hover:scale-110 transition-transform group">
                            <img src="Логотип_MAX.svg" alt="MAX"
                                class="w-full h-full object-contain grayscale group-hover:grayscale-0 transition-all">
                        </a>
                        <a href="https://vk.com/emoji_tours" target="_blank"
                            class="w-8 h-8 flex items-center justify-center hover:scale-110 transition-transform group">
                            <img src="VK_Compact_Logo_(2021-present).svg.png" alt="VK"
                                class="w-full h-full object-contain grayscale group-hover:grayscale-0 transition-all">
                        </a>
                    </div>'''

# Также регулярное выражение для баннера MAX (если он есть на страницах)
max_banner_pattern = re.compile(
    r'(<!-- MAX Channel Banner -->.*?<a href=")#[^"]*(")',
    re.DOTALL
)
max_banner_link = r'https://max.ru/join/0haRr-rt5CMasX93mYrj_DuaLtUNy7gLfKyjXIdKFys'

def update_files():
    count_footer = 0
    count_banner = 0
    
    for filename in os.listdir(target_dir):
        if filename.endswith(".html"):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Обновляем подвал
            content = footer_socials_pattern.sub(r'\1' + new_footer_socials, content)
            if content != original_content:
                count_footer += 1
                
            # Обновляем баннер MAX (если есть)
            original_content_2 = content
            content = max_banner_pattern.sub(r'\1' + max_banner_link + r'\2', content)
            if content != original_content_2:
                count_banner += 1

            if content != original_content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Обновлен: {filename}")
    
    print(f"\nГотово! Обновлено подвалов в файлах: {count_footer}")
    print(f"Обновлено ссылок в баннерах MAX: {count_banner}")

if __name__ == "__main__":
    update_files()
