import ocrmypdf
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-p","--pdf_path", type = str , help = "Provides path to the pdf")
parser.add_argument("-t","--Text_file_path", type = str , help  = "Provides path for the text output of the file")
args = parser.parse_args()

input_pdf =  args.pdf_path

output_pdf = args.Text_file_path

ocrmypdf.ocr(input_pdf, output_pdf, language='eng')

