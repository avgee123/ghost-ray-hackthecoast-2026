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

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi
GENAI_API_KEY = "AIzaSyBMVdMrT60J1jYCXNX1G0e8v4RoloGrdME"
genai.configure(api_key=GENAI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')
yolo_model = YOLO('backend/best.pt') 
engine = SustainabilityEngine('backend/WorldSustainabilityDataset.csv')
cap = cv2.VideoCapture(0)

def get_auto_country_code():
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        return data.get('country_code_iso3', 'IDN') 
    except:
        return 'CAN' 

@app.get("/video_feed")
def video_feed():
    def generate_frames():
        while True:
            success, frame = cap.read()
            if not success: break
            results = yolo_model(frame, conf=0.6, verbose=False)
            annotated_frame = results[0].plot()
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# --- PAGE 1: HANYA DETEKSI & MINT NFT ---
@app.post("/process_detection")
async def process_detection(manual_country: str = None):
    country_code = manual_country if manual_country else get_auto_country_code()
    
    success, frame = cap.read()
    if not success: return {"status": "error", "message": "Camera failed"}

    results = yolo_model(frame, conf=0.6, verbose=False)
    if len(results[0].boxes) == 0:
        return {"status": "no_debris", "message": "No debris detected"}

    temp_img = "detected_debris.jpg"
    cv2.imwrite(temp_img, results[0].plot())

    img = PIL.Image.open(temp_img)
    prompt = "Identify debris and return JSON: {'total_weight': float_in_kg}"
    response = gemini_model.generate_content([prompt, img])
    
    try:
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        analysis = json.loads(clean_json)
        total_kg = analysis.get('total_weight', 0)
    except:
        total_kg = 0.5 
    
    if os.path.exists(temp_img): os.remove(temp_img)

    multiplier, breakdown = engine.get_multiplier(country_code)
    # Kalkulasi reward tapi JANGAN dikirim dulu
    final_reward = total_kg * 0.01 * multiplier

    # MINT NFT dengan atribut tambahan (Wallet & Amount)
    nft_address = None
    try:
        nft_address = solana_service.mint_impact_nft(
            receiver_addr="98bmG75oh3ZeUyDLrM5BkWu7HvzC7SV1ke1Wtr3C3AfW",
            country=country_code,
            mass=total_kg,
            reward=final_reward, # Pastikan fungsi mint_impact_nft di solana_service terima ini
            status="COLLECTED"
        )
    except Exception as e:
        print(f"NFT Minting failed: {e}")

    return {
        "status": "success",
        "message": "Impact Reported! Reward pending recycling verification.",
        "location": country_code,
        "weight": total_kg,
        "reward_sol_pending": final_reward,
        "nft_address": nft_address
    }

# --- PAGE 3: RECYCLER CONFIRMATION (TRANSFER SOL + UPDATE NFT) ---
@app.post("/confirm_recycle")
async def confirm_recycle(
    nft_address: str = Body(...), 
    collector_wallet: str = Body(...), 
    amount: float = Body(...)
):
    try:
        # 1. Eksekusi Pembayaran & Memo (Satu Transaksi)
        tx_sig = solana_service.send_reward_with_memo(
            country="Verified", 
            weight="Recycled",
            multiplier=1.0,
            amount_sol=amount,
            receiver_pubkey_str=collector_wallet
        )

        if tx_sig:
            # 2. Update Status cNFT via Shyft
            update_res = solana_service.update_to_recycled(nft_address)
            return {
                "status": "success",
                "signature": tx_sig,
                "nft_update": update_res
            }
        
        return {"status": "error", "message": "Transaction failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}