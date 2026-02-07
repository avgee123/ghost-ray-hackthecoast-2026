import cv2
from ultralytics import YOLO
import solana_service 
import time

# 1. Load Model
model = YOLO('nets-3/runs/detect/train/weights/best.pt')

cap = cv2.VideoCapture(0)

# VARIABEL SAKLAR (Agar tidak bayar berkali-kali)
sudah_dibayar = False

print("--- GHOST-RAY SYSTEM: MODE OTOMATIS AKTIF ---")
print("Mencari jaring hantu... Pembayaran akan dilakukan otomatis saat terdeteksi pertama kali.")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Jalankan deteksi
    results = model(frame, conf=0.7, verbose=False) # conf dinaikkan ke 0.7 agar lebih akurat
    
    annotated_frame = results[0].plot()
    net_detected = len(results[0].boxes) > 0

    # LOGIKA OTOMATIS
    if net_detected and not sudah_dibayar:
        print("\n[OTOMATIS] Jaring Terdeteksi! Memproses Insentif Pemerintah...")
        
        # Kirim uang ke Phantom kamu
        tx_sig = solana_service.log_net_report("Fishing Net", 0.90)
        
        if tx_sig:
            print(f"✅ PEMBAYARAN BERHASIL: {tx_sig}")
            sudah_dibayar = True # Kunci agar tidak mengirim lagi
        else:
            print("❌ Transaksi gagal, mencoba lagi di frame berikutnya...")

    # Tampilan visual untuk Juri
    if sudah_dibayar:
        status_text = "STATUS: INSENTIF TERKIRIM"
        color = (255, 0, 0) # Biru
    elif net_detected:
        status_text = "STATUS: MENGIRIM DANA..."
        color = (0, 255, 0) # Hijau
    else:
        status_text = "STATUS: MENCARI JARING..."
        color = (0, 0, 255) # Merah

    cv2.putText(annotated_frame, status_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow("Ghost-Ray Automated Monitor", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()