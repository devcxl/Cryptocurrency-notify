```
usage: coin-check [-h] --proxy PROXY --to TO [--title TITLE] [--coin COIN] --price PRICE --smtp-server SMTP_SERVER --smtp-port SMTP_PORT
                  --smtp-username SMTP_USERNAME --smtp-password SMTP_PASSWORD [--verbose]

邮件发送代币信息

options:
  -h, --help            show this help message and exit
  --proxy PROXY         为程序设置代理
  --to TO               邮件接收地址
  --title TITLE         邮件标题
  --coin COIN           代币的coingeko-api名称
  --price PRICE         提醒价格(美元)
  --smtp-server SMTP_SERVER
                        邮件发送程序服务器
  --smtp-port SMTP_PORT
                        邮件发送程序服务器端口
  --smtp-username SMTP_USERNAME
                        邮件发送程序服务器的用户名
  --smtp-password SMTP_PASSWORD
                        邮件发送程序服务器的密码
  --verbose             是否启用详细模式
```
