```
 _____             _                                                   _   _ ___       
|     |___ _ _ ___| |_ ___ ___ _ _ ___ ___ ___ ___ ___ _ _ ___ ___ ___| |_|_|  _|_ _   
|   --|  _| | | . |  _| . |  _| | |  _|  _| -_|   |  _| | |___|   | . |  _| |  _| | |  
|_____|_| |_  |  _|_| |___|___|___|_| |_| |___|_|_|___|_  |   |_|_|___|_| |_|_| |_  |  
          |___|_|     
```

[English](/README.md)

Cryptocurrency-notify 是一个通知工具，旨在检测区块链代币的价格，旨在帮助个人从加密货币市场获得更大的回报。

## 用法

```
usage: cryptocurrency-notify [-h] --config CONFIG [--verbose]

options:
  -h, --help       显示此帮助消息并退出
  --config CONFIG  配置路径
  --verbose        启用详细模式
```

## 安装

1. 克隆代码

    `git clone https://github.com/devcxl/cryptocurrency-notify.git`

2. 创建新的虚拟环境

    `python3 -m venv .env`

3. 激活虚拟环境

    `source .env/bin/activate`

4. 安装依赖关系

    `pip install -r requirements.txt`

5. 构建

    `bash build.sh`

6. 安装二进制文件

    `mv dist/main /usr/bin/cryptocurrency-notify`

7. 创建系统配置

    `sudo vim /etc/systemd/system/cryptocurrency-notify.service`

8. 添加以下内容:

    ```
    [Unit]
    Description=Cryptocurrency-notify
    After=network.target

    [Service]
    ExecStart=/usr/bin/cryptocurrency-notify --config /etc/cryptocurrency-notify/config.yaml
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
9. 配置

    [Example](/example.yaml)

    `sudo vim /etc/cryptocurrency-notify/config.yaml`

10. 在后台运行

    `sudo systecmtl daemon-reload`

    `sudo systemctl enable --now cryptocurrency-notify.service`

## 删除

`sudo rm /etc/systemd/system/cryptocurrency-notify.service`

`sudo rm -r /etc/cryptocurrency-notify/`

`sudo rm  /usr/bin/cryptocurrency-notify`


## Docker

1. 克隆代码

   `git clone https://github.com/devcxl/cryptocurrency-notify.git`

2. 构建镜像

   `docker build -t cryptocurrency-notify .`

3. 运行

   `docker run -it --name cryptocurrency-notify -v ${PWD}/config/config.yaml:/etc/coin/config.yaml cryptocurrency-notify`

4. 检查

   `docker log cryptocurrency-notify`

   ```
   2024-01-14 01:43:54,720 [INFO] daemon successful!
   ```