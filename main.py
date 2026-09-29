import argparse
import sys
import time
import urllib.error
import urllib.request

CHUNK_SIZE = 64 * 1024  # читаем ответ кусками по 64 КБ
MB = 1024 * 1024


def download(url: str, timeout: float) -> tuple[int, float]:
    """Скачивает url целиком. Возвращает (байт получено, секунд затрачено)."""
    
    # Без сжатия и кеша
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "speedtest-script/1.0",
            "Cache-Control": "no-cache",
            "Accept-Encoding": "identity",
        },
    )
    total = 0
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
    elapsed = time.perf_counter() - start
    return total, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(description="Замер скорости скачивания по URL.")
    parser.add_argument("url", help="адрес файла/картинки для скачивания")
    parser.add_argument("-n", "--requests", type=int, default=10,
                        help="количество последовательных запросов (по умолчанию 10)")
    parser.add_argument("-t", "--timeout", type=float, default=30.0,
                        help="таймаут одного запроса в секундах (по умолчанию 30)")
    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        print("Ошибка: адрес должен начинаться с http:// или https://", file=sys.stderr)
        return 2

    print(f"Цель: {args.url}")
    print(f"Запросов: {args.requests}\n")

    times: list[float] = []
    total_bytes = 0

    for i in range(1, args.requests + 1):
        try:
            size, elapsed = download(args.url, args.timeout)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"[{i:>2}/{args.requests}] ошибка: {exc}")
            continue

        times.append(elapsed)
        total_bytes += size
        speed = size / MB / elapsed if elapsed > 0 else 0.0
        print(f"[{i:>2}/{args.requests}] {size / MB:7.2f} МБ за {elapsed:6.2f} с  ->  {speed:6.2f} МБ/с")

    if not times:
        print("\nНи один запрос не завершился успешно.", file=sys.stderr)
        return 1

    total_time = sum(times)
    avg_time = total_time / len(times)
    speed_mb = total_bytes / MB / total_time
    speed_mbit = speed_mb * 8

    print("\n--- Итог ---")
    print(f"Успешных запросов:    {len(times)} из {args.requests}")
    print(f"Среднее время запроса: {avg_time:.2f} с")
    print(f"Скачано всего:         {total_bytes / MB:.2f} МБ")
    print(f"Средняя скорость:      {speed_mb:.2f} МБ/с ({speed_mbit:.2f} Мбит/с)")
    return 0


if __name__ == "__main__":
    sys.exit(main())