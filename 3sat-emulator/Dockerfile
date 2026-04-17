# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Jupyter notebooks and supporting files
COPY *.ipynb .
COPY Db2.sql .

# Create non-root user for security
RUN useradd -m -u 1000 quantum && \
    chown -R quantum:quantum /app && \
    mkdir -p /home/quantum/.jupyter

# Copy Jupyter config
COPY jupyter_server_config.py /home/quantum/.jupyter/
RUN chown -R quantum:quantum /home/quantum/.jupyter

# Switch to non-root user
USER quantum

# Expose Jupyter port
EXPOSE 8888

# Set entrypoint to start Jupyter Lab
ENTRYPOINT ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]