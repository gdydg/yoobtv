#!/bin/sh

# 如果 Zeabur 设置了 PORT 变量，就用它；否则默认 8080
PORT=${PORT:-8080}

echo "Starting IPTV Aggregator on port $PORT..."

# 使用 Gunicorn 启动 Flask 应用
# -w 4: 开启 4 个工作进程，提高并发处理能力
# -b: 绑定地址和端口
# --timeout 120: 防止爬虫抓取时间过长导致 502 超时
exec gunicorn --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    main:app
