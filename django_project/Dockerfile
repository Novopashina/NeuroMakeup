FROM python:3.12 AS py312

RUN python3.12 -m venv /venv/py312
ENV PATH="/venv/py312/bin:$PATH"

COPY requirements_py312.txt /requirements_py312.txt

RUN /venv/py312/bin/pip install --upgrade pip && /venv/py312/bin/pip install -r /requirements_py312.txt

WORKDIR /neurosnaps

COPY . /neurosnaps

EXPOSE 8000

CMD ["/venv/py312/bin/python", "neurosnaps/manage.py", "runserver", "0.0.0.0:8000"]
