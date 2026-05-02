# Start from the official Python 3.9 slim image
# Slim is smaller than the full image, which saves space
FROM python:3.9-slim
# Set the working directory inside the container
# All following commands run in this directory
WORKDIR /app
# Copy the requirements file
# This goes first because it rarely changes (good for caching)
COPY requirements.txt .
# Install any Python dependencies
# --no-cache-dir saves space in the image
RUN pip install --no-cache-dir -r requirements.txt
# Copy the word counter script into the container
# This goes last because it changes frequently
COPY word_counter.py .
# Create a non-root user for security
# This prevents someone from running the container as root
RUN useradd -m counter && chown -R counter:counter /app
# Switch to the non-root user
USER counter
# Set environment variables if needed
# PYTHONUNBUFFERED ensures print statements appear immediately
ENV PYTHONUNBUFFERED=1
# The default command when the container starts
# This uses the word counter script
# Arguments will be passed when running the container
ENTRYPOINT [ "python", "word_counter.py" ]
