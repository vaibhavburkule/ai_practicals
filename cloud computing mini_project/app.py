

import os
import math
import json
import requests
from flask import Flask, request, render_template, send_file, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import io

HDFS_HOST = "http://localhost:9870"         # Your HDFS NameNode address
HDFS_USER = "hdfs"                          # HDFS username
HDFS_BASE_PATH = "/college_cloud/files"     # Where files are stored in HDFS
BLOCK_SIZE = 64 * 1024 * 1024              # 64 MB per block (64 * 1024 * 1024 bytes)
SECRET_KEY = b"MySecretKey12345MySecretKey12345"  # 32 bytes = AES-256 key (KEEP THIS SECRET!)

LOCAL_MODE = True
LOCAL_STORAGE = "./local_hdfs_storage"     # Folder that acts like HDFS

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # Max upload: 500MB
os.makedirs(LOCAL_STORAGE, exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("downloads", exist_ok=True)

def split_file_into_blocks(file_data: bytes, block_size: int = BLOCK_SIZE):
   
    blocks = []
    total_size = len(file_data)
    num_blocks = math.ceil(total_size / block_size)
    
    print(f"[SPLIT] File size: {total_size} bytes")
    print(f"[SPLIT] Block size: {block_size} bytes")
    print(f"[SPLIT] Total blocks: {num_blocks}")
    
    for i in range(num_blocks):
        start = i * block_size
        end = min(start + block_size, total_size)
        block = file_data[start:end]
        blocks.append(block)
        print(f"[SPLIT] Block {i}: bytes {start} to {end} (size: {len(block)} bytes)")
    
    return blocks

def encrypt_block(block_data: bytes, key: bytes = SECRET_KEY):
    """
    Encrypts one block using AES-256 CBC mode.
    
    AES-256 = Advanced Encryption Standard with 256-bit key
    It's so strong that even supercomputers can't crack it!
    
    How it works:
      - Generates a random IV (Initialization Vector) - like a random salt
      - Encrypts data using key + IV
      - Returns: IV + encrypted_data (we need IV to decrypt later)
    
    Args:
        block_data: Raw bytes of one block
        key: 32-byte secret key
    
    Returns:
        Encrypted bytes (IV prepended)
    """
    iv = get_random_bytes(16)           # Random 16-byte IV
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(block_data, AES.block_size)  # Pad to multiple of 16 bytes
    encrypted = cipher.encrypt(padded_data)
    
    # Store IV + encrypted data together
    # We need the IV to decrypt, so we save it at the start
    result = iv + encrypted
    print(f"[ENCRYPT] Block encrypted: {len(block_data)} -> {len(result)} bytes")
    return result


# ─────────────────────────────────────────────
#  STEP 2B: DECRYPT a block using AES-256
# ─────────────────────────────────────────────
def decrypt_block(encrypted_data: bytes, key: bytes = SECRET_KEY):
    
    iv = encrypted_data[:16]              # First 16 bytes = IV
    cipher_text = encrypted_data[16:]     # Rest = actual encrypted data
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(cipher_text)
    original = unpad(decrypted, AES.block_size)  # Remove padding
    print(f"[DECRYPT] Block decrypted: {len(encrypted_data)} -> {len(original)} bytes")
    return original


# ─────────────────────────────────────────────
#  STEP 3A: UPLOAD block to HDFS (or local)
# ─────────────────────────────────────────────
def upload_block_to_hdfs(block_data: bytes, hdfs_path: str):
    
    if LOCAL_MODE:
        # Save to local folder (simulates HDFS for testing)
        local_path = LOCAL_STORAGE + hdfs_path
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(block_data)
        print(f"[UPLOAD-LOCAL] Saved to: {local_path}")
    else:
        # Real HDFS upload using WebHDFS REST API
        url = f"{HDFS_HOST}/webhdfs/v1{hdfs_path}?op=CREATE&user.name={HDFS_USER}&overwrite=true"
        response = requests.put(url, data=block_data, allow_redirects=True)
        if response.status_code not in [200, 201]:
            raise Exception(f"HDFS upload failed: {response.status_code} {response.text}")
        print(f"[UPLOAD-HDFS] Uploaded to: {hdfs_path}")


# ─────────────────────────────────────────────
#  STEP 3B: DOWNLOAD block from HDFS (or local)
# ─────────────────────────────────────────────
def download_block_from_hdfs(hdfs_path: str):
    
    if LOCAL_MODE:
        local_path = LOCAL_STORAGE + hdfs_path
        with open(local_path, "rb") as f:
            data = f.read()
        print(f"[DOWNLOAD-LOCAL] Read from: {local_path}")
        return data
    else:
        url = f"{HDFS_HOST}/webhdfs/v1{hdfs_path}?op=OPEN&user.name={HDFS_USER}"
        response = requests.get(url, allow_redirects=True)
        if response.status_code != 200:
            raise Exception(f"HDFS download failed: {response.status_code}")
        print(f"[DOWNLOAD-HDFS] Downloaded from: {hdfs_path}")
        return response.content


# ─────────────────────────────────────────────
#  MAIN UPLOAD WORKFLOW
#  (Split -> Encrypt -> Upload to HDFS)
# ─────────────────────────────────────────────
def upload_file_to_cloud(file_data: bytes, filename: str, uploader: str):
    
    print(f"\n{'='*50}")
    print(f"UPLOADING FILE: {filename}")
    print(f"UPLOADER: {uploader}")
    print(f"{'='*50}")
    
    # Step 1: Split
    blocks = split_file_into_blocks(file_data)
    
    # Steps 2 & 3: Encrypt and Upload each block
    block_paths = []
    for i, block in enumerate(blocks):
        # Encrypt the block
        encrypted_block = encrypt_block(block)
        
        # Define HDFS path for this block
        # Example: /college_cloud/files/assignment.pdf/block_0.enc
        block_path = f"{HDFS_BASE_PATH}/{filename}/block_{i}.enc"
        
        # Upload encrypted block to HDFS
        upload_block_to_hdfs(encrypted_block, block_path)
        block_paths.append(block_path)
        
        print(f"[PROGRESS] Block {i+1}/{len(blocks)} uploaded ✓")
    
    # Save metadata (so we know how to reassemble the file later)
    metadata = {
        "filename": filename,
        "uploader": uploader,
        "total_size": len(file_data),
        "num_blocks": len(blocks),
        "block_size": BLOCK_SIZE,
        "block_paths": block_paths
    }
    
    # Save metadata to HDFS/local
    meta_path = f"{HDFS_BASE_PATH}/{filename}/metadata.json"
    meta_bytes = json.dumps(metadata, indent=2).encode()
    upload_block_to_hdfs(meta_bytes, meta_path)
    
    print(f"\n[SUCCESS] File '{filename}' uploaded in {len(blocks)} blocks!")
    return metadata


# ─────────────────────────────────────────────
#  MAIN DOWNLOAD WORKFLOW
#  (Download -> Decrypt -> Reassemble)
# ─────────────────────────────────────────────
def download_file_from_cloud(filename: str):
    
    print(f"\n{'='*50}")
    print(f"DOWNLOADING FILE: {filename}")
    print(f"{'='*50}")
    
    # Step 1: Get metadata
    meta_path = f"{HDFS_BASE_PATH}/{filename}/metadata.json"
    meta_bytes = download_block_from_hdfs(meta_path)
    metadata = json.loads(meta_bytes.decode())
    
    print(f"[META] Total blocks: {metadata['num_blocks']}")
    print(f"[META] Original size: {metadata['total_size']} bytes")
    
    # Steps 2 & 3: Download and Decrypt each block
    reassembled = b""
    for i, block_path in enumerate(metadata["block_paths"]):
        # Download encrypted block
        encrypted_block = download_block_from_hdfs(block_path)
        
        # Decrypt it
        decrypted_block = decrypt_block(encrypted_block)
        
        # Append to reassembled file
        reassembled += decrypted_block
        print(f"[PROGRESS] Block {i+1}/{metadata['num_blocks']} decrypted ✓")
    
    print(f"\n[SUCCESS] File '{filename}' downloaded and reassembled!")
    print(f"[SIZE] Reassembled size: {len(reassembled)} bytes (original: {metadata['total_size']})")
    return reassembled


# ─────────────────────────────────────────────
#  WEB ROUTES (Flask Web Server)
# ─────────────────────────────────────────────

@app.route("/")
def home():
    """Show the main dashboard page"""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle file upload from web form"""
    if "file" not in request.files:
        return jsonify({"error": "No file selected"}), 400
    
    file = request.files["file"]
    uploader = request.form.get("uploader", "Anonymous")
    
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400
    
    try:
        file_data = file.read()
        metadata = upload_file_to_cloud(file_data, file.filename, uploader)
        return jsonify({
            "success": True,
            "message": f"File '{file.filename}' uploaded successfully!",
            "blocks": metadata["num_blocks"],
            "size": metadata["total_size"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<filename>")
def download(filename):
    """Handle file download request"""
    try:
        file_data = download_file_from_cloud(filename)
        return send_file(
            io.BytesIO(file_data),
            download_name=filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/files")
def list_files():
    """List all uploaded files"""
    files = []
    if LOCAL_MODE:
        base = LOCAL_STORAGE + HDFS_BASE_PATH
        if os.path.exists(base):
            for fname in os.listdir(base):
                meta_path = f"{base}/{fname}/metadata.json"
                if os.path.exists(meta_path):
                    with open(meta_path) as f:
                        meta = json.load(f)
                    files.append({
                        "filename": fname,
                        "uploader": meta.get("uploader"),
                        "size": meta.get("total_size"),
                        "blocks": meta.get("num_blocks")
                    })
    return jsonify(files)


# ─────────────────────────────────────────────
#  RUN THE SERVER
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  DISTRIBUTED COLLEGE DATA MANAGEMENT CLOUD")
    print("  Cloud Controller starting...")
    print(f"  Mode: {'LOCAL (testing)' if LOCAL_MODE else 'HDFS (production)'}")
    print("  Open browser: http://localhost:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
