# Use a build argument for the python version to support matrix builds
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# Create a non-root user and group for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy the application code
COPY app.py .

# Change ownership to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Run the memory-hog application
CMD ["python", "app.py"]




