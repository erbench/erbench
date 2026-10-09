FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

RUN apt-get update --allow-insecure-repositories && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader -d /usr/local/share/nltk_data stopwords punkt_tab

COPY fork-deepblocker .
COPY splitter.py settings.py ./

# This allows to run the container as `docker run --rm <yourImageName> <args>`
ENTRYPOINT ["python", "-u", "splitter.py"]
CMD []
