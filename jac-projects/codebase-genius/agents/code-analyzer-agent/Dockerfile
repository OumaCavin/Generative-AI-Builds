# Dockerfile for Codebase Genius Code Analyzer
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install tree-sitter CLI
RUN curl -L https://github.com/tree-sitter/tree-sitter/releases/latest/download/tree-sitter-linux-x64.gz | \
    gunzip | \
    tee /usr/local/bin/tree-sitter > /dev/null && \
    chmod +x /usr/local/bin/tree-sitter

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install JAC runtime
RUN pip install jaclang jac-cloud

# Create necessary directories
RUN mkdir -p logs cache output config tests parsers data temp

# Copy application code
COPY main.jac .
COPY config/ config/

# Copy test files
COPY tests/ tests/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV JAC_SERVE_HOST=0.0.0.0
ENV JAC_SERVE_PORT=8081

# Expose port for API
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8081/api/health || exit 1

# Create entrypoint script
COPY <<EOF /entrypoint.sh
#!/bin/bash
set -e

echo "🌳 Initializing Tree-sitter parsers..."

# Wait for service to be ready
echo "🚀 Starting Code Analyzer service..."
exec jac serve main.jac
EOF

RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
