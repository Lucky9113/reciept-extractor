import os
import sys
import argparse
from pathlib import Path
import subprocess

class ReceiptProcessor:
    def __init__(self, temp_dir="/home/lakshay/Downloads/project_files/Sample_text_01", 
                 output_dir="/home/lakshay/Downloads/project_files/Sample_CSV_01"):
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)
        self.image_dir = Path("/home/lakshay/Downloads/project_files/Sample_images_01")
        
        # Verify directories exist
        if not self.temp_dir.exists():
            raise FileNotFoundError(f"Temp directory not found: {self.temp_dir}")
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {self.output_dir}")
        if not self.image_dir.exists():
            raise FileNotFoundError(f"Image directory not found: {self.image_dir}")
        
    def process_single_receipt(self, pdf_path, output_csv_name=None):
        """Process a single PDF receipt through the complete pipeline"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Generate output CSV name if not provided
        if output_csv_name is None:
            output_csv_name = f"{pdf_path.stem}_extracted.csv"
        
        print(f"Processing: {pdf_path.name}")
        
        try:
            # Step 1: Convert PDF to images
            print("Step 1: Converting PDF to images...")
            
            # Clear old images in image directory
            for f in self.image_dir.glob('page*.jpg'):
                f.unlink()
            
            result = subprocess.run([
                'python3', 'Image-extractor.py', 
                '-p', str(pdf_path), 
                '-i', str(self.image_dir) + '/'
            ], capture_output=True, text=True, check=True)
            
            # Step 2: Process all generated images
            print("Step 2: Extracting text from images...")
            image_files = list(self.image_dir.glob('page*.jpg'))
            
            if not image_files:
                raise RuntimeError("No images were generated from PDF")
            
            all_text = ""
            for image_file in sorted(image_files):
                result = subprocess.run([
                    'python3', 'Image_to_text.py',
                    '-i', str(image_file),
                    '-t', str(self.temp_dir) + '/'
                ], capture_output=True, text=True, check=True)
                
                # Read the generated text file
                output_text_file = self.temp_dir / "output.txt"
                if output_text_file.exists():
                    with open(output_text_file, 'r', encoding='utf-8') as f:
                        page_text = f.read()
                    all_text += f"\n--- Page {image_file.stem} ---\n{page_text}"
                    
                    # Rename to avoid conflicts with next iteration
                    new_name = self.temp_dir / f"{image_file.stem}_output.txt"
                    output_text_file.rename(new_name)
            
            # Step 3: Combine all text and process to CSV
            print("Step 3: Extracting fields and generating CSV...")
            combined_text_file = self.temp_dir / f"{pdf_path.stem}_combined.txt"
            with open(combined_text_file, 'w', encoding='utf-8') as f:
                f.write(all_text)
            
            # Determine output CSV path
            if output_csv_name.startswith('/'):
                output_csv_path = Path(output_csv_name)
            else:
                output_csv_path = self.output_dir / output_csv_name
            
            # FIXED: Use -t flag instead of -i for text_to_csv.py
            result = subprocess.run([
                'python3', 'text_to_csv.py',
                '-t', str(combined_text_file),
                '-o', str(output_csv_path)
            ], capture_output=True, text=True, check=True)
            
            print(f"✅ Successfully processed! CSV saved to: {output_csv_path}")
            
            # Cleanup temporary files
            self.cleanup_temp_files(pdf_path.stem)
            
            return output_csv_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error in subprocess: {e}")
            print(f"Error output: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ Error processing {pdf_path.name}: {e}")
            raise
    
    def process_batch(self, input_dir="/home/lakshay/Downloads/project_files/Sample_Invoices_01"):
        """Process all PDF files in the input directory"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            print(f"Input directory not found: {input_path}")
            return
        
        pdf_files = list(input_path.glob('*.pdf'))
        
        if not pdf_files:
            print(f"No PDF files found in {input_path}")
            return
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        successful = 0
        failed = 0
        
        for pdf_file in pdf_files:
            try:
                self.process_single_receipt(pdf_file)
                successful += 1
            except Exception as e:
                print(f"Failed to process {pdf_file.name}: {e}")
                failed += 1
        
        print(f"\n📊 Batch processing complete:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
    
    def cleanup_temp_files(self, prefix):
        """Clean up temporary files for a specific processing run"""
        temp_files = list(self.temp_dir.glob(f"{prefix}*"))
        for temp_file in temp_files:
            if temp_file.is_file():
                temp_file.unlink()

def main():
    parser = argparse.ArgumentParser(description="Process receipt PDFs to extract data into CSV")
    parser.add_argument("-f", "--file", type=str, help="Single PDF file to process")
    parser.add_argument("-d", "--directory", type=str, 
                       default="/home/lakshay/Downloads/project_files/Sample_Invoices_01", 
                       help="Directory containing PDF files")
    parser.add_argument("-o", "--output", type=str, help="Output CSV filename (for single file mode)")
    parser.add_argument("--temp-dir", type=str, 
                       default="/home/lakshay/Downloads/project_files/Sample_text_01", 
                       help="Temporary directory")
    parser.add_argument("--output-dir", type=str, 
                       default="/home/lakshay/Downloads/project_files/Sample_CSV_01", 
                       help="Output directory")
    
    args = parser.parse_args()
    
    processor = ReceiptProcessor(temp_dir=args.temp_dir, output_dir=args.output_dir)
    
    if args.file:
        # Process single file
        try:
            processor.process_single_receipt(args.file, args.output)
        except Exception as e:
            print(f"Failed to process file: {e}")
            sys.exit(1)
    else:
        # Process batch
        processor.process_batch(args.directory)

if __name__ == "__main__":
    main()

