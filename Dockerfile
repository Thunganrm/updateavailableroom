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
    && apt-get clean

# Cài đặt Node.js 18 và Yarn để sử dụng Playwright
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install --global yarn

WORKDIR /app

# Tạo package.json cho Playwright
RUN echo '{"name": "playwright-app", "version": "1.0.0", "devDependencies": {"playwright": "^1.24.0"}}' > package.json

# Cài đặt Playwright
RUN yarn install

# Cài đặt Playwright trình duyệt Chromium
RUN yarn playwright install chromium

# Nếu không cần cache, bỏ qua phần sao chép cache
RUN yarn playwright install --force

# Tạo thư mục để lưu trữ cache Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers
ENV XDG_CACHE_HOME=/root/.cache

# Cài đặt các thư viện Python cần thiết
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn vào container
COPY . /app
WORKDIR /app

# Cài đặt thư viện yêu cầu
RUN pip install -r requirements.txt

# Mở cổng cho ứng dụng Flask
EXPOSE 5000

# Lệnh để chạy ứng dụng của bạn
CMD ["python", "main.py"]
