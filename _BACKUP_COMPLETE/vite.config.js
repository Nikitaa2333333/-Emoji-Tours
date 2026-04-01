import { defineConfig } from 'vite';
import { resolve } from 'path';
import fs from 'fs';

// Ищем все файлы с расширением .html в текущей папке
const htmlFiles = fs.readdirSync(__dirname).filter(file => file.endsWith('.html'));

const inputs = {};
htmlFiles.forEach(file => {
  // Название ключа будет названием файла (например, 'maldives' для 'maldives.html')
  const name = file.replace('.html', '');
  inputs[name] = resolve(__dirname, file);
});

export default defineConfig({
  build: {
    rollupOptions: {
      input: inputs
    }
  }
});
