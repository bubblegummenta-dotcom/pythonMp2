FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=7080 \
    MPD_HOST=mpd \
    MPD_PORT=6600

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/

# Expose web port
EXPOSE 7080

# Command to run the application
CMD ["python", "-m", "app.main"]
