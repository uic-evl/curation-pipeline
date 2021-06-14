FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive

ARG USER=docker
ARG UID=1000
ARG GID=1000
ARG PW=docker

RUN apt-get -y update && apt-get install -y --no-install-recommends cmake g++ ghostscript gsfonts-x11 git gnupg gnupg2 gnupg1 locales locales-all make python-dev python-numpy python-pip python3-pip python3.7 sudo unzip wget xvfb
RUN useradd -m ${USER} --uid=${UID} && echo "${USER}:${PW}" | chpasswd && adduser ${USER} sudo

# ---------
# Environmental variables.
# UTF-8 Locales for xpdf, display for headless chrome, and DPI for image extraction 
# ---------
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV DISPLAY :99
ENV DPI 300

# ---------
# Install opencv 2.4 to run on python 2.7. Numpy is required to add the python wrapper
# ---------
RUN cd /home \
    && git clone --recursive https://github.com/skvark/opencv-python.git \
    && cd /home/opencv-python/opencv \
    && git checkout 2.4 \
    && mkdir -p build \
    && cd /home/opencv-python/opencv/build \
    && cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D BUILD_EXAMPLES=OFF .. \
    && make \
    && make install \
    && rm -r /home/opencv-python

# ---------
# chromedriver
# ---------
RUN wget -q -O - --no-check-certificate https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add \
    && echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get -y update && apt-get -y --no-install-recommends install google-chrome-stable \
    && wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chown root:root /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm chromedriver_linux64.zip

# ---------
# xpdf tools. Note: apt install xpdf does not work (maybe it's bin32?), stick
# to the provided TAR.
# ---------
RUN cd /home \
    && wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.03.tar.gz \
    && tar -zxvf /home/xpdf-tools-linux-4.03.tar.gz \
    && rm /home/xpdf-tools-linux-4.03.tar.gz \
    && cp /home/xpdf-tools-linux-4.03/bin64/pdftohtml /usr/local/bin \
    && rm -r /home/xpdf-tools-linux-4.03

# ---------
# Display configuration for headless Chrome
# ---------
ADD xvfb.sh ./xvfb.sh
RUN chmod a+x ./xvfb.sh
CMD ./xvfb.sh

# ---------
# Python dependencies for the runner (py3) and the legacy py2 code.
# ---------
RUN pip install --upgrade pip && pip install lxml Pillow scipy selenium && pip3 install Pillow numpy execnet requests

# force busting the cache to clone again repo
ARG CACHEBUST=1
RUN cd /home && git clone https://github.com/uic-evl/curation-pipeline.git && cd curation-pipeline && git checkout python3


# ---------
# Clean-up packages only needed for installation
# ---------
RUN rm ./xvfb.sh \ 
    && apt-get -y remove wget gnupg gnupg2 gnupg1 unzip cmake g++ \
    && apt-get clean && apt-get autoclean & rm -rf /var/lib/apt/lists/*

USER ${UID}:${GID}
WORKDIR /home/${USER}


# ---------
# Build image
# ---------
# export UID=$(id -u)
# export GID=$(id -g)
# docker build --build-arg USER=$USER \
#              --build-arg UID=$UID \
#              --build-arg GID=$GID \
#              --build-arg PW=<PASSWORD IN CONTAINER> \
#              -t <IMAGE NAME> \
#              -f <DOCKERFILE NAME>\
#              .
# e.g. docker build --build-arg USER=$USER --build-arg UID=$UID --build-arg GID=$GID --build-arg PW=juan --build-arg CACHEBUST=$(date +%s) -t curation/pipeline:1.0 .
# ---------
# Run image
# ---------
# docker run --user root --workdir /root -it <IMAGE NAME> /bin/bash
# e.g. docker run -it -v /home/juan/projects/storage/pipeline:/mnt/output curation/create:1.0 /bin/bash
