# QR Toolkit

A powerful command-line toolkit for decoding QR codes from images and camera feeds, with special support for 2FA secret extraction and management.

## Features

- **Multi-source input**: Process images, directories, or use camera feed
- **2FA support**: Extract and export `otpauth://` secrets to JSON format compatible with authenticator apps
- **Flexible output**: Print to console, save as JSON/text, open URLs, or copy to clipboard
- **Batch processing**: Handle multiple files and directories efficiently
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/skye-cyber/qr-toolkit.git
cd QRToolkit
```

2. **Install dependencies**:
```bash
pip install -e .
```

## Dependencies

- `opencv-python` - Computer vision library for image processing
- `pyzbar` - QR code decoding library
- `Pillow` - Image handling support
- `pyperclip` - Clipboard operations (optional)

## Usage

### Basic Examples

```bash
# Decode a single QR code image
qrtool image.png

# Process multiple images
qrtool image1.png image2.jpg

# Scan all images in a directory
qrtool -d ./qr_codes/

# Use camera to scan QR code (30 second timeout)
qrtool -c

# Export 2FA secrets to JSON file
qrtool screenshot.png -j -o auth_backup.json

# Open URLs found in QR codes
qrtool url_qr.png -u

# Save decoded content to text file
qrtool codes/*.png -t -o output.txt

# Quiet mode - only save output, no console messages
qrtool image.png -j -o output.json --quiet
```

### Advanced Examples

```bash
# Batch process with 2FA extraction and URL opening
qrtool -d ./screenshots/ -j -u --quiet

# Camera scan with custom timeout
qrtool -c --timeout 15 -j -o camera_capture.json

# Process specific image types only
qrtool *.png *.jpg -j -o backup.json

# Combine multiple output options
qrtool image.png -j -o backup.json --copy --open-url
```

## Command Line Options

### Input Options
- `inputs` : One or more image files to process
- `-d, --directory` : Directory containing images to process
- `-c, --camera` : Use camera to scan QR codes
- `-s, --screenshot` : Capture screenshot (not implemented)

### Output Options
- `-o, --output` : Output file path
- `-j, --json` : Save as JSON format (2FA secrets or generic data)
- `-t, --text` : Save as text file
- `-u, --open-url` : Automatically open detected URLs
- `--copy` : Copy first result to clipboard
- `--quiet` : Suppress console output
- `--print` : Print to console (default)

### Processing Options
- `--batch` : Process multiple files
- `--timeout` : Camera timeout in seconds (default: 30)

## Output Formats

### 2FA JSON Format
```json
{
  "version": 1,
  "generated": "2024-01-15T10:30:45.123456",
  "entries": [
    {
      "type": "totp",
      "label": "Service:user@example.com",
      "secret": "JBSWY3DPEHPK3PXP",
      "issuer": "Service",
      "algorithm": "SHA1",
      "digits": "6",
      "period": "30"
    }
  ]
}
```

### Text Output
```
https://example.com
otpauth://totp/Service:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Service
Plain text content from QR
```

## Project Structure

```
qr-toolkit/
├── cli.py                 # Command-line interface
├── core/
│   ├── decoder.py        # QR code decoding logic
│   ├── processor.py      # Data processing and validation
│   └── __init__.py
├── outputs/
│   ├── json_handler.py   # JSON output handling
│   ├── text_handler.py   # Text output handling
│   ├── url_handler.py    # URL validation and opening
│   └── __init__.py
├── setup.py              # Package configuration
└── README.md
```

## Error Handling

The toolkit provides comprehensive error handling for:
- Missing or invalid image files
- Images without QR codes
- Invalid URLs and malformed 2FA secrets
- Camera access issues
- File permission errors

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## Suggested Additional Features

Here are some features that could enhance the toolkit:

### 1. **Enhanced Input Sources**
- [ ] **Screenshot capture** (`-s` flag implementation)
- [ ] **Screen region selection** for targeted QR code capture
- [ ] **PDF document support** - extract QR codes from PDF pages
- [ ] **Video file support** - process QR codes in video files
- [ ] **Webcam selection** - choose between multiple cameras

### 2. **Advanced Output Options**
- [ ] **QR code generation** - create QR codes from text/URLs
- [ ] **Multiple format export** - simultaneous JSON, text, and CSV output
- [ ] **Cloud integration** - auto-upload to Google Drive, Dropbox, etc.
- [ ] **Encrypted backup** - password-protected 2FA secret storage
- [ ] **Import/export compatibility** with popular 2FA apps (Authy, Google Authenticator format)

### 3. **Processing Enhancements**
- [ ] **Duplicate detection** - skip already processed QR codes
- [ ] **Content filtering** - process only specific types (URLs, 2FA, emails, etc.)
- [ ] **Batch renaming** - rename files based on QR code content
- [ ] **OCR fallback** - attempt OCR when QR decoding fails
- [ ] **Image preprocessing** - auto-rotate, deskew, enhance contrast

### 4. **Security Features**
- [ ] **Secure deletion** of source images after processing
- [ ] **Audit logging** of all operations
- [ ] **Password protection** for sensitive operations
- [ ] **VPN/Proxy support** for URL opening
- [ ] **Content validation** - detect malicious URLs

### 5. **User Experience**
- [ ] **GUI interface** alongside CLI
- [ ] **Progress indicators** for batch processing
- [ ] **Configuration file** for persistent settings
- [ ] **Plug-in system** for extensibility
- [ ] **Auto-update mechanism**

### 6. **Integration Features**
- [ ] **Browser extension** companion
- [ ] **REST API** for remote processing
- [ ] **Mobile app version**
- [ ] **Database integration** for storing results
- [ ] **Webhook support** for automated workflows

### 7. **Advanced 2FA Management**
- [ ] **2FA code generation** - live TOTP code generation
- [ ] **Backup verification** - test 2FA secrets before import
- [ ] **Multi-account support** - handle QR codes with multiple 2FA secrets
- [ ] **Expiration tracking** - monitor 2FA backup ages
- [ ] **Recovery code extraction** - parse backup codes from QR content

### Implementation Priority Recommendation:
1. **Screenshot capture** (-s flag) - High priority, already in CLI
2. **QR code generation** - Useful complement to decoding
3. **PDF support** - Many 2FA QR codes are in PDF documents
4. **Enhanced filtering** - Better control over output
5. **GUI interface** - Makes tool accessible to non-technical users
