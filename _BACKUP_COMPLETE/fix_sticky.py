import os
import re

def fix_css_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False

    original_content = content

    # 1. Remove sticky-breaking styles from body and html
    # This was previously: body { ... overflow-x: hidden; width: 100%; }
    # Or in many variations. We'll use regex to find and clean body/html blocks
    
    body_pattern = r'(body\s*\{[^}]*)overflow-x:\s*hidden;\s*width:\s*100%;\s*'
    content = re.sub(body_pattern, r'\1', content)
    
    html_pattern = r'(html\s*\{[^}]*)overflow-x:\s*hidden;\s*'
    content = re.sub(html_pattern, r'\1', content)
    
    # Clean up double spaces or semi-colons left over
    content = content.replace('; ;', ';')
    content = content.replace('{ ;', '{')
    content = content.replace('  ', ' ')

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

print(f"Sticky/Fixed behavior fixed in {len(files_updated)} files.")
