import asyncio
import json
import httpx
import requests
from colorama import Fore, init

webhook_url = "https://discord.com/api/webhooks/1094615841066205234/54Ano1i_jejTyf3XIzczdIV0RKKUs0e9Wkt8IZ50mlPcJO3eK-tYVAXmReV1uHfLQ-WA"
init(autoreset=True)

async def try_vanity(vanity: str, guild: str, token: str, session: httpx.AsyncClient, tried_vanities: set):
    while True:
        if vanity.casefold() in tried_vanities: 
            break

        resp = await session.patch(
            f"https://discord.com/api/v9/guilds/{guild}/vanity-url",
            data=json.dumps({"code": vanity.casefold()}),
            headers={"Content-Type": "application/json", "Authorization": token},
        )

        if resp.status_code == 200: 
            tried_vanities.add(vanity.casefold()) 
            requests.post(webhook_url, json={"content": f"Yeni URL: discord.gg/{vanity} başarıyla çekildi | GG :smile: ||@everyone||", "username": "berk"})
            print(f"{Fore.LIGHTGREEN_EX}-> {vanity} URL'si başarıyla alındı.")
            break 

        elif resp.status_code == 429: 
            retry_after = int(resp.headers["Retry-After"])
            print(f"{Fore.YELLOW}{vanity} URL'si alınamadı. Yeniden denemek için {retry_after} saniye bekleyin.")
            await asyncio.sleep(retry_after)

        elif resp.status_code in [401, 403]: 
            print(f"{Fore.RED}Geçersiz token.")
            break

        else: 
            print(f"{Fore.RED}{vanity} URL'si alınamadı. Hata kodu: {resp.status_code}")

        await asyncio.sleep(1.9)

async def main():
    token = input("Token -> ").strip()

    while True:
        try:
            num_urls = int(input("Kaç URL almak istersiniz? "))
            if num_urls <= 0:
                raise ValueError("Lütfen pozitif bir tamsayı girin.")
            break
        except ValueError as e:
            print(f"{Fore.RED}{e}")
            continue
    
    urls = []
    for i in range(num_urls):
        url = input(f"Alınacak URL {i+1} -> ").strip()
        urls.append(url)

    guild = input("Alınacak Sunucu ID -> ").strip()

    tried_vanities = set() 
    async with httpx.AsyncClient() as session:
        tasks = [asyncio.create_task(try_vanity(url, guild, token, session, tried_vanities)) for url in urls]
        await asyncio.gather(*tasks)

asyncio.run(main())
