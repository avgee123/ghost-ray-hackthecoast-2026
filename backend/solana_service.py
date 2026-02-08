import json
import requests
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solana.rpc.api import Client
from solders.transaction import Transaction
from solders.instruction import Instruction

# Konfigurasi Network & Wallet
client = Client("https://api.devnet.solana.com")
with open("backend/my-wallet.json", "r") as f:
    secret = json.load(f)
sender_keypair = Keypair.from_bytes(bytes(secret))

# API Config
MEMO_PROGRAM_ID = Pubkey.from_string("MemoSq4gqAB2Cc9BnZ98zWn8YSbt9YEzMBeUZ3q6P40")
SHYFT_API_KEY = "Kjqw1pkOSTd9LwBI" 

def send_reward_with_memo(country, weight, multiplier, amount_sol, receiver_pubkey_str):
    """Fungsi ini dipanggil oleh Recycler di Page 3 saat melakukan pembayaran"""
    receiver_pubkey = Pubkey.from_string(receiver_pubkey_str)
    
    lamports = int(amount_sol * 1_000_000_000)
    transfer_ix = transfer(TransferParams(
        from_pubkey=sender_keypair.pubkey(),
        to_pubkey=receiver_pubkey,
        lamports=lamports
    ))

    memo_data = {
        "org": "UN-GhostRay",
        "loc": country,
        "mass": weight,
        "status": "FINALIZED"
    }
    memo_ix = Instruction(
        program_id=MEMO_PROGRAM_ID,
        data=json.dumps(memo_data).encode('utf-8'),
        accounts=[]
    )

    txn = Transaction()
    txn.add(transfer_ix)
    txn.add(memo_ix)

    result = client.send_transaction(txn, sender_keypair)
    return str(result.value)

def mint_impact_nft(receiver_addr, country, mass, reward, status):
    """Dipanggil di Page 1: Mencatat pengumpulan pertama kali"""
    url = "https://api.shyft.to/sol/v1/nft/compressed/mint"
    headers = {"Content-Type": "application/json", "x-api-key": SHYFT_API_KEY}
    
    payload = {
        "network": "devnet",
        "creator_wallet": "98bmG75oh3ZeUyDLrM5BkWu7HvzC7SV1ke1Wtr3C3AfW",
        "metadata": {
            "name": f"Ocean Guardian: {country}",
            "symbol": "GRAY",
            "description": f"Verified debris collection in {country}.",
            "attributes": [
                {"trait_type": "Location", "value": country},
                {"trait_type": "Mass", "value": f"{mass}kg"},
                {"trait_type": "Status", "value": status},
                {"trait_type": "Reward_Value", "value": f"{reward}"},
                {"trait_type": "Collector_Wallet", "value": receiver_addr}
            ],
            "image": "https://gateway.pinata.cloud/ipfs/QmZ..." 
        },
        "receiver": receiver_addr,
        "fee_payer": "98bmG75oh3ZeUyDLrM5BkWu7HvzC7SV1ke1Wtr3C3AfW"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        return res_data["result"]["mint"] if res_data.get("success") else None
    except Exception as e:
        print(f"Error Minting: {e}")
        return None

def update_to_recycled(nft_address):
    """Dipanggil di Page 3: Merubah status NFT di Blockchain"""
    url = "https://api.shyft.to/sol/v1/nft/compressed/update"
    headers = {"Content-Type": "application/json", "x-api-key": SHYFT_API_KEY}
    
    payload = {
        "network": "devnet",
        "nft_address": nft_address,
        "authority_address": "98bmG75oh3ZeUyDLrM5BkWu7HvzC7SV1ke1Wtr3C3AfW",
        "attributes": [
            {"trait_type": "Status", "value": "RECYCLED"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error Updating NFT: {e}")
        return None