import os
from web3 import Web3
from hexbytes import HexBytes
from dotenv import load_dotenv

load_dotenv()

ETH_ACCOUNT = os.getenv('ETH_ACCOUNT')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
ETH_HTTP_PROVIDER = os.getenv('ETH_HTTP_PROVIDER')
NULL_ADDRESS = '0x0000000000000000000000000000000000000000'
CHAIN_ID = 11155111

w3 = Web3(Web3.HTTPProvider(ETH_HTTP_PROVIDER))

print(ETH_ACCOUNT)
print(w3.from_wei(w3.eth.get_balance(ETH_ACCOUNT), 'ether'))

def create_provenance(web3, input, nonce):
    transaction = {
        'to': NULL_ADDRESS,
        'from': ETH_ACCOUNT,
        'value': 0,
        'data': input.encode('utf-8').hex(),
        'gas': 200000,
        'maxFeePerGas': web3.to_wei(100, 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei(2, 'gwei'),
        'nonce': nonce,
        'chainId': CHAIN_ID}
    signed = web3.eth.account.sign_transaction(transaction, ETH_PRIVATE_KEY)
    return web3.eth.send_raw_transaction(signed.rawTransaction)

nonce = w3.eth.get_transaction_count(ETH_ACCOUNT)
print(nonce)
while True:
    input_text = input('What text do you want to prove provenance on? ')
    print(HexBytes(create_provenance(w3, input_text, nonce)).hex())
    nonce += 1 