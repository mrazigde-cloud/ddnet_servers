import requests
from datetime import datetime, timezone, timedelta

URL = "https://status.tw"
HEADERS = {
    "User-Agent": "DDNet-GitHub-Monitor/1.0"
}

def fetch_servers():
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        # Поддержка разных форматов ответа API
        servers = data.get("servers", data) if isinstance(data, dict) else data
        return servers if isinstance(servers, list) else []
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return []

def update_readme(servers):
    msk_time = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M МСК")
    
    content = [
        "# Мониторинг серверов DDNet / Teeworlds",
        f"Последнее обновление: {msk_time}\n",
        "Для подключения откройте консоль в игре (F1) и введите команду из колонки подключения.\n",
        "| Название сервера | Карта | Игроки | Команда подключения |",
        "| :--- | :--- | :---: | :--- |"
    ]
    
    # Сортируем серверы по количеству игроков (от большего к меньшему)
    valid_servers = [s for s in servers if isinstance(s, dict)]
    valid_servers.sort(key=lambda x: len(x.get("clients", [])) if isinstance(x.get("clients"), list) else int(x.get("num_players", 0)), reverse=True)
    
    if valid_servers:
        for srv in valid_servers[:50]:  # Топ-50 активных серверов
            name = str(srv.get("name", "Без названия")).replace("|", "/")
            map_name = str(srv.get("map", {}).get("name", srv.get("map", "-"))).replace("|", "/")
            
            clients = srv.get("clients")
            num_players = len(clients) if isinstance(clients, list) else srv.get("num_players", 0)
            max_players = srv.get("max_clients", srv.get("max_players", "?"))
            
            ip = srv.get("ip", srv.get("address", ""))
            port = srv.get("port", "")
            connect_cmd = f"connect {ip}:{port}" if ip and port else f"{ip}"
            
            content.append(f"| {name} | {map_name} | {num_players}/{max_players} | {connect_cmd} |")
    else:
        content.append("| Список серверов временно пуст или источник недоступен. | - | - | - |")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(content))

if __name__ == "__main__":
    servers_list = fetch_servers()
    update_readme(servers_list)
