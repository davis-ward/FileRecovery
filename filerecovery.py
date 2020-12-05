from binascii import unhexlify
import binascii
import re
import struct
import sys


# Command line args
if (len(sys.argv) != 2):
    print ("Please try again: python FileRecovery.py filename")
    exit(1)

filename = sys.argv[1]




# This is broken on python3 for some reason. please use python
with open(filename, 'rb') as f:
    content = f.read()
hexdump = (binascii.hexlify(content))



'''
Regular expression strings
'''
png_regex = "89504e470d0a1a0a(.*?)49454e44ae426082"
pdf_header = "25504446"
pdf_footer = "0a2525454f46"
avi_regex = "52494646"
gif_regex = "474946383961(.*?)00003b000000"
bmp_regex = "424d.{8}0{8}.{33}1"
docx_regex = "504b030414000600(.+?)504b0506"
zip_regex= "504b0304(.{8}0[0-7]00(.+?)504b(.{34}000000))"

def gif(): 
    print("--- GIFs ---")
    gif_headers = re.finditer(gif_regex, hexdump)
    gif_locations = []
    for g in gif_headers:
        offset = g.span()[0]/2
        size = ((g.span()[1]-6)/2 - g.span()[0]/2)
        gif_locations.append((offset, size))
        print("Offset: " + str(offset))
        print("Size: " + str(size))
    return gif_locations

def png():
    print("--- PNGS ---")
    png_headers = re.finditer(png_regex, hexdump)
    png_locations = []
    for element in png_headers:
        png_locations.append((element.span()[0]/2, element.span()[1]/2 - element.span()[0]/2))
        print("offset: " + str(element.span()[0]/2))
        print("count: " + str(element.span()[1]/2 - element.span()[0]/2))
    return png_locations

'''
    PDF Strategy

    Because PDFs are known to have EOF flags prematurely, we set up an algorithm
    that matches each header with the farthest away footer that
    still precedes the next header. 
'''
def pdf():
    print("\n\n--- PDFS ---")

    # Finds headers and footers and puts them in lists
    headiter = re.finditer(pdf_header, hexdump)
    footiter = re.finditer(pdf_footer, hexdump)

    pdfHeaders = []
    pdfFooters = []
    for element in headiter:
        pdfHeaders.append(element.span()[0]/2)

    for element in footiter:
        pdfFooters.append(element.span()[1]/2)

    pdfLocations = []
    for i in range(len(pdfHeaders)):
        if i == len(pdfHeaders)-1:
            temp = pdfFooters[len(pdfFooters)-1]
            tuppdf = (pdfHeaders[i], temp)
            pdfLocations.append(tuppdf)
            break
        for j in range(len(pdfFooters)):
            if pdfFooters[j] > pdfHeaders[i] and pdfFooters[j] < pdfHeaders[i+1]:
                temp = pdfFooters[j]
        tuppdf = (pdfHeaders[i], temp)

        pdfLocations.append(tuppdf)

    # Print 
    for element in pdfLocations:
        print("offset : " + str(element[0]))
        print("count : " + str(element[1] - element[0]))

'''
    AVI Strategy

    The file size is in the second 4 bytes, i.e. second 8 characters. 
    This loop finds the sizes of the files.
    Odd thing we found is that the size is short by 8 every time, so we add 8 manually. 
'''
def avi(): 
    print("\n\n--- AVIS ---")

    # Finds AVI Headers
    
    aviHeaders = re.finditer(avi_regex, hexdump)
    aviLocations = []

    for element in aviHeaders:
        avioffset = element.span()[0]/2
        size = hexdump[element.span()[0]+8:element.span()[0]+16]
        print("size in hex, before flipping order: " + str(size))
        avicount = struct.unpack("<i", unhexlify(size))[0] + 8
        aviLocations.append((avioffset,avicount))
        print ("offset: " + str(avioffset))
        print ("size: " + str(avicount))


def bmp():
    print("\n\n--- BMP ---")

    bmp = re.finditer(bmp_regex, hexdump)

    for element in bmp:
        bmpoffset = element.span()[0]/2
        print("offset: " + str(bmpoffset))
        size = hexdump[element.span()[0]+4:element.span()[0]+12]
        print(size)
        bmpcount = struct.unpack("<i", unhexlify(size))[0]
        print("Size: " + str(bmpcount))

'''
    zip and docx are extremely similar
'''
def docx_and_zip():

    print("\n\n--- .Docx ---")

    docx_files = re.finditer(docx_regex, hexdump)
    docx_locations = []

    for d in docx_files:
        offset = d.span()[0]/2
        size = d.span()[1]/2 - d.span()[0]/2 + 18
        docx_locations.append((offset, size))
        print('Offset: ' + str(offset))
        print('size: ' + str(size))


    print("\n\n--- ZIP ---")

    
    zip_files = re.finditer(zip_regex, hexdump)
    zip_locations = []

    for z in zip_files:
        
        offset = z.span()[0]/2
        size = z.span()[1]/2 - z.span()[0]/2
        zip_locations.append((offset, size))
        print('Offset: ' + str(offset))
        print('size: ' + str(size))
        
        skip= False
        for d in docx_locations:
            if (d[0] ==  offset):
                skip = True

        if (not skip):
            size = z.span()[1]/2 - z.span()[0]/2
            zip_locations.append((offset, size))
            print('Offset: ' + str(offset))
            print('size: ' + str(size))
    # if (offset == docx_locations[i][j] for i,j in docx_locations):
    #     break
    

def jpg():

    print("\n\n--- JPEG ---")

    jpg_regex = "ffd8ffe(0|1|2|8)(.+?)ffd90"
    jpg_regex = "ffd8ffe2"
    jpg_files = re.finditer(jpg_regex, hexdump)
    jpg_locations = []


    for j in jpg_files:
        jpg_type = hexdump[j.span()[0]+7]
        offset = j.span()[0]/2
        size = j.span()[1]/2 - offset
        jpg_locations.append((offset, size, jpg_type))
        print("Offset: " + str(offset))
        print("Size: " + str(size))


pdf()
