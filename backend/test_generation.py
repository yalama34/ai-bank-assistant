"""
Тестовый скрипт для проверки генерации ответов на письма для каждой категории стилей.
Проверяет: STRICT_OFFICIAL, CORPORATE, CLIENT_ORIENTED, BRIEF
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к app в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app.services.generation import GenerationService
from app.services.system_prompts import GenerationPrompts

# Тестовые письма для каждого стиля
TEST_LETTERS = {
    GenerationPrompts.STRICT_OFFICIAL: [
        "Добрый день, у меня задержка платежа №12345, что делать?",
        "Здравствуйте! Прошу предоставить информацию о статусе рассмотрения заявки на кредитную линию для ООО 'Компания'.",
        "Требую объяснений по поводу списания комиссии с моего счета без предупреждения.",
    ],
    GenerationPrompts.CORPORATE: [
        """Добрый день!

Мы представляем сеть АЗС «СеверТопливо» (120 станций в ЦФО и СЗФО).

Предлагаем запустить совместную ко-брендинговую программу лояльности и подключить эквайринг ПСБ на всех наших точках.

Со своей стороны готовы:
- предоставить размещение баннеров и POS‑материалов ПСБ на стойках оплаты;
- продвигать продукты ПСБ (карты и кредиты) в наших digital‑каналах;
- интегрировать API бонусной программы.

Рассматриваем банк‑партнёр на эксклюзивной основе.

Готовы обсудить детали.

С уважением,
Директор по развитию ООО «СеверТопливо»""",
        """Здравствуйте!

Наша компания занимается организацией онлайн‑лотерей. Предлагаем ПСБ выступить финансовым партнёром: проводить платежи участников, а также совместно продвигать лотереи среди клиентов банка.

Готовы предоставить процент от оборота.""",
        """Добрый день.

Мы хотим предложить вашему банку сотрудничество по продвижению финансовых услуг через нашу платформу.

Если интересно, можем обсудить детали.""",
    ],
    GenerationPrompts.CLIENT_ORIENTED: [
        """Добрый день!  
Рассматриваю покупку квартиры в ипотеку, бюджет — около 12 млн рублей. Доход официальный, работаю в IT, стаж 6 лет.  
Какие условия можете предложить? Хотелось бы без скрытых комиссий и с удобным сервисом.""",
        """Здравствуйте.
Рассматриваю переход на премиальное обслуживание. Интересуют персональный менеджер, доступ к инвестиционным инструментам и повышенные лимиты по картам.
Какие предложения есть у ПСБ для такого сегмента?""",
        """Привет! Хочу открыть кредитную карту на 500 000 рублей. Какие у вас условия? И есть ли кэшбэк?""",
    ],
    GenerationPrompts.BRIEF: [
        "Здравствуйте. Подскажите, какая сейчас комиссия за снятие наличных по вашей дебетовой карте за рубежом?",
        "Добрый день! Какой процент по вкладу на 1 год?",
        "Здравствуйте. У меня списали какую‑то сумму вчера вечером, я ничего не оплачивал. Объясните, что происходит.",
    ],
}


async def test_generation_for_style(style: GenerationPrompts, letter: str, test_num: int):
    """Тестирует генерацию ответа для конкретного стиля и письма."""
    print(f"\n{'=' * 80}")
    print(f"СТИЛЬ: {style.name}")
    print(f"ТЕСТ #{test_num}")
    print(f"{'=' * 80}")
    print(f"\nВХОДЯЩЕЕ ПИСЬМО:\n{letter}\n")
    print(f"{'-' * 80}")

    try:
        service = GenerationService()
        print("Генерация ответа...")

        response = await service.generate_response(
            letter_text=letter,
            style=style,
            extra_context="",  # Можно добавить историю переписки
            filters=None,  # Можно фильтровать прецеденты
            k=3,  # Количество прецедентов для RAG
        )

        print(f"\nСГЕНЕРИРОВАННЫЙ ОТВЕТ:\n{response}\n")
        print(f"{'=' * 80}")

        # Проверки качества ответа
        checks = {
            "Начинается с 'Здравствуйте'": response.strip().startswith("Здравствуйте"),
            "Нет упоминаний ИИ": "ИИ" not in response and "искусственный интеллект" not in response.lower(),
            "Обращение на 'Вы'": "Вы" in response or "Вас" in response or "Ваш" in response,
            "Нет 'ты'": " ты " not in response.lower() and " тебе " not in response.lower(),
            "Есть подпись": "ПСБ" in response or "Банк" in response,
        }

        print("\nПРОВЕРКИ КАЧЕСТВА:")
        for check, passed in checks.items():
            status = "[OK]" if passed else "[FAIL]"
            print(f"  {status} {check}")

        passed_count = sum(checks.values())
        total_count = len(checks)
        print(f"\nИтого: {passed_count}/{total_count} проверок пройдено")

        return {
            "success": True,
            "response": response,
            "checks": checks,
            "score": passed_count / total_count * 100,
        }

    except Exception as e:
        print(f"\n[ERROR] Ошибка генерации: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
        }


async def test_all_styles():
    """Тестирует генерацию для всех стилей."""
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ГЕНЕРАЦИИ ОТВЕТОВ ПО КАТЕГОРИЯМ")
    print("=" * 80)

    results = {}

    for style, letters in TEST_LETTERS.items():
        print(f"\n\n{'#' * 80}")
        print(f"# ТЕСТИРОВАНИЕ СТИЛЯ: {style.name}")
        print(f"{'#' * 80}\n")

        style_results = []
        for i, letter in enumerate(letters, 1):
            result = await test_generation_for_style(style, letter, i)
            style_results.append(result)

            # Небольшая пауза между запросами
            await asyncio.sleep(1)

        results[style.name] = style_results

    # Итоговая статистика
    print("\n\n" + "=" * 80)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 80)

    for style_name, style_results in results.items():
        print(f"\n{style_name}:")
        successful = sum(1 for r in style_results if r.get("success"))
        total = len(style_results)

        if successful > 0:
            avg_score = sum(r.get("score", 0) for r in style_results if r.get("success")) / successful
            print(f"  Успешных тестов: {successful}/{total}")
            print(f"  Средний балл качества: {avg_score:.1f}%")
        else:
            print(f"  Успешных тестов: 0/{total}")
            print(f"  Все тесты завершились с ошибками")

    print("\n" + "=" * 80)


async def test_single_style(style_name: str):
    """Тестирует генерацию для одного стиля."""
    style_map = {
        "STRICT_OFFICIAL": GenerationPrompts.STRICT_OFFICIAL,
        "CORPORATE": GenerationPrompts.CORPORATE,
        "CLIENT_ORIENTED": GenerationPrompts.CLIENT_ORIENTED,
        "BRIEF": GenerationPrompts.BRIEF,
    }

    if style_name.upper() not in style_map:
        print(f"Неизвестный стиль: {style_name}")
        print(f"Доступные стили: {', '.join(style_map.keys())}")
        return

    style = style_map[style_name.upper()]
    letters = TEST_LETTERS[style]

    print(f"Тестирование стиля: {style.name}")
    print(f"Количество тестовых писем: {len(letters)}\n")

    for i, letter in enumerate(letters, 1):
        await test_generation_for_style(style, letter, i)
        await asyncio.sleep(1)


async def main():
    """Главная функция."""
    import sys

    if len(sys.argv) > 1:
        # Тестируем один стиль
        style_name = sys.argv[1]
        await test_single_style(style_name)
    else:
        # Тестируем все стили
        await test_all_styles()


if __name__ == "__main__":
    asyncio.run(main())