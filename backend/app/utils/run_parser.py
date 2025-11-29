#!/usr/bin/env python3
"""
Простой скрипт для запуска парсера FAQ
"""
import sys
import os

# Добавляем путь к корню проекта


from .FAQ_parser import FAQParser



def run_parser():

    parser = FAQParser()
    result = parser.parse_all()
    sorted_cats = sorted(
        result['by_category'].items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    return sorted_cats


