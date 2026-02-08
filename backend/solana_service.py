import os
import json
import requests
import base58
import base64
import uuid
from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
import time
import random

load_dotenv()

# ============================
# CONFIG (Ambil dari .env)
# ============================
SHYFT_API_KEY = os.getenv("SHYFT_API_KEY")
PINATA_JWT = os.getenv("PINATA_JWT")
UN_PK_STR = os.getenv("UN_PRIVATE_KEY")

# Inisialisasi Wallet
sender_keypair = Keypair.from_bytes(base58.b58decode(UN_PK_STR))
UN_ADDRESS_STR = str(sender_keypair.pubkey())

# Alamat Merkle Tree yang kamu temukan
MERKLE_TREE = "6Q6Bdyk5Gv5sXSgBo8vBAAanhrmAWN8LjhQ6aDzWSPhf"

print(f"[OK] GhostRay Backend Active")
print(f"[OK] Wallet: {UN_ADDRESS_STR}")

# ============================
# FUNCTION: UPLOAD JSON TO PINATA
# ============================
def upload_json_to_pinata(metadata):
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }
    payload = {
        "pinataMetadata": {"name": f"ghostray-{uuid.uuid4()}"},
        "pinataContent": metadata
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        if "IpfsHash" in data:
            return f"https://gateway.pinata.cloud/ipfs/{data['IpfsHash']}"
    except Exception as e:
        print(f"[ERROR] Pinata Upload: {e}")
    return None

# ============================
# FUNCTION: MINT CNFT (FINAL VERSION)
# ============================

def mint_impact_nft(receiver_addr, country, mass, reward, status):
    print(f"\n[STEP] Starting Minting Process for: {receiver_addr}")

    # 1. Build Metadata
    metadata = {
        "name": f"GhostRay: {country}",
        "symbol": "GRAY",
        "description": f"Verified debris collection in {country}.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Shark.jpg",
        "seller_fee_basis_points": 500, 
        "attributes": [
            {"trait_type": "Location", "value": country},
            {"trait_type": "Mass", "value": f"{mass}"},
            {"trait_type": "Status", "value": status},
            {"trait_type": "Reward", "value": str(reward)}
        ],
        "properties": {
            "creators": [{"address": UN_ADDRESS_STR, "share": 100}],
            "files": [{"uri": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Shark.jpg", "type": "image/jpg"}]
        }
    }

    # 2. Upload to IPFS
    metadata_uri = upload_json_to_pinata(metadata)
    if not metadata_uri:
        return "ERROR: IPFS Fail"
    print(f"[OK] Metadata IPFS: {metadata_uri}")

    # 3. Request Minting Draft from Shyft (WITH RETRY LOGIC)
    mint_url = "https://api.shyft.to/sol/v1/nft/compressed/mint"
    headers = {"x-api-key": SHYFT_API_KEY, "Content-Type": "application/json"}
    
    payload = {
        "network": "devnet",
        "creator_wallet": UN_ADDRESS_STR,
        "merkle_tree": MERKLE_TREE,
        "metadata_uri": metadata_uri,
        "receiver": receiver_addr,
        "fee_payer": UN_ADDRESS_STR,
        "seller_fee_basis_points": 500 
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = requests.post(mint_url, headers=headers, json=payload)
            
            # CHECK FOR RATE LIMIT (429)
            if res.status_code == 429:
                wait_time = (2 ** attempt) + random.random()
                print(f"[!] Rate Limit (429). Retrying in {wait_time:.2f}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
                continue

            data = res.json()
            
            if not data.get("success"):
                print("[FAILED] Shyft API Error:", data)
                return "Mint draft failed"

            # 4. SIGNING & BROADCAST
            encoded_tx = data["result"]["encoded_transaction"]
            tx_bytes = base64.b64decode(encoded_tx)
            raw_tx = VersionedTransaction.from_bytes(tx_bytes)
            signed_tx = VersionedTransaction(raw_tx.message, [sender_keypair])
            
            shyft_rpc_url = f"https://devnet-rpc.shyft.to?api_key={SHYFT_API_KEY}"
            rpc_payload = {
                "jsonrpc": "2.0", "id": 1,
                "method": "sendTransaction",
                "params": [
                    base64.b64encode(bytes(signed_tx)).decode("utf-8"), 
                    {"encoding": "base64"}
                ]
            }
            
            rpc_res = requests.post(shyft_rpc_url, json=rpc_payload)
            rpc_result = rpc_res.json()

            if "result" in rpc_result:
                sig = rpc_result["result"]
                print(f"\n[BOOM!] SUCCESS!")
                print(f"Signature: {sig}")
                return sig
            else:
                print("[ERROR] Broadcast failed")
                return None

        except Exception as e:
            print(f"[ERROR]: {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(2)
            
    return "Error: Max retries reached"
    
def send_reward_with_memo(receiver_pubkey_str, amount_sol, country="Verified", weight="Recycled"):
    """
    Transfer SOL otomatis dari UN_ADDRESS ke User.
    """
    url = "https://api.shyft.to/sol/v1/wallet/send_sol"
    headers = {
        "x-api-key": SHYFT_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "network": "devnet",
        "from_address": UN_ADDRESS_STR,
        "to_address": receiver_pubkey_str,
        "amount": float(amount_sol)
    }

    try:
        # 1. Build Transaksi via Shyft
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()

        if not data.get("success"):
            return f"Error: {data.get('message')}"

        # 2. Sign Otomatis pakai Keypair UN
        signer = Keypair.from_base58_string(UN_PK_STR)
        tx_bytes = base64.b64decode(data["result"]["encoded_transaction"])
        signed_tx = VersionedTransaction(VersionedTransaction.from_bytes(tx_bytes).message, [signer])

        # 3. Broadcast ke RPC
        rpc_url = f"https://devnet-rpc.shyft.to?api_key={SHYFT_API_KEY}"
        rpc_payload = {
            "jsonrpc": "2.0", "id": 1,
            "method": "sendTransaction",
            "params": [base64.b64encode(bytes(signed_tx)).decode("utf-8"), {"encoding": "base64"}]
        }

        rpc_res = requests.post(rpc_url, json=rpc_payload).json()
        
        if "result" in rpc_res:
            return rpc_res["result"] # Ini Signature-nya
        return f"Error: {rpc_res}"

    except Exception as e:
        return f"Error: {str(e)}"