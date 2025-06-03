import time
import traceback
import uuid

import requests
import yaml
from requests import RequestException

import utils.Utils as Utl
from push.tg_bot import push_message
import re
import emoji

sub_url = "https://drive.www.baidu.com.cn/2323/fdafda/init_proxies.yaml"

# sing_box UA: SFA/1.8.4 (188; sing-box 1.8.4)
headers = {
    'User-agent': 'ClashMetaForAndroid/2.9.1.Meta-Alpha.debug'
}

ban_word = ['官网', '重置', 'tg', 'TG', '刷新', '下次', '临时', '群组', '禁止', '机场', '一元', '免费', '以下', '流量',
            '到期', '套餐', '过期', '频道', '失联', '阿呆', 't.me', '群', '剩余', '剩', '更新', '订阅']
sub_info = ['流量', '到期', '过期']


def is_in_list(txt, arr):
    # 判断数组里的词，是否在列表里
    for w in arr:
        if w in txt:
            return False
    return True


def get_server_by_name(mark_name, release_yaml_path):
    new_servers = []
    with open(release_yaml_path, mode='r', encoding='utf-8') as o:
        dict_res = yaml.load(o, Loader=yaml.FullLoader)
        servers = dict_res['proxies']
        if not mark_name:
            return servers
        for server in servers:
            if mark_name in server['name'] and server['server'] != '127.0.0.1':
                new_servers.append(server)
    return new_servers


def generate_proxies_file(py_dict, path):
    with open(path, mode='w+', encoding='utf8') as release:
        yaml.dump(py_dict, release, allow_unicode=True)


def get_sub():
    # 清空日志文件
    with open('logs/error.log', mode='w', encoding='utf-8') as file:
        file.write("")
        pass
    proxies = []
    free_proxies = []
    oracle_proxies = []
    pc_proxies = []
    one_proxies = []
    yaml_text = ""
    # 已存在server+port列表
    # exists_server_list = []
    # try:
    #     resp = Utl.requests.get(url=sub_url, headers=headers, timeout=10)
    #     resp.encoding = 'utf-8'
    #     yaml_text = resp.text
    #     dict_obj = yaml.safe_load(yaml_text)
    #     for proxy in dict_obj['proxies']:
    #         # 如果不是无效节点则开始优化
    #         if is_in_list(proxy['name'], ban_word):
    #             # 获取节点IP信息
    #             ip_info = Utl.server_info(proxy)
    #             if ip_info is None:
    #                 continue
    #             # 查询入口IP
    #             in_ip = dns_resolver(proxy['server'])
    #             tmp_info = f"{in_ip}:{ip_info['ip']}"
    #             # 入口IP如果和出口IP如果在列表里则跳过
    #             if tmp_info in exists_server_list:
    #                 continue
    #             else:
    #                 exists_server_list.append(tmp_info)
    #             emoji_list = emoji.emoji_list(proxy['name'])
    #             if len(emoji_list) > 0 and emoji_list[0]['match_start'] == 0:
    #                 proxy['name'] = proxy['name'][emoji_list[0]['match_end']:]
    #             if 'network' in proxy:
    #                 if proxy['type'] == 'vmess' and proxy['port'] == 80 and proxy['network'] == 'ws':
    #                     proxy['name'] = f'll{proxy["name"]}'
    #             if ip_info['flix_status'] == 200:
    #                 if ip_info['ai_status'] != 400:
    #                     proxy['name'] = f'{Utl.code2emoji(ip_info["country"])}▪️🔹{proxy["name"]}'
    #                 else:
    #                     proxy['name'] = f'{Utl.code2emoji(ip_info["country"])}🔹{proxy["name"]}'
    #             elif ip_info['ai_status'] == 403:
    #                 proxy['name'] = f'{Utl.code2emoji(ip_info["country"])}▪️{proxy["name"]}'
    #             else:
    #                 proxy['name'] = f'{Utl.code2emoji(ip_info["country"])}{proxy["name"]}'
    #             if ip_info["country"] != 'CN':
    #                 proxy['name'] = f'{proxy["name"]}🔹'
    #             # 区分免流和非免流节点
    #             proxy['name'] = proxy['name'].replace('有新公告-', "")
    #             proxy['name'] = proxy['name'].replace('新优惠卷已发放-', "")
    #             proxy['name'] = proxy['name'].replace('已暂时性开始注册-', "")
    #             proxy['name'] = proxy['name'].replace('邀请依旧连带-', "")
    #             proxy['name'] = proxy['name'].replace('元', "")
    #             proxy['name'] = proxy['name'].replace('10元', "")
    #             proxy['name'] = proxy['name'].replace('15元', "")
    #             try:
    #                 if 'network' in proxy:
    #                     if proxy['type'] == 'vmess' and proxy['port'] == 80 and proxy['network'] == 'ws':
    #                         if 'ws-opts' in proxy:
    #                             ws_opts = proxy['ws-opts']['path']
    #                         else:
    #                             ws_opts = '/'
    #                         free_proxy = {"name": proxy['name'], "server": proxy['server'], "port": 80, "type": "vmess",
    #                                       "uuid": proxy['uuid'], "alterId": 0, "cipher": "auto", "tls": False,
    #                                       "skip-cert-verify": True, "network": "ws", "udp": True,
    #                                       "ws-opts": {"path": ws_opts,
    #                                                   "headers": {"Host": "pull.free.video.10010.com"}},
    #                                       "ws-path": ws_opts,
    #                                       "ws-headers": {"Host": "pull.free.video.10010.com"}}
    #                         proxies.append(free_proxy)
    #                         one_proxies.append(free_proxy)
    #                         # pc_proxies.append(free_proxy)
    #                         # 仅接收cn节点
    #                         if '🇨🇳' in proxy['name']:
    #                             oracle_proxies.append(free_proxy)
    #                             pc_proxies.append(free_proxy)
    #                     elif '🇨🇳' not in proxy['name']:
    #                         proxies.append(proxy)
    #                 elif '🇨🇳' not in proxy['name']:
    #                     proxies.append(proxy)

    #             except Exception as e:
    #                 print(f"proxy:\n{proxy}\nerror_info:{e.args[0]}")
    # except RequestException:
    #     traceback.print_exc()
    #     pattern = re.compile("[\u4e00-\u9fa5]+")  # 匹配 Unicode 中的中文字符范围
    #     result = re.findall(pattern, yaml_text)
    #     push_message("机场订阅获取失败",
    #                               f"url: \n{sub_url}\nmark_name: 七牛\n"
    #                               f"关键信息：{'.'.join(result)}\n uid：{uuid.uuid1()}\n 订阅返回信息{yaml_text}")

    info_servers = [
        {
            'name': f'🟢 {time.strftime("%m-%d %H:%M", time.localtime())} 更新',
            "port": 7890,
            "server": "127.0.0.1",
            "type": "http"
        },
        {
            'name': f'🟢 3小时更新一次',
            "port": 7890,
            "server": "127.0.0.1",
            "type": "http"
        }
    ]
    oracle_origin_proxies = get_server_by_name("", "proxies/oracle_origin_proxies.yaml")
    pc_origin_proxies = get_server_by_name("", "proxies/pc_origin_proxies.yaml")
    oracle_origin_proxies.extend(info_servers)
    pc_origin_proxies.extend(info_servers)

    # 一个proxies对应一个配置文件
    proxies.extend(pc_origin_proxies)
    one_proxies.extend(info_servers)

    oracle_proxies.extend(oracle_origin_proxies)
    # pc_proxies.extend(pc_origin_proxies)
    pc_origin_proxies.extend(pc_proxies)

    # 生成对应proxies文件
    generate_proxies_file({'proxies': proxies}, "proxies/proxies.yaml")
    generate_proxies_file({'proxies': one_proxies}, "proxies/one_proxies.yaml")
    generate_proxies_file({'proxies': oracle_proxies}, "proxies/oracle_proxies.yaml")
    generate_proxies_file({'proxies': pc_origin_proxies}, "proxies/pc_proxies.yaml")


def oracle_sort_key(elem):
    """
        排序key
        将数组里的元素按照香港-新加坡-日本-美国进行排序
    """
    v_name = elem['name']
    if '🇨🇳' in v_name or '中国' in v_name:
        return 0
    if '🇭🇰' in v_name or '香港' in v_name:
        return 1
    elif '🇸🇬' in v_name or '新加坡' in v_name:
        return 2
    elif '🇯🇵' in v_name or '日本' in v_name:
        return 3
    elif '🇺🇸' in v_name or '美国' in v_name:
        return 4
    else:
        return 5


def dns_resolver(server):
    domain_regex = r'^([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    # 使用re.match进行匹配
    match = re.match(domain_regex, server)
    if not bool(match):
        return server
    url = f"http://127.0.0.1:d22323/dns/query?name={server}&type=A"
    try:
        resp = requests.get(url=url, timeout=10)
        if resp.status_code == 200:
            return resp.json()['Answer'][0]['data']
    except Exception as e:
        print(f"调用dns解析失败{str(e)}")
