FROM docker.io/library/ubuntu:22.04

ENV \
    GPU_DEVICE="drm:/dev/dri/card0" \
    DEBCONF_NONINTERACTIVE_SEEN="true" \
    DEBIAN_FRONTEND="noninteractive" \
    APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE="DontWarn"

WORKDIR /app

COPY . .

RUN \
    apt-get -qq update \
    && \
    apt-get install --no-install-recommends -y \
        python3 \
        python3-pip \
        intel-gpu-tools \
        tini \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get autoremove -y \
    && apt-get clean \
    && pip install --no-cache-dir -r requirements.txt \
    && \
    rm -rf \
        /tmp/* \
        /var/lib/apt/lists/* \
        /var/cache/apt/* \
        /var/tmp/*

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/bin/python3", "/app/intel-gpu-exporter.py"]

EXPOSE 8080/tcp

LABEL \
    org.opencontainers.image.base.name="ghcr.io/millercentral/intel-gpu-exporter" \
    org.opencontainers.image.authors="James Miller <james@millercentral.com>"
