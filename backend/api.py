import cv2
import os
import json
import requests
import PIL.Image
import google.generativeai as genai
from ultralytics import YOLO
import solana_service
from engine import SustainabilityEngine
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel

# Load Environment Variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SKEMA DATA & VARIABLE GLOBAL ---
class RecycleRequest(BaseModel):
    nft_address: str
    collector_wallet: str
    amount: float

# Variable ini menyimpan hasil scan terakhir agar bisa dibaca Page 3
last_scan_data = {
    "items_count": 0,
    "reward_sol": 0.0,
    "collector_wallet": "",
    "nft_address": ""
}

# --- KONFIGURASI AI & MODEL ---
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')
yolo_model = YOLO('best.pt') 
engine = SustainabilityEngine('WorldSustainabilityDataset.csv')

cap = cv2.VideoCapture(0)

def get_auto_country_code():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        return data.get('country_code_iso3', 'CAN') 
    except:
        return 'CAN' 

@app.get("/video_feed")
def video_feed():
    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success: break
            results = yolo_model(frame, conf=0.25, verbose=False)
            annotated_frame = results[0].plot()
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# --- PAGE 1: DETEKSI & MINT NFT ---
@app.post("/process_detection")
async def process_detection(manual_country: str = None):
    global last_scan_data
    print("\n[STEP 1] Starting Detection...")
    
    country_code = manual_country if manual_country else get_auto_country_code()
    success, frame = cap.read()
    if not success: 
        return {"status": "error", "message": "Camera failed"}

    results = yolo_model(frame, conf=0.15, verbose=False)
    # Kita hitung jumlah item dari hasil YOLO
    items_found = len(results[0].boxes)
    
    if items_found == 0:
        print("[-] No debris detected by YOLO.")
        return {"status": "no_debris", "message": "No debris detected"}

    temp_img = "detected_debris.jpg"
    cv2.imwrite(temp_img, frame)

    print("[STEP 2] Analyzing with Gemini...")
    prompt = "Identify debris type and estimate weight in kg. Return ONLY raw JSON: {'total_weight': float}. No explanation."
    total_kg = 0.5 
    
    try:
        with PIL.Image.open(temp_img) as img:
            response = gemini_model.generate_content([prompt, img])
        raw_text = response.text.strip()
        clean_json = raw_text.replace('```json', '').replace('```', '').strip()
        analysis = json.loads(clean_json)
        total_kg = analysis.get('total_weight', 0.5)
        print(f"[+] Gemini estimation: {total_kg} kg")
    except Exception as e:
        print(f"[!] Gemini Error: {e}")
    
    if os.path.exists(temp_img):
        os.remove(temp_img)

    # HITUNG REWARD
    multiplier, _ = engine.get_multiplier(country_code)
    final_reward = round(total_kg * 0.01 * multiplier, 6)

    # MINT NFT
    print(f"[STEP 3] Minting NFT for {country_code}...")
    collector_wallet = os.getenv("COLLECTOR_WALLET_ADDRESS")
    
    try:
        nft_address = solana_service.mint_impact_nft(
            receiver_addr=collector_wallet,
            country=country_code,
            mass=total_kg,
            reward=final_reward,
            status="COLLECTED"
        )
        final_status = "success" if nft_address and not str(nft_address).startswith("Error") else "error"
    except Exception as e:
        nft_address = f"Error: {str(e)}"
        final_status = "error"

    detected_label = "Debris"
    if items_found > 0:
        class_id = int(results[0].boxes[0].cls[0])
        detected_label = yolo_model.names[class_id]
        print(f"[+] Verified Label: {detected_label}") #

    # UPDATE DATA GLOBAL (Agar bisa dibaca /api/last-scan)
    last_scan_data = {
        "items_count": items_found,
        "item_type": detected_label, # Tambahkan ini
        "reward_sol": final_reward,
        "collector_wallet": collector_wallet,
        "nft_address": str(nft_address)
    }

    return last_scan_data

# --- PAGE 3: DATA SYNC & CONFIRMATION ---

@app.get("/api/last-scan")
async def get_last_scan():
    """Mengirimkan data hasil scan terakhir ke Page 3"""
    return last_scan_data

@app.post("/confirm_recycle")
async def confirm_recycle(req: RecycleRequest):
    """Proses pembayaran otomatis dari UN_ADDRESS ke User"""
    print(f"\n[STEP 4] Recycler Confirming Payment...")
    print(f"[>] Sending: {req.amount} SOL to {req.collector_wallet}")

    try:
        tx_sig = solana_service.send_reward_with_memo(
            receiver_pubkey_str=req.collector_wallet,
            amount_sol=req.amount,
            country="Verified", 
            weight="Recycled"
        )

        if tx_sig and not str(tx_sig).startswith("Error"):
            return {
                "status": "success", 
                "signature": tx_sig,
                "explorer_url": f"https://explorer.solana.com/tx/{tx_sig}?cluster=devnet"
            }
        
        return {"status": "error", "message": str(tx_sig)}

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)