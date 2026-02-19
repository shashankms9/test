import logging
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "images")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_blob_service_client():
    if not AZURE_STORAGE_CONNECTION_STRING:
        raise ValueError(
            "AZURE_STORAGE_CONNECTION_STRING environment variable is not set."
        )
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def ensure_container_exists(blob_service_client):
    container_client = blob_service_client.get_container_client(
        AZURE_STORAGE_CONTAINER_NAME
    )
    if not container_client.exists():
        container_client.create_container()
    return container_client


def list_uploaded_images():
    try:
        client = get_blob_service_client()
        container_client = ensure_container_exists(client)
        blobs = []
        for blob in container_client.list_blobs():
            blob_client = container_client.get_blob_client(blob.name)
            blobs.append(
                {
                    "name": blob.name,
                    "url": blob_client.url,
                    "size": blob.size,
                    "last_modified": blob.last_modified,
                }
            )
        return blobs
    except Exception as exc:
        logging.warning("Could not list blobs: %s", exc)
        return []


@app.route("/", methods=["GET"])
def index():
    images = list_uploaded_images()
    return render_template("index.html", images=images)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash(
            "Invalid file type. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS),
            "error",
        )
        return redirect(url_for("index"))

    try:
        filename = secure_filename(file.filename)
        # Prepend a unique prefix to avoid overwriting existing files
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        extension = filename.rsplit(".", 1)[1].lower()
        content_type_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "bmp": "image/bmp",
            "webp": "image/webp",
        }
        content_type = content_type_map.get(extension, "application/octet-stream")

        client = get_blob_service_client()
        container_client = ensure_container_exists(client)
        blob_client = container_client.get_blob_client(unique_filename)

        blob_client.upload_blob(
            file.stream,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )

        flash(f'Image "{filename}" uploaded successfully!', "success")
    except ValueError as exc:
        flash(str(exc), "error")
    except Exception as exc:
        flash(f"Upload failed: {exc}", "error")

    return redirect(url_for("index"))


@app.route("/delete/<path:blob_name>", methods=["POST"])
def delete(blob_name):
    try:
        client = get_blob_service_client()
        container_client = ensure_container_exists(client)
        container_client.delete_blob(blob_name)
        flash(f'Image "{blob_name}" deleted successfully.', "success")
    except Exception as exc:
        flash(f"Delete failed: {exc}", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
