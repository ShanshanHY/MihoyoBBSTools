import hmac
import json
import tools
import config
import hashlib
import setting
from request import http
from loghelper import log
from error import CookieError


def login():
    if config.config["account"]["cookie"] == '':
        log.error("请填入Cookies!")
        config.clear_cookies()
        raise CookieError('No cookie')
    # 判断Cookie里面是否有login_ticket 没有的话直接退了
    if "login_ticket" in config.config["account"]["cookie"]:
        temp_cookies = config.config["account"]["cookie"].split(";")
        for i in temp_cookies:
            if i.split("=")[0] == " login_ticket":
                config.config["account"]["login_ticket"] = i.split("=")[1]
                break
        # 这里获取Stuid，但是实际是可以直接拿cookie里面的Uid
        data = http.get(url=setting.bbs_cookie_url.format(config.config["account"]["login_ticket"])).json()
        if "成功" in data["data"]["msg"]:
            config.config["account"]["stuid"] = str(data["data"]["cookie_info"]["account_id"])
            data = http.get(url=setting.bbs_cookie_url2.format(
                config.config["account"]["login_ticket"], config.config["account"]["stuid"])).json()
            config.config["account"]["stoken"] = data["data"]["list"][0]["token"]
            log.info("登录成功！")
            log.info("正在保存Config！")
            config.save_config()
        else:
            log.error("cookie已失效,请重新登录米游社抓取cookie")
            config.clear_cookies()
            raise CookieError('Cookie expires')
    else:
        log.error("cookie中没有'login_ticket'字段,请重新登录米游社，重新抓取cookie!")
        config.clear_cookies()
        raise CookieError('Cookie lost login_ticket')


# 将cookie转换成字典
def ck_to_dict(cookie_str) -> dict:
    cookie = {}
    for line in cookie_str.split(';'):
        key, value = line.split('=', 1)
        cookie[key] = value
        return cookie


# 数据签名校验
def sign_data(data) -> str:
    key = setting.cloudgenshin_sign
    sign = hmac.new(key.encode(), data.encode(), digestmod=hashlib.sha256).hexdigest()
    return sign

# 指定json转换格式（默认转换格式有一个空格，会导致云原神服务器判定错误（channel_id）)
def json_dumps(dic) -> str:
    data = json.dumps(dic, separators=(',', ':'))
    return data


def cloud_genshin() -> bool:
    device_id = tools.get_device_id()
    cloud_headers = {
        'Host': 'hk4e-sdk.mihoyo.com',
        'Accept': '*/*',
        'x-rpc-channel_id': '1',
        'x-rpc-channel_version': '2.9.0.6',
        'x-rpc-device_id': device_id
    }
    mys_headers = {}
    mys_headers.update(setting.headers)
    mys_cookie = config.config["account"]["cookie"]
    mys_headers["Cookie"] = mys_cookie
    mys_headers["User-Agent"] = tools.get_useragent()
    mys_headers["x-rpc-device_id"] = device_id
    mys_headers["DS"] = tools.get_ds(web=True)
    mys_headers["Referer"] = "https://app.ihoyo.com"

    # 使用stuid stoken从米游社获取game_token
    uid = config.config["account"]["stuid"]
    stoken = config.config["account"]["stoken"]
    get_token_url = f'{setting.cloud_get_gametoken}stoken={stoken}&uid={uid}'

    resp = http.get(get_token_url, headers=mys_headers)
    resp_data = resp.json()

    if resp_data["retcode"] != 0:
        log.error("获取game_token获取失败")
        return False

    # 从云原神服务器获取combo_token
    game_token = resp_data["data"]["game_token"]
    game_data_data = {"uid": uid, "token": game_token}
    game_data = {
        "data": json_dumps(game_data_data),
        "app_id": 4,
        "channel_id": 1,
        "device": device_id
    }
    signdata = f"app_id=4&channel_id=1&data={json_dumps(game_data_data)}&device={device_id}"
    game_data["sign"] = sign_data(signdata)
    resp = http.post(setting.cloud_get_ct,
                        headers=cloud_headers,
                        data=json_dumps(game_data))
    resp_data = resp.json()
    if resp_data["retcode"] != 0:
        log.error("获取combo_token获取失败")
        return False

    ct = resp_data["data"]["combo_token"]
    oi = resp_data["data"]["open_id"]
    signctoken = f"app_id=4&channel_id=1&combo_token={ct}&open_id={oi}"
    ctoken = f"ai=4;ci=1;oi={oi};ct={ct};si={sign_data(signctoken)};bi=hk4e_cn"

    # 保存到配置文件
    conf = config.config
    conf["cloud_games"]["genshin"]["token"] = ctoken
    config.save_config(None, conf)
    return True
