#!/usr/bin/env python3
"""
Open Library API Test - PoC for Media Tracker
Проверяет работу Open Library API для поиска книг
"""

import requests
import json

# Open Library API - бесплатный и открытый
# Docs: https://openlibrary.org/developers/api
OPENLIB_BASE_URL = "https://openlibrary.org"

def search_books(query, limit=5):
    """Search books by title/author"""
    url = f"{OPENLIB_BASE_URL}/search.json"
    params = {
        "q": query,
        "limit": limit,
        "fields": "key,title,author_name,first_publish_year,cover_i,subject"
    }

    response = requests.get(url, params=params)
    return response.json()

def get_book_details(cover_id):
    """Get book cover URL"""
    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    return None

def main():
    # Test queries
    test_queries = [
        "1984 Оруэлл",
        "Мастер и Маргарита",
        "Atomic Habits",
        "The Hobbit",
    ]

    print("=" * 60)
    print("Open Library API Test - PoC")
    print("=" * 60)

    for query in test_queries:
        print(f"\nПоиск книги: '{query}'")
        print("-" * 40)

        try:
            results = search_books(query)

            if "docs" in results and len(results["docs"]) > 0:
                print(f"Найдено книг: {results.get('numFound', 0)}")

                # Show top 3 results
                for i, book in enumerate(results["docs"][:3], 1):
                    title = book.get("title", "N/A")
                    authors = book.get("author_name", ["Unknown"])
                    year = book.get("first_publish_year", "N/A")
                    cover_id = book.get("cover_i")
                    subjects = book.get("subject", [])[:3]

                    print(f"\n{i}. {title}")
                    print(f"   Автор: {', '.join(authors)}")
                    print(f"   Год первого издания: {year}")

                    # Cover URL
                    cover_url = get_book_details(cover_id)
                    if cover_url:
                        print(f"   Обложка: {cover_url}")

                    if subjects:
                        print(f"   Темы: {', '.join(subjects)}")

            else:
                print("Ничего не найдено!")

        except Exception as e:
            print(f"Ошибка: {e}")

    print("\n" + "=" * 60)
    print("Тест завершён!")

if __name__ == "__main__":
    main()