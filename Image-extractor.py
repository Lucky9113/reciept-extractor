import argparse
from pdf2image import convert_from_path

parser = argparse.ArgumentParser()
#parser.add_argument("Square", help= "Dispaly a square of a given number",type=int)
#args = parser.parse_args()
#print(args.Square**2)
#images = convert_from_path('~/')
parser.add_argument("-p","--pdf_path",type=str, help = "adds the path of the pdf" )
parser.add_argument("-i","--image_path",type=str, help = "defines image path" )
args = parser.parse_args()
pdf_path = args.pdf_path
image_path = args.image_path
images =  convert_from_path(pdf_path)
for i in range(len(images)):
    images[i].save(image_path+'page'+str(i)+'.jpg','JPEG')

#print(f"pdf_path = {pdf_path} and image_path = {image_path}" )
