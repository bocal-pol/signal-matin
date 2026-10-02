# ============================================================
# Signal Matin — image dédiée à l'exécution via n8n.
# Un wrapper HTTP minimal (server.py, FastAPI) expose POST /generate :
# n8n l'appelle via un nœud HTTP Request (réseau Docker interne, aucun accès
# au socket Docker de l'hôte). Le PDF produit est lu depuis le volume nommé
# partagé signal-matin-output.
# ============================================================

FROM python:3.12-slim

# Dépendances système requises par Chromium (Playwright) en mode headless.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
        libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
        libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
        fonts-liberation ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 signalmatin \
    && useradd --uid 1000 --gid signalmatin --shell /bin/sh --create-home signalmatin

# Chemin de cache Playwright fixe et partagé — sans ça, l'installation (faite
# ici en root) atterrit dans /root/.cache alors que le process tourne en
# user signalmatin (uid 1000) au runtime et cherche dans son propre $HOME.
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY main.py ./
COPY server.py ./
COPY config.example.yaml ./

RUN pip install --no-cache-dir -e . "fastapi>=0.115" "uvicorn[standard]>=0.32" \
    && python -m playwright install chromium \
    && python -m playwright install-deps chromium \
    && chmod -R a+rX /opt/playwright-browsers

RUN mkdir -p /app/output /home/signalmatin/.cache \
    && chown -R signalmatin:signalmatin /app /home/signalmatin

USER signalmatin

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
