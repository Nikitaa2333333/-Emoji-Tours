import os
import re

# Полный HTML-код формы (взят из index.html и адаптирован для вставки)
FULL_FORM_TEMPLATE = """
        <section id="booking-form" class="py-32 px-8 bg-surface-container-high relative overflow-hidden">
            <div class="absolute top-0 right-0 w-1/3 h-full bg-primary-container/10 -skew-x-12 transform translate-x-1/2 -z-0"></div>
            <div class="max-w-4xl mx-auto relative z-10">
                <div class="text-center mb-16 space-y-4">
                    <h2 class="text-5xl font-headline font-extrabold text-on-surface">Заполните анкету</h2>
                    <p class="text-on-surface-variant text-lg font-light">Мы подберем идеальный тур, исходя из ваших желаний и эмоционального настроя.</p>
                </div>
                <form class="bg-surface rounded-3xl p-10 md:p-16 shadow-2xl space-y-12">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
                        <!-- Personal Info -->
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">Имя и Фамилия</label>
                            <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" placeholder="Иван Иванов" type="text"/>
                        </div>
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">E-mail</label>
                            <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" placeholder="hello@example.com" type="email"/>
                        </div>
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">Телефон</label>
                            <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" placeholder="+7 (___) ___-__-__" type="tel"/>
                        </div>
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">Ожидаемое направление</label>
                            <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" value="{country_name}" type="text"/>
                        </div>
                        <!-- Trip Specs -->
                        <div class="grid grid-cols-2 gap-4">
                            <div class="space-y-2">
                                <label class="block text-sm font-bold text-on-surface-variant ml-1">Взрослых</label>
                                <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" min="1" type="number" value="2"/>
                            </div>
                            <div class="space-y-2">
                                <label class="block text-sm font-bold text-on-surface-variant ml-1">Детей (и возраст)</label>
                                <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" placeholder="1 реб, 5 лет" type="text"/>
                            </div>
                        </div>
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">Бюджет (RUB)</label>
                            <input class="w-full bg-[#fff9ed] border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" placeholder="От 200 000" type="text"/>
                        </div>
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">Количество ночей</label>
                            <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" min="1" type="number" value="7"/>
                        </div>
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">Дата начала</label>
                            <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" type="date"/>
                        </div>
                    </div>
                    <!-- Radio Buttons -->
                    <div class="space-y-4">
                        <label class="block text-sm font-bold text-on-surface-variant ml-1">Нужны ли экскурсии?</label>
                        <div class="flex flex-wrap gap-8">
                            <label class="flex items-center gap-3 cursor-pointer group">
                                <input class="w-5 h-5 text-primary focus:ring-primary bg-surface-container-low border-none" name="excursion" type="radio"/>
                                <span class="text-on-surface group-hover:text-primary transition-colors">Да, обязательно</span>
                            </label>
                            <label class="flex items-center gap-3 cursor-pointer group">
                                <input class="w-5 h-5 text-primary focus:ring-primary bg-surface-container-low border-none" name="excursion" type="radio"/>
                                <span class="text-on-surface group-hover:text-primary transition-colors">Нет, только отдых</span>
                            </label>
                            <label class="flex items-center gap-3 cursor-pointer group">
                                <input class="w-5 h-5 text-primary focus:ring-primary bg-surface-container-low border-none" name="excursion" type="radio"/>
                                <span class="text-on-surface group-hover:text-primary transition-colors">Пока не знаю</span>
                            </label>
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">Предпочтения по отелю</label>
                            <textarea class="w-full bg-[#fff9ed] border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" placeholder="Напр. первая линия, только 5*, наличие детского клуба..." rows="3"></textarea>
                        </div>
                        <div class="space-y-2">
                            <label class="block text-sm font-bold text-on-surface-variant ml-1">Аэропорт вылета</label>
                            <input class="w-full bg-surface-container-low border-none rounded-lg p-4 focus:ring-2 focus:ring-primary transition-all" placeholder="Шереметьево, Пулково..." type="text"/>
                        </div>
                    </div>
                    <div class="pt-8 flex justify-center">
                        <button class="bg-primary text-on-primary px-12 py-5 rounded-full text-xl font-bold shadow-2xl hover:scale-105 active:scale-95 transition-all" type="submit">Отправить заявку на мечту</button>
                    </div>
                </form>
            </div>
        </section>"""

def upgrade_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Находим название страны из h1
    country_match = re.search(r'<h1[^>]*id="page-title"[^>]*>(.*?)</h1>', content, re.DOTALL)
    if not country_match:
        # Попробуем из тега title если h1 не подошел
        country_match = re.search(r'<title>(.*?) — Emoji Tours</title>', content)
    
    if country_match:
        country_name = country_match.group(1).strip()
        # Убираем возможные HTML теги из названия (например <span class="text-primary">)
        country_name = re.sub(r'<[^>]+>', '', country_name)
    else:
        country_name = "Выбранное направление"

    # 2. Заменяем старую секцию формы на новую
    # Ищем от <section id="booking-form" до следующего </section>
    pattern = r'<section id="booking-form"[^>]*>.*?</section>'
    
    new_form = FULL_FORM_TEMPLATE.format(country_name=country_name)
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, new_form, content, flags=re.DOTALL)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Upgraded form in: {file_path} (Country: {country_name})")
    else:
        print(f"Form not found in {file_path}")

def main():
    # Исключаем индекс, шаблоны и памятки
    exclude = ['index.html', 'template.html', 'template_memo.html']
    files = [f for f in os.listdir('.') if f.endswith('.html') and f not in exclude and not f.startswith('memo-')]
    
    for file in files:
        upgrade_file(file)

if __name__ == "__main__":
    main()
