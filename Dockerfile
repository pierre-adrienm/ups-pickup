FROM python:3.10-slim

# WORKDIR /app
# COPY app/requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY app/ .
# CMD ["python", "app.py"]

# Installer Chrome, Node.js, cron
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg ca-certificates wget unzip cron gnupg2 \
    fonts-liberation libnss3 libxss1 libasound2 libatk1.0-0 \
    libatk-bridge2.0-0 libgtk-3-0 libgbm1 libx11-xcb1 libdrm2 \
    libxcomposite1 libxdamage1 libxrandr2 libvulkan1 xdg-utils \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Installer Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# Variables Puppeteer
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome-stable

# Dossier de travail
RUN mkdir -p /data
WORKDIR /app

# Copier fichiers
COPY app/ ./
COPY app/test-puppeteer.js .
COPY app/screenshot.py .
COPY app/screenshot.cjs .
COPY app/.env . 

# Installer Node et Python
RUN npm install puppeteer
RUN pip install --no-cache-dir -r requirements.txt

# Ajouter cron job (écrit un timestamp toutes les minutes dans cron.log)
# RUN echo "* * * * * echo \"Cron job exécuté à: \$(date)\" >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron-job \
#     && chmod 0644 /etc/cron.d/my-cron-job \
#     && crontab /etc/cron.d/my-cron-job
# Alias optionnel si tu veux garder 'python'
RUN ln -s /usr/local/bin/python3 /usr/bin/python

RUN echo "* * * * * python3 /app/screenshot.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron-job \
    && chmod 0644 /etc/cron.d/my-cron-job \
    && crontab /etc/cron.d/my-cron-job

# Tester Puppeteer pendant le build
RUN node test-puppeteer.js

# Commande de démarrage
CMD ["sh", "-c", "touch /var/log/cron.log && cron && tail -F /var/log/cron.log"]
