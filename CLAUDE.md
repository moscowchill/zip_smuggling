# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Tool
```bash
# Basic usage (recommended: use level 2, 3, or 4 for fast execution)
python zip_smuggle.py <payload_name> <exe_file> [obfuscation_level] [pdf_decoy]

# Example with fast obfuscation
python zip_smuggle.py report payload.exe 2

# Example with PDF decoy
python zip_smuggle.py quarterly_report payload.exe 2 decoy.pdf

# Create test PDF
python create_test_pdf.py
```

### Generating Templates
```bash
# Generate PowerShell-based LNK template
powershell -ExecutionPolicy Bypass -File template/template_generator.ps1

# Generate CMD-based LNK template (for level 3 obfuscation)
powershell -ExecutionPolicy Bypass -File template/cmd_template_generator.ps1
```

### Diagnostics
```bash
# Diagnose PDF extraction issues
powershell -ExecutionPolicy Bypass -File diagnose_pdf_issue.ps1 -zipPath <path_to_zip>

# Compare original and extracted PDFs
powershell -ExecutionPolicy Bypass -File compare_pdfs.ps1 -originalPath <original.pdf> -extractedPath <extracted.pdf>
```

## Architecture Overview

This project implements a ZIP smuggling technique that embeds executables (and optionally PDFs) into ZIP files using malicious LNK files. The key architectural components:

### Obfuscation Levels
- **Level 0-1**: Original implementation with recursive directory search (SLOW: 30-60s)
- **Level 2**: String manipulation with optimized search (FAST: 1-2s) - Recommended
- **Level 3**: CMD wrapper using certutil encoding (FAST: 1-2s)
- **Level 4**: Clean optimized version (FAST: 1-2s)

### Data Structure
The ZIP file structure after modification:
1. Standard ZIP headers and content
2. LNK file (appears as document shortcut)
3. Embedded PDF data (optional)
4. Embedded EXE data (marked with 0x55555555 pattern)
5. ZIP End of Central Directory record

### Execution Flow
1. Victim opens ZIP and clicks the LNK file
2. LNK executes obfuscated PowerShell/CMD command
3. Command searches for the ZIP file in common directories (Downloads, Desktop, Documents, Temp, PWD)
4. Extracts embedded data using byte pattern matching
5. If PDF present: Opens PDF first for legitimacy
6. Executes the embedded executable after a short delay

### Performance Optimizations (Levels 2-4)
- Targeted directory search instead of recursive profile scan
- Efficient byte pattern matching using for loops
- .NET Array.Copy for large data operations
- Eliminates the 30+ second delay of original implementation