# AI Bank Assistant

Упрощенная версия банковского ассистента для обработки входящих писем и генерации ответов.

## Структура проекта

- `backend/` - FastAPI бэкенд
- `frontend/` - React фронтенд

## Быстрый старт

### Бэкенд

1. Перейдите в директорию бэкенда:
```bash
cd backend
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `env.example`:
```env
YANDEX_FOLDER_ID=your_folder_id
YANDEX_API_KEY=your_api_key
API_KEY=  # Опционально, для разработки можно оставить пустым
```

4. Запустите сервер:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступно по адресу: http://localhost:8000

### Фронтенд

1. Перейдите в директорию фронтенда:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Создайте файл `.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_API_KEY=  # Опционально
```

4. Запустите dev сервер:
```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:3000

## Использование

1. Откройте приложение в браузере
2. Введите текст входящего письма в поле ввода
3. Нажмите "Обработать письмо"
4. Дождитесь результата - будет показан:
   - Оригинальное письмо
   - Сгенерированный ответ
   - Оценка валидации
   - Параметры анализа
   - Рекомендации (если есть)

## API

### POST `/api/letters/process`

Обработка письма и генерация ответа.

**Запрос:**
```json
{
  "content": "Текст письма",
  "subject": "Тема письма (необязательно)"
}
```

**Ответ:**
```json
{
  "original_letter": "Текст письма",
  "generated_response": "Сгенерированный ответ",
  "validation_score": 85,
  "validation_result": {
    "score": 85,
    "auto_send_eligible": true,
    "issues": [],
    "recommendations": []
  },
  "processing_params": {
    "letter_type": "info_request",
    "urgency": "medium",
    "formality_level": "formal"
  },
  "request_category": "general",
  "auto_send_eligible": true
}
```

## Парсинг FAQ

Для парсинга FAQ с банковских сайтов используйте скрипт:

```bash
cd backend
python scripts/parse_faq.py
```

Парсер извлекает вопросы и ответы с сайтов и группирует их по темам. Результаты сохраняются в `backend/data/`.

Подробнее: `backend/scripts/README_parser.md`

## Примечания

- Если API ключи Yandex GPT не настроены, будут использоваться моковые ответы
- Для работы без БД все данные обрабатываются в памяти
- CORS настроен для работы с фронтендом на localhost:3000 и localhost:5173

