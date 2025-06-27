# Use an official Python runtime as a base image.
FROM python:3.12-slim

# Environment variables to ensure proper Python behavior.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG_MODE=False

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY src/app.py /app/
COPY tests /app/tests

# Expose the port the app runs on.
EXPOSE 4000

# Define the command to run the app.
CMD ["python", "app.py"]

