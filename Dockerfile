FROM docker.io/python:3.10 AS builder

RUN pip install --user pipenv

# Tell pipenv to create venv in the current directory
ENV PIPENV_VENV_IN_PROJECT=1

ADD Pipfile.lock Pipfile /usr/src/

WORKDIR /usr/src

RUN /root/.local/bin/pipenv sync

RUN /usr/src/.venv/bin/python3 -c "import pykube; print(pykube.__version__)"

FROM docker.io/python:3.10 AS runtime

RUN mkdir -v /usr/src/venv

COPY --from=builder /usr/src/.venv/ /usr/src/venv/

RUN /usr/src/venv/bin/python3 -c "import pykube; print(pykube.__version__)"

WORKDIR /usr/src/

COPY controller.py .

CMD ["./venv/bin/python", "controller.py"]
