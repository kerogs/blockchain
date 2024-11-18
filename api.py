import os
import json
from fastapi import FastAPI, HTTPException
from helpers.blockchain import *  
from helpers.info import * 


app = FastAPI()

# === API endpoints ===

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