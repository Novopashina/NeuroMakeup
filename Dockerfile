FROM continuumio/miniconda3 AS anaconda

COPY requirements_py36.txt /requirements_py36.txt
RUN conda create -n py36_env python=3.6 && \
    echo "conda activate py36_env" >> ~/.bashrc && \
    /bin/bash -c "source ~/.bashrc && conda install --file /requirements_py36.txt"

ENV PATH /opt/conda/envs/py36_env/bin:$PATH

WORKDIR /DMT
COPY . /DMT
