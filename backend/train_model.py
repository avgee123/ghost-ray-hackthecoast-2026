from ultralytics import YOLO

def main():
    # 1. Load model dasar (Pre-trained)
    model = YOLO('yolov8n.pt')

    # 2. Jalankan Training
    # Pastikan path ke data.yaml sudah benar sesuai lokasi folder datasetmu
    model.train(
        data='TACO-1/data.yaml', 
        epochs=10, 
        imgsz=640, 
        device='cpu' # Ganti ke '0' jika kamu punya kartu grafis NVIDIA
    )

if __name__ == '__main__':
    main()