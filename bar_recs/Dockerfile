# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /machine_learning_client

# Install necessary system dependencies for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pipenv
RUN python -m pip install --upgrade pip && pip install pipenv

# Copy Pipfile and Pipfile.lock for dependency installation
COPY Pipfile Pipfile.lock ./

# Install dependencies with pipenv
RUN pipenv install --python $(which python3) --deploy --ignore-pipfile

# Copy the rest of the application code into the container
COPY . .

EXPOSE 5002

# Set the command to run the ML client
CMD ["pipenv", "run", "python", "bar_recs.py"]
