# Sử dụng hình ảnh Python chính thức
FROM python:3.11
RUN echo "deb http://archive.debian.org/debian/ buster main" >> /etc/apt/sources.list

# Cài đặt các thư viện hệ thống cần thiết để Chromium chạy trong chế độ headless
RUN apt-get update && apt-get install -y \
    libnss3 \
    libxss1 \
    libX11-xcb.so.1 \  
    libappindicator3-1 \
    libgdk-pixbuf2.0-0 \
    libdbus-1-3 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgtk-3-0 \
    libnss3-dev \
    && apt-get clean

# Cài đặt các thư viện Python và Playwright
RUN pip install --upgrade pip
RUN pip install playwright

RUN playwright install


# Sao chép mã nguồn vào Docker container
COPY . /app
WORKDIR /app

# Cài đặt các phụ thuộc của ứng dụng
RUN pip install -r requirements.txt

# Mở cổng mà ứng dụng sẽ lắng nghe
EXPOSE 10000

# Chạy ứng dụng khi container bắt đầu
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]
