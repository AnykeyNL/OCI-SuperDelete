# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY delete.py .
COPY ocimodules/ ./ocimodules/

# Create directory for OCI config
RUN mkdir -p /root/.oci

# Set environment variables
ENV OCI_CONFIG_FILE=/root/.oci/config
ENV OCI_CONFIG_PROFILE=DEFAULT

# Create volume mount point for OCI config
VOLUME ["/root/.oci"]

# Set the entrypoint
ENTRYPOINT ["python", "delete.py"] 