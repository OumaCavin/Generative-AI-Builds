# DocGenie Agent Dockerfile
# Phase 5: Documentation Generation Service Container
# Build: docker build -t docgenie-agent .
# Run: docker run -p 8080:8080 docgenie-agent

FROM python:3.11-slim

# Metadata
LABEL maintainer="MiniMax Agent"
LABEL description="DocGenie Agent - Automatic Code Documentation Generator"
LABEL version="1.0.0"
LABEL phase="5"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCGENIE_CONFIG_PATH=/app/config/config.json
ENV DOCGENIE_LOG_LEVEL=INFO
ENV DOCGENIE_OUTPUT_DIR=/app/outputs

# Create app directory and user
RUN groupadd -r docgenie && useradd -r -g docgenie docgenie

# Install system dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    graphviz-dev \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p templates outputs diagrams cache logs tests/demo_data && \
    chown -R docgenie:docgenie /app

# Set proper permissions
RUN chmod +x deploy.sh && \
    chmod +x setup.py && \
    chmod +x main.jac

# Switch to non-root user
USER docgenie

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Default command
CMD ["python", "-m", "jac_lang", "run", "main.jac"]

# Alternative commands for different modes
# CMD ["python", "setup.py", "--validate-only"]
# CMD ["python", "tests/test_documentation.py"]
# CMD ["./deploy.sh", "demo"]
