FROM python:3.11

WORKDIR /workspace
COPY requirements.txt .

RUN pip install --no-cache-dir "setuptools<58"
RUN pip install --no-cache-dir -r requirements.txt

# this should be after pip install, to cache layers more efficient
COPY entrypoint.py .
COPY transform.py .

# This allows to run the container as `docker run --rm <yourImageName> <args>`
ENTRYPOINT ["python", "-u", "entrypoint.py"]
CMD []
