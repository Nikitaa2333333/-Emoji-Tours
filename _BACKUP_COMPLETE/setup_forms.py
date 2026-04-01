import os
import re

# Ваша ссылка из Google Apps Script (укажите свежую, если создали новый аккаунт)
GOOGLE_URL = 'https://script.google.com/macros/s/AKfycbwi0-K7Jqf86nWEyit6OB7DgiBlHEjhQF7SvlDcl0BUEnTl8WGMjrM5nGx5wSUoAk-7/exec'

# Код маски телефона и модалки
MODAL_AND_MASK_CODE = f"""
    <!-- Success Modal -->
    <div id="success-modal" class="fixed inset-0 z-[200] flex items-center justify-center opacity-0 pointer-events-none transition-opacity duration-500">
        <div class="absolute inset-0 bg-black/30 backdrop-blur-sm"></div>
        <div class="bg-white p-8 md:p-12 rounded-[3rem] shadow-2xl relative z-10 max-w-sm w-full text-center space-y-6 transform scale-90 transition-transform duration-500" id="success-card">
            <div class="w-24 h-24 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                <span class="material-symbols-outlined text-5xl">check</span>
            </div>
            <h3 class="text-3xl font-black tracking-tight">Заявка принята!</h3>
            <p class="text-on-surface-variant font-medium leading-relaxed">
                Мы уже получили ваши данные и начали подбор идеального тура. Наш эксперт свяжется с вами в ближайшее время!
            </p>
            <button onclick="closeModal()" class="w-full bg-black text-white py-5 rounded-full text-xl font-bold hover:scale-105 active:scale-95 transition-all shadow-xl shadow-black/10 mt-4">
                Супер!
            </button>
        </div>
    </div>

    <!-- Scripts: IMask & Form Handler -->
    <script src="https://unpkg.com/imask"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // 1. Настройка маски телефона
            const phoneInputs = document.querySelectorAll('input[type="tel"]');
            phoneInputs.forEach(input => {{
                IMask(input, {{
                    mask: '+7 (000) 000-00-00',
                    lazy: false // Маска видна сразу
                }});
            }});

            // 2. Обработка формы
            const GOOGLE_URL = '{GOOGLE_URL}';
            const form = document.getElementById('booking-form');
            const modal = document.getElementById('success-modal');
            const card = document.getElementById('success-card');

            if (form) {{
                form.addEventListener('submit', function(e) {{
                    e.preventDefault();
                    
                    const btn = form.querySelector('button[type="submit"]');
                    const originalText = btn.innerHTML;
                    
                    btn.disabled = true;
                    btn.innerHTML = `
                        <span class="material-symbols-outlined animate-spin mr-3">progress_activity</span>
                        Отправляем...
                    `;
                    
                    const formData = new FormData(form);
                    const params = new URLSearchParams();
                    
                    for (const [key, value] of formData.entries()) {{
                        params.append(key, value);
                    }}

                    fetch(GOOGLE_URL, {{
                        method: 'POST',
                        mode: 'no-cors',
                        headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                        body: params.toString()
                    }})
                    .then(() => {{
                        modal.classList.add('opacity-100', 'pointer-events-auto');
                        card.style.transform = 'scale(1)';
                        form.reset();
                    }})
                    .catch(err => {{
                        console.error('Error:', err);
                        alert('Ошибка при отправке. Пожалуйста, позвоните нам!');
                    }})
                    .finally(() => {{
                        btn.disabled = false;
                        btn.innerHTML = originalText;
                    }});
                }});
            }}
        }});

        function closeModal() {{
            const modal = document.getElementById('success-modal');
            const card = document.getElementById('success-card');
            modal.classList.remove('opacity-100', 'pointer-events-auto');
            card.style.transform = 'scale(0.9)';
        }}
    </script>
"""

def update_html(filename):
    if filename == "setup_forms.py": return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Присваиваем ID форме
        if '<form' in content and 'id="booking-form"' not in content:
            content = re.sub(r'<form\b([^>]*)>', r'<form id="booking-form" \1>', content)
        content = content.replace('id="booking-form-el"', 'id="booking-form"')

        # 2. Атрибуты name для инпутов
        replacements = {
            'Имя и Фамилия': 'userName',
            'E-mail': 'userEmail',
            'Телефон': 'userPhone',
            'Направление': 'destination',
            'направление': 'destination',
            'Взрослых': 'adults',
            'Детей': 'children',
            'Бюджет': 'budget',
            'ночей': 'nights',
            'Дата начала': 'startDate',
            'Аэропорт': 'airport',
            'отелю': 'hotelPrefs'
        }

        for label, name in replacements.items():
            if f'name="{name}"' not in content:
                pattern = rf'({label}.*?<(?:input|textarea)[^>]*)>'
                content = re.sub(pattern, rf'\1 name="{name}">', content, flags=re.DOTALL)

        # 3. Убираем старые скрипты и модалки, если они были
        content = re.sub(r'<!-- Success Modal -->.*?<script>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<script>.*?const GOOGLE_URL.*?</script>', '', content, flags=re.DOTALL)

        # 4. Добавляем новый единый блок перед </body>
        if 'id="success-modal"' not in content:
            content = content.replace('</body>', MODAL_AND_MASK_CODE + '</body>')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename} обновлен (Маска + Форма).")
    except Exception as e:
        print(f"❌ Ошибка в {filename}: {e}")

# Обходим все файлы
for file in os.listdir('.'):
    if file.endswith('.html'):
        update_html(file)
print("\n🔥 ВСЁ ГОТОВО! Теперь на всех страницах есть маска телефона +7 и авто-отправка.")
