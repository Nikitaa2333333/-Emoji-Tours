import os
import re

def normalize_text(text):
    # Rule 9: NO CAPS. If text is mostly upper, but contains space and letters, title case it.
    if text.isupper() and len(text) > 3:
        return text.capitalize()
    return text

def process_file(file_path):
    print(f"Processing {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Container Padding
    # Find the main container (usually the one with max-w-7xl and px-8)
    content = content.replace('px-8 relative flex flex-col', 'px-6 md:px-8 relative flex flex-col')
    content = content.replace('px-8 relative flex flex-row', 'px-6 md:px-8 relative flex flex-row')
    
    # 2. Update Header Font Sizes (Responsive)
    # H1: text-7xl md:text-9xl -> text-5xl md:text-7xl lg:text-9xl
    content = re.sub(
        r'class="([^"]*?)text-7xl md:text-9xl([^"]*?)"',
        r'class="\1text-5xl md:text-7xl lg:text-9xl\2"',
        content
    )
    # H2: text-6xl -> text-3xl md:text-5xl lg:text-6xl
    content = re.sub(
        r'class="([^"]*?)text-6xl([^"]*?)"',
        r'class="\1text-3xl md:text-5xl lg:text-6xl\2"',
        content
    )

    # 3. Normalized Title Case for H1/H2 (Rule 9)
    def fix_caps(match):
        tag_open = match.group(1)
        text = match.group(2)
        tag_close = match.group(3)
        if text.isupper():
            text = text.capitalize()
        return f"{tag_open}{text}{tag_close}"

    content = re.sub(r'<(h[12][^>]*?)>(.*?)</(h[12])>', fix_caps, content, flags=re.IGNORECASE)

    # 4. Standardize Navigation Trigger CSS
    nav_css = """
/* --- Premium Navigation Trigger (Mobile Only) --- */
#nav-navigation-trigger {
    position: fixed;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    color: #fff;
    padding: 14px 28px;
    border-radius: 100px;
    display: flex;
    align-items: center;
    gap: 12px;
    border: 1px solid rgba(255, 252, 245, 0.1);
    cursor: pointer;
    font-family: 'Manrope', sans-serif;
    font-size: 15px;
    font-weight: 700;
    z-index: 9999;
    box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
@media (min-width: 1024px) { #nav-navigation-trigger { display: none !important; } }
#nav-navigation-trigger:active { transform: translateX(-50%) scale(0.95); }
#nav-navigation-trigger svg { transition: transform 0.5s; }
#nav-navigation-trigger:hover svg { transform: rotate(90deg); }

#nav-bottom-sheet {
    position: fixed;
    bottom: -110%;
    left: 0;
    width: 100%;
    background: #fffcf5;
    border-radius: 3rem 3rem 0 0;
    padding: 2.5rem 1.5rem;
    z-index: 10001;
    transition: bottom 0.6s cubic-bezier(0.32, 0.72, 0, 1);
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 -20px 50px rgba(0,0,0,0.15);
}
#nav-bottom-sheet.open { bottom: 0; }
.sheet-handle { width: 40px; height: 4px; background: #e5e0d4; border-radius: 10px; margin: 0 auto 1.5rem; }
.sheet-title { font-size: 11px; color: #8c887d; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 2rem; text-align: center; font-weight: 800; }
#nav-links-list { display: flex; flex-direction: column; gap: 0.6rem; }
.nav-link-item { display: flex; justify-content: space-between; align-items: center; padding: 1.2rem 1rem; color: #1a1a1a; text-decoration: none; font-size: 1.1rem; font-weight: 700; background: rgba(0,0,0,0.03); border-radius: 1rem; transition: all 0.2s; }
.nav-link-item:active { background: #f5e2a1; transform: scale(0.98); }
#nav-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); opacity: 0; visibility: hidden; z-index: 10000; transition: all 0.4s; backdrop-filter: blur(6px); }
#nav-overlay.visible { opacity: 1; visibility: visible; }
"""
    # Replace old custom nav styles if they exist, or inject into <style>
    if '<style>' in content:
        # Check if we already have our nav-navigation-trigger block
        if '#nav-navigation-trigger' not in content:
            content = content.replace('</style>', nav_css + '\n</style>')
        else:
            # Update existing block
            content = re.sub(r'/\* --- Premium Navigation Trigger .*? \*/.*?#nav-overlay\.visible \{.*?\}', nav_css, content, flags=re.DOTALL)
            # Also handle the manual one if there wasn't a comment
            if '#nav-navigation-trigger {' in content and '/* --- Premium Navigation Trigger' not in content:
                 content = re.sub(r'#nav-navigation-trigger \{.*?#nav-overlay\.visible \{.*?\}', nav_css, content, flags=re.DOTALL)

    # 5. Standardize Navigation Component HTML
    nav_html = """
    <!-- Premium Navigation Component (Mobile) -->
    <button id="nav-navigation-trigger">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
        <span>Навигация</span>
    </button>
    <div id="nav-overlay"></div>
    <div id="nav-bottom-sheet">
        <div class="sheet-handle"></div>
        <div class="sheet-title">СОДЕРЖАНИЕ</div>
        <div id="nav-links-list"></div>
    </div>
"""
    # Navigation Script
    nav_script = """
    <script>
    document.addEventListener('DOMContentLoaded', () => {
        const trigger = document.getElementById('nav-navigation-trigger');
        const sheet = document.getElementById('nav-bottom-sheet');
        const overlay = document.getElementById('nav-overlay');
        const list = document.getElementById('nav-links-list');

        if (!trigger || !sheet || !overlay || !list) return;

        // Generate links from H2 or H1
        const headings = Array.from(document.querySelectorAll('h2')).filter(h => h.innerText.trim().length > 0);
        
        function generateLinks(elements) {
            list.innerHTML = '';
            elements.forEach((h, index) => {
                if (!h.id) h.id = 'section-' + index;
                const link = document.createElement('a');
                link.className = 'nav-link-item';
                link.href = '#' + h.id;
                link.innerHTML = `<span>${h.innerText.trim()}</span><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>`;
                
                link.onclick = (e) => {
                    e.preventDefault();
                    const target = document.getElementById(h.id);
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
            const h1s = Array.from(document.querySelectorAll('h1'));
            if (h1s.length > 0) generateLinks(h1s);
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

    if '</body>' in content:
        # Check if component already exists
        if 'nav-navigation-trigger' not in content:
             content = content.replace('</body>', nav_html + '\n' + nav_script + '\n</body>')
        else:
             # Update script and html
             # First, remove old script if it exists
             content = re.sub(r'<script>\s*document\.addEventListener\(\'DOMContentLoaded\', \(\) => \{\s*const trigger = document\.getElementById\(\'nav-navigation-trigger\'\);.*?\}\);\s*</script>', nav_script, content, flags=re.DOTALL)
             # Update HTML trigger button contents
             content = re.sub(r'<button id="nav-navigation-trigger">.*?</button>', '<button id="nav-navigation-trigger">\n        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>\n        <span>Навигация</span>\n    </button>', content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Target files
files = [f for f in os.listdir('.') if f.endswith('.html') and f not in ['template.html', 'template_memo.html', 'dashboard.html']]
for f in files:
    process_file(f)

# Also update templates
process_file('template.html')
process_file('template_memo.html')
