FROM ubuntu:18.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get install -y --no-install-recommends cmake g++ ghostscript git gnupg gnupg2 gnupg1 locales locales-all make ttf-mscorefonts-installer python-dev python-numpy python-pip python3-pip python3.7 unzip wget xvfb

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Install opencv 2.4 to run on python 2.7. Numpy is required to add the python wrapper
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

# chromedriver
RUN wget -q -O - --no-check-certificate https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add \
    && echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get -y update && apt-get -y --no-install-recommends install google-chrome-stable \
    && wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/bin/chromedriver \
    && chown root:root /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm chromedriver_linux64.zip

# xpdf tools and imagemagick
RUN mkdir -p /home/pdfigcapx_dependencies \
    && cd /home/pdfigcapx_dependencies \
    && wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.02.tar.gz \
    && mkdir -p imagemagick-7.0.10-45 \
    && cd imagemagick-7.0.10-45 \
    && wget --no-check-certificate https://imagemagick.org/download/binaries/ImageMagick-7.0.10-45-portable-Q16-x86.zip \
    && unzip /home/pdfigcapx_dependencies/imagemagick-7.0.10-45/ImageMagick-7.0.10-45-portable-Q16-x86.zip \
    && rm /home/pdfigcapx_dependencies/imagemagick-7.0.10-45/ImageMagick-7.0.10-45-portable-Q16-x86.zip \
    && rm -rf /var/lib/apt/lists/* \
    && cd .. && tar -zxvf /home/pdfigcapx_dependencies/xpdf-tools-linux-4.02.tar.gz \
    && rm /home/pdfigcapx_dependencies/xpdf-tools-linux-4.02.tar.gz

ENV DISPLAY=:99
ADD xvfb.sh ./xvfb.sh
RUN chmod a+x ./xvfb.sh
CMD ./xvfb.sh

## RUN 
RUN pip install --upgrade pip && pip install lxml Pillow scipy selenium && pip3 install Pillow numpy execnet
RUN rm ./xvfb.sh \ 
    && apt-get -y remove wget gnupg gnupg2 gnupg1 unzip cmake g++ \
    && apt-get clean && apt-get autoclean & rm -rf /var/lib/apt/lists/*
