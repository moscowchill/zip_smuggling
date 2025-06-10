# ZIP Smuggling - Optimized Edition

An enhanced version of the ZIP smuggling technique that embeds executables (and optionally PDF decoys) into ZIP files using specially crafted LNK files. This optimized version eliminates the 30+ second delay of the original and adds PDF decoy functionality.

## 🚀 Key Improvements

- **⚡ Fast Execution**: Reduced from 30+ seconds to 1-2 seconds
- **📄 PDF Decoy Support**: Open a legitimate-looking PDF before payload execution
- **🔒 Multiple Obfuscation Levels**: Choose your preferred obfuscation technique
- **🎯 Optimized Search**: No more recursive directory scanning

## 📋 Requirements

- Python 3.x
- Windows target system (for payload execution)
- Template LNK files (included in `template/` directory)

## 🛠️ Installation

```bash
git clone <repository>
cd zip_smuggling
```

## 📖 Usage

### Basic Usage
```bash
python zip_smuggle_optimized.py <payload_name> <exe_file> [obfuscation_level] [pdf_decoy]
```

### Examples

**Simple payload (fast execution):**
```bash
python zip_smuggle_optimized.py report ChromeUpdate.exe 2
```

**With PDF decoy:**
```bash
python zip_smuggle_optimized.py quarterly_report ChromeUpdate.exe 2 decoy.pdf
```

**Create test PDF:**
```bash
python create_test_pdf.py
```

## 🎭 Obfuscation Levels

| Level | Type | Speed | Description |
|-------|------|-------|-------------|
| 0 | Original | ❌ SLOW | Unobfuscated with recursive search |
| 1 | Basic | ❌ SLOW (30s+) | Variable randomization with recursive search |
| **2** | **String Manipulation** | **✅ FAST** | **Optimized with string obfuscation** |
| **3** | **CMD Wrapper** | **✅ FAST** | **Certutil-based obfuscation** |
| **4** | **Optimized Basic** | **✅ FAST** | **Clean optimized version** |

**💡 Recommendation**: Use levels 2, 3, or 4 for fast execution (1-2 seconds)

## 🎯 How It Works

1. **ZIP Creation**: Creates a ZIP file with a malicious LNK file
2. **Data Embedding**: Embeds EXE (and optionally PDF) after ZIP structure
3. **Execution Flow**:
   - User opens ZIP and clicks LNK file
   - PowerShell extracts embedded data
   - If PDF included: Opens PDF first (social engineering)
   - Executes payload after delay

### Data Structure
```
[ZIP Header]
[LNK File]
[PDF Data] (optional - if provided)
[EXE Data] (marked with 0x55555555)
[ZIP Central Directory]
[End of Central Directory]
```

## 🔧 Performance Optimizations

### Original Issues (Level 0-1)
- Recursive search through entire user profile
- Inefficient byte pattern matching
- 30-60+ second execution time

### Optimizations (Level 2-4)
- Targeted directory search (Downloads, Desktop, Documents, Temp, PWD)
- Efficient for-loop byte searching
- .NET Array.Copy for large data operations
- 1-2 second execution time

## 📄 PDF Decoy Feature

The PDF decoy adds legitimacy to the attack:

```bash
# Victim sees: financial_report.zip
# Contains: financial_report.lnk (looks like document shortcut)
# Opens: PDF showing financial data
# Hidden: Malware executes 2 seconds later
```

### Creating Custom PDFs
- Use any PDF file as a decoy
- Keep size reasonable for performance
- Name should match social engineering scenario

## 🛡️ Detection Considerations

- ZIP appears unmodified to most tools
- LNK file looks like document shortcut
- PowerShell execution may trigger security tools
- Consider application whitelisting bypasses

## 📊 Performance Comparison

| Operation | Original | Optimized |
|-----------|----------|-----------|
| File Search | 30-60s | <0.5s |
| Pattern Match | 5-10s | <0.5s |
| Total Time | 35-70s | 1-2s |

## 🔍 Troubleshooting

**"File not found" errors:**
- Ensure ZIP is in one of the searched directories
- Use level 4 for most reliable search

**PDF not opening:**
- Verify PDF is valid
- Check PDF file path
- Ensure default PDF reader is installed

**Slow execution:**
- Don't use levels 0 or 1
- Use levels 2, 3, or 4 for optimized performance

## ⚠️ Disclaimer

This tool is for authorized security testing and research only. Users are responsible for complying with applicable laws and regulations. The authors assume no liability for misuse or damage.

## 🤝 Contributing

Contributions welcome! Please submit pull requests with:
- Performance improvements
- New obfuscation techniques
- Bug fixes
- Documentation updates

## 📝 License

[Include your license here]

---

**Note**: Always use the optimized version (`zip_smuggle_optimized.py`) for production use. The original version is kept for reference only.
