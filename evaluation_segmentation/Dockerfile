FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN git clone https://github.com/deepmind/surface-distance.git /surface-distance

RUN pip install --no-cache-dir pandas synapseclient evalutils SimpleITK numpy
RUN pip install /surface-distance


#RUN chmod +x /usr/local/bin/surface_distance

# EXPOSE 80

ENV NAME World

CMD ["python", "score_seg.py"]
