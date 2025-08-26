# Origo Backend Dockerfile - Optimized for faster builds

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only essential system dependencies
# gcc and g++ needed for some Python packages compilation
# curl needed for health checks
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
# NOTE: PyTorch installation commented out - not needed for current simulated calculations
# When implementing real AI models, uncomment the line below:
# RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# NOTE: NLTK data download removed - not needed for current simulated calculations
# When implementing real NLP models, uncomment and ensure NLTK is in requirements.txt:
# RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Expose port
EXPOSE 8000

# Health check using curl to match docker-compose.yml
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]