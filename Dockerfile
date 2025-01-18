# Bắt đầu từ image Python chính thức
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
    && apt-get clean

# Cài đặt Node.js và Yarn để sử dụng Playwright
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && npm install --global yarn

# Tạo thư mục ứng dụng cho Playwright và tạo file package.json (không cần mã nguồn Node.js)
WORKDIR /app

# Tạo một package.json trống
RUN echo '{"name": "playwright-app", "version": "1.0.0", "devDependencies": {"playwright": "^1.24.0"}}' > package.json

# Cài đặt Playwright mà không cần mã nguồn Node.js
RUN yarn install

# Cài đặt Playwright
RUN yarn playwright install chromium

# Tạo thư mục để lưu trữ cache Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers
ENV XDG_CACHE_HOME=/root/.cache

# Store/pull Playwright cache with build cache
RUN if [ ! -d "$PLAYWRIGHT_BROWSERS_PATH" ]; then \
      echo "...Copying Playwright Cache from Build Cache" && \
      cp -R $XDG_CACHE_HOME/playwright/ $PLAYWRIGHT_BROWSERS_PATH; \
    else \
      echo "...Storing Playwright Cache in Build Cache" && \
      cp -R $PLAYWRIGHT_BROWSERS_PATH $XDG_CACHE_HOME; \
    fi

# Cài đặt các thư viện Python cần thiết cho dự án của bạn
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
