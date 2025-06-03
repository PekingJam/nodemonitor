import sys
import time

import emoji
import os

import upyun
from qiniu import Auth, put_file
from webdav3.client import Client
from peewee import *
import yaml
import requests
import traceback
import json

db = SqliteDatabase("db/orange_bot.db")
headers = {"user-agent": "curl/7.81.0"}
proxies = {
    'http': 'http://127.0.0.1:32580',
    'https': 'http://127.0.0.1:32580'
}


def upload_to_upyun(file_paths, remote_path):
    print("🟠上传到又拍云...")
    service = "oss-sso"
    username = ""
    password = ""
    up = upyun.UpYun(service, username, password)

    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        remote_file_path = f"{remote_path}/{file_name}"

        with open(file_path, 'rb') as f:
            # 上传文件
            try:
                res = up.put(remote_file_path, f, checksum=True)
                print(f"✅ 上传成功: {file_name}")
            except upyun.UpYunServiceException as e:
                print(f"❌ 上传失败: {file_name} - 错误: {e.msg}")
            except upyun.UpYunClientException as e:
                print(f"❌ 客户端错误: {file_name} - 错误: {e.msg}")
                
def upload_to_myoss(files, remote_path):
    print("🟠上传至www.baidu.com")
    url = "https://www.baidu.com/upload"

    headers = {
        'Authorization': ""
    }
    for file in files:
        file_name = os.path.basename(file)
        payload = {'remote_path': f"{remote_path}"}
        with open(file, 'rb') as f:
            files = {'file': (os.path.basename(file), f)}
            response = requests.post(
                url, data=payload, files=files, headers=headers)
            print(f"✅ 上传成功: {file_name}")


class IpInfo(Model):
    ip = CharField(primary_key=True)
    country = CharField()
    name = CharField()

    class Meta:
        database = db
        table_name = 'ipinfo'


class Emojis(Model):
    id = CharField(primary_key=True)
    name = CharField()
    code = CharField()
    emojis = CharField()

    class Meta:
        database = db
        table_name = 'emojis'


def is_emoji(text):
    dict_emoji = emoji.emoji_list(text)
    if len(dict_emoji) > 0:
        return True
    return False


def code2emoji(code):
    db.connect()
    resp = Emojis.get_or_none(Emojis.code == code)
    db.close()
    if resp is not None:
        return resp.emojis
    print(f"没有该国家的emoji，国家代码:{code}，返回通用代码：🤷‍♀️")
    return "🤷‍♀️"


def qiniu(dirs, remote_path):
    # 要上传的空间
    bucket_name = 'orange-health-space1'
    for path in dirs:
        # 上传后保存的文件名
        key = f'{remote_path}{os.path.basename(path)}'
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, key)
        # 要上传文件的本地路径
        ret, info = put_file(token, key, path, version='v2')
        path = json.loads(info.text_body)['key']
        print(f"🟢{str(info.status_code)}📂{path}")
    }
    client = Client(options)
    for file in files:
        file_name = os.path.basename(file)
        client.upload_file(f"{remote_path}/{file_name}", file)
        print(f"✅ 上传成功: {file_name}")


def server_info(server):
    log_pre = f"ℹ️{server['name']}:{server['server']}:{server['port']}\n"
    with open('kernel/config.yaml', mode='r', encoding='utf-8') as o:
        dict_res = yaml.load(o, Loader=yaml.FullLoader)
        dict_res['proxies'] = [server]
        dict_res['proxy-groups'][0]['proxies'] = [server['name']]
        with open('kernel/config.yaml', mode='w+', encoding='utf8') as release:
            yaml.dump(dict_res, release, allow_unicode=True)
    abs_path = os.getcwd() + "/kernel/config.yaml"
    abs_path = abs_path.replace("\\", '/')
    url = 'http://127.0.0.1:32581/configs?force=true'
    m_head = {
        'Content-Type': 'application/json'
    }
    data = {
        'path': abs_path
    }
    try:
        response = requests.put(url, headers=m_head, json=data, timeout=15)
        print(response.text)
    except requests.exceptions.RequestException:
        traceback.print_exc()
        log_out(log_pre, f"❌ 热更新配置异常,请检查是否安装并成功运行mihomo")
        sys.exit(1)
    try:
        # db.connect()
        print(f"🔔 节点{server['name']} ℹ️ {server['server']}:{server['port']}")
        print(f"    🔎 调用ipinfo网络接口查询ℹ️")
        net_ipinfo = search_ip_info(server)
        if net_ipinfo is not None:
            try:
                if net_ipinfo['country'] != 'CN':
                    # 检查流媒体
                    print(f"    🔍 流媒体解锁测试")
                    flix_status = netflix_test()
                else:
                    flix_status = 404
            except Exception as e:
                flix_status = 404
                print(f"❌ 奈飞解锁测试出错：{str(e)}")
            try:
                if net_ipinfo['country'] != 'CN':
                    print(f"    🤖 ChatGPT解锁测试")
                    ai_status = openai_test()
                else:
                    ai_status = 400
            except Exception as e:
                ai_status = 400
                print(f"❌ ChatGPT解锁测试出错：{str(e)}")
            # 保存到数据库
            info_data = {
                'ip': net_ipinfo['ip'],
                'country': net_ipinfo['country'],
                'name': server['server'],
                'flix_status': flix_status,
                "ai_status": ai_status
            }
            # IpInfo.create(**info_data)
            return info_data
        else:
            log_out(log_pre, f"    ⛔ 三次IP查询均失败，遗弃该节点❗")
        return None
    except requests.exceptions.Timeout:
        log_out(log_pre, f"        ❌ 超时")
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            log_out(log_pre, f"        ❌ 未知异常，信息如下❗ code{e.response.status_code}, msg{e.response.text}")
        else:
            log_out(log_pre, f"        ❌ 未知异常，无法获取详细信息")
        traceback.print_exc()
    except PeeweeException:
        traceback.print_exc()
        log_out(log_pre, f"        ❌ 数据库操作失败，可能是IP查询失败导致❗ ")
    finally:
        db.close()


def test_connectivity(node):
    urls = [
        {"name": "谷歌", "url": "http://www.gstatic.com/generate_204"},
        {"name": "火狐", "url": "http://detectportal.firefox.com/success.txt"},
        {"name": "谷歌2", "url": "http://www.google-analytics.com/generate_204"},
        {"name": "小米", "url": "http://connect.rom.miui.com/generate_204"},
    ]
    print(f"🔔可用性测试 ℹ️节点:{node['name']}:{node['server']}:{node['port']}")
    for url in urls:
        try:
            resp = requests.get(url=url['url'], timeout=8, proxies=proxies, headers=headers)
            sec = round(resp.elapsed.total_seconds() * 1000, 2)
            print(f"    🟢网络畅通无阻！ ⏰ {sec}秒")
            return 200
        except requests.exceptions.Timeout:
            print("   ❌ 超时 ", end="")
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                print(f"    ❌ 未知错误 code{e.response.status_code},msg{e.response.text}❗")
            else:
                print(f"    ❌ 未知异常，无法获取详细信息❗")
            traceback.print_exc()
        print(f"    🔹使用{url['name']}再次尝试中....")
    return 502


def search_ip_info(node):
    log_pre = f"ℹ️{node['name']}:{node['server']}:{node['port']}\n"
    if 'CN' in node['name']:
        return {
            'ip': node['server'],
            'country': 'CN'
        }
    try:
        url = "http://ipinfo.io"
        net_resp = None
        try:
            net_resp = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            info_res = net_resp.json()
            print(f"    ✅ 成功 🔗{info_res['ip']}:{info_res['country']}")
            return info_res
        except Exception:
            print(f"    ❌ 数据解析失败！响应数据:{net_resp.text}\n \n    🟡 尝试使用ip-score接口...")
            url = 'http://127.0.0.1:32581/connections'
            requests.delete(url)
            time.sleep(0.5)
            url = f'http://ip-score.com/json'
            c_resp = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            if c_resp.status_code == 200:
                net_ipinfo = {
                    'ip': c_resp.json()['ip'],
                    'country': c_resp.json()['geoip1']['countrycode']
                }
                print(f"    ✅ 成功 🔗{net_ipinfo['ip']}:{net_ipinfo['country']}")
                return net_ipinfo
            else:
                print(c_resp.text)
    except requests.exceptions.Timeout:
        log_out(log_pre, f"    ❌ 超时 ")
    except requests.exceptions.SSLError as se:
        log_out(log_pre, f"   ❌ 证书错误❗msg:{str(se)}")
    except Exception as e:
        log_out(log_pre, f"    ❌ 未知异常，无法获取详细信息❗{str(e)}")
        traceback.print_exc()
    return None


def ip_tool_net_check(server):
    url = f"https://www.toolsdaquan.com/toolapi/public/ipchecking/{server['server']}/{server['port']}"
    t_head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Referer': f'https://www.toolsdaquan.com/ipcheck/'
    }
    resp = requests.get(url, headers=t_head)
    if resp.status_code == 200 and resp.json()['tcp'] == 'success':
        return 200
    return 500


def log_out(pre, content):
    print(content)
    with open("logs/error.log", mode="a", encoding='utf-8') as f:
        f.write(pre + content)


def netflix_test():
    url = "https://www.netflix.com/title/70143836"
    n_head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.14'
    }
    resp = requests.get(url=url, headers=n_head, proxies=proxies, timeout=15)
    if resp.status_code == 200:
        country_code = resp.url.split('/')[3].upper()
        print(f"    ✅ 节点已解锁Netflix，区域: {country_code}")
    else:
        print(f"    ⚠️ 节点未解锁Netflix！")
    return resp.status_code


def openai_test():
    url = "https://android.chat.openai.com"
    n_head = {
        'User-Agent': 'curl/7.54.0'
    }
    resp = requests.get(url=url, headers=n_head, proxies=proxies, timeout=15)
    if resp.status_code != 400:
        print(f"    ✅ 节点已解锁ChatGPT")
    else:
        print(f"    ⚠️ 节点未解锁ChatGPT！")
    return resp.status_code
