# 🚀 Simple File Sharing (AWS EC2 + S3)

A lightweight **Flask web app** that lets you upload files to **Amazon S3** and instantly get a **temporary (pre-signed) download link**.  
Perfect for sharing files securely without exposing your S3 bucket.

---

## ✨ Features
- 📤 Upload files directly from your browser  
- 🔒 Files are stored in a **private S3 bucket**  
- ⏱️ Generates **pre-signed download links** with expiration  
- ⚡ Deployable on **AWS EC2** in minutes  
- 🐍 Simple Python + Flask stack  

---

## 🛠️ Run Locally (optional)

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export BUCKET_NAME=your-bucket-name
export AWS_REGION=ap-south-1   # change if needed

# Run the app
python app.py
```

Now open 👉 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)  

> ⚠️ If running locally, make sure AWS credentials are configured (`aws configure`) or provided via environment variables.  
> On **EC2**, use an **IAM instance role** (no hardcoded keys!).  

---

## ⚙️ Environment Variables

| Variable                | Required | Default       | Description |
|--------------------------|----------|---------------|-------------|
| `BUCKET_NAME`            | ✅ Yes   | —             | Your S3 bucket name |
| `AWS_REGION`             | ❌ No    | ap-south-1    | AWS region |
| `DEFAULT_EXPIRY_SECONDS` | ❌ No    | 3600 (1h)     | Default link lifetime |
| `MAX_EXPIRY_SECONDS`     | ❌ No    | 86400 (24h)   | Max link lifetime |
| `MAX_CONTENT_LENGTH`     | ❌ No    | 50MB          | Max upload size |

---

## 🔐 Security Notes
- Keep the S3 bucket **private** (`Block Public Access = ON`)  
- Files are only accessible through **pre-signed URLs**  
- For production:
  - Use **Gunicorn + Nginx** (instead of Flask’s dev server)  
  - Enable **HTTPS** (e.g., via Let’s Encrypt)  

---

## 📦 Tech Stack
- [Python 3](https://www.python.org/)  
- [Flask](https://flask.palletsprojects.com/)  
- [Boto3](https://boto3.amazonaws.com/)  
- [AWS S3 + EC2](https://aws.amazon.com/)  
