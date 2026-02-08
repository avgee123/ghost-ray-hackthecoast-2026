import os
import json
import requests
import base58 # Tambahkan ini (pip install base58)
from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solana.rpc.api import Client
from solders.transaction import Transaction
from solders.instruction import Instruction

load_dotenv()

# --- CONFIGURATION ---
client = Client("https://api.devnet.solana.com")
SHYFT_API_KEY = os.getenv("SHYFT_API_KEY")

# Mengambil dompet UN dari Private Key di .env
un_pk_str = os.getenv("UN_PRIVATE_KEY")
sender_keypair = Keypair.from_bytes(base58.b58decode(un_pk_str))
UN_ADDRESS_STR = str(sender_keypair.pubkey())

MEMO_PROGRAM_ID = Pubkey.from_string("MemoSq4gqAB2Cc9BnZ98zWn8YSbt9YEzMBeUZ3q6P40")

def send_reward_with_memo(country, weight, amount_sol, receiver_pubkey_str):
    """Kirim SOL dari UN ke Nelayan"""
    receiver_pubkey = Pubkey.from_string(receiver_pubkey_str)
    lamports = int(amount_sol * 1_000_000_000)
    
    transfer_ix = transfer(TransferParams(
        from_pubkey=sender_keypair.pubkey(),
        to_pubkey=receiver_pubkey,
        lamports=lamports
    ))

    memo_data = {"org": "UN-GhostRay", "loc": country, "mass": weight, "status": "FINALIZED"}
    memo_ix = Instruction(
        program_id=MEMO_PROGRAM_ID,
        data=json.dumps(memo_data).encode('utf-8'),
        accounts=[]
    )

    txn = Transaction()
    txn.add(transfer_ix)
    txn.add(memo_ix)

    # Kirim transaksi menggunakan dompet UN
    result = client.send_transaction(txn, sender_keypair)
    return str(result.value)

def mint_impact_nft(receiver_addr, country, mass, reward, status):
    """Mencatat pengumpulan di Page 1"""
    url = "https://api.shyft.to/sol/v1/nft/compressed/mint"
    headers = {"Content-Type": "application/json", "x-api-key": SHYFT_API_KEY}
    
    payload = {
        "network": "devnet",
        "creator_wallet": UN_ADDRESS_STR, # Gunakan alamat UN
        "metadata": {
            "name": f"Ocean Guardian: {country}",
            "symbol": "GRAY",
            "description": f"Verified debris collection in {country}.",
            "attributes": [
                {"trait_type": "Location", "value": country},
                {"trait_type": "Mass", "value": f"{mass}kg"},
                {"trait_type": "Status", "value": status},
                {"trait_type": "Reward_Value", "value": f"{reward}"}
            ],
            "image": "https://gateway.pinata.cloud/ipfs/QmZ..." 
        },
        "receiver": receiver_addr, # Dikirim ke Nelayan
        "fee_payer": UN_ADDRESS_STR # UN yang bayar biaya minting
    }
    # ... (sisanya sama)

def update_to_recycled(nft_address):
    """Update status NFT di Page 3"""
    url = "https://api.shyft.to/sol/v1/nft/compressed/update"
    headers = {"Content-Type": "application/json", "x-api-key": SHYFT_API_KEY}
    
    payload = {
        "network": "devnet",
        "nft_address": nft_address,
        "authority_address": UN_ADDRESS_STR, # UN sebagai otoritas
        "attributes": [
            {"trait_type": "Status", "value": "RECYCLED"}
        ]
    }
    # ... (sisanya sama)

    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error Updating NFT: {e}")
        return None