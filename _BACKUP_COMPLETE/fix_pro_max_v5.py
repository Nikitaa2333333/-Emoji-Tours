import os
import re

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False

    original_content = content

    # --- 1. CSS FIXES (Syntax errors & Overflow) ---
    # Fix double @media queries (bug in some files)
    content = re.sub(r'@media\s*\(max-width:\s*1023px\)\s*\{\s*@media\s*\(max-width:\s*1023px\)\s*\{', '@media (max-width: 1023px) {', content)
    
    # Ensure overflow-x: hidden on body and html
    if 'body' in content and 'overflow-x: hidden' not in content:
        content = content.replace('body {', 'body { overflow-x: hidden; width: 100%;')
        content = content.replace('body  {', 'body  { overflow-x: hidden; width: 100%;')
    if 'html' in content and 'overflow-x: hidden' not in content:
        content = content.replace('html {', 'html { overflow-x: hidden;')
        content = content.replace('html  {', 'html  { overflow-x: hidden;')

    # --- 2. IMAGE RESPONSIVENESS (Prevent cropping) ---
    # Replace h-[500px], h-[400px], h-72, h-[55vh] with h-auto md:h-[...]
    # This prevents the "cut off" effect on mobile by allowing aspect-ratio scaling
    patterns = [r'h-\[500px\]', r'h-\[400px\]', r'h-\[300px\]', r'h-72', r'h-\[55vh\]']
    for p in patterns:
        content = re.sub(f'class="([^"]*)\\b({p})\\b([^"]*)"', r'class="\1h-auto md:\2\3"', content)
        content = re.sub(f'class=\'([^\']*)\\b({p})\\b([^\']*)\'', r'class=\'\1h-auto md:\2\3\'', content)
    
    # Ensure object-cover images are centered
    if 'object-cover' in content and 'object-center' not in content:
        content = content.replace('object-cover', 'object-cover object-center')

    # --- 3. BAGGAGE SECTION (Собирая багаж) ---
    if "Собирая багаж" in content:
        # 3a. Ensure it's an H2 with ID
        has_correct_h2 = 'id="section-sobiraya-bagazh"' in content
        if not has_correct_h2:
            # Look for it as any tag or just bold text
            content = re.sub(
                r'<(p|div|h1|h2|h3)[^>]*>\s*Собирая багаж\s*</\1>', 
                r'<h2 id="section-sobiraya-bagazh" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">Собирая багаж</h2>', 
                content
            )
            # If it's a bold text without tags
            content = re.sub(
                r'<strong>\s*Собирая багаж\s*</strong>', 
                r'<h2 id="section-sobiraya-bagazh" class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-[1.1] md:leading-none">Собирая багаж</h2>', 
                content
            )

        # 3b. Ensure link in menu (#quick-links)
        if 'id="quick-links"' in content and 'href="#section-sobiraya-bagazh"' not in content:
            link_html = '                            <a href="#section-sobiraya-bagazh" class="nav-link">Собирая багаж</a>'
            
            # Smart insertion: after "Перед отъездом" or "Дети" or at start
            if '#section-pered-otezdom' in content:
                content = re.sub(
                    r'(<a href="#section-pered-otezdom"[^>]*>.*?</a>)', 
                    r'\1\n' + link_html, 
                    content
                )
            else:
                content = content.replace(
                    '<nav id="quick-links" class="flex flex-col border-l border-black/5">',
                    '<nav id="quick-links" class="flex flex-col border-l border-black/5">\n' + link_html
                )

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Execution
path = os.getcwd()
files_updated = []
for filename in os.listdir(path):
    if filename.endswith('.html'):
        if process_file(filename):
            files_updated.append(filename)

print(f"DONE! Updated {len(files_updated)} files.")
for f in files_updated:
    print(f" - {f}")
