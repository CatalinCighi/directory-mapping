# Base image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . ./

# Set the default command to run the script
CMD ["python", "mapdir.py"]
