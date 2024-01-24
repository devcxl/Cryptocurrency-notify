import argparse
import datetime
import json
import logging
import os
import smtplib
import sys
import threading
import time
from decimal import Decimal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict

import matplotlib.pyplot as plt
import requests
import yaml
from minio import Minio
from pydantic import BaseModel, Field

log = logging.getLogger('coin-check')


class EmailSetting(BaseModel):
    smtp_server: str = Field(description="SMTP发送服务器")
    # 一般为587或者465
    smtp_port: int = Field(description="SMTP发送服务器端口号")
    # 发件人的邮箱和密码
    sender_email: str = Field(description="SMTP发件人")
    sender_password: str = Field(description="SMTP密码")


class MinioS3Setting(BaseModel):
    endpoint: str = Field(description="上传端点")
    bucket: str = Field(description="存储桶名称")
    access_key: str = Field(description='访问密钥')
    secret_key: str = Field(description='密钥')


class Coin(BaseModel):
    max: Decimal
    min: Decimal


class Setting(BaseModel):
    """配置类"""
    email: EmailSetting = Field(description="Email setting")
    minio_s3: MinioS3Setting = Field(description="File Setting")
    coinlist: Dict[str, Coin] = Field(description="关注的代币列表")
    sendto: str = Field(description='邮件收件人')
    proxy: str = Field(description='请求代理')


def load_config(config_file: str, format: str):
    """加载配置文件"""
    log.info(f'加载配置文件:{config_file}')
    if config_file:
        with open(config_file) as file:
            if format == 'json':
                return Setting.model_validate_json(file.read(), strict=True)
            elif format == 'yaml':
                config_data = yaml.safe_load(file.read())
                json_data = json.dumps(config_data)
                return Setting.model_validate_json(json_data, strict=True)


class CoinCheck(threading.Thread):

    def __init__(self) -> None:
        threading.Thread.__init__(self)

        parser = argparse.ArgumentParser(description='CoinCheck')
        parser.add_argument('--config', '-f', required=True,
                            type=str, help="配置文件路径")
        parser.add_argument('--format', '-t', default='yaml',
                            type=str, help="配置文件格式化类型。可选：yaml（默认），json")
        parser.add_argument('--verbose', action='store_true', help='是否启用详细模式')

        args = parser.parse_args()

        self.conf = load_config(args.config, args.format)

        # 获取可执行文件所在目录
        base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

        # 构建配置文件的绝对路径
        config_file_path = os.path.join(base_path, 'template.html')

        temp = open(config_file_path, 'r')
        self.template = temp.read()
        temp.close()

        self.client = Minio(
            endpoint=self.conf.minio_s3.endpoint,
            access_key=self.conf.minio_s3.access_key,
            secret_key=self.conf.minio_s3.secret_key,
        )

        found = self.client.bucket_exists(self.conf.minio_s3.bucket)
        if not found:
            self.client.make_bucket(self.conf.minio_s3.bucket)
            log.info("Created bucket", self.conf.minio_s3.bucket)
        else:
            log.info("Bucket", self.conf.minio_s3.bucket, "already exists")

        self.url = "https://api.coingecko.com/api/v3/simple/price"

        self.headers = {
            "Accept": "application/json"
        }

        self.coins = ",".join(self.conf.coinlist.keys())
        log.info(f'listen coins: {self.coins}')

        self.params = {
            'ids': f'{self.coins}',
            'vs_currencies': 'USD',
            'precision': 8,
            'include_last_updated_at': 'true',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }

        customLevel = logging.INFO
        if args.verbose:
            customLevel = logging.DEBUG
        # 配置日志记录
        logging.basicConfig(level=customLevel,
                            format='%(asctime)s [%(levelname)s] %(message)s')

    def dateformat(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M')

    def get_chart(self, coin, days=14) -> str:
        headers = {
            "Accept": "application/json"
        }
        params = {
            'vs_currency': 'USD',
            'precision': 8,
            'days': days
        }
        url = f'https://api.coingecko.com/api/v3/coins/{coin}/market_chart'
        response = requests.get(url,
                                params,
                                proxies={"http": self.conf.proxy,
                                         "https": self.conf.proxy},
                                headers=headers)
        if response.status_code == 200:
            json_data = response.json()
            # 创建折线图
            plt.figure(figsize=(12, 12))
            prices = json_data["prices"]
            market_caps = json_data["market_caps"]
            total_volumes = json_data["total_volumes"]
            dates = [datetime.datetime.fromtimestamp(
                ts / 1000.0) for ts, _ in prices]

            # 价格曲线
            plt.subplot(3, 1, 1)
            plt.plot(dates, [price for _, price in prices],
                     label=coin, c='r')
            plt.xlabel('Date')
            plt.ylabel('USD')
            plt.title('Price')

            # 总交易量曲线
            plt.subplot(3, 1, 2)
            plt.plot(dates, [total_volume for _, total_volume in total_volumes],
                     label=coin, c='g')
            plt.xlabel('Date')
            plt.ylabel('USD')
            plt.title('Total Volume')

            # 市值曲线
            plt.subplot(3, 1, 3)
            plt.plot(dates, [market_cap for _, market_cap in market_caps],
                     label=coin, c='b')
            plt.xlabel('Date')
            plt.ylabel('USD')
            plt.title('Market Cap')

            plt.suptitle(f'Cryptocurrency {coin}')

            plt.gcf().autofmt_xdate()
            filename = f'cryptocurrency_{coin}_{int(time.time())}.png'
            plt.savefig(f'/tmp/{filename}')
            self.client.fput_object(
                self.conf.minio_s3.bucket, f'/public/{filename}', f'/tmp/{filename}',
            )
            plt.close()
            return f'https://{self.conf.minio_s3.endpoint}/{self.conf.minio_s3.bucket}/public/{filename}'

    def generateHtml(self, data):
        '''生成HTML'''
        table_html = ""
        for currency, info in data.items():

            temp = "green" if info['usd_24h_change'] > 0 else "red"
            notifyPrice = self.conf.coinlist.get(currency)

            usd_color = "black"

            if info['usd'] > notifyPrice.max:
                usd_color = "green"
            elif info['usd'] < notifyPrice.min:
                usd_color = "red"

            table_html += f"""
            <tr>
            <td><img src="{self.get_chart(coin=currency)}"></td>
            <td><a>{currency}</a></td>
            <td style="color:{usd_color}">{info['usd']}</td>
            <td style="color:{temp}" >{round(info['usd_24h_change'], 6)}%</td>
            <td>{info['usd_market_cap']}</td>
            <td>{self.dateformat(info['last_updated_at'])}</td>
            </tr>
            """
        return table_html

    def check_coin_price(self):
        '''检查关注的Coin的价格'''
        while True:
            notification_flag = False
            response = requests.get(self.url, self.params, proxies={
                "http": self.conf.proxy, "https": self.conf.proxy},
                                    headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                for currency, info in data.items():
                    notifyPrice = self.conf.coinlist.get(currency)
                    if notifyPrice:
                        currentPrice = info['usd']
                        log.debug(
                            f'resp:{currency},{notifyPrice},{currentPrice}')
                        if currentPrice > notifyPrice.max or currentPrice < notifyPrice.min:
                            notification_flag = True
                if notification_flag:
                    self.notify(data)
            else:
                log.error("Request CoinGeko api failed")

            time.sleep(600)

    def notify(self, data):
        '''发送通知邮件'''
        context = self.template.replace(
            '<!-- context -->', self.generateHtml(data=data))
        message = MIMEMultipart()
        message["From"] = self.conf.email.sender_email
        message["To"] = self.conf.sendto
        message["Subject"] = "Notify Cryptocurrency Status!!!"

        html_part = MIMEText(context, "html")
        # 将HTML内容添加到邮件
        message.attach(html_part)

        try:
            email_sender = smtplib.SMTP_SSL(
                self.conf.email.smtp_server, self.conf.email.smtp_port)
            email_sender.login(
                self.conf.email.sender_email, self.conf.email.sender_password)
            email_sender.sendmail(
                self.conf.email.sender_email, self.conf.sendto, message.as_string())
            log.info(f"notify: {self.conf.sendto} successful!")
        except smtplib.SMTPException as e:
            log.error("email send failed:", str(e))

    def run(self):
        self.check_coin_price()


if __name__ == "__main__":
    check = CoinCheck()
    check.start()
    log.info("daemon successful!")
