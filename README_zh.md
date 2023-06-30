```
   _____      _        _____ _               _    
  / ____|    (_)      / ____| |             | |   
 | |     ___  _ _ __ | |    | |__   ___  ___| | __
 | |    / _ \| | '_ \| |    | '_ \ / _ \/ __| |/ /
 | |___| (_) | | | | | |____| | | |  __/ (__|   < 
  \_____\___/|_|_| |_|\_____|_| |_|\___|\___|_|\_\
```

[English](/README.md)

CoinCheck是一个通知工具，旨在检测区块链代币的价格，旨在帮助个人从加密货币市场获得更大的回报。

## 用法

```
usage: coin-check [-h] --config CONFIG [--verbose]

options:
  -h, --help       显示此帮助消息并退出
  --config CONFIG  配置路径
  --verbose        启用详细模式
```

## 安装

1. 克隆代码

    `git clone https://github.com/devcxl/coin-check.git`

2. 创建新的虚拟环境

    `python3 -m venv .env`

3. 激活虚拟环境

    `source .env/bin/activate`

4. 安装依赖关系

    `pip install -r requirements.txt`

5. 构建

    `bash build.sh`

6. 安装二进制文件

    `mv dist/coin-check /usr/bin/coin-check`

7. 创建系统配置

    `sudo vim /etc/systemd/system/coincheck.service`

8. 添加以下内容:

    ```
    [Unit]
    Description=CoinCheck
    After=network.target

    [Service]
    ExecStart=/usr/bin/coin-check --config /etc/coincheck/config.json
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
9. 配置

    [Example](/example_config.json)

    `sudo vim /etc/coincheck/config.json`

10. 在后台运行

    `sudo systecmtl daemon-reload`

    `sudo systemctl enable --now coincheck.service`

## 删除

`sudo rm /etc/systemd/system/coincheck.service`

`sudo rm -r /etc/coincheck/`

`sudo rm  /usr/bin/coin-check`
