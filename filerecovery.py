from binascii import unhexlify
import re
import struct

f = open("Project2Updated.dd", "r")

hexdump = f.read().encode("hex")

#x = re.search("474946383961(.*?)21(.*?)003b(.*?)003b(.*?)003b(.*?)003b", hexdump)

#pngreg = "89504e470d0a1a0a(.*?)49454e44ae426082"
'''
png = re.finditer("89504e470d0a1a0a(.*?)49454e44ae426082", hexdump)

#png = re.search("89504e470d0a1a0a(.*?)49454e44ae426082", hexdump)

print("PNGS ---")
for element in png:
    print("offset: " + str(element.span()[0]/2))
    print("count : " + str(element.span()[1]/2 - element.span()[0]/2))



pdfbegin = re.finditer("25504446", hexdump)
pdfend = re.finditer("0a2525454f46", hexdump)

headers = []
footers = []
for element in pdfbegin:
    headers.append(element.span()[0]/2)

for element in pdfend:
    footers.append(element.span()[0]/2)

finalpdflist = []
for i in range(len(headers)):
    if i == len(headers)-1:
        temp = footers[len(footers)-1]
        tuppdf = (headers[i], temp)
        finalpdflist.append(tuppdf)
        break
    for j in range(len(footers)):
        if footers[j] > headers[i] and footers[j] < headers[i+1]:
            temp = footers[j]
    tuppdf = (headers[i], temp)
    finalpdflist.append(tuppdf)

print("\n\n\nPDFS ---")
for element in finalpdflist:
    print("offset : " + str(element[0]))
    print("count : " + str(element[1] - element[0]))

print("\n\n\nAVIS ---")

avi = re.finditer("52494646", hexdump)

for element in avi:
    avioffset = element.span()[0]/2
    print("offset: " + str(avioffset))
    size = hexdump[element.span()[0]+8:element.span()[0]+16]
    print(size)
    avicount = struct.unpack("<i", unhexlify(size))[0]
    print(avicount)
'''

print("BMP ---")

bmp = re.finditer("424d.{8}.{16}28.{23}1", hexdump)

for element in bmp:
    print(element.span()[0]/2)
    bmpoffset = element.span()[0]/2
    print("offset: " + str(bmpoffset))
    size = hexdump[element.span()[0]+4:element.span()[0]+12]
    print(size)
    bmpcount = struct.unpack("<i", unhexlify(size))[0]
    print(bmpcount)







