import requests
import json
import pprint
import base58

response = requests.get("https://api.dexscreener.com/latest/dex/search?q=SOL")
pair_address = response.json()['pairs'][11]['pairAddress']
chain_id = response.json()['pairs'][11]['chainId']
print(pair_address, ' ', chain_id)
web_address =f'https://api.dexscreener.com/latest/dex/pairs/{chain_id}/{pair_address}' 
new_response = requests.get(web_address)
# print('DEXSCREENER Search -----------------------')
# pprint.pprint(response.json()['pairs'][11])

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
# print('Pair Data ----------')
# pprint.pprint(new_response.json())

token_address = new_response.json()['pair']['baseToken']['address']
print('Token Address', token_address)
# byte_data = bytes.fromhex(token_address[2:])
# print('Byte Data - ', byte_data)
base58_data = base58.b58encode(bytes(token_address, 'utf-8'))
print('Base 58 Data - ', base58_data)
coin_address = '57LY5XaC9gVNxeqEUSANUpSwgdkGwULiZLZ5b95qpump'
# coin_address = '8bv72ei1fiHFDpz3GBmBYa3ecjWcqnsBvfhTVkhpump'
rugcheck_response = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{coin_address}/report")
data = rugcheck_response.json()
# print('Rugcheck Response ----------' )
# pprint.pprint(rugcheck_response.json())
# is_good = data.get("score", "") == "good"
# print(is_good)