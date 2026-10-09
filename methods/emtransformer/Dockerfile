FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-runtime

WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fork-emtransformer/src .
COPY entrypoint.py .
COPY transform.py .

# This allows to run the container as `docker run --rm <yourImageName> <args>`
ENTRYPOINT ["python", "-u", "./entrypoint.py"]
CMD []
