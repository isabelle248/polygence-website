FROM gradle:jdk17-alpine
# FROM gradle:jdk17

# GET AUDIVERIS CODE
# RUN apk update && apk add git
RUN apt-get update && apt-get install -y git
WORKDIR /
RUN git clone https://github.com/Audiveris/audiveris.git

# BUILD
WORKDIR /audiveris
RUN git checkout 5.2.5
# RUN apk update && apk add tesseract-ocr tesseract-ocr-data-ita
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-ita
RUN gradle wrapper --stacktrace
RUN ./gradlew clean build
RUN tar -xf build/distributions/Audiveris-5.3-alpha.tar


# other requirements
RUN apt-get update && apt-get install -y lilypond libsndfile-dev
# No apk alternative... maybe you must install it with sh but seams do not enought
# RUN wget https://lilypond.org/download/binaries/linux-64/lilypond-2.22.2-1.linux-64.sh && sh lilypond-2.22.2-1.linux-64.sh

WORKDIR /data

ENTRYPOINT "/audiveris/Audiveris-5.3-alpha/bin/Audiveris"