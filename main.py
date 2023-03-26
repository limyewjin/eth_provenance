import os
from web3 import Web3
from hexbytes import HexBytes
from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import hashlib

import datastore

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

# Create a sub-application, in order to access just the query endpoint in an OpenAPI schema, found at http://0.0.0.0:8000/sub/openapi.json when the app is running locally
sub_app = FastAPI(
    title="ETH Provenance API",
    description="An API for creating ETH provenance",
    version="1.0.0",
    servers=[{"url": "https://your-app-url.com"}],
)
app.mount("/sub", sub_app)

bearer_scheme = HTTPBearer()
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
assert BEARER_TOKEN is not None

ETH_ACCOUNT = os.getenv('ETH_ACCOUNT')
ETH_PRIVATE_KEY = os.getenv('ETH_PRIVATE_KEY')
ETH_HTTP_PROVIDER = os.getenv('ETH_HTTP_PROVIDER')
NULL_ADDRESS = '0x0000000000000000000000000000000000000000'
CHAIN_ID = 11155111
EXPLORER_URL_BASE = "https://sepolia.etherscan.io/tx/"


def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return credentials


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
    tx_hash = HexBytes(web3.eth.send_raw_transaction(signed.rawTransaction)).hex()
    return tx_hash, f"{EXPLORER_URL_BASE}{tx_hash}"


from pydantic import BaseModel
from typing import List

class CertifyResponse(BaseModel):
    tx_hash: str
    explorer_url: str

class CertifyRequestMulti(BaseModel):
    data: List[str]

class CertifyResponseMulti(BaseModel):
    tx_hashes: List[str]
    explorer_urls: List[str]

async def get_file_content(file: UploadFile) -> str:
    contents = await file.read()
    return contents

@app.post(
    "/certify-file",
    response_model=CertifyResponse,
)
async def certify_file(
    file: UploadFile = File(...),
    token: HTTPAuthorizationCredentials = Depends(validate_token),
):
    content = await get_file_content(file)
    try:
        digest = hashlib.sha256(content).hexdigest()
        nonce = w3.eth.get_transaction_count(ETH_ACCOUNT)
        tx_hash, explorer_url = create_provenance(w3, digest, nonce)
        return CertifyResponse(tx_hash=tx_hash, explorer_url=explorer_url)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"str({e})")


@app.post(
    "/certify-multi",
    response_model=CertifyResponseMulti,
)
async def certify_multi(
    request: CertifyRequestMulti = Body(...),
    token: HTTPAuthorizationCredentials = Depends(validate_token),
):
    try:
        # create SHA256 digest for each document
        digests = [hashlib.sha256(data).hexdigest() for data in request.data]
        # create provenance for each digest on the Ethereum blockchain
        tx_hashes = []
        explorer_urls = []
        for digest in digests:
            nonce = w3.eth.get_transaction_count(ETH_ACCOUNT)
            tx_hash, explorer_url = create_provenance(w3, digest, nonce)
            tx_hashes.append(tx_hash)
            explorer_urls.append(explorer_url)
        return CertifyResponseMulti(tx_hashes=tx_hashes, explorer_urls=explorer_urls)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")


@app.on_event("startup")
async def startup():
    global w3, ds
    w3 = Web3(Web3.HTTPProvider(ETH_HTTP_PROVIDER))
    ds = datastore.DataStore()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
