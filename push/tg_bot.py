#!/usr/bin/env python3
# _*_ coding:utf-8 _*_
import requests

TG_BOT_TOKEN = "7049881517323:AAFvi32323323d_g0zMNF7eqMqPBsla5EvLx323R8erGOo"
TG_USER_ID = "3723273872"


def push_message(title: str, content: str) -> None:
    """
    使用 telegram 机器人 推送消息。
    """

    # url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    url = f"https://bot.889969.xyz/bot{TG_BOT_TOKEN}/sendMessage"

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "parse_mode": "Markdown",
        "chat_id": TG_USER_ID,
        "text": f"*{title}*\n{content}",
        "disable_web_page_preview": "true",
    }
    proxies = None
    response = requests.post(
        url=url, headers=headers, params=payload, proxies=proxies
    ).json()

    if response["ok"]:
        print("tg 推送成功！")
    else:
        print("tg 推送失败！")


if __name__ == '__main__':
    msg = """```
欢迎留言，不定时在线，消息看到后都会一一及时回复！
```
    """
    push_message("*使用教程*", msg)
