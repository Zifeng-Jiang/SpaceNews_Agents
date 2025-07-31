# 使用官方的Python基础镜像
FROM python:3.12-slim

# 切换APT源到清华源并安装必要的系统依赖
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bookworm-updates main" >> /etc/apt/sources.list

# 更新APT缓存并安装依赖包
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    xvfb \
    libnss3 \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Chrome using official Google repository
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver using webdriver-manager (handled by Python package)
# No need to manually download ChromeDriver as webdriver-manager will handle it

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 启动Xvfb并运行应用程序
CMD ["sh", "-c", "rm -rf /tmp/chrome-user-data* && mkdir -p /tmp && Xvfb :99 -screen 0 1920x1080x24 & echo | streamlit run main.py --server.port 8502"]
