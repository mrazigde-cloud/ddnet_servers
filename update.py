import json
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
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("servers", [])
        return []
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return []

def _map_name(srv):
    map_obj = srv.get("map") or {}
    if isinstance(map_obj, dict):
        return str(map_obj.get("name", "-") or "-")
    return str(map_obj or "-")

def _game_type(srv):
    gt = srv.get("gameType") or {}
    if isinstance(gt, dict):
        return str(gt.get("name", "DDraceNetwork") or "DDraceNetwork")
    return "DDraceNetwork"

def _version(srv):
    ver = srv.get("version") or {}
    if isinstance(ver, dict):
        return str(ver.get("version", "") or "")
    return ""

def update_readme(servers):
    msk_time = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M МСК")

    lines = [
        "# Мониторинг серверов DDNet / Teeworlds",
        f"Последнее обновление: {msk_time}\n",
        "Источник: [status.tw](https://status.tw) (`api.status.tw/server/list`)\n",
        "Для подключения: консоль (F1) → команда из колонки.\n",
        "| Название сервера | Карта | Игроки | Команда подключения |",
        "| :--- | :--- | :---: | :--- |",
    ]

    valid = [s for s in servers if isinstance(s, dict)]
    valid.sort(
        key=lambda x: int(x.get("numClients") or x.get("numPlayers") or 0),
        reverse=True,
    )

    if valid:
        for srv in valid[:50]:
            name = str(srv.get("name", "Без названия")).replace("|", "/")
            map_name = _map_name(srv).replace("|", "/")
            num = int(srv.get("numClients") or srv.get("numPlayers") or 0)
            max_p = srv.get("maxClients") or srv.get("maxPlayers") or "?"
            ip = srv.get("ip", "")
            port = srv.get("port", "")
            connect = f"connect {ip}:{port}" if ip and port else "-"
            lines.append(f"| {name} | {map_name} | {num}/{max_p} | `{connect}` |")
    else:
        lines.append("| Список серверов временно пуст или источник недоступен. | - | - | - |")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"README.md: {min(50, len(valid))} servers")

def write_servers_json(servers):
    """Формат совместим с CServerBrowserHttp::Parse (master DDNet)."""
    out = {"servers": []}

    for srv in servers:
        if not isinstance(srv, dict):
            continue
        ip = srv.get("ip")
        port = srv.get("port")
        if not ip or port is None:
            continue

        clients_in = srv.get("clients") or []
        clients_out = []
        if isinstance(clients_in, list):
            for c in clients_in:
                if not isinstance(c, dict):
                    continue
                country = -1
                ctry = c.get("country")
                if isinstance(ctry, dict) and ctry.get("code") is not None:
                    try:
                        country = int(ctry.get("code"))
                    except (TypeError, ValueError):
                        country = -1
                clients_out.append({
                    "name": str(c.get("name", "")),
                    "clan": str(c.get("clan", "") or ""),
                    "country": country,
                    "score": int(c.get("score", 0) or 0),
                    "is_player": bool(c.get("isPlayer", True)),
                })

        max_clients = int(srv.get("maxClients") or srv.get("maxPlayers") or 64)
        max_players = int(srv.get("maxPlayers") or srv.get("maxClients") or max_clients)

        out["servers"].append({
            "addresses": [f"tw-0.6+udp://{ip}:{port}"],
            "info": {
                "name": str(srv.get("name", "")),
                "map": {"name": _map_name(srv)},
                "game_type": _game_type(srv),
                "version": _version(srv),
                "max_clients": max_clients,
                "max_players": max_players,
                "passworded": bool(srv.get("hasPassword")),
                "clients": clients_out,
            },
        })

    with open("servers.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"servers.json: {len(out['servers'])} servers")

if __name__ == "__main__":
    servers_list = fetch_servers()
    print(f"fetched: {len(servers_list)}")
    update_readme(servers_list)
    write_servers_json(servers_list)
