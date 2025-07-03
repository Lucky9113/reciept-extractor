# Receipt Extractor

Receipt Extractor is a Python tool designed to automatically extract key information from scanned receipt PDFs, such as date, total amount, vendor, and item details. The extracted data is saved in a structured CSV format, making expense management and analysis fast and easy.

## Features

- Extracts date, total amount, vendor, and itemized information from receipts
- Processes scanned PDF receipts using OCR
- Outputs results in CSV format
- Simple command-line interface

## Installation

1. **Clone the repository:**
    ```
    git clone https://github.com/Lucky9113/reciept-extractor.git
    cd reciept-extractor
    ```

2. **Install Python dependencies:**
    ```
    pip install -r requirements.txt
    ```

3. **Install Tesseract OCR:**
    - **Ubuntu:**
        ```
        sudo apt-get install tesseract-ocr
        ```
    - **Windows:**
        Download the Tesseract installer from [here](https://github.com/tesseract-ocr/tesseract) and add it to your system PATH.

## Usage

python extract_receipt.py --input path/to/receipt.pdf --output output.csv


- `--input`: Path to the scanned receipt PDF file
- `--output`: Path to save the extracted CSV file

## Example

python extract_receipt.py --input receipts/sample.pdf --output results/sample.csv


## Requirements

- Python 3.7 or higher
- Tesseract OCR (installed separately)

## Dependencies

See [requirements.txt](requirements.txt) for the full list of Python dependencies.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or suggestions.

