# v0.2.3
# 使用官方的Python基础镜像
FROM python:3.11-bullseye

# 切换APT源到清华源并安装必要的系统依赖
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bullseye main" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bullseye-updates main" >> /etc/apt/sources.list

# 更新APT缓存并安装依赖包
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libappindicator1 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxtst6 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    libasound2 \
    libgbm1 \
    libu2f-udev && apt-get clean && rm -rf /var/lib/apt/lists/*

# 下载和安装指定版本的Chrome
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip -d /usr/local/ && \
    rm chrome-linux64.zip && \
    ln -s /usr/local/chrome-linux64/chrome /usr/local/bin/google-chrome

# 下载和安装指定版本的ChromeDriver
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/ && \
    rm -rf chromedriver-linux64 chromedriver-linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . .

# 输出Chrome和ChromeDriver的版本信息
RUN google-chrome --version
RUN chromedriver --version

# 设置环境变量
ENV DISPLAY=:99
ENV DASHSCOPE_API_KEY=<YOUR_DASHSCOPE_API_KEY>
ENV OPENAI_API_VERSION=<YOUR_AZURE_OPENAI_API_VERSION>
ENV AZURE_OPENAI_API_KEY=<YOUR_AZURE_OPENAI_API_KEY>
ENV AZURE_OPENAI_ENDPOINT=<YOUR_AZURE_OPENAI_ENDPOINT>

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 启动Xvfb并运行应用程序
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & echo | streamlit run main.py --server.port 8502 --server.enableCORS false"]
