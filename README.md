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
   Message: HELLO WORLD
   ```
4. **Enable verbose mode (optional)**:
   
   Adding 1 at the end provides additional debug info:
   ```bash
   python qr_main.py samples/hello_world.png 1
   Version: 1
   Level: L
   Mask: 0
   ...
   Message: HELLO WORLD
   ```

   
## Limitations
   - The QR reader may not work for all QR codes.
   - The QR code must be horizontally and vertically aligned (no rotation support yet).
   - The image processing step may fail on low-quality or distorted images.
   - The QR reader can detect errors but cannot yet restore corrupted data.

## Supported encoding modes
   - Numeric
   - Alphanumeric
   - Byte
   - ECI (Extended Channel Interpretation)

## Technical Details  
   This project implements QR code decoding from scratch, including:  

   - **Reed-Solomon error correction** for data recovery  
   - **Galois field arithmetic** for error correction calculations  
   - **Bitstream parsing** to interpret QR encoding modes (numeric, alphanumeric, byte)  
   - **Mask pattern detection** to extract data correctly  
   - **Basic image processing** for converting QR images into a binary matrix  

   QR code generation is currently in development.
