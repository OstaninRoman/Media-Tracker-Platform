#!/usr/bin/env python3
"""
TMDB API Test - PoC for Media Tracker
Проверяет работу TMDB API для поиска фильмов

Обход DNS блокировки через подмену socket.getaddrinfo
"""

import requests
import json
import socket

# TMDB API Configuration
TMDB_API_KEY = "858e37ef0424fed70858d44465fc3a71"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_HOST = "api.themoviedb.org"
# Real IPs from https://www.ipaddress.com/website/api.themoviedb.org/
TMDB_IPS = ["3.170.19.94", "3.170.19.97", "3.170.19.104", "3.170.19.106"]

# Save original getaddrinfo
_original_getaddrinfo = socket.getaddrinfo

def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """Patch socket.getaddrinfo to use real TMDB IPs instead of blocked DNS"""
    if host == TMDB_HOST:
        # Use first available IP from our list
        ip = TMDB_IPS[0]
        return _original_getaddrinfo(ip, port, family, type, proto, flags)
    return _original_getaddrinfo(host, port, family, type, proto, flags)

# Apply the patch
socket.getaddrinfo = _patched_getaddrinfo

def search_movies(query, year=None):
    """Search movies by title"""
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "ru-RU"
    }
    if year:
        params["year"] = year

    response = requests.get(url, params=params, timeout=15)
    return response.json()

def get_movie_details(movie_id):
    """Get full movie details"""
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "ru-RU"
    }
    response = requests.get(url, params=params, timeout=15)
    return response.json()

def main():
    test_queries = [
        ("Интерстеллар", 2014),
        ("Начало", None),
        ("Побег из Шоушенка", None),
        ("The Matrix", 1999),
        ("")
    ]

    print("=" * 60)
    print("TMDB API Test - PoC")
    print("=" * 60)

    for query, year in test_queries:
        print(f"\nПоиск: '{query}' (год: {year or 'любой'})")
        print("-" * 40)

        try:
            results = search_movies(query, year)

            if "results" in results and len(results["results"]) > 0:
                print(f"Найдено фильмов: {len(results['results'])}")

                for i, movie in enumerate(results["results"][:3], 1):
                    title = movie.get("title", "N/A")
                    orig_title = movie.get("original_title", "")
                    year_release = movie.get("release_date", "")[:4] if movie.get("release_date") else "N/A"
                    overview = movie.get("overview", "")[:100] + "..." if movie.get("overview") else ""

                    print(f"\n{i}. {title} ({year_release})")
                    if orig_title != title:
                        print(f"   Оригинальное название: {orig_title}")
                    print(f"   Описание: {overview}")

                    if i == 1:
                        print("   Получаю подробности...")
                        details = get_movie_details(movie["id"])
                        if "runtime" in details:
                            print(f"   Длительность: {details['runtime']} мин")
                        if "genres" in details:
                            genres = ", ".join([g["name"] for g in details["genres"]])
                            print(f"   Жанры: {genres}")
                        if "vote_average" in details:
                            print(f"   Рейтинг TMDB: {details['vote_average']:.1f}/10")
            else:
                print("Ничего не найдено!")

        except Exception as e:
            print(f"Ошибка: {e}")

    print("\n" + "=" * 60)
    print("Тест завершён!")

if __name__ == "__main__":
    main()
