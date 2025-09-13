import os
import uuid
import mimetypes
from flask import Flask, request, render_template, redirect, url_for, flash
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# ---------- Config ----------
BUCKET_NAME = os.environ.get("BUCKET_NAME", "").strip()   #Enter actual BUCKET_NAME
AWS_REGION = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "ap-south-1")).strip()  # default to Mumbai
MAX_EXPIRY_SECONDS = int(os.environ.get("MAX_EXPIRY_SECONDS", "86400"))  # max 24 hours
DEFAULT_EXPIRY_SECONDS = int(os.environ.get("DEFAULT_EXPIRY_SECONDS", "3600"))  # default 1 hour
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", str(50 * 1024 * 1024)))  # 50 MB default

ALLOWED_EXTENSIONS = set([
    "txt","pdf","png","jpg","jpeg","gif","doc","docx","ppt","pptx","xls","xlsx","csv","zip","rar","7z","mp4","mp3","wav"
])

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Create S3 client (credentials will come from EC2 instance role)
s3 = boto3.client("s3", region_name=AWS_REGION)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", bucket_set=bool(BUCKET_NAME))

@app.route("/upload", methods=["POST"])
def upload():
    if not BUCKET_NAME:
        flash("Server is not configured. Set BUCKET_NAME env var on the EC2 instance.")
        return redirect(url_for("index"))

    if "file" not in request.files:
        flash("No file part in the request.")
        return redirect(url_for("index"))
    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for("index"))
    if not allowed_file(file.filename):
        flash("File type not allowed.")
        return redirect(url_for("index"))

    # Parse desired expiry
    try:
        requested_expiry = int(request.form.get("expiry_seconds", str(DEFAULT_EXPIRY_SECONDS)))
    except ValueError:
        requested_expiry = DEFAULT_EXPIRY_SECONDS
    expiry = max(60, min(requested_expiry, MAX_EXPIRY_SECONDS))  # clamp between 1 min and MAX_EXPIRY_SECONDS

    # Create a unique key for S3
    ext = os.path.splitext(file.filename)[1].lower()
    key = f"uploads/{uuid.uuid4().hex}{ext}"

    # Guess content type
    content_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    try:
        # Upload the file object to S3
        s3.upload_fileobj(
            Fileobj=file,
            Bucket=BUCKET_NAME,
            Key=key,
            ExtraArgs={
                "ContentType": content_type,
                "Metadata": {
                    "original-filename": file.filename
                }
            }
        )

        # Generate presigned URL for downloading the file
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": BUCKET_NAME, "Key": key},
            ExpiresIn=expiry
        )

        # Show the URL to the user
        flash("Upload successful! Copy your download link below. It will expire automatically.")
        return render_template("index.html", download_url=url, expiry_seconds=expiry, original=file.filename, bucket_set=True)

    except (BotoCoreError, ClientError) as e:
        print("Upload error:", e)
        flash("Upload failed. Check server logs and IAM permissions.")
        return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
