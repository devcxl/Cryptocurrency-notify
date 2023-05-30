```
   _____      _        _____ _               _    
  / ____|    (_)      / ____| |             | |   
 | |     ___  _ _ __ | |    | |__   ___  ___| | __
 | |    / _ \| | '_ \| |    | '_ \ / _ \/ __| |/ /
 | |___| (_) | | | | | |____| | | |  __/ (__|   < 
  \_____\___/|_|_| |_|\_____|_| |_|\___|\___|_|\_\
```


CoinCheck is a notification tool designed to detect prices of blockchain tokens, with the aim of assisting individuals in achieving greater returns from the cryptocurrency market.

## Usage

```
usage: coin-check [-h] --config CONFIG [--verbose]

检查代币信息

options:
  -h, --help       Show this help message and exit
  --config CONFIG  Config path
  --verbose        Enable verbose mode
```

## Install

1. Clone code

    `git clone https://github.com/devcxl/coin-check.git`

2. create a new virtual environment

    `python3 -m venv .env`

3. activate

    `source .env/bin/activate`

4. Installation dependencies 

    `pip install -r requirements.txt`

5. Build

    `bash build.sh`

6. Install Binary 

    `mv dist/coin-check /usr/bin/coin-check`

7. Create systemd configuration

    `sudo vim /etc/systemd/system/coincheck.service`

8. Add context:

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
9. Configuration

    [Example](/example_config.json)

    `sudo vim /etc/coincheck/config.json`

10. run in background

    `sudo systecmtl daemon-reload`

    `sudo systemctl enable --now coincheck.service`

## Remove

`sudo rm /etc/systemd/system/coincheck.service`

`sudo rm -r /etc/coincheck/`

`sudo rm  /usr/bin/coin-check`
