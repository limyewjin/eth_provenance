from dotenv import load_dotenv
import os

load_dotenv()
ETH_ACCOUNT = os.environ["ETH_ACCOUNT"]
ETH_PRIVATE_KEY = os.environ["ETH_PRIVATE_KEY"]
ETH_HTTP_PROVIDER = os.environ["ETH_HTTP_PROVIDER"]

from web3 import Web3
w3 = Web3(Web3.HTTPProvider(ETH_HTTP_PROVIDER))

print(w3.from_wei(w3.eth.get_balance(ETH_ACCOUNT), 'ether'))

def create_provenance(web3, input):
  transaction= {
    'to': '0x0000000000000000000000000000000000000000',
    'from': ETH_ACCOUNT,
    'value': 0,
    'data': input.encode('utf-8').hex(),
    'gas': 200000,
    'maxFeePerGas': web3.to_wei(100, 'gwei'),
    'maxPriorityFeePerGas': web3.to_wei(2, 'gwei'),
    'nonce': 1,
    'chainId':11155111}
  signed = web3.eth.account.sign_transaction(transaction, ETH_PRIVATE_KEY)
  return web3.eth.send_raw_transaction(signed.rawTransaction)

from hexbytes import HexBytes
print(HexBytes(create_provenance(w3, "this is a test")))
