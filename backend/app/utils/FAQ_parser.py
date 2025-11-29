"""
Парсер FAQ с сайтов банков
Парсит вопросы и ответы, группирует по темам
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import os
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import time


class FAQParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.faq_data = []

    def clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов и пробелов"""
        if not text:
            return ""
        # Удаляем множественные пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        # Удаляем пробелы в начале и конце
        text = text.strip()
        # Удаляем невидимые символы
        text = re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', text)
        return text

    def is_valid_question(self, text: str) -> bool:
        """Проверка, является ли текст валидным вопросом"""
        if not text or len(text) < 5:
            return False
        if len(text) > 500:  # Слишком длинный для вопроса
            return False
        # Должен содержать знак вопроса или начинаться с вопросительных слов
        has_question_mark = '?' in text
        question_words = ['как', 'что', 'где', 'когда', 'почему', 'зачем', 'кто', 'чей', 'какой', 'какая', 'какое',
                          'какие']
        starts_with_question = any(text.lower().startswith(word) for word in question_words)
        # Или должен быть коротким и заканчиваться знаком вопроса
        is_short_question = len(text) < 150 and text.strip().endswith('?')
        return has_question_mark or starts_with_question or is_short_question

    def is_valid_answer(self, text: str) -> str:
        """Проверка и очистка ответа"""
        if not text:
            return ""
        text = self.clean_text(text)
        # Минимальная длина ответа
        if len(text) < 20:
            return ""
        # Удаляем слишком короткие фрагменты в начале
        sentences = re.split(r'[.!?]\s+', text)
        # Берем только осмысленные предложения
        valid_sentences = [s for s in sentences if len(s.strip()) > 10]
        if not valid_sentences:
            return ""
        return ' '.join(valid_sentences)

    def parse_psbank_ru(self) -> List[Dict[str, Any]]:
        """Парсинг FAQ с psbank.ru/bank/faq"""
        url = "https://www.psbank.ru/bank/faq"
        print(f"Парсинг {url}...")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            faqs = []

            # Удаляем ненужные элементы
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()

            # Метод 1: Поиск по специфичным классам и структуре
            # Ищем все элементы, которые могут содержать FAQ
            faq_containers = soup.find_all(['div', 'section', 'article'],
                                           class_=re.compile(r'faq|question|answer|accordion|collapse|item', re.I))

            for container in faq_containers:
                # Ищем вопрос - обычно это заголовок или кнопка
                question_elem = None
                for tag in ['button', 'summary', 'h2', 'h3', 'h4', 'h5', 'div', 'span']:
                    question_elem = container.find(tag,
                                                   class_=re.compile(r'question|title|header|trigger|heading', re.I))
                    if question_elem:
                        break

                if not question_elem:
                    # Пробуем найти первый заголовок в контейнере
                    question_elem = container.find(['h2', 'h3', 'h4', 'h5', 'button', 'summary'])

                if question_elem:
                    question = self.clean_text(question_elem.get_text())

                    # Пропускаем если не похоже на вопрос
                    if not self.is_valid_question(question):
                        continue

                    # Ищем ответ
                    answer_elem = container.find(['div', 'p', 'section'],
                                                 class_=re.compile(r'answer|content|body|panel|text', re.I))

                    if not answer_elem:
                        # Пробуем найти следующий элемент после вопроса
                        answer_elem = question_elem.find_next(['div', 'p', 'section'])

                    if answer_elem:
                        answer = self.is_valid_answer(answer_elem.get_text())
                    else:
                        # Берем весь текст контейнера, исключая вопрос
                        full_text = container.get_text()
                        answer = self.is_valid_answer(full_text.replace(question, '', 1))

                    if question and answer:
                        faqs.append({
                            'question': question,
                            'answer': answer,
                            'source': 'psbank.ru',
                            'url': url
                        })

            # Метод 2: Поиск по структуре заголовок + следующий контент
            if len(faqs) < 5:
                headers = soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
                for header in headers:
                    question = self.clean_text(header.get_text())

                    # Проверяем, что это валидный вопрос
                    if not self.is_valid_question(question):
                        continue

                    # Ищем ответ в следующих элементах
                    answer_parts = []
                    current = header.find_next_sibling()
                    depth = 0
                    max_depth = 8

                    while current and depth < max_depth:
                        if hasattr(current, 'name') and current.name:
                            # Пропускаем заголовки
                            if current.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                                break

                            if current.name in ['div', 'p', 'section', 'article']:
                                text = self.clean_text(current.get_text())
                                if text and len(text) > 15:
                                    # Проверяем, что это не новый вопрос
                                    if not self.is_valid_question(text):
                                        answer_parts.append(text)
                                        if len(' '.join(answer_parts)) > 100:  # Достаточно текста
                                            break
                        elif isinstance(current, str):
                            text = self.clean_text(current)
                            if text and len(text) > 15 and not self.is_valid_question(text):
                                answer_parts.append(text)

                        current = getattr(current, 'next_sibling', None)
                        depth += 1

                    if answer_parts:
                        answer = self.is_valid_answer(' '.join(answer_parts[:5]))
                        if answer:
                            faqs.append({
                                'question': question,
                                'answer': answer,
                                'source': 'psbank.ru',
                                'url': url
                            })

            # Метод 3: Поиск в списках (dl, ul с вопросами)
            if len(faqs) < 5:
                # Списки определений
                dl_lists = soup.find_all('dl')
                for dl in dl_lists:
                    dts = dl.find_all('dt')
                    dds = dl.find_all('dd')
                    for dt, dd in zip(dts, dds):
                        question = self.clean_text(dt.get_text())
                        answer = self.is_valid_answer(dd.get_text())

                        if self.is_valid_question(question) and answer:
                            faqs.append({
                                'question': question,
                                'answer': answer,
                                'source': 'psbank.ru',
                                'url': url
                            })

                # Обычные списки с вопросами
                ul_lists = soup.find_all(['ul', 'ol'])
                for ul in ul_lists:
                    items = ul.find_all('li')
                    for item in items:
                        text = self.clean_text(item.get_text())
                        # Пробуем разделить на вопрос и ответ
                        if ':' in text or '?' in text:
                            parts = re.split(r'[?:]\s+', text, 1)
                            if len(parts) == 2:
                                question = parts[0].strip()
                                if not question.endswith('?'):
                                    question += '?'
                                answer = self.is_valid_answer(parts[1])

                                if self.is_valid_question(question) and answer:
                                    faqs.append({
                                        'question': question,
                                        'answer': answer,
                                        'source': 'psbank.ru',
                                        'url': url
                                    })

            # Удаляем дубликаты и невалидные записи
            seen = set()
            unique_faqs = []
            for faq in faqs:
                # Проверяем валидность
                if not self.is_valid_question(faq['question']) or not faq['answer']:
                    continue

                # Проверяем на дубликаты
                key = (faq['question'].lower()[:60], faq['answer'].lower()[:60])
                if key not in seen:
                    seen.add(key)
                    unique_faqs.append(faq)

            print(f"Найдено {len(unique_faqs)} валидных FAQ на psbank.ru")
            return unique_faqs

        except Exception as e:
            print(f"Ошибка при парсинге psbank.ru: {e}")
            import traceback
            traceback.print_exc()
            return []

    def parse_psbnpf_ru(self) -> List[Dict[str, Any]]:
        """Парсинг FAQ с psbnpf.ru/faq"""
        url = "https://psbnpf.ru/faq/"
        print(f"Парсинг {url}...")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            faqs = []

            # Удаляем ненужные элементы
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Метод 1: Поиск FAQ блоков
            faq_blocks = soup.find_all(['div', 'section', 'article'],
                                       class_=re.compile(r'faq|question|answer|item', re.I))

            for block in faq_blocks:
                # Ищем вопрос
                question_elem = (block.find(['button', 'summary', 'h2', 'h3', 'h4', 'div', 'span'],
                                            class_=re.compile(r'question|title|header|trigger', re.I)) or
                                 block.find(['h2', 'h3', 'h4', 'h5']))

                # Ищем ответ
                answer_elem = (block.find(['div', 'p', 'span'],
                                          class_=re.compile(r'answer|content|text|body|panel', re.I)) or
                               block.find(['div', 'p']))

                if question_elem:
                    question = self.clean_text(question_elem.get_text())

                    if not self.is_valid_question(question):
                        continue

                    if answer_elem:
                        answer = self.is_valid_answer(answer_elem.get_text())
                    else:
                        # Берем весь текст блока кроме вопроса
                        full_text = block.get_text()
                        answer = self.is_valid_answer(full_text.replace(question, '', 1))

                    if question and answer:
                        faqs.append({
                            'question': question,
                            'answer': answer,
                            'source': 'psbnpf.ru',
                            'url': url
                        })

            # Метод 2: Поиск по структуре заголовок + контент
            if not faqs or len(faqs) < 3:
                headers = soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6'])
                for header in headers:
                    question = self.clean_text(header.get_text())

                    if not self.is_valid_question(question):
                        continue

                    # Ищем ответ
                    answer_parts = []
                    current = header.find_next_sibling()
                    depth = 0

                    while current and depth < 8:
                        if hasattr(current, 'name'):
                            if current.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                                break

                            if current.name in ['div', 'p', 'section', 'article']:
                                text = self.clean_text(current.get_text())
                                if text and len(text) > 15 and not self.is_valid_question(text):
                                    answer_parts.append(text)
                        elif isinstance(current, str):
                            text = self.clean_text(current)
                            if text and len(text) > 15 and not self.is_valid_question(text):
                                answer_parts.append(text)

                        current = getattr(current, 'next_sibling', None)
                        depth += 1

                    if answer_parts:
                        answer = self.is_valid_answer(' '.join(answer_parts[:4]))
                        if answer:
                            faqs.append({
                                'question': question,
                                'answer': answer,
                                'source': 'psbnpf.ru',
                                'url': url
                            })

            # Удаляем дубликаты и невалидные записи
            seen = set()
            unique_faqs = []
            for faq in faqs:
                if not self.is_valid_question(faq['question']) or not faq['answer']:
                    continue

                key = (faq['question'].lower()[:60], faq['answer'].lower()[:60])
                if key not in seen:
                    seen.add(key)
                    unique_faqs.append(faq)

            print(f"Найдено {len(unique_faqs)} валидных FAQ на psbnpf.ru")
            return unique_faqs

        except Exception as e:
            print(f"Ошибка при парсинге psbnpf.ru: {e}")
            import traceback
            traceback.print_exc()
            return []

    def parse_ib_psbank_ru(self) -> List[Dict[str, Any]]:
        """Парсинг с ib.psbank.ru (страница продукта, может содержать FAQ)"""
        url = "https://ib.psbank.ru/store/products/your-cashback-new"
        print(f"Парсинг {url}...")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            faqs = []

            # Удаляем ненужные элементы
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Метод 1: Ищем FAQ секции
            faq_sections = soup.find_all(['div', 'section', 'article'],
                                         class_=re.compile(r'faq|question|answer|help|accordion', re.I))

            for section in faq_sections:
                question_elem = (section.find(['button', 'summary', 'h2', 'h3', 'h4', 'div'],
                                              class_=re.compile(r'question|title|header', re.I)) or
                                 section.find(['h2', 'h3', 'h4']))
                answer_elem = section.find(['div', 'p'], class_=re.compile(r'answer|content|body', re.I))

                if question_elem:
                    question = self.clean_text(question_elem.get_text())

                    if not self.is_valid_question(question):
                        continue

                    if answer_elem:
                        answer = self.is_valid_answer(answer_elem.get_text())
                    else:
                        # Берем весь текст секции
                        full_text = section.get_text()
                        answer = self.is_valid_answer(full_text.replace(question, '', 1))

                    if question and answer:
                        faqs.append({
                            'question': question,
                            'answer': answer,
                            'source': 'ib.psbank.ru',
                            'url': url
                        })

            # Метод 2: Ищем информацию о продукте (условия, тарифы и т.д.)
            product_sections = soup.find_all(['div', 'section'],
                                             class_=re.compile(r'product|info|description|condition|tariff', re.I))

            for section in product_sections:
                headers = section.find_all(['h2', 'h3', 'h4', 'h5', 'strong', 'b'])
                for header in headers:
                    title = header.get_text(strip=True)
                    if len(title) > 5 and len(title) < 200:
                        # Ищем контент после заголовка
                        content_elem = header.find_next(['div', 'p', 'ul', 'ol'])
                        if content_elem:
                            text = content_elem.get_text(strip=True)
                            if text and len(text) > 30:
                                # Формируем вопрос из заголовка
                                question = title if '?' in title else f"Что такое {title}?"
                                faqs.append({
                                    'question': question,
                                    'answer': text,
                                    'source': 'ib.psbank.ru',
                                    'url': url
                                })

            # Метод 3: Ищем списки условий/тарифов
            lists = soup.find_all(['ul', 'ol'])
            for list_elem in lists:
                items = list_elem.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if len(text) > 30 and len(text) < 500:
                        # Разделяем на вопрос и ответ если есть двоеточие
                        text_clean = self.clean_text(text)
                        if ':' in text_clean:
                            parts = text_clean.split(':', 1)
                            if len(parts) == 2:
                                question = parts[0].strip()
                                if not question.endswith('?'):
                                    question += '?'
                                answer = self.is_valid_answer(parts[1])

                                if self.is_valid_question(question) and answer:
                                    faqs.append({
                                        'question': question,
                                        'answer': answer,
                                        'source': 'ib.psbank.ru',
                                        'url': url
                                    })

            # Удаляем дубликаты и невалидные записи
            seen = set()
            unique_faqs = []
            for faq in faqs:
                if not self.is_valid_question(faq['question']) or not faq['answer']:
                    continue

                key = (faq['question'].lower()[:60], faq['answer'].lower()[:60])
                if key not in seen:
                    seen.add(key)
                    unique_faqs.append(faq)

            print(f"Найдено {len(unique_faqs)} валидных FAQ на ib.psbank.ru")
            return unique_faqs

        except Exception as e:
            print(f"Ошибка при парсинге ib.psbank.ru: {e}")
            import traceback
            traceback.print_exc()
            return []

    def categorize_faqs(self, faqs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Группировка FAQ по темам на основе ключевых слов"""

        categories = {
            'Карты и платежи': [
                'карт', 'платеж', 'оплат', 'снятие', 'пополнение', 'банкомат', 'pos',
                'миром', 'visa', 'mastercard', 'unionpay', 'бесконтактн', 'nfc',
                'apple pay', 'google pay', 'samsung pay', 'эквайринг'
            ],
            'Кредиты': [
                'кредит', 'займ', 'заем', 'процент', 'ставка', 'погашение', 'досрочн',
                'кредитная линия', 'овердрафт', 'рефинансирование'
            ],
            'Вклады и депозиты': [
                'вклад', 'депозит', 'процент', 'начисление', 'выплат', 'снятие средств',
                'пополняемый', 'срочный', 'до востребования'
            ],
            'Санкции и ограничения': [
                'санкц', 'ограничен', 'блокировк', 'запрет', 'работа', 'действ',
                'иностранн', 'валют', 'зарубеж'
            ],
            'Интернет-банк и мобильное приложение': [
                'интернет-банк', 'мобильн', 'приложен', 'онлайн', 'перевод', 'платеж',
                'личный кабинет', 'вход', 'регистрация', 'восстановление'
            ],
            'Безопасность': [
                'безопасн', 'защит', 'мошенничеств', 'пароль', 'pin', 'блокировк',
                'sms', 'подтверждение', 'двухфакторная', 'фишинг'
            ],
            'Обслуживание счетов': [
                'счет', 'открытие', 'закрытие', 'обслуживание', 'комисс', 'тариф',
                'расчетный счет', 'текущий счет', 'сберегательный'
            ],
            'Ипотека': [
                'ипотек', 'недвижимост', 'квартир', 'дом', 'жилье', 'ипотечный кредит'
            ],
            'Инвестиции': [
                'инвестиц', 'ценные бумаги', 'портфель', 'брокер', 'акции', 'облигации',
                'паевой фонд', 'управление активами'
            ],
            'Кэшбэк и бонусы': [
                'кэшбэк', 'cashback', 'бонус', 'начисление', 'программа лояльности',
                'возврат', 'накопление'
            ],
            'Переводы и платежи': [
                'перевод', 'платеж', 'перечисление', 'реквизит', 'swift', 'iban',
                'международный перевод', 'внутренний перевод'
            ],
            'Прочее': []
        }

        categorized = {cat: [] for cat in categories.keys()}

        for faq in faqs:
            question_lower = faq['question'].lower()
            answer_lower = faq['answer'].lower()
            text = question_lower + ' ' + answer_lower

            # Подсчитываем совпадения для каждой категории
            category_scores = {}
            for category, keywords in categories.items():
                if category == 'Прочее':
                    continue
                score = sum(1 for keyword in keywords if keyword in text)
                if score > 0:
                    category_scores[category] = score

            # Выбираем категорию с наибольшим количеством совпадений
            if category_scores:
                best_category = max(category_scores.items(), key=lambda x: x[1])[0]
                categorized[best_category].append(faq)
            else:
                categorized['Прочее'].append(faq)

        return categorized

    def save_to_json(self, data: Dict[str, Any], filename: str = 'faq_data.json'):
        """Сохранение данных в JSON файл"""
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в {filepath}")
        return filepath

    def parse_all(self):
        """Парсинг всех сайтов"""
        print("Начало парсинга FAQ...")

        all_faqs = []

        # Парсим каждый сайт
        all_faqs.extend(self.parse_psbank_ru())
        time.sleep(2)  # Пауза между запросами

        all_faqs.extend(self.parse_psbnpf_ru())
        time.sleep(2)

        all_faqs.extend(self.parse_ib_psbank_ru())

        print(f"\nВсего найдено {len(all_faqs)} FAQ")

        # Группируем по темам
        print("\nГруппировка по темам...")
        categorized = self.categorize_faqs(all_faqs)

        # Статистика по категориям
        print("\nСтатистика по категориям:")
        for category, items in categorized.items():
            print(f"  {category}: {len(items)} вопросов")

        # Сохраняем результаты
        result = {
            'total_faqs': len(all_faqs),
            'by_category': categorized,
            'all_faqs': all_faqs
        }

        self.save_to_json(result, 'faq_data.json')

        # Также сохраняем по категориям в отдельные файлы
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)

        for category, items in categorized.items():
            if items:
                # Очищаем имя файла от недопустимых символов
                safe_name = re.sub(r'[^\w\s-]', '', category.lower())
                safe_name = re.sub(r'[-\s]+', '_', safe_name)
                filename = f'faq_{safe_name}.json'
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(items, f, ensure_ascii=False, indent=2)
                print(f"Сохранено {len(items)} FAQ в {filepath}")

        return result


if __name__ == '__main__':
    parser = FAQParser()
    result = parser.parse_all()
    print("\nПарсинг завершен!")

