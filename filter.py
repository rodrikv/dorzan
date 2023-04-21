from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json
import random
import string

username = "USERNAME"
password = "PASSWORD"
cloudflare_api = "https://api.cloudflare.com"
marzban_host = "https://example.com"
cloudflare_email = "user@exmple.com"
zone_identifier = "xxx"
api_key = 'Bearer xxx'
marzban_headers: dict = {
    'User-Agent': 'own-application/1.0.0',
    'Content-Type': 'application/x-www-form-urlencoded'
}
cloudflare_headers = {
    'Content-Type': "application/json",
    'X-Auth-Email': cloudflare_email,
    'Authorization': api_key
}
server_ip = "x.x.x.x"

class TokenError(Exception):
    pass

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
    token_response = request_token(username, password)
    hosts = get_hosts(token_response["access_token"])
    cloudflare_res = set_dns_cloudflare(get_random_string(16), server_ip)
    
    if not cloudflare_res:
        SystemExit()

    sni = cloudflare_res["result"]["name"]

    for inbound_tag, inbounds in hosts.items():
        for settings in inbounds:
            settings["sni"] = sni
            settings["host"] = sni

    set_hosts(hosts, token_response["access_token"])
