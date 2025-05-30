#Docker File

# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ..

# Run the application
CMD ["uvicorn", "main:app","--host", "0.0.0.0", "--port", "8000"]
