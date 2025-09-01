# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Install dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code
COPY src /code/src

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
