import requests
from datetime import datetime, timezone, timedelta

URL = "https://api.status.tw/server/list"
HEADERS = {
    "User-Agent": "DDNet-GitHub-Monitor/1.0",
    "Accept": "application/json",
}

def fetch_servers():
    try:
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else data.get("servers", [])
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return []

def update_readme(servers):
    msk_time = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M МСК")

    content = [
        "# Мониторинг серверов DDNet / Teeworlds",
        f"Последнее обновление: {msk_time}\n",
        "Источник: [status.tw](https://status.tw) (`api.status.tw/server/list`)\n",
        "Для подключения: консоль (F1) → команда из колонки.\n",
        "| Название сервера | Карта | Игроки | Команда подключения |",
        "| :--- | :--- | :---: | :--- |",
    ]

    valid = [s for s in servers if isinstance(s, dict)]
    valid.sort(key=lambda x: int(x.get("numClients") or x.get("numPlayers") or 0), reverse=True)

    if valid:
        for srv in valid[:50]:
            name = str(srv.get("name", "Без названия")).replace("|", "/")
            map_obj = srv.get("map") or {}
            map_name = str(map_obj.get("name", "-") if isinstance(map_obj, dict) else map_obj).replace("|", "/")

            num = int(srv.get("numClients") or srv.get("numPlayers") or 0)
            max_p = srv.get("maxClients") or srv.get("maxPlayers") or "?"

            ip = srv.get("ip", "")
            port = srv.get("port", "")
            connect = f"connect {ip}:{port}" if ip and port else "-"

            content.append(f"| {name} | {map_name} | {num}/{max_p} | `{connect}` |")
    else:
        content.append("| Список серверов временно пуст или источник недоступен. | - | - | - |")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(content) + "\n")

if __name__ == "__main__":
    update_readme(fetch_servers())
