import requests
import json
import pprint

response = requests.get("https://api.dexscreener.com/latest/dex/search?q=SOL")
pair_address = response.json()['pairs'][1]['pairAddress']
chain_id = response.json()['pairs'][1]['chainId']
web_address =f'https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}' 
new_response = requests.get(web_address)

# for pair in response.json()['pairs']:
#     dev_data = pair.get("info", {}).get("dev", {}).get("address", "").lower()
#     pprint.pprint(dev_data)
# pprint.pprint(len(response.json()['pairs']))
pprint.pprint(new_response.json())