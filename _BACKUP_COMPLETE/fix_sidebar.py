import os
import re

# Новые стили для содержания (с прокруткой и правильной высотой)
NEW_CSS = """
        /* Исправление для содержания */
        #quick-links {
            max-height: calc(100vh - 220px); /* Ограничиваем высоту */
            overflow-y: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        #quick-links::-webkit-scrollbar {
            display: none;
        }

        .nav-link {
            display: block;
            padding: 0.6rem 1.5rem;
            border-left: 2px solid transparent;
            font-size: 0.85rem;
            line-height: 1.3;
            color: #4b4b4b;
            transition: all 0.2s ease;
        }

        .nav-link:hover {
            color: #000;
            background: rgba(245, 226, 161, 0.1);
        }

        .nav-link.active {
            color: #000;
            font-weight: 700;
            border-left-color: #f5e2a1;
            background: rgba(245, 226, 161, 0.2);
        }
"""

# Новая структура сайдбара
NEW_SIDEBAR = """
            <!-- ═══ SIDEBAR NAVIGATION (LEFT, STICKY) ═══ -->
            <aside class="hidden lg:block w-64 pt-20">
                <div class="sticky top-24 h-fit max-h-screen pb-10">
                    <div>
                        <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-black/40 mb-6 px-6">Содержание</p>       
                        <nav id="quick-links" class="flex flex-col border-l border-black/5">
                             <!-- Сюда вставим ссылки скриптом -->
                        </nav>
                    </div>
                </div>
            </aside>
"""

# Улучшенный JS
NEW_JS = """
        // ScrollSpy: подсветка активного пункта в меню при скролле
        const sections = document.querySelectorAll('h2[id]');
        const navLinks = document.querySelectorAll('.nav-link');

        window.addEventListener('scroll', () => {
            let current = "";
            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                if (pageYOffset >= (sectionTop - 150)) {
                    current = section.getAttribute('id');
                }
            });

            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === "#" + current) {
                    link.classList.add('active');
                    
                    const parent = document.getElementById('quick-links');
                    if (parent) {
                        const linkTop = link.offsetTop;
                        const parentHeight = parent.offsetHeight;
                        const parentScroll = parent.scrollTop;
                        
                        if (linkTop > (parentScroll + parentHeight - 50) || linkTop < parentScroll) {
                            parent.scrollTo({
                                top: linkTop - 100,
                                behavior: 'smooth'
                            });
                        }
                    }
                }
            });
        });
"""

def fix_file(filepath):
    print(f"Обработка: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Заменяем CSS
    css_pattern = r'\.nav-link\s*\{.*?\}\s*\.nav-link\.active\s*\{.*?\}'
    if re.search(css_pattern, content, flags=re.DOTALL):
        content = re.sub(css_pattern, NEW_CSS.strip(), content, flags=re.DOTALL)

    # 2. Заменяем Sidebar
    sidebar_pattern = r'(<!-- ═══ SIDEBAR NAVIGATION.*?-->.*?<aside.*?>).*?(</aside>)'
    if re.search(sidebar_pattern, content, flags=re.DOTALL):
        content = re.sub(sidebar_pattern, NEW_SIDEBAR.strip(), content, flags=re.DOTALL)

    # 3. Заменяем ScrollSpy JS
    js_pattern = r'// ScrollSpy: подсветка активного пункта.*?navLinks\.forEach\(link => \{.*?\}\);\s*\}\);'
    if re.search(js_pattern, content, flags=re.DOTALL):
        content = re.sub(js_pattern, NEW_JS.strip(), content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Обрабатываем template.html и все html файлы
for filename in os.listdir('.'):
    if filename.endswith('.html'):
        try:
            fix_file(filename)
        except Exception as e:
            print(f"Ошибка в {filename}: {e}")

print("\nГотово! Все страницы обновлены.")
