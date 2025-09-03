# API Setup and Usage Guide

## 1. Local Development Setup

### Prerequisites

-   Python **3.11+**
-   pip or Poetry for dependency management

### Steps

1. Clone the repository:

```bash
git clone https://github.com/georgemarsh1809/GlobalTask.git
cd GlobalTask
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the API locally:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

5. Open the interactive API docs in your browser: 👉 http://localhost:8000/docs

## 2. Run with Docker

### Prerequisites

-   Docker installed and running

### Steps

1. Build the image:

```bash
docker build -t creative-approval-api .
```

2. Run the container:

```bash
docker run -p 8000:8000 creative-approval-api
```

3. Open the interactive API docs: 👉 http://localhost:8000/docs

## 3. Run Tests

The project uses **pytest** with tiny test images generated at runtime.

Locally:

```bash
pytest -v
```

In Docker:

```bash
docker run creative-approval-api pytest -v
```

## 4. API Endpoints

-   `GET /health` → Service status
-   `POST /creative-approval` → Upload a creative for validation
    -   **Input**: multipart form with:
        -   `file`: PNG/JPEG/small GIF
        -   `metadata`: optional JSON string (`market`, `placement`, `audience`,
            `category`)
    -   **Output**: JSON with:
        -   `status`: `"APPROVED"`, `"REJECTED"`, `"REQUIRES_REVIEW"`
        -   `reasons`: list of rule triggers
        -   `img_format`, `img_width`, `img_height`, `img_size`
