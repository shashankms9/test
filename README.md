# Azure Blob Image Upload Application

A simple Python/Flask web application to upload, view, and delete images stored in **Azure Blob Storage**.

## Features

- Upload images (PNG, JPG, JPEG, GIF, BMP, WEBP) up to 16 MB
- View all uploaded images in a gallery
- Delete images from Azure Blob Storage
- Drag-and-drop file selection

## Prerequisites

- Python 3.8+
- An [Azure Storage Account](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create)

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd <repo-directory>
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your Azure Storage credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=<your_account>;AccountKey=<your_key>;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=images
FLASK_SECRET_KEY=<a-random-secret-key>
```

You can find your connection string in the Azure Portal under:  
**Storage Account → Access Keys → Connection string**

### 4. Run the application

```bash
python app.py
```

The app will be available at `http://localhost:5000`.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `AZURE_STORAGE_CONNECTION_STRING` | Full Azure Storage connection string | *(required)* |
| `AZURE_STORAGE_CONTAINER_NAME` | Blob container name | `images` |
| `FLASK_SECRET_KEY` | Flask session secret key | `dev-secret-key` |

## Notes

- The application automatically creates the blob container if it does not exist.
- Each uploaded file gets a unique UUID prefix to prevent overwrites.
- Images are served directly from Azure Blob Storage URLs.
