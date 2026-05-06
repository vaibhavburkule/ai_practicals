# ☁ DISTRIBUTED COLLEGE DATA MANAGEMENT CLOUD
## Complete Beginner Guide (Step by Step)

---

## 📌 WHAT IS THIS PROJECT?

Think of this like Google Drive, but:
- It runs on YOUR lab's local network (LAN)
- YOU write the code (Cloud Controller)
- Files are stored in HDFS (Hadoop Distributed File System)
- Every file is ENCRYPTED before storing (very secure!)

---

## 📌 HOW IT WORKS (Simple Explanation)

```
UPLOAD:
  Your File (e.g. 200 MB PDF)
       ↓
  Split into Blocks [Block 0: 64MB] [Block 1: 64MB] [Block 2: 64MB] [Block 3: 8MB]
       ↓
  Encrypt each block with AES-256 (Lock with secret key)
       ↓
  Upload each encrypted block to HDFS storage
       ↓
  Save metadata.json (how many blocks, where they are)

DOWNLOAD:
  Request file
       ↓
  Read metadata.json (find all block paths)
       ↓
  Download each encrypted block from HDFS
       ↓
  Decrypt each block (unlock with secret key)
       ↓
  Join all blocks = Original file! ✓
```

---

## 📌 WHAT YOU NEED TO INSTALL

### Step 1: Install Python
- Go to https://python.org
- Download Python 3.x (latest version)
- Install it (check "Add to PATH" during installation)
- Open terminal/cmd and type: `python --version`
- You should see something like: Python 3.11.0

### Step 2: Install required libraries
Open terminal/cmd in the project folder and run:
```bash
pip install flask pycryptodome requests
```

That's it! These 3 libraries are all you need.

---

## 📌 PROJECT FILES EXPLAINED

```
college_cloud/
│
├── app.py              ← MAIN FILE (Cloud Controller code)
├── requirements.txt    ← List of libraries needed
├── README.md           ← This guide
│
├── templates/
│   └── index.html      ← Web interface (what user sees in browser)
│
├── local_hdfs_storage/ ← Created automatically (simulates HDFS for testing)
├── uploads/            ← Temporary folder for uploads
└── downloads/          ← Temporary folder for downloads
```

---

## 📌 HOW TO RUN (Step by Step)

### Method A: LOCAL MODE (Test on your laptop - NO Hadoop needed!)

1. Open terminal/command prompt
2. Go to project folder:
   ```
   cd college_cloud
   ```
3. Run the server:
   ```
   python app.py
   ```
4. Open browser and go to:
   ```
   http://localhost:5000
   ```
5. You should see the web interface!
6. Try uploading a file and downloading it back.

### Method B: With Real HDFS (For lab with Hadoop installed)

1. Make sure Hadoop/HDFS is running on your lab PC
2. Open `app.py` and change line 48:
   ```python
   LOCAL_MODE = False                     # Change True to False
   HDFS_HOST = "http://YOUR_PC_IP:9870"   # Your NameNode IP
   ```
3. Run: `python app.py`

---

## 📌 KEY CONCEPTS EXPLAINED SIMPLY

### What is HDFS?
- HDFS = Hadoop Distributed File System
- It's like a very big hard disk that can be spread across many computers
- Files are automatically divided into "blocks" and stored across multiple machines
- Even if one machine fails, your file is safe (it has copies!)

### What is a Block?
- When you store a big file (say 500 MB) in HDFS...
- HDFS doesn't store it as one piece
- It cuts it into pieces of 64 MB or 128 MB each
- Each piece = "block"
- These blocks can be on different computers

### What is AES-256 Encryption?
- AES = Advanced Encryption Standard
- 256 = key length (256 bits = very very strong)
- It's like a super-complicated lock
- Only someone with the SECRET KEY can unlock/read the file
- Even hackers with supercomputers can't crack AES-256!

### What is a Cloud Controller?
- It's your Python code (app.py)
- It controls EVERYTHING:
  - Receives files from users
  - Splits files into blocks
  - Encrypts blocks
  - Uploads to HDFS
  - Downloads from HDFS
  - Decrypts blocks
  - Joins blocks back into original file
  - Shows a web interface to users

---

## 📌 UNDERSTANDING THE CODE (app.py)

### Function 1: split_file_into_blocks()
```python
# This is like cutting a loaf of bread into equal slices
# Input: whole file (bytes)
# Output: list of blocks (slices)
blocks = split_file_into_blocks(file_data)
# If file is 200MB and block_size is 64MB:
# blocks = [block0(64MB), block1(64MB), block2(64MB), block3(8MB)]
```

### Function 2: encrypt_block()
```python
# This locks each block with AES-256
# Input: one block (plain bytes)
# Output: encrypted block (locked bytes)
encrypted = encrypt_block(block)
# encrypted = IV (16 bytes) + cipher text
```

### Function 3: decrypt_block()
```python
# This unlocks each block
# Input: encrypted block
# Output: original plain block
decrypted = decrypt_block(encrypted)
```

### Function 4: upload_block_to_hdfs()
```python
# This saves encrypted block to HDFS
# Uses WebHDFS REST API (HTTP PUT request)
upload_block_to_hdfs(encrypted_block, "/college_cloud/files/myfile.pdf/block_0.enc")
```

### Function 5: download_block_from_hdfs()
```python
# This fetches a block from HDFS
# Uses WebHDFS REST API (HTTP GET request)
data = download_block_from_hdfs("/college_cloud/files/myfile.pdf/block_0.enc")
```

---

## 📌 HOW TO EXPLAIN IN VIVA/PRESENTATION

**Question: What is your project?**
> "We built a private cloud storage system for our college lab. It runs on the local LAN and allows students and teachers to upload and download files securely. The files are split into blocks and encrypted with AES-256 before storing."

**Question: What is the Cloud Controller?**
> "The Cloud Controller is our Python code (app.py) that manages all operations - receiving uploads, splitting files, encrypting, uploading to HDFS, and reversing the process for downloads."

**Question: Why AES-256?**
> "AES-256 is the industry-standard encryption algorithm. The 256-bit key makes it practically uncrackable. It ensures that even if someone accesses the HDFS storage directly, they cannot read the files without the secret key."

**Question: What is WebHDFS?**
> "WebHDFS is a REST API that allows HTTP-based access to HDFS. We use HTTP PUT to upload blocks and HTTP GET to download blocks. This makes our controller independent of Hadoop libraries."

**Question: What is the block size and why?**
> "We use 64 MB blocks, following HDFS convention. This allows parallel processing and distributed storage across multiple nodes. Smaller files become 1 block, larger files are split into multiple blocks."

---

## 📌 COMMON ERRORS & FIXES

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: flask` | Flask not installed | Run: `pip install flask` |
| `ModuleNotFoundError: Crypto` | pycryptodome not installed | Run: `pip install pycryptodome` |
| `Port 5000 already in use` | Another app using port 5000 | Change port in app.py to 5001 |
| HDFS connection refused | HDFS not running | Set `LOCAL_MODE = True` |
| File too large to upload | Max size exceeded | Change `MAX_CONTENT_LENGTH` in app.py |

---

## 📌 TECH STACK SUMMARY

| Component | Technology | Purpose |
|-----------|------------|---------|
| Cloud Controller | Python 3 | Main logic code |
| Web Framework | Flask | Web server & routing |
| Encryption | PyCryptodome (AES-256) | File security |
| Storage | HDFS / Local folder | Block storage |
| HDFS API | WebHDFS REST API | HTTP-based HDFS access |
| Web UI | HTML + CSS + JavaScript | User interface |

---

## 📌 MINI DEMO STEPS FOR PRESENTATION

1. Start server: `python app.py`
2. Open browser: `http://localhost:5000`
3. Show the web interface
4. Upload a small file (e.g., a PDF)
5. Show the terminal - explain what is happening:
   - File being split into blocks
   - Each block being encrypted
   - Blocks being stored
6. Go to `local_hdfs_storage/` folder - show the encrypted .enc files
7. Download the file back - show it's the same original file

---

## 📌 HOW TO SUBMIT / REPORT

Your mini-project should include:
1. **Source Code**: app.py + templates/index.html
2. **Report sections**:
   - Introduction (What is cloud computing, SaaS, HDFS)
   - Architecture Diagram (show the flow)
   - Implementation Details (explain each function)
   - Screenshots (web UI, terminal output)
   - Conclusion

---

All the best! You've got this! 💪
