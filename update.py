import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

URL = "https://gs4u.net"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_servers():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    servers = []
    rows = soup.select("table tr")
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) >= 4 and ":" in row.text:
            text_parts = [p for p in cols if p]
            if len(text_parts) >= 3:
                servers.append(" | ".join(text_parts[:5]))
    return servers

def update_readme(servers):
    msk_time = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M МСК")
    
    content = [
        "# Мониторинг серверов DDNet / Teeworlds",
        f"Последнее обновление: {msk_time}\n",
        "Для подключения откройте консоль в игре (F1) и введите connect IP:порт.\n",
        "| Данные сервера (Название / IP / Карта / Онлайн) |",
        "| :--- |"
    ]
    
    if servers:
        for srv in servers[:40]:
            clean_srv = srv.replace("|", " — ")
            content.append(f"| {clean_srv} |")
    else:
        content.append("| Не удалось получить данные или сайт временно ограничил доступ. |")

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(content))

if name == "main":
    data = fetch_servers()
    update_readme(data)
