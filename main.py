
import requests
import datetime
from emailSender import EmailSender
import argparse
import logging
import threading
import time


class CoinCheck(threading.Thread):

    def __init__(self) -> None:

        self.url = "https://api.coingecko.com/api/v3/simple/price"

        self.headers = {
            "Accept": "application/json"
        }

        # 通知价格
        self.notification_price = {
            "ethereum": {
                "max": 1000.00,
                # "max": 1865.00,
                "min": 1775.00
            },
            "bitcoin": {
                "max": 27400.00,
                "min": 26400.00
            },
            "matic-network": {
                "max": 0.941255,
                "min": 0.861837
            },
            "binancecoin": {
                "max": 314.57,
                "min": 302.15
            },
            "tron": {
                "max": 0.072512,
                "min": 0.079269
            }
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
        parser = argparse.ArgumentParser(description='邮件发送代币信息')

        # 添加命令行参数
        parser.add_argument('--proxy', type=str,
                            required=True,  help='为程序设置代理')
        parser.add_argument('--to',  type=str,
                            required=True, help='邮件接收地址')
        parser.add_argument('--title', type=str, default='关注代币信息', help='邮件标题')

        parser.add_argument('--smtp-server', type=str,
                            required=True, help='邮件发送程序服务器')
        parser.add_argument('--smtp-port', type=int,
                            required=True, help='邮件发送程序服务器端口')
        parser.add_argument('--smtp-username', type=str,
                            required=True, help='邮件发送程序服务器的用户名')
        parser.add_argument('--smtp-password', type=str,
                            required=True, help='邮件发送程序服务器的密码')
        parser.add_argument('--verbose', action='store_true', help='是否启用详细模式')
        # 解析命令行参数
        self.args = parser.parse_args()

        customLevel = logging.INFO
        if self.args.verbose:
            customLevel = logging.DEBUG
        # 配置日志记录
        logging.basicConfig(level=customLevel,
                            format='%(asctime)s [%(levelname)s] %(message)s')

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
            <th>24小时内交易活跃度(百分比)</th>
            <th>最后更新时间</th>
            </tr>
        """

        for currency, info in data.items():
            table_html += f"""
            <tr>
            <td>{currency}</td>
            <td>{info['usd']}</td>
            <td>{info['usd_24h_change']}</td>
            <td>{info['usd_market_cap']}</td>
            <td>{info['usd_24h_change']/info['usd_market_cap']*100}%</td>
            <td>{self.dateformat(info['last_updated_at'])}</td>
            </tr>
            """

        table_html += """</table>"""

        return table_html

    def check_coin_price(self):
        '''检查关注的Coin的价格'''

        while True:

            response = requests.get(self.url, self.params, proxies={
                                    "http": self.args.proxy, "https": self.args.proxy}, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                for currency, info in data.items():
                    notifyPrice = self.notification_price[currency]
                    currentPrice = info['usd']
                    logging.debug(f'resp:{currency},{notifyPrice},{currentPrice}')
                    if currentPrice > notifyPrice['max'] or currentPrice < notifyPrice['min']:
                        self.notify(data)
            else:
                logging.error("Request failed with status code:",
                              response.status_code)

            time.sleep(60)

    def notify(self, data):
        context = self.generateHtml(data=data)
        logging.debug("generate HTML succcessful!")
        sender = EmailSender(self.args.smtp_server, self.args.smtp_port,
                             self.args.smtp_username, self.args.smtp_password)
        logging.debug("EmailSender ready!")
        sender.sendHtml(to=self.args.to,
                        title=self.args.title, context=context)
        logging.info(f"notify: {self.args.to} successful!")

    def run(self):
        self.check_coin_price()


if __name__ == "__main__":
    check = CoinCheck()
    check.start()
    logging.info("daemon successful!")
