# AI Bank Assistant - Frontend

Фронтенд приложение для банковского ассистента на React + TypeScript + Vite.

## Установка

```bash
npm install
```

## Настройка

Создайте файл `.env` на основе `.env.example`:

```bash
VITE_API_URL=http://localhost:8000
VITE_API_KEY=your_api_key_here
```

## Запуск

```bash
npm run dev
```

Приложение будет доступно по адресу http://localhost:3000

## Сборка

```bash
npm run build
```

## Структура проекта

- `src/api/` - API клиенты для работы с бэкендом
- `src/components/` - Переиспользуемые компоненты
- `src/hooks/` - React Query хуки
- `src/pages/` - Страницы приложения
- `src/types/` - TypeScript типы
- `src/styles/` - Стили

## Основные страницы

- `/` - Дашборд с таблицей входящих писем
- `/letters/:id` - Детальная информация о письме
- `/approvals` - Согласования
- `/analytics` - Аналитика с графиками

