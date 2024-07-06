
# FROM python:3.9


# WORKDIR /usr/local/bin


# COPY . /usr/local/bin


# RUN pip install --no-cache-dir pandas numpy SimpleITK synapseclient evalutils


# RUN git clone https://github.com/deepmind/surface-distance.git && \
#     pip install ./surface-distance && \
#     rm -rf surface-distance


# COPY utils.py /usr/local/bin/utils.py

FROM python:3.10-slim

WORKDIR /usr/local/bin

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*


RUN git clone https://github.com/deepmind/surface-distance.git /surface-distance

RUN pip install --no-cache-dir pandas synapseclient evalutils SimpleITK numpy
RUN pip install /surface-distance

COPY *.py .


#RUN chmod +x /usr/local/bin/surface_distance

# EXPOSE 80

# ENV NAME World

# CMD ["python", "score_seg.py"]


