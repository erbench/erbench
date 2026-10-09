 # don't change the base image, other images doesn't work with apex
FROM pytorch/pytorch:1.9.1-cuda11.1-cudnn8-runtime

RUN apt-get update --allow-insecure-repositories && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_lg
RUN python -m nltk.downloader -d /usr/local/share/nltk_data stopwords

COPY fork-ditto .
COPY *.py .

# This allows to run the container as `docker run --rm <yourImageName> <args>`
ENTRYPOINT ["python", "-u", "./entrypoint.py"]
CMD []
