import os
import glob
import re

def repair_file(path):
    print(f"Исправление {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # --- 1. Исправляем битый JS (Sync Sidebar block) ---
    # Этот блок был поврежден в некоторых файлах
    bad_js_pattern = re.compile(r'// Sync Sidebar to Bottom Sheet\s*\);\s*\}, 300\);\s*.*?dst\.appendChild\(cln\);\s*\}\);\s*\}\s*\}\s*\}', re.DOTALL)
    
    clean_toggle = """// Sync Sidebar to Bottom Sheet
        function toggleTOC() {
            const drw = document.getElementById('mobile-drawer');
            const ovl = document.getElementById('drawer-overlay');
            if(!drw || !ovl) return;
            const isOpen = drw.classList.toggle('open');
            ovl.classList.toggle('visible');
            document.body.style.overflow = isOpen ? 'hidden' : '';

            if (isOpen) {
                const src = document.getElementById('quick-links');
                const dst = document.getElementById('mobile-nav-list');
                if (src && dst) {
                    dst.innerHTML = '';
                    src.querySelectorAll('.nav-link').forEach(l => {
                        const cln = l.cloneNode(true);
                        cln.className = 'drawer-link';
                        cln.onclick = (e) => {
                           toggleTOC();
                           setTimeout(() => {
                               const targetId = cln.getAttribute('href');
                               if(targetId) {
                                   const target = document.querySelector(targetId);
                                   if(target) target.scrollIntoView({behavior: 'smooth'});
                               }
                           }, 300);
                        };
                        dst.appendChild(cln);
                    });
                }
            }
        }"""
    
    if '// Sync Sidebar' in content:
         # Ищем специфическую поломку "); }, 300);"
         if ');' in content.split('// Sync Sidebar')[-1][:100]:
              content = re.sub(r'// Sync Sidebar to Bottom Sheet.*?function toggleTOC\(\) \{', '// Sync Sidebar to Bottom Sheet\n        function toggleTOC() {', content, flags=re.DOTALL) # пробуем исправить если затерто начало
              content = bad_js_pattern.sub(clean_toggle, content)
              # Если regex не сработал полностью, делаем грубую замену блока
              if ');' in content.split('// Sync Sidebar')[-1][:100]:
                   start_idx = content.find('// Sync Sidebar to Bottom Sheet')
                   end_idx = content.find('</script>', start_idx)
                   if start_idx != -1 and end_idx != -1:
                        content = content[:start_idx] + clean_toggle + "\n    " + content[end_idx:]

    # --- 2. Глобальное скрытие всех кнопок навигации на ПК (Desktop) ---
    hide_rule = """
/* Hide Mobile Navigation on Desktop */
@media (min-width: 1024px) { 
    #nav-navigation-trigger, 
    #nav-navigation-container, 
    #nav-overlay, 
    #nav-bottom-sheet, 
    #mobile-toc-button,
    #mobile-drawer,
    #drawer-overlay,
    #scroll-progress { 
        display: none !important; 
    } 
}
"""
    # Удаляем старые/дублирующиеся правила
    content = re.sub(r'/\* Hide Navigation on Desktop .*?\}', '', content, flags=re.DOTALL)
    content = re.sub(r'/\* Hide Mobile Navigation on Desktop .*?\}', '', content, flags=re.DOTALL)
    
    # Вставляем новое правило в первый блок <style>
    if '</style>' in content:
        pos = content.find('</style>')
        content = content[:pos] + hide_rule + content[pos:]

    # --- 3. Исправляем медиа-запрос в head (Missing Opening Brace) ---
    if '#mobile-toc-button {' in content and '@media (max-width: 1023px)' not in content:
        content = content.replace('#scroll-progress {', '@media (max-width: 1023px) {\n        #scroll-progress {')
        if '@media (max-width: 1023px)' not in content:
             content = content.replace('#mobile-toc-button {', '@media (max-width: 1023px) {\n        #mobile-toc-button {')

    # --- 4. Добавляем медиа-запрос к стилям плашки внизу ---
    if '/* Кнопка-плашка */' in content and '@media (max-width: 1023px)' not in content.split('/* Кнопка-плашка */')[-1]:
         content = content.replace('/* Кнопка-плашка */', '@media (max-width: 1023px) {\n/* Кнопка-плашка */')
         # Ищем </style> после этого блока
         style_pos = content.find('</style>', content.find('/* Кнопка-плашка */'))
         if style_pos != -1:
              content = content[:style_pos] + '}\n' + content[style_pos:]

    # --- 5. Классы Tailwind для надежности ---
    content = content.replace('id="nav-navigation-container"', 'id="nav-navigation-container" class="lg:hidden"')
    content = content.replace('id="mobile-toc-button"', 'id="mobile-toc-button" class="lg:hidden"')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Обрабатываем все HTML файлы
files = glob.glob("*.html")
for f in files:
    if f == "index.html": continue
    try:
        repair_file(f)
    except Exception as e:
        print(f"Ошибка в {f}: {e}")

print("\n✨ Готово! Навигация полностью исправлена и скрыта на ПК.")
