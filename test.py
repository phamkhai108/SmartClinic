import torch

if torch.cuda.is_available():
    print(f"✅ CUDA is available! GPU name: {torch.cuda.get_device_name(0)}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"Current device: {torch.cuda.current_device()}")
else:
    print("❌ CUDA is NOT available. Running on CPU.")
