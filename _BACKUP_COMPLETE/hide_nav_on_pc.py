import os
import re

def fix_nav_visibility(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False
    
    # CSS rule to hide the navigation trigger on desktop
    hide_css = """
/* Hide Navigation on Desktop (Fix for user) */
@media (min-width: 1024px) { 
    #nav-navigation-trigger, 
    #nav-navigation-container, 
    #nav-overlay, 
    #nav-bottom-sheet, 
    #mobile-toc-button { 
        display: none !important; 
    } 
}
"""
    
    # 1. Check if we already have the hide rule
    if "/* Hide Navigation on Desktop (Fix for user) */" in content:
        return False

    # 2. Look for the style block containing #nav-navigation-trigger or #mobile-toc-button
    if "#nav-navigation-trigger" in content or "#mobile-toc-button" in content:
        if "</style>" in content:
            # We insert it right before the closing </style> tag that follows the trigger definition
            parts = content.split('</style>')
            found = False
            for i, part in enumerate(parts):
                if "#nav-navigation-trigger" in part or "#mobile-toc-button" in part:
                    parts[i] = part + hide_css
                    found = True
                    break
            
            if found:
                content = "</style>".join(parts)
                changed = True

    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = [f for f in os.listdir('.') if f.endswith('.html')]
    updated_count = 0
    for f in files:
        if fix_nav_visibility(f):
            print(f"✅ Fixed: {f}")
            updated_count += 1
        else:
            pass # print(f"  - No changes: {f}")

    print(f"\nDone! Updated {updated_count} files.")

if __name__ == "__main__":
    main()
