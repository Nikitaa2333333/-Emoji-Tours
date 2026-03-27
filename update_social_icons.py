import os

# Конфигурация
target_dir = "."
old_block = """                    <div class="flex gap-4">
                        <a href="#" class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary transition-colors">
                            <span class="material-symbols-outlined text-lg">public</span>
                        </a>
                        <a href="#" class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary transition-colors">
                            <span class="material-symbols-outlined text-lg">chat</span>
                        </a>
                    </div>"""

new_block = """                    <div class="flex gap-6">
                        <a href="#" class="w-8 h-8 flex items-center justify-center hover:scale-110 transition-transform group">
                            <img src="Логотип_MAX.svg" alt="MAX" class="w-full h-full object-contain grayscale group-hover:grayscale-0 transition-all">
                        </a>
                        <a href="#" class="w-8 h-8 flex items-center justify-center hover:scale-110 transition-transform group">
                            <img src="VK_Compact_Logo_(2021-present).svg.png" alt="VK" class="w-full h-full object-contain grayscale group-hover:grayscale-0 transition-all">
                        </a>
                    </div>"""

def update_files():
    count = 0
    for filename in os.listdir(target_dir):
        if filename.endswith(".html"):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_block in content:
                new_content = content.replace(old_block, new_block)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Обновлен: {filename}")
                count += 1
    
    print(f"\nГотово! Обновлено файлов: {count}")

if __name__ == "__main__":
    update_files()
