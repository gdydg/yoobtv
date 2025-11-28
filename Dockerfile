FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY app/ /app/

# 暴露端口 (Zeabur 会自动识别这个端口)
EXPOSE 5000

# 启动命令
CMD ["python", "main.py"]
