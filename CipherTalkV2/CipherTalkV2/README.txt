CIPHERTALK V2 - QR CODE IMPLEMENTATION
=====================================

OVERVIEW
--------
CipherTalk V2 is a peer-to-peer encrypted chat application that now includes QR code functionality for easy connection establishment. The application allows users to connect via IP address or by sharing QR codes/text codes containing connection information.

FEATURES IMPLEMENTED
-------------------
1. **QR Code Generation**: Automatically generates QR codes containing connection information
2. **Text Code Display**: Shows connection data in text format for manual sharing
3. **Connection Parsing**: Can parse QR codes/text codes to establish connections
4. **Dual Connection Methods**: Support for both IP-based and QR code-based connections
5. **Automatic IP Detection**: Automatically detects local IP address for connection sharing
6. **Secure Handshake**: Maintains the existing secure handshake protocol

NEW COMPONENTS
--------------
1. **qr_service.py**: Core QR code functionality
   - QR code generation and saving
   - Connection data packaging
   - IP address detection
   - Connection data parsing

2. **Enhanced run.py**: Updated main application
   - QR code integration
   - Multiple connection options
   - Improved user interface

3. **Updated requirements.txt**: Added dependencies
   - qrcode: For QR code generation
   - pillow: For image processing

CONNECTION INFORMATION PACKAGED
------------------------------
The QR code and text code contain the following information:
- Type identifier: "cipher_talk_connection"
- Version: "1.0"
- Username: The user's chosen username
- Public Key: User's public key for encryption
- IP Address: Local IP address (auto-detected)
- Port: Listening port (default: 9000)

USAGE INSTRUCTIONS
------------------

1. **Starting the Application**:
   ```
   python run.py
   ```

2. **Initial Setup**:
   - Enter your username when prompted
   - The app will generate and display your connection information
   - A QR code image will be saved to ~/cipher_talk/qr_codes/

3. **Connection Methods**:
   
   **Option 1: IP Address Connection**
   - Choose option 1 when prompted
   - Enter the peer's IP address
   - Traditional connection method

   **Option 2: QR Code/Text Code Connection**
   - Choose option 2 when prompted
   - Two sub-options available:
     a) Enter connection code manually (paste the text code)
     b) Scan QR code (manual process using external scanner)

4. **Sharing Your Connection**:
   - Your connection code is displayed in the terminal
   - QR code image is saved automatically
   - Share either the text code or QR code image with others

5. **Connecting to Others**:
   - Use option 2 in the connection menu
   - Paste their connection code or scan their QR code
   - The app will automatically establish the connection

FILE STRUCTURE
--------------
```
CipherTalkV2/CipherTalkV2/
├── run.py                 # Main application (enhanced with QR support)
├── qr_service.py          # QR code functionality
├── requirements.txt       # Dependencies (updated)
├── crypto_service.py      # Cryptographic operations
├── keystore.py           # Key management
├── local_storage.py      # Database operations
├── friend_service.py     # Contact management
├── message_service.py    # Message encryption/decryption
├── file_service.py       # File handling
└── tcp_connection.py     # Network operations
```

DEPENDENCIES
------------
- pynacl: For cryptographic operations
- cryptography: Additional crypto support
- sqlalchemy: Database management
- typer: Command line interface
- python-dotenv: Environment variables
- pycryptodome: Crypto operations
- qrcode: QR code generation
- pillow: Image processing

INSTALLATION
------------
1. Navigate to the application directory
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python run.py
   ```

SECURITY FEATURES
-----------------
- End-to-end encryption using public key cryptography
- Secure handshake protocol
- Session key generation for each connection
- Encrypted file sharing support
- Local key storage with protection

TESTING
-------
To test the QR code functionality:
1. Run the app on two different machines or terminals
2. Generate connection codes on both
3. Use the QR code/text code method to connect
4. Verify that messages are encrypted and delivered correctly

NOTES
-----
- QR codes are saved in ~/cipher_talk/qr_codes/ directory
- Connection codes are valid JSON format for easy parsing
- The app automatically detects your local IP address
- All existing security features are preserved
- Backward compatibility with IP-based connections maintained

BRANCH INFORMATION
------------------
This implementation is on the "QRcodeImplementation" branch, created from the "test" branch.
The implementation adds QR code functionality while preserving all existing features. 