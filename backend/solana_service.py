import json
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from solders.message import Message
from solders.transaction import Transaction

# 1. Koneksi ke Devnet
RPC_URL = "https://api.devnet.solana.com"
client = Client(RPC_URL)

def log_net_report(label, amount_sol):
    """Fungsi kirim SOL dinamis berdasarkan berat dari Gemini"""
    try:
        # Load wallet PEMERINTAH
        with open("backend/my-wallet.json", "r") as f:
            secret = json.load(f)
        gov_keypair = Keypair.from_bytes(bytes(secret))
        
        # Alamat PHANTOM (Nelayan)
        PHANTOM_ADDRESS = "98bmG75oh3ZeUyDLrM5BkWu7HvzC7SV1ke1Wtr3C3AfW"
        receiver = Pubkey.from_string(PHANTOM_ADDRESS)
        
        # Konversi SOL ke Lamports (1 SOL = 1.000.000.000 lamports)
        lamports = int(amount_sol * 1_000_000_000)
        
        # Minimal transfer biasanya 1000 lamports untuk menghindari error
        if lamports < 1000: lamports = 1000

        print(f"--- Memproses Transaksi: {amount_sol} SOL ---")
        
        # 2. Ambil blockhash terbaru
        recent_blockhash = client.get_latest_blockhash().value.blockhash
        
        # 3. Buat Instruksi Transfer (Dinamis)
        ix = transfer(
            TransferParams(
                from_pubkey=gov_keypair.pubkey(),
                to_pubkey=receiver,
                lamports=lamports 
            )
        )
        
        # 4. Bungkus ke Message
        message = Message([ix], gov_keypair.pubkey())
        
        # 5. Buat Transaksi
        txn = Transaction([gov_keypair], message, recent_blockhash)
        
        # 6. Kirim
        res = client.send_transaction(txn)
        
        return res.value 
    except Exception as e:
        print(f"❌ Error Solana: {e}")
        return None