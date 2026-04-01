import os
import re

def analyze_memo(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 1. H1 Overlap
    if 'leading-none' in re.search(r'<h1.*?>', content, re.DOTALL).group(0):
        issues.append("H1_OVERLAP (leading-none)")
        
    # 2. Layout Breakage (duplicated closing divs before form)
    if re.search(r'</div>\s*</div>\s*</div>\s*<!-- ═══ ФОРМА \(ШАБЛОН\) ═══ -->\s*</div>\s*</div>\s*</div>', content, re.DOTALL):
        issues.append("LAYOUT_BROKEN (double-closing-divs)")
    
    # 3. Oversized Contact H2s
    keywords = ['@', 'www.', 'rusemb', 'embassy', 'сайт:', 'е-mail:', 'посол:', 'генконсул:']
    h2_tags = re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.DOTALL)
    for h2 in h2_tags:
        text = re.sub(r'<[^>]+>', '', h2).lower()
        if any(key in text for key in keywords):
            issues.append(f"OVERSIZED_H2 ({text[:30]}...)")
            break
            
    # 4. Aside presence
    if '<aside' not in content:
        issues.append("MISSING_ASIDE")
        
    return issues

def main():
    files = [f for f in os.listdir('.') if f.startswith('memo-') and f.endswith('.html')]
    results = {}
    for f in files:
        results[f] = analyze_memo(f)
    
    print("\n=== АНАЛИЗ СОСТОЯНИЯ ПАМЯТОК ===\n")
    for f, issues in sorted(results.items()):
        status = "❌ " + ", ".join(issues) if issues else "✅ В норме"
        print(f"{f:30} {status}")

if __name__ == "__main__":
    main()
