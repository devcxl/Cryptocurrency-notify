# 阶段一：构建应用程序
FROM python:3.9-slim-bookworm AS builder
WORKDIR /app
COPY . .
# 构建应用程序
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y binutils && \
    pip install -r requirements.txt -i https://mirrors.ustc.edu.cn/pypi/web/simple && \
    pyinstaller --clean -F main.py -n main --add-data "template.html:."

FROM debian:12-slim
COPY --from=builder /app/dist/ /usr/bin/
CMD [ "main", "-f", "/etc/coin/config.yaml" ]