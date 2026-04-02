import os
import re

# Sunlit Editorial Pro Max Skin CSS (Premium Overrides & Global Fixes)
overlay_styles = """
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
<script src="https://cdn.tailwindcss.com?plugins=forms"></script>
<script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'primary': '#f5e2a1',
            'background': '#fffcf5',
            'on-surface': '#000000',
            'on-surface-variant': '#000000',
            'surface-container-high': '#fffaf0',
            'primary-container': '#f5e2a1',
          },
          fontFamily: {
            'headline': ['Manrope'],
            'body': ['Manrope']
          },
          borderRadius: {
            'full': '9999px',
            '3xl': '3rem',
          }
        }
      }
    }
</script>
<style>
    /* Global Skin Overrides - Sunlit Editorial Premium */
    body, .t-body { 
        background-color: #fffcf5 !important; 
        font-family: 'Manrope', sans-serif !important; 
        color: #000 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important; /* Fix white gap & horizontal scroll */
    }
    
    #allrecords, .t-records {
        background-color: #fffcf5 !important;
    }

    /* 1. Header & Logo Fixes (Global) */
    .t-menu__logo img, 
    a[href="/"] img, 
    .t794__logo img,
    .t228__logo img,
    .t199__logo img {
        max-height: 48px !important; /* Constrain huge logos */
        width: auto !important;
        transition: all 0.3s ease;
    }

    /* Glassmorphism Menu */
    .t-menu__container, .t794, .t228, .t199, .t456 {
        background-color: rgba(255, 252, 245, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-bottom: 1px solid rgba(0,0,0,0.05) !important;
    }

    /* Typography - "The Bold Look" */
    .t-title, .t-name, .t-heading, h1, h2, h3 { 
        font-family: 'Manrope', sans-serif !important; 
        font-weight: 900 !important;
        letter-spacing: -0.05em !important;
        line-height: 0.95 !important;
        color: #000 !important;
    }
    
    .t-text, .t-descr, p, li {
        font-family: 'Manrope', sans-serif !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        color: #1a1a1a !important;
    }

    /* Buttons - "Pill Style" */
    .t-btn, .t-submit, .t706__carticon {
        border-radius: 9999px !important;
        background-color: #000 !important;
        color: #fff !important;
        font-weight: 800 !important;
        text-transform: none !important;
        letter-spacing: -0.01em !important;
        padding: 1.25rem 2.5rem !important;
        height: auto !important;
        border: none !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1) !important;
    }
    
    .t-btn:hover, .t-submit:hover {
        transform: scale(1.05) translateY(-2px) !important;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.15) !important;
    }

    /* Panels & Cards - "Soft Floating" */
    .t-rec, .t-container, .t-col, .t-card__container {
        border-radius: 3rem !important;
    }
    
    .t-img, .t-col img, .t-bgimg, .t-slds__bgimg {
        border-radius: 2.5rem !important;
    }

    /* Custom Checkboxes & Radios */
    .t-checkbox__indicator {
        border-radius: 0.75rem !important;
        border: 2px solid #000 !important;
        background-color: transparent !important;
        transition: all 0.3s ease !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    .t-checkbox:checked + .t-checkbox__indicator {
        background-color: #f5e2a1 !important;
        border-color: #f5e2a1 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' height='24' viewBox='0 -960 960 960' width='24'%3E%3Cpath d='M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z'/%3E%3C/svg%3E") !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
    }
    
    .t-radio__indicator {
        border-radius: 50% !important;
        border: 2px solid #000 !important;
        background-color: transparent !important;
        transition: all 0.3s ease !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    .t-radio:checked + .t-radio__indicator {
        background-color: #f5e2a1 !important;
        border-color: #f5e2a1 !important;
        box-shadow: inset 0 0 0 4px #fffcf5 !important;
    }

    /* Remove Tilda branding */
    .t-tildalabel, .t-menusub__list { display: none !important; }
    
    /* Form Inputs */
    .t-input {
        border-radius: 9999px !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        background-color: #fffcf5 !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        font-family: 'Manrope', sans-serif !important;
    }
    
    .t-input:focus {
        border-color: #f5e2a1 !important;
        box-shadow: 0 0 0 2px rgba(245, 226, 161, 0.4) !important;
    }
</style>
"""

# The EXACT Booking Form Section from index.html
booking_form_html = """
  <!-- Questionnaire Section -->
  <section id="journey" class="py-24 md:py-32 px-4 md:px-8 bg-surface-container-high relative overflow-hidden">
    <!-- Abstract Decoration -->
    <div
      class="absolute top-0 right-0 w-full md:w-1/3 h-full bg-primary-container/20 -skew-x-12 transform md:translate-x-1/2 -z-0 blur-3xl">
    </div>
    <div class="max-w-4xl mx-auto relative z-10 text-black">
      <div class="text-center mb-10 md:mb-8 space-y-4 px-2">
        <h2 class="text-4xl md:text-5xl font-headline font-black text-on-surface tracking-tight leading-none">
          Ваша новая история...</h2>
        <p class="text-on-surface-variant text-base md:text-lg font-medium leading-relaxed">Мы подберем
          идеальный тур, исходя из ваших желаний
          и эмоционального настроя.</p>
      </div>
      <form id="booking-form"
        class="bg-[#fffcf5] border border-black/5 rounded-[2rem] md:rounded-[3rem] p-6 sm:p-10 md:p-16 shadow-2xl shadow-[#5f531a]/10 space-y-10 md:space-y-12 relative overflow-hidden">
        <!-- Gradient line removed -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6 md:gap-y-8 mt-2">
          <!-- Personal Info -->
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">Имя и Фамилия</label>
            <input
              class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              name="userName" placeholder="Иван Иванов" type="text" required />
          </div>
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">E-mail</label>
            <input
              class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              name="userEmail" placeholder="hello@example.com" type="email" required />
          </div>
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">Телефон</label>
            <input
              class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              name="userPhone" placeholder="+7 (___) ___-__-__" type="tel" required />
          </div>
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">Ожидаемое
              направление</label>
            <input
              class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              name="destination" placeholder="Напр. Таиланд или Море" type="text" />
          </div>
          <!-- Trip Specs -->
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2 text-left">
              <label class="block text-sm font-bold text-on-surface-variant ml-1">Взрослых</label>
              <input
                class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                min="1" type="number" value="2" name="adults">
            </div>
            <div class="space-y-2 text-left">
              <label class="block text-sm font-bold text-on-surface-variant ml-1">Детей (и
                возраст)</label>
              <input
                class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
                placeholder="1 реб, 5 лет" type="text" name="children">
            </div>
          </div>
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">Бюджет (RUB)</label>
            <input
              class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              name="budget" placeholder="От 200 000" type="text" />
          </div>
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">Количество ночей</label>
            <input
              class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              min="1" type="number" value="7" name="nights">
          </div>
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">Дата начала</label>
            <input
              class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              name="startDate" type="date" />
          </div>
        </div>
        <!-- Radio Buttons -->
        <div class="space-y-4 text-left">
          <label class="block text-sm font-bold text-on-surface-variant ml-1">Нужны ли экскурсии?</label>
          <div class="flex flex-wrap gap-8">
            <label class="flex items-center gap-3 cursor-pointer group">
              <input
                class="w-5 h-5 text-primary border-black/20 rounded-full transition-colors cursor-pointer"
                name="excursions" type="radio" value="Да" />
              <span class="text-on-surface group-hover:text-primary transition-colors">Да, обязательно</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer group">
              <input
                class="w-5 h-5 text-primary border-black/20 rounded-full transition-colors cursor-pointer"
                name="excursions" type="radio" value="Нет" />
              <span class="text-on-surface group-hover:text-primary transition-colors">Нет, только отдых</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer group">
              <input
                class="w-5 h-5 text-primary border-black/20 rounded-full transition-colors cursor-pointer"
                name="excursions" type="radio" value="Пока не знаю" />
              <span class="text-on-surface group-hover:text-primary transition-colors">Пока не знаю</span>
            </label>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">Предпочтения по отелю</label>
            <textarea
              class="w-full bg-transparent border border-black/15 rounded-[2.5rem] p-6 md:p-8 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              name="hotelPrefs" placeholder="Напр. первая линия, только 5*, наличие детского клуба..." rows="3"></textarea>
          </div>
          <div class="space-y-2 text-left">
            <label class="block text-sm font-bold text-on-surface-variant ml-1">Аэропорт вылета</label>
            <input
              class="w-full bg-transparent border border-black/15 rounded-full p-4 hover:border-black/30 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all"
              placeholder="Шереметьево, Пулково..." type="text" name="airport">
          </div>
        </div>
        <div class="pt-8 flex justify-center w-full">
          <button
            class="w-full sm:w-auto bg-black text-white px-10 md:px-14 py-5 rounded-full text-lg md:text-xl font-bold shadow-xl shadow-black/15 hover:scale-[1.02] active:scale-95 transition-all flex items-center justify-center"
            type="submit">
            Отправить заявку
          </button>
        </div>
      </form>
    </div>
  </section>

  <!-- Success Modal -->
  <div id="success-modal" class="fixed inset-0 z-[200] flex items-center justify-center opacity-0 pointer-events-none transition-opacity duration-500">
      <div class="absolute inset-0 bg-black/30 backdrop-blur-sm"></div>
      <div class="bg-white p-8 md:p-12 rounded-[3rem] shadow-2xl relative z-10 max-w-sm w-full text-center space-y-6 transform scale-90 transition-transform duration-500" id="success-card">
          <div class="w-24 h-24 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <span class="material-symbols-outlined text-5xl">check</span>
          </div>
          <h3 class="text-3xl font-black tracking-tight text-black">Заявка принята!</h3>
          <p class="text-on-surface-variant font-medium leading-relaxed text-black/70">
              Мы уже получили ваши данные и начали подбор идеального тура. Наш эксперт свяжется с вами в ближайшее время!
          </p>
          <button onclick="closeModal()" class="w-full bg-black text-white py-5 rounded-full text-xl font-bold hover:scale-105 active:scale-95 transition-all shadow-xl shadow-black/10 mt-4">
              Супер!
          </button>
      </div>
  </div>

  <script src="https://unpkg.com/imask"></script>
  <script>
      document.addEventListener('DOMContentLoaded', function() {
          const phoneInputs = document.querySelectorAll('input[type="tel"]');
          phoneInputs.forEach(input => { IMask(input, { mask: '+7 (000) 000-00-00', lazy: false }); });

          const form = document.getElementById('booking-form');
          const modal = document.getElementById('success-modal');
          const card = document.getElementById('success-card');
          const GOOGLE_URL = 'https://script.google.com/macros/s/AKfycbwi0-K7Jqf86nWEyit6OB7DgiBlHEjhQF7SvlDcl0BUEnTl8WGMjrM5nGx5wSUoAk-7/exec';

          if (form) {
              form.addEventListener('submit', function(e) {
                  e.preventDefault();
                  const btn = form.querySelector('button[type="submit"]');
                  const originalText = btn.innerHTML;
                  btn.disabled = true;
                  btn.innerHTML = 'Отправляем...';
                  
                  const formData = new FormData(form);
                  const params = new URLSearchParams();
                  for (const [key, value] of formData.entries()) { params.append(key, value); }

                  fetch(GOOGLE_URL, {
                      method: 'POST',
                      mode: 'no-cors',
                      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                      body: params.toString()
                  })
                  .then(() => {
                      modal.classList.add('opacity-100', 'pointer-events-auto');
                      card.style.transform = 'scale(1)';
                      form.reset();
                  })
                  .finally(() => { btn.disabled = false; btn.innerHTML = originalText; });
              });
          }
      });
      function closeModal() {
          const modal = document.getElementById('success-modal');
          const card = document.getElementById('success-card');
          modal.classList.remove('opacity-100', 'pointer-events-auto');
          card.style.transform = 'scale(0.9)';
      }
  </script>
"""

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

        # Inject styles before </head>
        new_content = content.replace('</head>', overlay_styles + '</head>')
        
        # Link fixing with normalization (Only relative paths)
        new_content = re.sub(r'(src|href|data-original|data-content-cover-bg)="images/', r'\1="../tilda_raw/emojitours.ru/images/', new_content)
        new_content = re.sub(r'(src|href)="css/', r'\1="../tilda_raw/emojitours.ru/css/', new_content)
        new_content = re.sub(r'(src|href)="js/', r'\1="../tilda_raw/emojitours.ru/js/', new_content)
        
        # Add a specific fix for full-width covers to ignore the global border-radius
        cover_fix = "\n    .t-cover, .t-cover__carrier, .t-cover__filter { border-radius: 0 !important; }\n"
        new_content = new_content.replace('</style>', cover_fix + '</style>')

        # Internal links redirection
        links_to_fix = re.findall(r'href="/(.*?)"', new_content)
        for link in links_to_fix:
            if not link or link.startswith('#') or '.' in link: continue
            new_content = new_content.replace(f'href="/{link}"', f'href="{link}.html"')
        new_content = new_content.replace('href="http://emojitours.ru/', 'href="')
        new_content = re.sub(r'href="([a-zA-Z0-9_\-]+)"', r'href="\1.html"', new_content)
        new_content = new_content.replace('.html#', '#')

        # Form Injection at the end
        if "<!--/allrecords-->" in new_content:
            new_content = new_content.replace("<!--/allrecords-->", booking_form_html + "\n<!--/allrecords-->")
        else:
            new_content = new_content.replace("</body>", booking_form_html + "\n</body>")

        # Determine output filename
        alias_match = re.search(r'data-tilda-page-alias="(.*?)"', new_content)
        out_name = f"{alias_match.group(1)}.html" if alias_match else os.path.basename(file_path)
        out_path = os.path.join(r"c:\Users\User\Downloads\tilda dododo\pages", out_name)
        
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f: f.write(new_content)
        return out_name

raw_dir = r"c:\Users\User\Downloads\tilda dododo\tilda_raw\emojitours.ru"
print("Starting global rebrand with layout fixes...")
for filename in os.listdir(raw_dir):
    if filename.endswith(".html") and "page" in filename: 
        try:
            print(f"Processing: {process_file(os.path.join(raw_dir, filename))}")
        except Exception as e: print(f"Error {filename}: {e}")
print("Done!")
