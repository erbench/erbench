FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

RUN apt-get update --allow-insecure-repositories && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the pre-trained model on English Wikipedia
# ADD https://zenodo.org/record/6466387/files/wiki.en.bin /workspace/embeddings/wiki.en.bin

COPY fork-deepmatcher .
COPY entrypoint.py .
COPY transform.py .
COPY HierMatcher.py .

# This allows to run the container as `docker run --rm <yourImageName> <args>`
ENTRYPOINT ["python", "-u", "./entrypoint.py"]
CMD []
