import json
import config
from request import http
from time import sleep
from loghelper import log


def captcha_check(gt: str, challenge: str, pageurl: str):
    if config.config["captcha_key"] == "":
        log.info(f"尚未配置验证码识别密钥，跳过识别")
        return None
    captcha_key = config.config["captcha_key"]
    api_server = "api.geetest.com"
    try:
        result = solve_captcha(gt, challenge, pageurl, captcha_key, api_server)
    except:
        log.warning(f"识别失败，程序出现未知错误")
        return None
    if "ERROR" in result:
        if result == "ERROR_WRONG_USER_KEY":
            log.warning(f"验证码识别平台key错误，跳过识别")
            return None
        if result == "ERROR_CAPTCHA_UNSOLVABLE":
            log.warning(f"验证码识别超时或无法正常获取，跳过识别")
            return None
        log.warning(f"发生错误：{result}，跳过识别")
        return None
    log.info(f"识别成功，正在重新签到")
    return result


def solve_captcha(gt: str, challenge: str, pageurl: str, captcha_key: str,
                  api_server: str):
    captcha_api = f"http://2captcha.com/in.php?key={captcha_key}&method=geetest&gt={gt}&challenge={challenge}&api_server={api_server}&pageurl={pageurl}&json=1"
    request = http.post(url=captcha_api)
    if str(request.status_code) != "200":
        return f"ERROR_{str(request.status_code)}_{request.text}"
    request_result = request.json()
    if str(request_result["status"]) == "1":
        solve_captcha_url = f"http://2captcha.com/res.php?key={captcha_key}&action=get&id={request_result['request']}&json=1"
        # 识别结果查询
        while True:
            sleep(5)
            captcha = http.post(url=solve_captcha_url)
            captcha_result = captcha.json()
            if str(captcha_result["status"]) == "1":
                result = captcha_result["request"]["geetest_validate"]
                break
            if captcha_result["request"] != "CAPCHA_NOT_READY":
                result = captcha_result["request"]
                break
        return result
    return request_result["request"]


def game_captcha(gt: str, challenge: str):
    pageurl = "https://bbs.mihoyo.com/ys"
    result = captcha_check(gt, challenge, pageurl)
    return result  # 失败返回None 成功返回validate


def bbs_captcha(gt: str, challenge: str):
    pageurl = "https://bbs.mihoyo.com/ys"
    result = captcha_check(gt, challenge, pageurl)
    return result
