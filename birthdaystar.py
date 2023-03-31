import tools
import config
import random
import setting
from time import sleep
from request import http
from loghelper import log
from account import get_account_list

class Birthdaystar:
    def __init__(self) -> None:
        self.headers = {}
        self.headers.update(setting.headers)
        self.headers['Cookie'] = config.config["account"]["cookie"]
        self.headers['User-Agent'] = tools.get_useragent()
        self.account_list = get_account_list("hk4e_cn", self.headers)

    # 获取查询用Token
    def get_e_hk4e_token(self, account):
        post_json = {
            "game_biz": "hk4e_cn",
            "lang": "zh_cn",
            "region": account[2],
            "uid": account[1]
        }
        req = http.post(url=setting.e_hk4e_token, headers=self.headers, json = post_json)
        data = req.json()
        if data['retcode'] == 0:
            # 重组新cookie
            self.headers_query = self.headers
            self.headers_query['Cookie'] = "e_hk4e_token=" + req.cookies.get("e_hk4e_token") + "; " + self.headers['Cookie']
            return True
        return False

    def celebrate(self) -> str:
        return_data = "留影叙佳期:\r\n"
        if len(self.account_list) != 0:
            for account in self.account_list:
                log.info(f"正在为旅行者{account[0]}执行留影叙佳期")
                log.info("正在获取留影叙佳期Token")
                # 尝试对每个账号获取Token
                if self.get_e_hk4e_token(account):
                    # 查询链接 收集卡片链接
                    birthdaystar_query = setting.birthdaystar_query.format(account[1], account[2])
                    birthdaystar_celebrate = setting.birthdaystar_celebrate.format(account[1], account[2])
                    sleep(random.randint(3, 6))
                    req = http.get(url=birthdaystar_query, headers=self.headers_query)
                    data = req.json()
                    if data['retcode'] == 0:
                        # 获取必要信息进卡片收集
                        birth_list = data['data']['role']
                        if len(birth_list) == 0:
                            log.info(f"今天没有人过生日哦～")
                        else:
                            for i in birth_list:
                                role_id = i['role_id']
                                name = i['name']
                                log.info(f"今天是{name}的生日哦！旅行者{account[0]}祝{name}生日快乐！")
                                return_data += f"今天是{name}的生日哦！旅行者{account[0]}祝{name}生日快乐！"
                                log.info(f"正在与{name}进行生日留影")
                                sleep(random.randint(8, 12))
                                req = http.post(url=birthdaystar_celebrate, headers=self.headers, json={"role_id": role_id})
                                data = req.json()
                                if data['retcode'] == 0:
                                    log.info(f"与{name}的生日留影完成啦！")
                                elif data['retcode'] == -512009:
                                    log.info(f"已经和{name}留影过啦！还想再拍一张嘛？")
                                sleep(random.randint(1, 3))
                    else:
                        log.error("查询生日信息失败")
                        return_data += "\n查询生日信息失败"
                        return return_data
                else:
                    log.error("留影叙佳期Token获取失败")
                    return_data += "\nToken获取失败"
                    return return_data
            log.info("留影叙佳期完成啦！")
        else:
            log.warning("账号没有绑定任何原神账号！")
            return_data += "\n并没有绑定任何原神账号"
        return return_data


if __name__ == '__main__':
    pass
