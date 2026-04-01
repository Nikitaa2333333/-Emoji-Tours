import os
import glob
import re

def fix_memo_lists(file_path):
    print(f"Обработка {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Заменяем старый золотой #f5d042 на новый песочный #f5e2a1
    # И меняем цвет тени, чтобы она соответствовала новому оттенку
    content = content.replace("bg-[#f5d042]", "bg-[#f5e2a1]")
    content = content.replace("rgba(245,208,66,0.4)", "rgba(245,226,161,0.5)")
    
    # На всякий случай ищем еще bg-primary, если где-то остался
    content = content.replace("bg-primary", "bg-[#f5e2a1]")

    # 2. Если в файлах еще нет структуры чекбоксов, создаем её (из обычных списков)
    list_pattern = r'(<p[^>]*>)[\s\n]*([•\-\–\—])[\s\n]*(.*?)(</p>)'
    
    def list_replacer(match):
        text = match.group(3).strip()
        if not text or len(text) < 2: return match.group(0)
        
        return f"""
<div class="group flex items-start gap-5 mb-6 transition-all pl-2">
    <div class="mt-1 flex-shrink-0 w-8 h-8 rounded-full bg-[#f5e2a1] flex items-center justify-center shadow-[0_4px_15px_rgba(245,226,161,0.5)] border-2 border-white transition-all">
        <span class="material-symbols-outlined text-[18px] font-black text-black">check</span>
    </div>
    <p class="text-lg md:text-xl leading-relaxed text-black font-normal flex-1 pt-1">
        {text}
    </p>
</div>"""

    # Применяем только к тем строкам, которые еще не обернуты в div.group
    # Чтобы не плодить вложенность, сначала проверим на отсутствие div перед p
    content = re.sub(list_pattern, list_replacer, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    path = "."
    files = glob.glob(os.path.join(path, "memo-*.html"))
    if os.path.exists(os.path.join(path, "template_memo.html")):
        files.append(os.path.join(path, "template_memo.html"))
        
    for f in files:
        fix_memo_lists(f)
        
    print("\n✅ ЦВЕТА ОБНОВЛЕНЫ НА ПЕСОЧНЫЙ (#F5E2A1)!")
