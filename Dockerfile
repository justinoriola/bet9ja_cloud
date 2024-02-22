FROM --platform=linux/amd64 python:3.11.4-slim-buster as build

# Set the working directory in the container
WORKDIR /main

# Add current directory code to the working directory
COPY . /main

# Install necessary packages
RUN apt-get update && \
    apt-get install -y wget snapd && \
    apt-get remove -y firefox && \
    apt-get autoremove -y && \
    apt-get install -y firefox-esr && \
    apt-get install -y coreutils

# Download geckodriver, extract, and move to the PATH
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz && \
    tar -xvzf geckodriver-v0.34.0-linux64.tar.gz && \
    mv geckodriver /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm -f geckodriver-v0.34.0-linux64.tar.gz

# Cleanup unnecessary files
#RUN rm -f geckodriver-v0.34.0-linux64.tar.gz

# Set Marionette port environment variable
ENV MOZ_HEADLESS=1
ENV MOZ_LOG=error
ENV MOZ_CRASHREPORTER_DISABLE=1
ENV GECKODRIVER_PORT=4444

# Install necessary dependencies from requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create ffuser and switch to non-root user
RUN groupadd ffgroup --gid 2000 && \
    useradd ffuser --create-home --home-dir /tmp/ffuser --gid 2000 --shell /bin/bash --uid 1000

# Set up directories and permissions
RUN mkdir -p /var/www/.mozilla /var/www/.cache && \
    chown -R ffuser:ffgroup /var/www && \
    chmod ugo+w /var/www/.cache

USER ffuser

# Copy the .env and Python scripts
COPY .env account_handler.py spreadsheet_handler.py logic_handler.py /main/

# Expose port 80
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]









































































































## Use an official Python runtime as a parent image
#FROM --platform=linux/amd64 python:3.11.4-slim-buster as build
#
## Set the working directory in the container
#WORKDIR  /main
#
## Add current directory code to working directory
#ADD . /main
#
##RUN apt-get update
#RUN apt-get install -f
#
## Download and install wget
#RUN apt-get update && \
#    apt-get install -y wget && \
#    apt-get install -y snapd && \
#    rm -rf /var/lib/apt/lists/*
#
## Uninstall pre-installed Firefox
#RUN apt-get update && \
#    apt-get remove -y firefox && \
#    apt-get autoremove -y && \
#    rm -rf /var/lib/apt/lists/*
#
#
#
## Install firefox-esr or other necessary packages
#RUN apt-get update && \
#    apt-get install -y firefox-esr && \
#    rm -rf /var/lib/apt/lists/*
#
## Download geckodriver
#RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
#
## Extract geckodriver
#RUN tar -xvzf geckodriver-v0.34.0-linux64.tar.gz
#
## Move geckodriver to a directory in the PATH
#RUN su -
#RUN mv geckodriver /usr/local/bin
#RUN chmod +x /usr/local/bin/geckodriver
#RUN apt-get update && apt-get install -y coreutils
#RUN touch geckodriver.log
#RUN chown root:root geckodriver.log
#RUN chmod ugo+w geckodriver.log
#RUN mkdir -p /var/www
#RUN mkdir /var/www/.mozilla
#RUN chown root:root /var/www/.mozilla
#RUN mkdir /var/www/.cache
#RUN chown root:root /var/www/.cache
#
## Cleanup unnecessary files
#RUN rm geckodriver-v0.34.0-linux64.tar.gz
#
## Install necessary dependencies
##RUN apt-get update && \
##    apt-get install -y wget bzip2
##
### Download and install Firefox
##RUN wget 'https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US' -O firefox.tar.bz2 && \
##    tar xjf firefox.tar.bz2 && \
##    mv firefox /usr/bin && \
##    chmod +x /usr/bin/firefox
##
### Clean up unnecessary files
##RUN rm -f firefox.tar.bz2
##
### Set the PATH environment variable
##ENV PATH="/usr/local/bin:${PATH}"
#
#
##RUN apt-get install -y firefox-esr
#
## Install any needed packages specified in requirements.txt
#RUN pip install --upgrade pip
#COPY requirements.txt /main
#RUN pip install --no-cache-dir -r requirements.txt
##RUN pip install --upgrade selenium
#
#RUN groupadd ffgroup --gid 2000  \
#    && useradd ffuser \
#    --create-home \
#    --home-dir /tmp/ffuser \
#    --gid 2000 \
#    --shell /bin/bash \
#    --uid 1000
#
## Copy the .env file into the image
#COPY .env /main
#COPY account_handler.py /main
#COPY spreadsheet_handler.py /main
#COPY logic_handler.py /main
#
## Remove remaining Firefox binary
#RUN rm -f /usr/bin/firefox
#
## Make port 80 available to the world outside this container
#EXPOSE 80
#
## Run app.py when the container launches
#CMD ["python", "main.py"]

