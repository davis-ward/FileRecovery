from binascii import unhexlify
import binascii
import re
import struct
import sys
import os
from hashlib import sha256 
import subprocess


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



def main():

    # Command line args
    if (len(sys.argv) != 2):
        print ("Please try again: python FileRecovery.py filename")
        exit(1)

    input_file = sys.argv[1]

    # This is broken on python3 for some reason. please use python
    with open(input_file, 'rb') as f:
        content = f.read()
    hexdump = (binascii.hexlify(content))

    pngs = png(hexdump)
    
    gifs = gif(hexdump) 
    pngs = png(hexdump)
    pdfs = pdf(hexdump)
    avis = avi(hexdump) 
    docs, zips = docx_and_zip(hexdump)    
    jpgs = jpg(hexdump)
    bmps = bmp(hexdump)
       
    file_list =[]

    
    superlist = [gifs, pngs, pdfs, avis, docs, zips, jpgs, bmps]
    file_count = 0

    name_list = ['gif', 'png', 'pdf', 'avi', 'docx', 'zip', 'jpg', 'bmp']
    
    i = 0
    for c in superlist:
        for g in c:
            file_name = 'file{}.{}'.format(file_count, name_list[i])
            tuple = (file_name, g[0], g[1], g[0]+g[1])
            file_list.append(tuple)
            file_count += 1
        i+=1


    for f in file_list:
        
        cmd = "dd if={} of={} bs=1 skip={} count={}".format(input_file, str(f[0]), str(f[1]), str(f[2]))
        #print(cmd)

        os.system(str(cmd))
    
        stream = os.popen('sha256sum {}'.format(str(f[0])))
        hash = stream.read()

        print(f[0])
        print("Offset: " + str(f[2]))
        print("Ending Offset: " + str(f[3]))
        print("SHA256: " + hash)


def gif(hexdump): 
    
    gif_headers = re.finditer(gif_regex, hexdump)
    gif_locations = []
    for g in gif_headers:
        offset = g.span()[0]/2
        size = ((g.span()[1]-6)/2 - g.span()[0]/2)
        gif_locations.append((offset, size))
    return gif_locations

def png(hexdump):
    
    png_headers = re.finditer(png_regex, hexdump)
    png_locations = []
    for element in png_headers:
        png_locations.append((element.span()[0]/2, element.span()[1]/2 - element.span()[0]/2))
    return png_locations

'''
    PDF Strategy

    Because PDFs are known to have EOF flags prematurely, we set up an algorithm
    that matches each header with the farthest away footer that
    still precedes the next header. 
'''
def pdf(hexdump):
    

    # Finds headers and footers and puts them in lists
    headiter = re.finditer(pdf_header, hexdump)
    footiter = re.finditer(pdf_footer, hexdump)

    pdf_headers = []
    pdf_footers = []
    for element in headiter:
        pdf_headers.append(element.span()[0]/2)

    for element in footiter:
        pdf_footers.append(element.span()[1]/2)

    pdf_locations = []
    for i in range(len(pdf_headers)):
        if i == len(pdf_headers)-1: # if we are on the last header, assign the last footer to it
            temp = pdf_footers[len(pdf_footers)-1]
            tuppdf = (pdf_headers[i], temp-pdf_headers[i])
            pdf_locations.append(tuppdf)
            break
        for j in range(len(pdf_footers)):
            if pdf_footers[j] > pdf_headers[i] and pdf_footers[j] < pdf_headers[i+1]:
                temp = pdf_footers[j]
        tuppdf = (pdf_headers[i], temp-pdf_headers[i]+1)

        pdf_locations.append(tuppdf)
    
    return pdf_locations
'''
    AVI Strategy

    The file size is in the second 4 bytes, i.e. second 8 characters. 
    This loop finds the sizes of the files.
    Odd thing we found is that the size is short by 8 every time, so we add 8 manually. 
'''
def avi(hexdump): 
    

    # Finds AVI Headers
    
    avi_headers = re.finditer(avi_regex, hexdump)
    avi_locations = []

    for element in avi_headers:
        avioffset = element.span()[0]/2
        size = hexdump[element.span()[0]+8:element.span()[0]+16]
        avicount = struct.unpack("<i", unhexlify(size))[0] + 8
        avi_locations.append((avioffset,avicount))
        
    
    return avi_locations

def bmp(hexdump):

    bmp = re.finditer(bmp_regex, hexdump)
    bmp_locations = []
    for element in bmp:
        bmpoffset = element.span()[0]/2
        
        size = hexdump[element.span()[0]+4:element.span()[0]+12]
        bmpcount = struct.unpack("<i", unhexlify(size))[0]
        bmp_locations.append((bmpoffset, bmpcount))
        

    return bmp_locations
'''
    zip and docx are extremely similar
'''
def docx_and_zip(hexdump):

    docx_files = re.finditer(docx_regex, hexdump)
    docx_locations = []

    for d in docx_files:
        offset = d.span()[0]/2
        size = d.span()[1]/2 - d.span()[0]/2 + 18
        docx_locations.append((offset, size))



    
    zip_files = re.finditer(zip_regex, hexdump)
    zip_locations = []

    # This loop will check if any zip addresses match a previously found docx address. 
    # Since the docx format is a more specific version of .zip, this should work.
    for z in zip_files:
        
        offset = z.span()[0]/2
        size = z.span()[1]/2 - z.span()[0]/2
        
        skip= False
        for d in docx_locations:
            if (d[0]==offset or ((d[1]+d[0])==(size+offset))):
                skip = True
            if (not skip):
                size = z.span()[1]/2 - z.span()[0]/2
                zip_locations.append((offset, size))
            

    return docx_locations, zip_locations
    

def jpg(hexdump):

    #print("\n\n--- JPEG ---")

    jpg_regex = "ffd8ffe(0|1|2|8)(.+?)ffd90"
    jpg_files = re.finditer(jpg_regex, hexdump)
    jpg_locations = []


    for j in jpg_files:
        jpg_type = hexdump[j.span()[0]+7] # identifies the type of JPEG, e.g. JFIF, EXIF, etc
        offset = j.span()[0]/2
        size = j.span()[1]/2 - offset
        jpg_locations.append((offset, size, jpg_type))
        

    return jpg_locations

main()