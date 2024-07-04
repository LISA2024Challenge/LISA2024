
FROM python:3.9


WORKDIR /usr/local/bin


COPY . /usr/local/bin


RUN pip install --no-cache-dir pandas numpy SimpleITK synapseclient evalutils


RUN git clone https://github.com/deepmind/surface-distance.git && \
    pip install ./surface-distance && \
    rm -rf surface-distance


COPY utils.py /usr/local/bin/utils.py


