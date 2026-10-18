# AUCoFF backend image. Base image is an unmodified official minimal image pinned by digest
# (constitution LIC-2 exception, LICENCES.md section 5a). Runs as a non-root user and works with a
# read-only root filesystem.
FROM docker.io/library/python@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f AS build
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN pip install --no-cache-dir uv==0.10.11
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY backend/app ./app

FROM docker.io/library/python@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
# pip/setuptools are not needed at run time; removing them (and the HIGH findings in their vendored
# libraries) shrinks the attack surface. Nothing is added to the base image.
RUN python -m pip uninstall -y pip setuptools wheel 2>/dev/null || python -m pip uninstall -y pip
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin aucoff
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/app /app/app
COPY backend/alembic.ini /app/alembic.ini
COPY backend/migrations /app/migrations
# The owner-authored control catalogue ships with the image (read at run time by GET /unified-controls).
COPY data/controls /app/data/controls
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
USER 10001
EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
