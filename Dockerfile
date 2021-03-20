FROM python:3.8-slim

# Install java
RUN set -eux; \
    mkdir -p /usr/share/man/man1; \
    apt-get update; \
    apt-get install --no-install-recommends -y \
        openjdk-11-jre-headless \
        wget \
    ; \
    rm -rf /var/lib/apt/lists/*

# Download & Install signal-cli
ENV SIGNAL_CLI_VERSION=0.8.1
RUN cd /tmp/ \
    && wget https://github.com/AsamK/signal-cli/releases/download/v"${SIGNAL_CLI_VERSION}"/signal-cli-"${SIGNAL_CLI_VERSION}".tar.gz \
    && tar xf signal-cli-"${SIGNAL_CLI_VERSION}".tar.gz -C /opt \
    && ln -s /opt/signal-cli-"${SIGNAL_CLI_VERSION}"/bin/signal-cli /usr/bin/si\
gnal-cli

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* ./

# Install Poetry & disable virtualenv creation
RUN pip install --no-cache poetry && \
    poetry config virtualenvs.create false

RUN poetry install --no-root --no-dev && \
    rm -rf ~/.cache/{pip,pypoetry}

# Copy app
COPY ./signal_cli_rest_api/ signal_cli_rest_api/

# Prepare mount point for signal-cli 
RUN mkdir -p $HOME/.config/signal-cli

EXPOSE 8000

CMD ["uvicorn", "signal_cli_rest_api.main:app", "--host", "0.0.0.0"]