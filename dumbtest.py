import requests
import json
import pprint

response = requests.get("https://api.dexscreener.com/latest/dex/search?q=SOL")
pair_address = response.json()['pairs'][11]['pairAddress']
chain_id = response.json()['pairs'][11]['chainId']
web_address =f'https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}' 
new_response = requests.get(web_address)
print('DEXSCREENER Search -----------------------')
pprint.pprint(response.json()['pairs'][11])

rugcheck_login_request = {
  "message": {
    "message": "Sign-in to Rugcheck.xyz",
    "publicKey": "string",
    "timestamp": 0
  },
  "signature": {
    "data": [
      0
    ],
    "type": "string"
  },
  "wallet": "string"
}

# pprint.pprint(rugcheck_response.json())

# for pair in response.json()['pairs']:
#     dev_data = pair.get("info", {}).get("dev", {}).get("address", "").lower()
#     pprint.pprint(dev_data)
# pprint.pprint(len(response.json()['pairs']))
print('Pair Data ----------')
pprint.pprint(new_response.json())

token_address = new_response.json()['pair']['baseToken']['address']
print(token_address)
rugcheck_response = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{token_address}/report")
print('Rugcheck Response ----------' )
pprint.pprint(rugcheck_response.json())