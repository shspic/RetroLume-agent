FROM task109_cached_base
RUN useradd --uid 10001 --user-group --create-home preview
WORKDIR /opt/preview
COPY vendor/playwright-core ./vendor/playwright-core
COPY host.cjs wrapper.html h0-counter.cjs input-manifest.json ./
USER 10001:10001
ENV XDG_CACHE_HOME=/home/preview/.cache XDG_CONFIG_HOME=/home/preview/.config
ENTRYPOINT ["node", "/opt/preview/h0-counter.cjs"]
