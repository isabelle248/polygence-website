# 1. Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# 2. Avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# 3. Install dependencies: Java, Python, Node, pip, wget, etc.
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    nodejs \
    npm \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 4. Download and install Audiveris .deb package
RUN wget https://github.com/Audiveris/audiveris/releases/download/5.6.2/audiveris_5.6.2-1_amd64.deb \
    && dpkg -i audiveris_5.6.2-1_amd64.deb || apt-get install -f -y \
    && rm audiveris_5.6.2-1_amd64.deb

# 5. Set working directory
WORKDIR /app

# 6. Copy Node package files first for caching
COPY package*.json ./
RUN npm install

# 7. Copy the rest of the project
COPY . .

# 8. Install Python dependencies for CREPE & music analysis
RUN pip3 install --no-cache-dir -r requirements.txt

# 9. Make your shell script executable
RUN chmod +x scripts/polygence.sh

# 10. Expose app port (change if needed)
EXPOSE 3000

# 11. Start the Node.js app
CMD ["npm", "start"]
