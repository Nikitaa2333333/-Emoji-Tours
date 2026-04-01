import os
import re

# Код компонента навигации
NAVIGATION_HTML = """
<!-- Навигационная плашка -->
<div id="nav-navigation-container" class="lg:hidden">
    <button id="nav-navigation-trigger">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-compass"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>
        <span>Навигация</span>
    </button>

    <div id="nav-bottom-sheet">
        <div class="sheet-handle"></div>
        <div class="sheet-title">Навигация</div>
        <div id="nav-links-list">
            <!-- Сюда JS добавит ссылки из h2 -->
        </div>
    </div>
    <div id="nav-overlay"></div>
</div>

<style>
@media (max-width: 1023px) {
    /* Кнопка-плашка */
    #nav-navigation-trigger {
        position: fixed;
        bottom: 3rem;
        left: 50%;
        transform: translateX(-50%);
        background: #000;
        color: #fff;
        padding: 14px 28px;
        border-radius: 100px;
        display: flex;
        align-items: center;
        gap: 12px;
        border: none;
        cursor: pointer;
        font-family: 'Manrope', sans-serif;
        font-size: 16px;
        font-weight: 600;
        z-index: 999;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }

    #nav-navigation-trigger:hover { 
        transform: translateX(-50%) translateY(-5px) scale(1.05);
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    }

    #nav-navigation-trigger svg { transition: transform 0.5s; }
    #nav-navigation-trigger:hover svg { transform: rotate(45deg); }

    /* Шторка (Bottom Sheet) */
    #nav-bottom-sheet {
        position: fixed;
        bottom: -110%;
        left: 0;
        width: 100%;
        background: #fffcf5;
        border-radius: 3.5rem 3.5rem 0 0;
        padding: 2.5rem 2rem;
        z-index: 10001;
        transition: bottom 0.6s cubic-bezier(0.32, 0.72, 0, 1);
        max-height: 85vh;
        overflow-y: auto;
        box-shadow: 0 -20px 50px rgba(0,0,0,0.15);
    }

    #nav-bottom-sheet.open { bottom: 0; }

    .sheet-handle {
        width: 50px;
        height: 5px;
        background: #e5e0d4;
        border-radius: 10px;
        margin: 0 auto 2rem;
    }

    .sheet-title {
        font-size: 13px;
        color: #8c887d;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 600;
    }

    #nav-links-list { 
        display: flex; 
        flex-direction: column; 
        gap: 0.8rem;
        max-width: 600px;
        margin: 0 auto;
    }

    .nav-link-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 1.2rem;
        color: #1a1a1a;
        text-decoration: none;
        font-size: 1.2rem;
        font-weight: 700;
        background: rgba(0,0,0,0.02);
        border-radius: 1.2rem;
        transition: all 0.2s;
    }

    .nav-link-item:hover { 
        background: #f5e2a1; 
        transform: translateX(5px);
    }

    .nav-link-item svg { opacity: 0.3; transition: 0.2s; }
    .nav-link-item:hover svg { opacity: 1; transform: translateX(5px); }

    /* Оверлей */
    #nav-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.5);
        opacity: 0; visibility: hidden;
        z-index: 10000;
        transition: all 0.4s;
        backdrop-filter: blur(8px);
    }

    #nav-overlay.visible { opacity: 1; visibility: visible; }
}
</style>


<script>
document.addEventListener('DOMContentLoaded', () => {
    const trigger = document.getElementById('nav-navigation-trigger');
    const sheet = document.getElementById('nav-bottom-sheet');
    const overlay = document.getElementById('nav-overlay');
    const list = document.getElementById('nav-links-list');

    // Находим все H2 (регионы)
    const headings = document.querySelectorAll('h2');
    
    function generateLinks(elements) {
        list.innerHTML = ''; // Очистка перед генерацией
        elements.forEach((h, index) => {
            if (!h.id) h.id = 'section-' + index;
            const link = document.createElement('a');
            link.className = 'nav-link-item';
            link.href = '#' + h.id;
            
            // Чистим текст заголовка
            const titleText = h.innerText.trim();
            
            link.innerHTML = `<span>${titleText}</span><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>`;
            
            link.onclick = (e) => {
                e.preventDefault();
                const target = document.getElementById(h.id);
                // Плавный скролл с отступом
                const yOffset = -100; 
                const y = target.getBoundingClientRect().top + window.pageYOffset + yOffset;
                window.scrollTo({top: y, behavior: 'smooth'});
                toggleMenu();
            };
            list.appendChild(link);
        });
    }

    if (headings.length > 0) {
        generateLinks(headings);
    } else {
        // Если H2 нет (например в памятке), ищем H1
        const titleLink = document.querySelectorAll('h1');
        if (titleLink.length > 0) generateLinks(titleLink);
    }

    function toggleMenu() {
        const isOpen = sheet.classList.toggle('open');
        overlay.classList.toggle('visible');
        document.body.style.overflow = isOpen ? 'hidden' : '';
    }

    trigger.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', toggleMenu);
});
</script>
"""

def update_html_files():
    root_dir = os.getcwd()
    excluded_files = ['template.html', 'index.html']
    
    count = 0
    for filename in os.listdir(root_dir):
        if filename.endswith('.html') and filename not in excluded_files:
            file_path = os.path.join(root_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # --- 1. ВЫЧИЩАЕМ СТАРУЮ НАВИГАЦИЮ ---
            
            # Удаляем старые HTML элементы по ID
            content = re.sub(r'<div id="drawer-overlay".*?</div>', '', content, flags=re.DOTALL)
            content = re.sub(r'<div id="mobile-drawer".*?</div>\s*</div>', '', content, flags=re.DOTALL) # учитываем структуру вложенности
            content = re.sub(r'<button id="mobile-toc-button".*?</button>', '', content, flags=re.DOTALL)
            
            # Если не сработало регуляркой выше (разная вложенность), удаляем точечно
            content = content.replace('<div id="drawer-overlay" onclick="toggleTOC()"></div>', '')
            
            # Удаляем блок стилей "Premium Mobile Navigation Pro Max"
            content = re.sub(r'/\* --- Premium Mobile Navigation Pro Max.*? \*/.*?\s*@media \(max-width: 1023px\) \{.*?\}', '', content, flags=re.DOTALL)
            
            # Удаляем функцию toggleTOC из скриптов
            content = re.sub(r'function toggleTOC\(\) \{.*?\}', '', content, flags=re.DOTALL)
            
            # Удаляем старую версию новой навигации если уже запускали
            if 'nav-navigation-container' in content:
                pattern = r'<!-- Навигационная плашка -->.*?</div>\s*<style>.*?</style>\s*<script>.*?</script>'
                content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            # --- 2. ВСТАВЛЯЕМ НОВУЮ НАВИГАЦИЮ ---
            if '</body>' in content:
                new_content = content.replace('</body>', NAVIGATION_HTML + '\n</body>')
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Обновлен: {filename}")
                count += 1
    
    print(f"\nИтого очищено и обновлено файлов: {count}")

if __name__ == "__main__":
    update_html_files()
