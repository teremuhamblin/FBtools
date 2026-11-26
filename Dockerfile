# syntax=docker/dockerfile:1
FROM python:3.12-slim AS build
WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir build && python -m build --wheel

FROM python:3.12-slim
LABEL org.opencontainers.image.title="FBtools" \
      org.opencontainers.image.description="CLI Python pour gérer des Pages Facebook via l'API Graph de Meta" \
      org.opencontainers.image.source="https://github.com/teremuhamblin/FBtools" \
      org.opencontainers.image.licenses="MIT"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FBTOOLS_CONFIG_DIR=/config
COPY --from=build /src/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl \
    && useradd --create-home --uid 1000 fbtools \
    && mkdir /config && chown fbtools /config
USER fbtools
WORKDIR /work
VOLUME ["/config"]
ENTRYPOINT ["fbtools"]
CMD ["--help"]
