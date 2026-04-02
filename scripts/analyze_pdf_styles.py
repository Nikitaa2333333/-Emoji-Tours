import pdfplumber
from collections import Counter
import os

pdf_path = r"c:\Users\User\Downloads\tilda dododo\Памятка туриста  Египет.pdf"
output_path = r"c:\Users\User\Downloads\tilda dododo\pdf_styles_analysis.txt"

def analyze_styles(pdf_path):
    styles = []
    text_samples = {} # Храним образцы текста для каждого стиля
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words(extra_attrs=["fontname", "size"])
            for w in words:
                style_key = (w['fontname'], round(w['size'], 1))
                styles.append(style_key)
                
                # Сохраняем пример текста для наглядности (первые 50 символов для каждого стиля)
                if style_key not in text_samples:
                    text_samples[style_key] = []
                if len(" ".join(text_samples[style_key])) < 100:
                    text_samples[style_key].append(w['text'])

    # Считаем частоту
    counter = Counter(styles)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("АНАЛИЗ СТИЛЕЙ PDF\n")
        f.write("="*30 + "\n\n")
        f.write(f"Шрифт | Размер | Кол-во слов | Пример текста\n")
        f.write("-" * 80 + "\n")
        
        # Сортируем по размеру (от большего к меньшему)
        for style, count in sorted(counter.items(), key=lambda x: x[0][1], reverse=True):
            font, size = style
            sample = " ".join(text_samples[style][:10])
            f.write(f"{font:<25} | {size:<6} | {count:<10} | {sample}...\n")

    print(f"Анализ готов! Откройте файл: {output_path}")

if os.path.exists(pdf_path):
    analyze_styles(pdf_path)
else:
    print("Файл не найден!")
