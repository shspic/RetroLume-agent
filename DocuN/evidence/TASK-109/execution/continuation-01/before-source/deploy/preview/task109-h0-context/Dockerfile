FROM mcr.microsoft.com/playwright@sha256:c091b21d9fae78c76e85cd4356431e9b018402f172a214fc7d7a5e9a7e29d8ac
RUN useradd --uid 10001 --user-group --create-home preview
WORKDIR /opt/preview
COPY vendor/playwright-core ./vendor/playwright-core
COPY host.cjs wrapper.html h0-counter.cjs input-manifest.json ./
USER 10001:10001
ENV XDG_CACHE_HOME=/home/preview/.cache XDG_CONFIG_HOME=/home/preview/.config
ENTRYPOINT ["node", "/opt/preview/h0-counter.cjs"]
