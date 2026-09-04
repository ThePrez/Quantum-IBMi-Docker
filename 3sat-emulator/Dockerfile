# Base image: Python 3.11 slim
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System dependencies:
#   gcc            — required to build several Python extension packages
#   libkrb5-dev    — Kerberos headers needed to compile the gssapi Python package
#   libgssapi-krb5-2 — Kerberos runtime library required by gssapi at import time
#   (gssapi is a transitive dependency of mapepire-python on Linux)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libkrb5-dev \
    libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy notebooks and supporting files
COPY *.ipynb .

# Run as non-root user for security
RUN useradd -m -u 1000 quantum && \
    chown -R quantum:quantum /app && \
    mkdir -p /home/quantum/.jupyter

COPY jupyter_server_config.py /home/quantum/.jupyter/
RUN chown -R quantum:quantum /home/quantum/.jupyter

USER quantum

EXPOSE 8888

ENTRYPOINT ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
