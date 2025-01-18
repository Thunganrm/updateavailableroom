FROM python:3.11-slim

# Cài đặt các dependencies hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    libx11-xcb1 \
    libglu1-mesa \
    libxi6 \
    libgdk-pixbuf2.0-0 \
    libasound2 \
    libatk1.0-0 \
    libnss3 \
    libxss1 \
    libxtst6 \
    libxrandr2 \
    libdbus-1-3 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    dbus \
    xvfb \
    xauth \
    && apt-get clean

# Cài đặt Node.js 18 và Yarn
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install --global yarn

WORKDIR /app

# Tạo package.json cho Playwright và cài đặt Playwright
RUN echo '{"name": "playwright-app", "version": "1.0.0", "devDependencies": {"playwright": "^1.24.0"}}' > package.json
RUN yarn install

# Cài đặt Playwright và các trình duyệt Chromium
RUN yarn playwright install

# Cài đặt Playwright trình duyệt Chromium
RUN yarn playwright install chromium

# Cài đặt các thư viện Python cần thiết
RUN pip install -r requirements.txt
RUN playwright install
EXPOSE 5000

# Chạy ứng dụng Flask với Xvfb để hỗ trợ Playwright (headless)
CMD xvfb-run -a python app.py
