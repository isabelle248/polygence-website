# -----------------------------
# Base image
# -----------------------------
FROM node:18-bullseye

# -----------------------------
# Set working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    openjdk-17-jre \
    python3 \
    python3-pip \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Install Audiveris (ZIP binary)
# -----------------------------
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.6.2/Audiveris-5.6.2.zip \
    && unzip Audiveris-5.6.2.zip -d /opt/ \
    && ln -s /opt/Audiveris-5.6.2/bin/audiveris /usr/local/bin/audiveris \
    && rm Audiveris-5.6.2.zip

# -----------------------------
# Python dependencies
# -----------------------------
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# -----------------------------
# Node dependencies
# -----------------------------
COPY package*.json ./
RUN npm install

# -----------------------------
# Copy project files
# -----------------------------
COPY . .

# -----------------------------
# Expose port for web server
# -----------------------------
EXPOSE 3000

# -----------------------------
# Start the server
# -----------------------------
CMD ["npm", "start"]
