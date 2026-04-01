import os
import re

NEW_FOOTER = """
    <footer class="bg-[#fffcf5] w-full border-t border-black/10 pt-20 pb-12 px-8">
        <div class="max-w-7xl mx-auto flex flex-col gap-12">
            <div class="flex flex-col md:flex-row justify-between items-start gap-12">
                <div class="space-y-6 max-w-md">
                    <img src="LogoB_300x.png" alt="Emoji Tours" class="h-16">
                    <p class="text-black/60 font-['Manrope'] text-sm leading-relaxed">
                        Мы верим, что путешествия — это лучший способ познать себя и окружающий мир. Позвольте нам стать вашим проводником в мир ярких эмоций.
                    </p>
                    <div class="flex gap-4">
                        <a href="#" class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary transition-colors">
                            <span class="material-symbols-outlined text-lg">public</span>
                        </a>
                        <a href="#" class="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary transition-colors">
                            <span class="material-symbols-outlined text-lg">chat</span>
                        </a>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-12">
                    <div class="space-y-4">
                        <h4 class="font-bold text-on-surface uppercase tracking-widest text-[10px] opacity-50">Связаться с нами</h4>
                        <div class="space-y-3 text-lg">
                            <a href="tel:+79636491852" class="block font-black hover:text-primary transition-all">+7 963-649-18-52</a>
                            <a href="mailto:trohin.zh@yandex.ru" class="block text-on-surface-variant hover:text-primary transition-all text-sm">trohin.zh@yandex.ru</a>
                        </div>
                    </div>
                    
                    <div class="space-y-4">
                        <h4 class="font-bold text-on-surface uppercase tracking-widest text-[10px] opacity-50">Юридическая информация</h4>
                        <div class="text-xs text-on-surface-variant leading-relaxed">
                            Индивидуальный предприниматель <br>
                            <strong>Трохин Евгений Альбертович</strong><br>
                            ИНН 503613656680 <br> 
                            ОГРН ИП 315507400016056
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="pt-12 border-t border-black/5 flex flex-col md:flex-row justify-between items-center gap-6">
                <div class="text-black/40 font-['Manrope'] text-xs">© 2026 Emoji Tours. Путешествия с душой.</div>
                <div class="flex gap-8 text-[10px] font-bold uppercase tracking-widest text-black/40">
                    <a href="#" class="hover:text-black transition-colors">Политика конфиденциальности</a>
                    <a href="index.html" class="hover:text-black transition-colors">Все страны</a>
                </div>
            </div>
        </div>
    </footer>
"""

def unify_footer(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Заменяем весь блок <footer>...</footer>
    pattern = r'<footer[^>]*>.*?</footer>'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, NEW_FOOTER, content, flags=re.DOTALL)
        # Заменяем 2024 и другие годы на 2026 во всем файле
        new_content = re.sub(r'202[0-5]', '2026', new_content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Unified footer in: {file_path}")
    else:
        # Если футера нет, вставляем перед </body>
        if '</body>' in content:
            new_content = content.replace('</body>', NEW_FOOTER + '\n</body>')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added missing footer to: {file_path}")

def main():
    # Обновляем все HTML файлы, включая шаблоны
    files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    for file in files:
        unify_footer(file)

if __name__ == "__main__":
    main()
