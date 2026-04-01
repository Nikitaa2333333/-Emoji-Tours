import os
import re

def fix_css_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False

    original_content = content

    # 1. Fix the "Extra braces before media query" issue
    # This often looks like } \n } \n /* Hide... */
    content = re.sub(r'}\s*}\s*/\* Hide Mobile Navigation on Desktop \*/', r'}\n\n        /* Hide Mobile Navigation on Desktop */', content)
    
    # 2. Fix the "Nested Media Query" corruption
    # This specifically targets the case where @media max-width 1023 is inside min-width 1024
    # Pattern: #drawer-overlay, \s* @media (max-width: 1023px) { \s* #scroll-progress {
    pattern = r'#drawer-overlay,\s*@media\s*\(max-width:\s*1023px\)\s*{\s*#scroll-progress\s*{\s*display:\s*none\s*!important;\s*}\s*}'
    replacement = r'#drawer-overlay,\n            #scroll-progress {\n                display: none !important;\n            }'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 3. Final safety cleanup of any remaining nested media queries of the same type
    content = re.sub(r'@media\s*\(min-width:\s*1024px\)\s*{\s*@media\s*\(max-width:\s*1023px\)\s*{', r'@media (min-width: 1024px) {\n        @media (max-width: 1023px) {', content) # Just in case
    # Actually, let's just use a more aggressive fix for the common corruption:
    
    # If we find "display: none !important; } }" inside a media query, check if it's double closed
    content = re.sub(r'@media\s*\(max-width:\s*1023px\)\s*{\s*@media\s*\(max-width:\s*1023px\)\s*{', '@media (max-width: 1023px) {', content)

    # 4. Fix the specific Egypt/Memo corruption
    # Many files have:
    # #drawer-overlay,
    # @media (max-width: 1023px) {
    #    #scroll-progress { 
    #    display: none !important; 
    # } 
    # }
    content = re.sub(r'#drawer-overlay,\s*@media\s*\(max-width:\s*1023px\)\s*{\s*#scroll-progress\s*{\s*display:\s*none\s*!important;\s*}\s*}', 
                     '#drawer-overlay, #scroll-progress { display: none !important; }', content)

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
        if fix_css_in_file(filename):
            files_updated.append(filename)

print(f"CSS Fixed in {len(files_updated)} files.")
