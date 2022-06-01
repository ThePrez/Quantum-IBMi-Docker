FROM python:buster 

RUN curl -k https://public.dhe.ibm.com/software/ibmi/products/odbc/debs/dists/1.1.0/ibmi-acs-1.1.0.list >> /etc/apt/sources.list

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y ibm-iaccess
RUN apt-get install -y build-essential poppler-utils texlive-latex-base texlive-latex-extra libopenblas-dev \
                       sudo unzip wget nano poppler-utils cmake git libssl-dev zlib1g-dev libncurses5-dev libgdbm-dev \
                       libnss3-dev libssl-dev libreadline-dev libffi-dev curl unixodbc-dev
RUN pip install --upgrade pip
RUN python --version
RUN pip install qiskit[visualization]
RUN pip install pyodbc
RUN mkdir jupyter-notebooks
COPY 3sat.ipynb jupyter-notebooks/3sat.ipynb
COPY dbsetup.ipynb jupyter-notebooks/dbsetup.ipynb
COPY odbc.ini /etc/odbc.ini

CMD [ "jupyter" , "notebook",  "--allow-root", "--ip=0.0.0.0", "--port=8889", "--notebook-dir=jupyter-notebooks", "--no-browser" ]