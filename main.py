
import requests
import datetime
from emailSender import EmailSender
import argparse
import logging
import threading
import time
import json
from collections import defaultdict


class Struct(object):
    def __init__(self, data):
        for name, value in data.items():
            setattr(self, name, self._wrap(value))

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value


class CoinCheck(threading.Thread):

    def __init__(self) -> None:

        self.url = "https://api.coingecko.com/api/v3/simple/price"

        self.headers = {
            "Accept": "application/json"
        }

        self.params = {
            'ids': 'ethereum,bitcoin,matic-network,binancecoin,tron',
            'vs_currencies': 'USD',
            'precision': 6,
            'include_last_updated_at': 'true',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }

        # 创建解析器对象
        parser = argparse.ArgumentParser(description='检查代币信息')

        parser.add_argument('--config', required=True, type=str, help="配置文件路径")

        parser.add_argument('--verbose', action='store_true', help='是否启用详细模式')
        # 解析命令行参数
        self.args = parser.parse_args()

        if self.args.config:
            with open(self.args.config) as file:
                self.config_dict = json.load(file)
                self.config = Struct(self.config_dict)

        customLevel = logging.INFO
        if self.args.verbose:
            customLevel = logging.DEBUG
        # 配置日志记录
        logging.basicConfig(level=customLevel,format='%(asctime)s [%(levelname)s] %(message)s')

        grf = '''
   _____      _        _____ _               _    
  / ____|    (_)      / ____| |             | |   
 | |     ___  _ _ __ | |    | |__   ___  ___| | __
 | |    / _ \| | '_ \| |    | '_ \ / _ \/ __| |/ /
 | |___| (_) | | | | | |____| | | |  __/ (__|   < 
  \_____\___/|_|_| |_|\_____|_| |_|\___|\___|_|\_\
                                                  
        '''

        logging.info(grf)

        logging.debug(self.args)

        threading.Thread.__init__(self)
        return

    def dateformat(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M')

    def generateHtml(self, data):
        '''生成HTML'''
        table_html = """
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
                font-family: Arial, sans-serif;
            }

            th {
                background-color: #f2f2f2;
                font-weight: bold;
                padding: 8px;
                text-align: left;
            }

            td {
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }

            tr:nth-child(even) {
                background-color: #f9f9f9;
            }

            tr:hover {
                background-color: #f5f5f5;
            }
        </style>

        <table>
            <tr>
            <th>币种</th>
            <th>当前价格(美元)</th>
            <th>24小时内涨跌(百分比)</th>
            <th>当前市值(美元)</th>
            <th>最后更新时间</th>
            </tr>
            <tr>
            <th>Token</th>
            <th>Price(USD)</th>
            <th>24H (%)</th>
            <th>Mkt Cap(USD)</th>
            <th>Last Update</th>
            </tr>
        """

        for currency, info in data.items():

            temp = "green" if info['usd_24h_change'] > 0 else "red"
            notifyPrice = self.config_dict['price'][currency]

            usd_color = "black"

            if info['usd'] > notifyPrice['max']:
                usd_color = "green"
            elif info['usd'] < notifyPrice['min']:
                usd_color = "red"

            table_html += f"""
            <tr>
            <td>{currency}</td>
            <td style="color:{ usd_color }">{info['usd']}</td>
            <td style="color:{ temp }" >{round(info['usd_24h_change'],6)}%</td>
            <td>{info['usd_market_cap']}</td>
            <td>{self.dateformat(info['last_updated_at'])}</td>
            </tr>
            """

        table_html += """</table>"""

        return table_html

    def check_coin_price(self):
        '''检查关注的Coin的价格'''

        while True:
            notification_flag = False
            response = requests.get(self.url, self.params, proxies={
                                    "http": self.config.proxy, "https": self.config.proxy}, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                for currency, info in data.items():
                    notifyPrice = self.config_dict['price'][currency]
                    currentPrice = info['usd']
                    logging.debug(
                        f'resp:{currency},{notifyPrice},{currentPrice}')
                    if currentPrice > notifyPrice['max'] or currentPrice < notifyPrice['min']:
                        notification_flag = True
                if notification_flag:
                    self.notify(data)
            else:
                logging.error("Request failed with status code:",
                              response.status_code)

            time.sleep(600)

    def notify(self, data):
        '''发送通知邮件'''
        context = self.generateHtml(data=data)
        logging.debug("generate HTML succcessful!")
        sender = EmailSender(self.config.smtp_server, self.config.smtp_port,
                             self.config.smtp_username, self.config.smtp_password)
        logging.debug("EmailSender ready!")
        sender.sendHtml(to=self.config.to,
                        title=self.config.title, context=context)
        logging.info(f"notify: {self.config.to} successful!")

    def run(self):
        self.check_coin_price()


if __name__ == "__main__":
    check = CoinCheck()
    check.start()
    logging.info("daemon successful!")
