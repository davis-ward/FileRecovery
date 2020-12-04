from binascii import unhexlify
import binascii
import re
import struct
import sys


# Command line args
if (len(sys.argv) != 2):
    print ("Please try again: python FileRecovery.py filename")
    exit(1)

filename = sys.argv[1];

# Old way we opened file, but encoding is broken on python3.
'''
f = open(filename, "r")

hexdump = f.read().encode("hex")
'''

# This is also broken on python3 for some reason. please use python
with open(filename, 'rb') as f:
    content = f.read()
hexdump = (binascii.hexlify(content))



# Attempts at finding the end of the GIF. impossible
#x = re.search("474946383961(.*?)21(.*?)003b(.*?)003b(.*?)003b(.*?)003b", hexdump)

'''
PNG finder
'''

print("--- PNGS ---")

pngHeaders = re.finditer("89504e470d0a1a0a(.*?)49454e44ae426082", hexdump)
pngLocations = []
for element in pngHeaders:
    pngLocations.append((element.span()[0]/2, element.span()[1]/2 - element.span()[0]/2))
    print("offset: " + str(element.span()[0]/2))
    print("count: " + str(element.span()[1]/2 - element.span()[0]/2))


print("\n\n--- PDFS ---")

# Finds headers and footers and puts them in lists
headiter = re.finditer("25504446", hexdump)
footiter = re.finditer("0a2525454f46", hexdump)

pdfHeaders = []
pdfFooters = []
for element in headiter:
    pdfHeaders.append(element.span()[0]/2)

for element in footiter:
    pdfFooters.append(element.span()[0]/2)

'''
PDF Strategy

Because PDFs are known to have EOF flags prematurely, we set up an algorithm
that matches each header with the farthest away footer that
still precedes the next header. 
'''

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




print("\n\n--- AVIS ---")

# Finds AVI Headers
aviHeaders = re.finditer("52494646", hexdump)

'''
AVI Strategy

The file size is in the second 4 bytes, i.e. second 8 characters. 
This loop finds the sizes of the files. 
'''
aviLocations = []

for element in aviHeaders:
    avioffset = element.span()[0]/2
    size = hexdump[element.span()[0]+8:element.span()[0]+16]
    avicount = struct.unpack("<i", unhexlify(size))[0]
    aviLocations.append((avioffset,avicount))
    print ("offset: " + str(avioffset))
    print ("size: " + str(avicount))
    
    




print("\n\n--- BMP ---")


'''
need to figure out how to find these MFs
'''

bmp = re.finditer("424d.{8}.{16}28.{23}1", hexdump)

for element in bmp:
    print(element.span()[0]/2)
    bmpoffset = element.span()[0]/2
    print("offset: " + str(bmpoffset))
    size = hexdump[element.span()[0]+4:element.span()[0]+12]
    bmpcount = struct.unpack("<i", unhexlify(size))[0]
    print("Size: " + str(bmpcount))



print("\n\n--- .Docx ---")

docx_regex = "504b030414000600(.+?)504b0506"

docx_files = re.finditer(docx_regex, hexdump)
docx_locations = []

for d in docx_files:
    offset = d.span()[0]/2
    size = d.span()[1]/2 - d.span()[0]/2
    docx_locations.append((offset, size))
    print('Offset: ' + str(offset))
    print('size: ' + str(size))


print("\n\n--- ZIP ---")
'''
zip and docx are extremely similar

'''
zip_regex = "504b0304(.+?)504b(.{34})0{12}"

zip_files = re.finditer(zip_regex, hexdump)
zip_locations = []

for z in zip_files:
    
    offset = z.span()[0]/2
    if (offset == docx_locations[i][j] for i,j in docx_locations):
        break
    
    size = z.span()[1]/2 - z.span()[0]/2
    zip_locations.append((offset, size))
    print('Offset: ' + str(offset))
    print('size: ' + str(size))