import json
import time
import tools
import config
import random
import captcha
import setting
from request import http
from loghelper import log
from error import CookieError

today_get_coins = 0
today_have_get_coins = 0  # 这个变量以后可能会用上，先留着了
have_coins = 0


class Mihoyobbs:
    def __init__(self):
        self.headers = {
            "DS": tools.get_ds(web=False),
            "cookie": f'stuid={config.config["account"]["stuid"]};stoken={config.config["account"]["stoken"]}',
            "x-rpc-client_type": setting.mihoyobbs_Client_type,
            "x-rpc-app_version": setting.mihoyobbs_version,
            "x-rpc-sys_version": "12",
            "x-rpc-channel": "miyousheluodi",
            "x-rpc-device_id": tools.get_device_id(),
            "x-rpc-device_name": tools.random_text(random.randint(1, 10)),
            "x-rpc-device_model": "Mi 10",
            "Referer": "https://app.mihoyo.com",
            "Host": "bbs-api.mihoyo.com",
            "User-Agent": "okhttp/4.8.0"
        }
        self.Task_do = {
            "bbs_Sign": False,
            "bbs_Read_posts": False,
            "bbs_Read_posts_num": 3,
            "bbs_Like_posts": False,
            "bbs_Like_posts_num": 5,
            "bbs_Share": False
        }
        self.get_tasks_list()
        # 如果这三个任务都做了就没必要获取帖子了
        if self.Task_do["bbs_Read_posts"] and self.Task_do["bbs_Like_posts"] and self.Task_do["bbs_Share"]:
            pass
        else:
            self.postsList = self.get_list()

    def refresh_list(self) -> None:
        self.postsList = self.get_list()

    def get_pass_challenge(self):
        req = http.get(url=setting.bbs_get_captcha, headers=self.headers)
        data = req.json()
        if data["retcode"] != 0:
            return None
        validate = captcha.bbs_captcha(data["data"]["gt"], data["data"]["challenge"])
        if validate is not None:
            check_req = http.post(url=setting.bbs_captcha_verify, headers=self.headers,
                                  json={"geetest_challenge": data["data"]["challenge"],
                                        "geetest_seccode": validate+"|jordan",
                                        "geetest_validate": validate})
            check = check_req.json()
            if check["retcode"] == 0:
                return check["data"]["challenge"]
        return None

    # 获取任务列表，用来判断做了哪些任务
    def get_tasks_list(self):
        global today_get_coins
        global today_have_get_coins
        global have_coins
        log.info("正在获取任务列表")
        req = http.get(url=setting.bbs_tasks_list, headers=self.headers)
        data = req.json()
        if "err" in data["message"] or data["retcode"] == -100:
            log.error("获取任务列表失败，你的cookie可能已过期，请重新设置cookie。")
            config.clear_cookies()
            raise CookieError('Cookie expires')
        else:
            today_get_coins = data["data"]["can_get_points"]
            today_have_get_coins = data["data"]["already_received_points"]
            have_coins = data["data"]["total_points"]
            # 如果当日可获取米游币数量为0直接判断全部任务都完成了
            if today_get_coins == 0:
                self.Task_do["bbs_Sign"] = True
                self.Task_do["bbs_Read_posts"] = True
                self.Task_do["bbs_Like_posts"] = True
                self.Task_do["bbs_Share"] = True
            else:
                # 如果第0个大于或等于62则直接判定任务没做
                if data["data"]["states"][0]["mission_id"] >= 62:
                    log.info(f"新的一天，今天可以获得{today_get_coins}个米游币")
                    pass
                else:
                    log.info(f"似乎还有任务没完成，今天还能获得{today_get_coins}")
                    for i in data["data"]["states"]:
                        # 58是讨论区签到
                        if i["mission_id"] == 58:
                            if i["is_get_award"]:
                                self.Task_do["bbs_Sign"] = True
                        # 59是看帖子
                        elif i["mission_id"] == 59:
                            if i["is_get_award"]:
                                self.Task_do["bbs_Read_posts"] = True
                            else:
                                self.Task_do["bbs_Read_posts_num"] -= i["happened_times"]
                        # 60是给帖子点赞
                        elif i["mission_id"] == 60:
                            if i["is_get_award"]:
                                self.Task_do["bbs_Like_posts"] = True
                            else:
                                self.Task_do["bbs_Like_posts_num"] -= i["happened_times"]
                        # 61是分享帖子
                        elif i["mission_id"] == 61:
                            if i["is_get_award"]:
                                self.Task_do["bbs_Share"] = True
                                # 分享帖子，是最后一个任务，到这里了下面都是一次性任务，直接跳出循环
                                break

    # 获取要帖子列表
    def get_list(self) -> list:
        temp_list = []
        log.info("正在获取帖子列表......")
        req = http.get(url=setting.bbs_post_list_url.format(setting.mihoyobbs_List_Use[0]["forumId"]),
                       headers=self.headers)
        data = req.json()["data"]["list"]
        for n in range(5):
            r_l = random.choice(data)
            while r_l["post"]["subject"] in str(temp_list):
                r_l = random.choice(data)
            temp_list.append([r_l["post"]["post_id"], r_l["post"]["subject"]])
            # temp_list.append([data["data"]["list"][n]["post"]["post_id"], data["data"]["list"][n]["post"]["subject"]])

        log.info("已获取{}个帖子".format(len(temp_list)))
        return temp_list

    # 进行签到操作
    def signing(self):
        if self.Task_do["bbs_Sign"]:
            log.info("讨论区任务已经完成过了~")
        else:
            log.info("正在签到......")
            header = {}
            header.update(self.headers)
            challenge = None
            for i in setting.mihoyobbs_List_Use:
                challenge = None
                check_pass = False
                for i2 in range(2):
                    if check_pass:
                        log.info("社区签到成功")
                        continue
                    header["DS"] = tools.get_ds2("", json.dumps({"gids": i["id"]}))
                    req = http.post(url=setting.bbs_sign_url, json={"gids": i["id"]}, headers=header)
                    data = req.json()
                    if data["retcode"] == 1034:
                        log.warning("社区签到触发验证码")
                        challenge = self.get_pass_challenge()
                        if challenge is not None:
                            header["x-rpc-challenge"] = challenge
                    elif "err" not in data["message"] and data["retcode"] == 0:
                        log.info(str(i["name"] + data["message"]))
                        check_pass = True
                        if challenge is not None:
                            challenge = None
                            header.pop("x-rpc-challenge")
                    else:
                        log.error("签到失败，你的cookie可能已过期，请重新设置cookie。")
                        config.clear_cookies()
                        raise CookieError('Cookie expires')
                    time.sleep(random.randint(2, 8))

    # 看帖子
    def read_posts(self):
        if self.Task_do["bbs_Read_posts"]:
            log.info("看帖任务已经完成过了~")
        else:
            log.info("正在看帖......")
            for i in range(self.Task_do["bbs_Read_posts_num"]):
                req = http.get(url=setting.bbs_detail_url.format(self.postsList[i][0]), headers=self.headers)
                data = req.json()
                if data["message"] == "OK":
                    log.debug("看帖：{} 成功".format(self.postsList[i][1]))
                time.sleep(random.randint(2, 8))

    # 点赞
    def like_posts(self):
        header = {}
        header.update(self.headers)
        challenge = None
        if self.Task_do["bbs_Like_posts"]:
            log.info("点赞任务已经完成过了~")
        else:
            log.info("正在点赞......")
            for i in range(self.Task_do["bbs_Like_posts_num"]):
                req = http.post(url=setting.bbs_like_url, headers=header,
                                json={"post_id": self.postsList[i][0], "is_cancel": False})
                data = req.json()
                if data["message"] == "OK":
                    log.debug("点赞：{} 成功".format(self.postsList[i][1]))
                    if challenge is not None:
                        challenge = None
                        header.pop("x-rpc-challenge")
                elif data["retcode"] == 1034:
                    log.warning("点赞触发验证码")
                    challenge = self.get_pass_challenge()
                    if challenge is not None:
                        header["x-rpc-challenge"] = challenge
                    # 判断取消点赞是否打开
                if config.config["mihoyobbs"]["cancel_like_posts"]:
                    time.sleep(random.randint(2, 8))
                    req = http.post(url=setting.bbs_like_url, headers=self.headers,
                                    json={"post_id": self.postsList[i][0], "is_cancel": True})
                    data = req.json()
                    if data["message"] == "OK":
                        log.debug("取消点赞：{} 成功".format(self.postsList[i][1]))
                time.sleep(random.randint(2, 8))

                # 分享操作

    def share_post(self):
        if self.Task_do["bbs_Share"]:
            log.info("分享任务已经完成过了~")
        else:
            log.info("正在执行分享任务......")
            for i in range(3):
                req = http.get(url=setting.bbs_share_url.format(self.postsList[0][0]), headers=self.headers)
                data = req.json()
                if data["message"] == "OK":
                    log.debug("分享：{} 成功".format(self.postsList[0][1]))
                    log.info("分享任务执行成功......")
                    break
                else:
                    log.debug(f"分享任务执行失败，正在执行第{i + 2}次，共3次")
                    time.sleep(random.randint(2, 8))
            time.sleep(random.randint(2, 8))
