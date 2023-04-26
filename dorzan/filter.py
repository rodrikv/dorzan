import time
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json
import random
import string
import dotenv
import os

dotenv.load_dotenv("env")

username = os.getenv("SUDO_USERNAME")
password = os.getenv("SUDO_PASSWORD")
marzban_host = os.getenv("XRAY_SUBSCRIPTION_URL_PREFIX")
cloudflare_email = os.getenv("CLOUDFLARE_EMAIL")
zone_identifier = os.getenv("ZONE_IDENTIFIER")
api_key = os.getenv("API_KEY")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", None)

cloudflare_api = "https://api.cloudflare.com"
marzban_headers: dict = {
    'User-Agent': 'own-application/1.0.0',
    'Content-Type': 'application/x-www-form-urlencoded'
}
cloudflare_headers = {
    'Content-Type': "application/json",
    'X-Auth-Email': cloudflare_email,
    'Authorization': api_key
}

class TokenError(Exception):
    pass

def get_server_ip():
    with urlopen("https://api.ipify.org?format=json") as res:
        return json.loads(res.read().decode())["ip"]

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def request(url, data=None, headers=None, method="GET") -> dict:
    httprequest = Request(
        url,
        data=data,
        method=method,
        headers=headers
    )
    for _ in range(3):
            with urlopen(httprequest) as response:
                print(response.getcode())
                response_data = response.read().decode()
                print(response_data)
                return json.loads(response_data)

def request_token(username, password):
    token_url = marzban_host + "/api/admin/token"

    data = {
        "username": username,
        "password": password
    }

    return request(
        token_url,
        data=urlencode(data).encode(),
        headers=marzban_headers,
        method="POST"
    )

def get_hosts(token):
    hosts_url = marzban_host + "/api/hosts"
    new_headers = marzban_headers.copy()
    new_headers.setdefault("Authorization", "Bearer " + token)
    return request(
        hosts_url,
        headers=new_headers,
    )

def set_hosts(hosts, token):
    hosts_url = marzban_host + "/api/hosts"
    new_headers = marzban_headers.copy()
    new_headers.setdefault("Authorization", "Bearer " + token)
    new_headers['Content-Type'] = "application/json"
    return request(
        hosts_url,
        headers=new_headers,
        data=json.dumps(hosts).encode(),
        method="PUT"
    )

def set_dns_cloudflare(name, content):
    dns_records_url = cloudflare_api + f"/client/v4/zones/{zone_identifier}/dns_records"
    payload = {
        "content": content,
        "name": name,
        "proxied": True,
        "type": "A",
        "comment": "Another not filtering domain",
        "ttl": 3600
    }
    return request(
        url=dns_records_url,
        data=json.dumps(payload).encode(),
        headers=cloudflare_headers,
        method="POST"
    )


if __name__ == "__main__":
    bot = None
    if telegram_bot_token:
        from telegram.bot import TelegramBot
        bot = TelegramBot(telegram_bot_token, [os.getenv("TELEGRAM_ADMIN_ID")])
    for i in range(3):
        e = None
        try:
            token_response = request_token(username, password)
            hosts = get_hosts(token_response["access_token"])
            cloudflare_res = set_dns_cloudflare(get_random_string(16), get_server_ip())

            sni = cloudflare_res["result"]["name"]

            for inbound_tag, inbounds in hosts.items():
                for settings in inbounds:
                    if "direct" in settings["remark"]:
                        continue
                    settings["sni"] = sni
                    settings["host"] = sni

            set_hosts(hosts, token_response["access_token"])
            if bot:
                text = f"""
                Hosts updated successfully:
                SNI: `{sni}`
                Host: `{sni}`
                """

                bot.broadcast_admins("Hosts updated successfully: ")
                break
        except Exception as e:
            if bot:
                bot.broadcast_admins(f"Error in updating hosts ({i+1}/3): `{e}`")

        time.sleep(5)
