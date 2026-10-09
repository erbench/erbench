FROM python:3.9

WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader -d /usr/local/share/nltk_data stopwords punkt_tab

# this should be after pip install, to cache layers more efficient
COPY splitter.py settings.py ./

# This allows to run the container as `docker run --rm <yourImageName> <args>`
ENTRYPOINT ["python", "-u", "splitter.py"]
CMD []
