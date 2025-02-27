# QR Reader & Generator (Python)  

An ongoing project to read and generate QR codes **without external libraries** like `qrcode` or `reedsolo`. Currently supports decoding QR codes from `.png` images. QR generation is in development.  

## Installation & Usage  
1. **Clone the repository:**  
   ```bash
   git clone https://github.com/hugoeidem/qr.git
   cd qr
   ```
2. **Install dependencies:**
   ```bash
   pip install pillow
   ```
3. **Run the program:**
   ```bash
   python qr_main samples/hello_world.png
   > message: HELLO WORLD
   ```
4. Enable verbose mode (optional):
   
   Adding 1 at the end provides additional debug info:
   ```bash
   python qr_main.py samples/hello_world.png 1
   ```
   
