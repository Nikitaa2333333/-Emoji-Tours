import os
import re

def generate_privacy():
    with open('pol', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replaces
    content = content.replace('ИП Мороз Станислав Владимирович', 'ИП Трохин Евгений Альбертович')
    content = content.replace('river-loft.ru', 'emojitours.ru')
    content = content.replace('info@river-loft.ru', 'trohin.zh@yandex.ru')
    content = content.replace('info@emojitours.ru', 'trohin.zh@yandex.ru')
    content = content.replace('Made on\t\tTilda', '')

    # Basic cleanup
    lines = content.split('\n')
    formatted_html = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # All lines as plain paragraphs, maintaining lists if present
        if line.startswith('–'): # Lists
            formatted_html += f'            <p class="pl-5 mb-2 opacity-80">{line}</p>\n'
        else:
            formatted_html += f'            <p class="mb-4 leading-relaxed">{line}</p>\n'

    template = """<!DOCTYPE html>
<html class="light" lang="ru">

<head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <title>Политика конфиденциальности — Эмоджи Турс</title>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap"
        rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
        rel="stylesheet" />
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <script id="tailwind-config">
        tailwind.config = {{
            darkMode: "class",
            theme: {{
                extend: {{
                    colors: {{
                        "background": "#fffcf5",
                        "surface": "#fffcf5",
                        "on-surface": "#000000",
                        "primary": "#f5e2a1",
                        "on-primary": "#000000",
                        "on-surface-variant": "#000000",
                        "surface-container-low": "#fffcf5",
                        "surface-container-high": "#fffaf0",
                        "primary-container": "#f5e2a1",
                        "on-primary-container": "#000000",
                    }},
                    fontFamily: {{
                        "headline": ["Manrope"],
                        "body": ["Manrope"]
                    }},
                    borderRadius: {{
                        "DEFAULT": "1rem",
                        "lg": "2rem",
                        "xl": "3rem",
                        "full": "9999px"
                    }},
                }},
            }},
        }}
    </script>
    <style>
        body {{ font-family: 'Manrope', sans-serif; scroll-behavior: smooth; }}
        .policy-content p {{ color: #1a1a1a; }}
    </style>
</head>

<body class="bg-background text-black overflow-x-hidden">
    <nav class="fixed top-0 w-full z-50 bg-[#fffcf5]/90 backdrop-blur-md border-b border-black/5 py-4">
        <div class="max-w-7xl mx-auto flex justify-between items-center px-4 md:px-8">
            <a href="index.html" class="flex-shrink-0">
                <img src="images/logo.png" alt="Эмоджи Турс" class="h-6 md:h-8">
            </a>
            <a href="index.html" class="flex items-center gap-1.5 font-bold text-[10px] md:text-xs hover:opacity-70 transition-opacity tracking-tight">
                <span class="material-symbols-outlined text-lg">arrow_back</span>
                <span>На главную</span>
            </a>
        </div>
    </nav>

    <header class="pt-24 pb-10 bg-primary px-4 md:px-8 text-center relative overflow-hidden text-black">
        <div class="max-w-xl mx-auto">
            <h1 class="text-xl md:text-3xl lg:text-4xl font-black tracking-tight leading-tight mb-2 break-words">
                Политика конфиденциальности
            </h1>
            <p class="text-[10px] md:text-xs font-bold opacity-40 tracking-tight">Эмоджи Турс — Путешествия с душой</p>
        </div>
    </header>

    <main class="py-10 md:py-14 px-4 md:px-8">
        <div class="max-w-4xl mx-auto bg-white rounded-[2rem] p-6 md:p-12 shadow-2xl shadow-black/[0.02] policy-content text-xs md:text-base">
            <p class="text-[9px] md:text-[10px] font-black text-gray-300 mb-8 tracking-tight border-b border-black/5 pb-4">
                Актуальная версия от 06 апреля 2026 г.
            </p>
            {content_body}
        </div>
    </main>

    <footer class="bg-surface-container-low w-full border-t border-black/5 pt-16 pb-10 px-4 md:px-8">
        <div class="max-w-7xl mx-auto flex flex-col gap-12 md:gap-16">
            <div class="flex flex-col md:flex-row justify-between items-start gap-12">
                <div class="space-y-6 max-w-sm text-center md:text-left mx-auto md:mx-0">
                    <img src="images/logo.png" alt="Emoji Tours" class="h-10 md:h-12 mx-auto md:mx-0">
                    <p class="text-black font-medium text-xs leading-relaxed opacity-60">Мы верим, что путешествия — это лучший способ познать себя и окружающий мир.</p>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-10 md:gap-16 w-full md:w-auto text-center md:text-left">
                    <div class="space-y-4">
                        <h4 class="font-bold text-black text-xs tracking-tight opacity-40">Контакты</h4>
                        <div class="space-y-2">
                            <a href="tel:+79636491852" class="block font-black text-black hover:text-primary transition-colors text-sm md:text-base">+7 963-649-18-52</a>
                            <a href="mailto:trohin.zh@yandex.ru" class="block text-black hover:text-black transition-colors text-xs font-medium">trohin.zh@yandex.ru</a>
                        </div>
                    </div>
                    <div class="space-y-4">
                        <h4 class="font-bold text-black text-xs tracking-tight opacity-40">Реквизиты</h4>
                        <div class="text-[10px] md:text-xs text-black leading-relaxed font-medium">
                            ИП Трохин Евгений Альбертович<br>
                            ИНН 503613656680<br>
                            ОГРН ИП 315507400016056
                        </div>
                    </div>
                </div>
            </div>
            <div class="pt-8 border-t border-black/5 flex flex-col md:flex-row justify-between items-center gap-6">
                <div class="text-black font-bold text-[10px] md:text-[11px] text-center md:text-left opacity-30 tracking-tight">© 2026 Emoji Tours. Путешествия с душой.</div>
            </div>
        </div>
    </footer>
</body>
</html>"""

    full_html = template.format(content_body=formatted_html)
    
    with open('privacy.html', 'w', encoding='utf-8') as f:
        f.write(full_html)
    print("privacy.html successfully generated without CAPS!")

if __name__ == "__main__":
    generate_privacy()
