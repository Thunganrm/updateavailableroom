# Sử dụng image Python chính thức làm base image
FROM python:3.11

# Cài đặt các phụ thuộc hệ thống cần thiết
RUN apt-get update -q && \
    apt-get install -y -qq --no-install-recommends \
        xvfb \
        libxcomposite1 \
        libxdamage1 \
        libatk1.0-0 \
        libasound2 \
        libdbus-1-3 \
        libnspr4 \
        libgbm1 \
        libatk-bridge2.0-0 \
        libcups2 \
        libxkbcommon0 \
        libatspi2.0-0 \
        libnss3

# Sao chép file requirements.txt vào Docker image
COPY requirements.txt .

# Cài đặt các Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt Playwright và các trình duyệt cần thiết
build -t playwright-chrome .
docker run -it playwright-chrome
# Sao chép mã nguồn ứng dụng
COPY app.py .

# Thiết lập biến môi trường DISPLAY
ENV DISPLAY=:99

# Lệnh chạy ứng dụng (bắt đầu Xvfb và sau đó chạy script)
CMD Xvfb :99 -screen 0 1024x768x16 & python3 app.py
