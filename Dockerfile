# Use an official Python runtime as a parent image.
# 'slim' is a good choice for keeping the image size down.
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# [FIX] Install system dependencies required for building audio packages.
# - build-essential: Installs compilers like gcc.
# - portaudio19-dev: The development files for the PortAudio library, required by pyaudio.
# - ffmpeg: Required by pydub for audio processing.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the file that lists the Python dependencies
COPY requirements.txt .

# Install Python packages specified in requirements.txt
# Using --no-cache-dir reduces the final image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Command to run your FastAPI application using uvicorn
# It will be accessible on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]