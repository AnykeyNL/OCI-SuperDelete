# Use Python 3.11 as base image with multi-arch support
FROM --platform=$BUILDPLATFORM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY delete.py .
COPY ocimodules/ ./ocimodules/

# Create non-root user and group & create directory for OCI config with proper permissions
RUN groupadd -r oci && \
  useradd -r -g oci oci && \
  mkdir -p /home/oci/.oci && \
  chown -R oci:oci /home/oci/.oci && \
  chown -R oci:oci /app

# Set environment variables
ENV OCI_CONFIG_FILE=/home/oci/.oci/config
ENV OCI_CONFIG_PROFILE=DEFAULT

# Create volume mount point for OCI config
VOLUME ["/home/oci/.oci"]

# Switch to non-root user
USER oci

# Set the entrypoint
ENTRYPOINT ["python", "delete.py"] 