```                                                                            
 _____             _                                                   _   _ ___       
|     |___ _ _ ___| |_ ___ ___ _ _ ___ ___ ___ ___ ___ _ _ ___ ___ ___| |_|_|  _|_ _   
|   --|  _| | | . |  _| . |  _| | |  _|  _| -_|   |  _| | |___|   | . |  _| |  _| | |  
|_____|_| |_  |  _|_| |___|___|___|_| |_| |___|_|_|___|_  |   |_|_|___|_| |_|_| |_  |  
          |___|_|                                     |___|                     |___|  
```

[中文](/README_zh.md)

Cryptocurrency-notify is a notification tool designed to detect prices of blockchain tokens, with the aim of assisting individuals in achieving greater returns from the cryptocurrency market.

## Usage

```
usage: cryptocurrency-notify [-h] --config CONFIG [--verbose]

options:
  -h, --help       Show this help message and exit
  --config CONFIG  Config path
  --verbose        Enable verbose mode
```

## Install

1. Clone code

    `git clone https://github.com/devcxl/cryptocurrency-notify.git`

2. create a new virtual environment

    `python3 -m venv .env`

3. activate

    `source .env/bin/activate`

4. Installation dependencies 

    `pip install -r requirements.txt`

5. Build

    `bash build.sh`

6. Install Binary 

    `mv dist/main /usr/bin/cryptocurrency-notify`

7. Create systemd configuration

    `sudo vim /etc/systemd/system/cryptocurrency-notify.service`

8. Add context:

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
9. Configuration

    [Example](/example.yaml)

    `sudo vim /etc/cryptocurrency-notify/config.yaml`

10. run in background

    `sudo systecmtl daemon-reload`

    `sudo systemctl enable --now cryptocurrency-notify.service`

## Remove

`sudo rm /etc/systemd/system/cryptocurrency-notify.service`

`sudo rm -r /etc/cryptocurrency-notify/`

`sudo rm  /usr/bin/cryptocurrency-notify`

## Docker

1. Clone code

   `git clone https://github.com/devcxl/cryptocurrency-notify.git`

2. build

   `docker build -t cryptocurrency-notify .`

3. run 

   `docker run -it --name cryptocurrency-notify -v ${PWD}/config/config.yaml:/etc/coin/config.yaml cryptocurrency-notify`

4. check 

   `docker log cryptocurrency-notify`

   ```
   2024-01-14 01:43:54,720 [INFO] daemon successful!
   ```