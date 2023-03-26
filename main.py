from dotenv import load_dotenv
import os

load_dotenv()
eth_account = os.environ["ETH_ACCOUNT"]
eth_private_key = os.environ["ETH_PRIVATE_KEY"]
eth_http_provider = os.environ["ETH_HTTP_PROVIDER"]

from web3 import Web3
w3 = Web3(Web3.HTTPProvider(eth_http_provider))

print(w3.from_wei(w3.eth.get_balance(eth_account), 'ether'))
