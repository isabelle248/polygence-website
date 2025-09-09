# syntax=docker/dockerfile:1

# Start from Debian base image
FROM eclipse-temurin:21-jdk

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    build-essential \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------
# Install Node.js (LTS or latest — we’ll use v22.18.0)
# ---------------------------------------------------
ENV NODE_VERSION=22.18.0

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# ---------------------------------------------------
# Install Java 17 for Audiveris
# ---------------------------------------------------
# Install OpenJDK 21 for Audiveris
RUN apt-get update && apt-get install -y openjdk-21-jdk && \
    rm -rf /var/lib/apt/lists/*

RUN java -version

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH


# ---------------------------------------------------
# Install & Build Audiveris
# ---------------------------------------------------
RUN git clone --branch development https://github.com/Audiveris/audiveris.git

WORKDIR /audiveris
RUN ./gradlew build --stacktrace --info

RUN mkdir /audiveris-extract && \
    tar -xvf /audiveris/build/distributions/Audiveris*.tar -C /audiveris-extract && \
    mv /audiveris-extract/Audiveris*/* /audiveris-extract/ && \
    rm -r /audiveris

# ---------------------------------------------------
# Set working directory for your Node app
# ---------------------------------------------------
WORKDIR /usr/src/app

# Copy package.json and install dependencies
COPY package*.json ./
RUN npm install --omit=dev

# Copy the rest of the app
COPY . .

# ---------------------------------------------------
# Expose API port & set default command
# ---------------------------------------------------
EXPOSE 3000
CMD ["npm", "start"]
