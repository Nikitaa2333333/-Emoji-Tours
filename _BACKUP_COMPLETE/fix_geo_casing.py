import os
import re

# Список корней географических названий для исправления
GEO_NAMES = [
    "мальдив", "египет", "египт", "турци", "вьетнам", "таиланд", "тайланд", 
    "инди", "росси", "китай", "куб", "доминикан", "мексик", "сейшел", 
    "маврики", "израил", "индонези", "итали", "испани", "кипр", "танзани",
    "мале", "хургад", "шарм-эль-шейх", "пхукет", "бали", "паттай", "хайнань",
    "оаэ", "эмират"
]

def capitalize_geo(text):
    for root in GEO_NAMES:
        # Ищем слово, начинающееся с корня в нижнем регистре
        # Используем границы слов \b, чтобы не задеть части других слов
        pattern = re.compile(rf'\b({root}[а-я]*)\b', re.IGNORECASE)
        
        def replace_func(match):
            word = match.group(0)
            # Если слово уже с большой буквы или в капсе — не трогаем
            if word[0].isupper():
                return word
            return word.capitalize()
            
        text = pattern.sub(replace_func, text)
    return text

def process_files():
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    count = 0
    
    for filename in html_files:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = capitalize_geo(content)
        
        if new_content != content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Исправлено: {filename}")
            count += 1
            
    print(f"\nГотово! Обработано файлов: {count}")

if __name__ == "__main__":
    process_files()
