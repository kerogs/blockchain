import os
import json
from fastapi import FastAPI, HTTPException
from helpers.blockchain import *  
from helpers.info import * 


# === FastAPI ===
app = FastAPI()

# === Init blockchain ===
blockchain = Blockchain(max_supply=200, initial_balance=200,gas_fee=0.01)

# === API endpoints ===

@app.get("/", summary="get if the api is running")
async def root() -> dict:
    return {"status": "API is running"}

@app.get("/info", summary="Get general information about blockchain and the API")
async def info() -> dict:
    """
    Returns general information about blockchain and the API :
    - Link to GitHub repository.
    - Blockchain version.
    - Cryptocurrency information (name, symbol, value).
    - API version.
    """
    blockchain_path = "blockchain_state.json"
    if not os.path.exists(blockchain_path):
        blockchain_exist = False
        crypto_value = None 
    else:
        blockchain_exist = True
        with open(blockchain_path, "r") as file:
            contents = json.load(file)
        crypto_value = contents.get("ksc_to_eur_rate", "Not available, no blockchain data found.") 

    return {
        "status": "API is running",
        "github_version": "1.1.2-beta", 
        "github_repo": "https://github.com/kerogs/blockchain",
        "blockchain": {
            "version": BLOCKCHAIN_VERSION,
            "attributes": {
                "exist": blockchain_exist,
                "crypto": {
                    "cryptoName": CRYPTO_NAME,
                    "cryptoSymbol": CRYPTO_SYMBOL,
                    "crypto_value": crypto_value,
                },
            },
        },
        "api": {
            "version": API_VERSION,
        },
    }


@app.get("/info/{attr}", summary="Get specific information")
async def info_focus(attr: str) -> dict:
    """
    Returns specific information about :
    - The blockchain: “blockchain”
    - The API : “api”
    - The cryptocurrency : “crypto”
    - The GitHub repository: “github”
    """
    data = await info()

    if attr == "blockchain":
        return data["blockchain"]
    elif attr == "api":
        return data["api"]
    elif attr == "crypto":
        return data["blockchain"]["attributes"]["crypto"]
    elif attr == "github":
        return {"github_repo": data["github_repo"]}
    else:
        raise HTTPException(status_code=404, detail=f"Attribut '{attr}' not found.")


@app.get("/blockchain", summary="Obtain detailed blockchain data")
async def get_blockchain_info() -> dict:
    """
    Returns detailed blockchain data:
    - Indicates whether it exists.
    - Attributes contained in blockchain_state.json (if any).
    """
    blockchain_path = "blockchain_state.json"
    if not os.path.exists(blockchain_path):
        return {
            "blockchain_exist": False,
            "attributes": "No blockchain data found.",
        }

    with open(blockchain_path, "r") as file:
        contents = json.load(file)

    return {
        "blockchain_exist": True,
        "attributes": contents,
    }
    
@app.post("/blockchain/give/{admin_key}/{address}/{amount}", summary="Give crypto to an address")
def give_money(admin_key: str, address: str, amount: float) -> dict:
    # give crypto to an address
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden. Invalid admin key.")
    
    r = blockchain.add_transaction(Transaction("kerogscoinminer", address, amount))
    
    r2 = blockchain.save_state()
    
    r3 = blockchain.mine_pending_transactions("kerogscoinminer")

    return {
        "transaction": r,
        "data": r2,
        "mine": r3,
        "attributes": {
            "to":address,
            "amount":amount
        }
    }
    