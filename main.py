
import requests
import datetime
from emailSender import EmailSender
import argparse
import logging
import os
import time
# 配置日志记录
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')

notification_flag = False


def dateformat(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y/%m/%d %H:%M')


def generateHtml(data):
    global notification_flag
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
    """

    for currency, info in data.items():
        table_html += f"""
        <tr>
          <td>{currency}</td>
          <td>{info['usd']}</td>
          <td>{info['usd_24h_change']}</td>
          <td>{info['usd_market_cap']}</td>
          <td>{dateformat(info['last_updated_at'])}</td>
        </tr>
        """
        if currency == args.coin:
            if info['usd'] >= args.price:
                notification_flag = True

    table_html += """</table>"""

    return table_html


# 创建解析器对象
parser = argparse.ArgumentParser(description='邮件发送代币信息')

# 添加命令行参数
parser.add_argument('--proxy', type=str, required=True,  help='为程序设置代理')
parser.add_argument('--to',  type=str,
                    required=True, help='邮件接收地址')
parser.add_argument('--title', type=str, default='关注代币信息', help='邮件标题')
parser.add_argument('--coin', type=str, default='bitcoin',
                    help='代币的coingeko-api名称')
parser.add_argument('--price', type=str, required=True, help='提醒价格(美元)')

parser.add_argument('--smtp-server', type=str, required=True, help='邮件发送程序服务器')
parser.add_argument('--smtp-port', type=int, required=True, help='邮件发送程序服务器端口')
parser.add_argument('--smtp-username', type=str,
                    required=True, help='邮件发送程序服务器的用户名')
parser.add_argument('--smtp-password', type=str,
                    required=True, help='邮件发送程序服务器的密码')
parser.add_argument('--verbose', action='store_true', help='是否启用详细模式')
# 解析命令行参数
args = parser.parse_args()

if args.verbose:
    logging.info(f'参数信息:{args}')

url = "https://api.coingecko.com/api/v3/simple/price"

headers = {
    "Accept": "application/json"
}

params = {
    'ids': 'ethereum,bitcoin,matic-network,binancecoin,tron',
    'vs_currencies': 'USD',
    'precision': 3,
    'include_last_updated_at': 'true',
    'include_24hr_change': 'true',
    'include_market_cap': 'true'
}

response = requests.get(url, params, proxies={
                        "http": args.proxy, "https": args.proxy}, headers=headers)

if response.status_code == 200:
    data = response.json()
    context = generateHtml(data)

    lasttime = os.environ['SEND_TIME']

    current_timestamp = int(time.time())

    if args.verbose:
        logging.info("GenerateHtml successful")
    sender = EmailSender(args.smtp_server, args.smtp_port,
                         args.smtp_username, args.smtp_password)
    if args.verbose:
        logging.info("Email Sending...")
    if notification_flag or current_timestamp-3600 >= lasttime:
        sender.sendHtml(args.to, args.title, context)
else:
    logging.error("Request failed with status code:", response.status_code)
