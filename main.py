import os
from web3 import Web3
from hexbytes import HexBytes
from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from hashlib import sha256

import datastore

from dotenv import load_dotenv
load_dotenv()

def get_document_from_file(file: UploadFile) -> str:
    contents = file.file.read()
    return sha256(contents).hexdigest()

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
    return web3.eth.send_raw_transaction(signed.rawTransaction)


from pydantic import BaseModel
from typing import List

class UpsertRequest(BaseModel):
    documents: List[str]

class UpsertResponse(BaseModel):
    ids: List[str]
    tx_hash: str

# If using the upsert route with multiple documents and tx_hashes:
class UpsertResponseMulti(BaseModel):
    ids: List[str]
    tx_hashes: List[str]


async def get_document_from_file(file: UploadFile) -> str:
    contents = await file.read()
    return sha256(contents).hexdigest()

@app.post(
    "/upsert-file",
    response_model=UpsertResponse,
)
async def upsert_file(
    file: UploadFile = File(...),
    token: HTTPAuthorizationCredentials = Depends(validate_token),
):
    document = await get_document_from_file(file)
    # create SHA256 digest of the document
    digest = hashlib.sha256(document).hexdigest()
    # create provenance on the Ethereum blockchain
    nonce = w3.eth.get_transaction_count(ETH_ACCOUNT)
    tx_hash = create_provenance(w3, digest, nonce)
    try:
        ids = await ds.upsert([document])
        return UpsertResponse(ids=ids, tx_hash=tx_hash)
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"str({e})")


@app.post(
    "/upsert",
    response_model=UpsertResponse,
)
async def upsert(
    request: UpsertRequest = Body(...),
    token: HTTPAuthorizationCredentials = Depends(validate_token),
):
    try:
        documents = request.documents
        # create SHA256 digest for each document
        digests = [hashlib.sha256(doc).hexdigest() for doc in documents]
        # create provenance for each digest on the Ethereum blockchain
        tx_hashes = []
        for digest in digests:
            nonce = w3.eth.get_transaction_count(ETH_ACCOUNT)
            tx_hashes.append(create_provenance(w3, digest, nonce))
        ids = await ds.upsert(documents)
        return UpsertResponse(ids=ids, tx_hashes=tx_hashes)
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
