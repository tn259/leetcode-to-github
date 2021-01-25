FROM python:3.8.1-buster AS builder
RUN apt-get update && apt-get install -y --no-install-recommends --yes python3-venv gcc libpython3-dev fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libgbm1 libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    curl unzip vim wget \
    xvfb && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip


# install chromedriver and google-chrome

RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

RUN CHROME_SETUP=google-chrome.deb && \
    wget -O $CHROME_SETUP "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" && \
    dpkg -i $CHROME_SETUP && \
    apt-get install -y -f && \
    rm $CHROME_SETUP

COPY requirements.txt /requirements.txt
RUN /venv/bin/pip install -r /requirements.txt

COPY . /app
WORKDIR /app
RUN /venv/bin/pytest

WORKDIR /app

ENV DISPLAY=:99
ENTRYPOINT ["/venv/bin/python3", "-m", "leetcode_to_github"]
#ENTRYPOINT ["bash"]
#USER 1001

LABEL name={NAME}
LABEL version={VERSION}
