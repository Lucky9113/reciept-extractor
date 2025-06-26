from PIL import Image
import pytesseract
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-i","--image_path", type = str , help = "Provides path to the image")
parser.add_argument("-t","--Text_file_path", type = str , help  = "Provides path for the text output of the file")
args = parser.parse_args()
image_path =  args.image_path
Text_file_path = args.Text_file_path
output = Text_file_path + "output.txt"
with open(output,"w") as f:
    f.write (pytesseract.image_to_string(Image.open(image_path)))

print()
