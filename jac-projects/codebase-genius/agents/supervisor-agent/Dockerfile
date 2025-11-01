# Supervisor Agent Dockerfile
# Phase 6: Multi-Agent Orchestration Service Container
# Build: docker build -t supervisor-agent .
# Run: docker run -p 8080:8080 supervisor-agent

FROM python:3.11-slim

# Metadata
LABEL maintainer="MiniMax Agent"
LABEL description="Supervisor Agent - Multi-Agent Orchestration System for Codebase Genius"
LABEL version="1.0.0"
LABEL phase="6"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SUPERVISOR_CONFIG_PATH=/app/config/config.json
ENV SUPERVISOR_LOG_LEVEL=INFO
ENV SUPERVISOR_LOG_DIR=/app/logs
ENV SUPERVISOR_TEMP_DIR=/app/temp
ENV SUPERVISOR_WORKFLOW_TIMEOUT=1800
ENV SUPERVISOR_MAX_CONCURRENT=5

# Create app directory and user
RUN groupadd -r supervisor && useradd -r -g supervisor supervisor

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
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
RUN mkdir -p logs temp workflow_data agent_communication workflow_templates metrics cache && \
    chown -R supervisor:supervisor /app

# Set proper permissions
RUN chmod +x deploy.sh && \
    chmod +x setup.py && \
    chmod +x main.jac

# Switch to non-root user
USER supervisor

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Default command
CMD ["python", "-m", "jac_lang", "run", "main.jac"]

# Alternative commands for different modes
# CMD ["python", "setup.py", "--validate-only"]
# CMD ["python", "tests/test_supervisor.py"]
# CMD ["./deploy.sh", "demo"]
# CMD ["./deploy.sh", "test"]
