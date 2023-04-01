import tools
import config
import setting
from request import http
from loghelper import log


class CloudGenshin:
    def __init__(self) -> None:
        self.headers = {
            'Host': 'api-cloudgame.mihoyo.com',
            'Accept': '*/*',
            'Referer': 'https://app.mihoyo.com',
            'x-rpc-combo_token': config.config['cloud_games']['genshin']['token'],
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 HBPC/12.1.1.301',
        
        }

    # 分钟转小时
    def time_conversion(self, minute: int) -> str:
        h = minute // 60
        s = minute % 60
        return f"{h}小时{s}分钟"

    def sign_account(self) -> str:
        ret_msg = "云原神:\r\n"
        req = http.get(url=setting.cloud_genshin_sgin, headers=self.headers)
        data = req.json()
        if data['retcode'] == 0:
            if int(data["data"]["free_time"]["send_freetime"]) > 0:
                log.info(f'签到成功，已获得{data["data"]["free_time"]["send_freetime"]}分钟免费时长')
                ret_msg += f'签到成功，已获得{data["data"]["free_time"]["send_freetime"]}分钟免费时长\n'
            elif int(data["data"]["free_time"]["free_time"]) == 600 :
                log.info(f'您的免费时长已达到10小时，无需签到')
                ret_msg += f'您的免费时长已达到10小时，无需签到\n'
            else:
                log.info('您今日已经签到过了哦～')
                ret_msg += '您今日已经签到过了哦～\n'
            ret_msg += f'当前拥有免费时长 {self.time_conversion(int(data["data"]["free_time"]["free_time"]))} ,' \
                       f'畅玩卡状态为 {data["data"]["play_card"]["short_msg"]}，拥有米云币 {data["data"]["coin"]["coin_num"]} 枚'
            log.info(ret_msg)
            self.ack_noti()
        elif data['retcode'] == -100:
            ret_msg = "云原神token失效/防沉迷"
            log.warning(ret_msg)
            config.clear_cookie_cloudgame()
        else:
            ret_msg = f'脚本签到失败，json文本:{req.text}'
            log.warning(ret_msg)
        return ret_msg

    def ack_noti(self):
        log.info(f'正在获取未确认签到消息列表')
        req = http.get(url=setting.cloud_genshin_list, headers=self.headers)
        data = req.json()
        if data['retcode'] == 0:
            noti_list = data["data"]["list"]
            if len(noti_list) == 0:
                log.info(f'已获取未确认签到消息列表，当前没有未确认的签到消息')
            else:
                log.info(f'已获取未确认签到消息列表，当前共有{len(noti_list)}条未确认的签到消息')
                i = [0, 0]
                for noti in noti_list:
                    i[0] += 1 
                    ack_json = {"id": noti["id"]}
                    req = http.post(url=setting.cloud_genshin_ack, headers=self.headers, json=ack_json)
                    data = req.json()
                    if data['retcode'] == 0:
                        log.info(f'第{i[0]}条签到消息确认成功！')
                    else:
                        i[1] += 1 
                        log.warning(f'第{i[0]}条签到消息确认失败！')
                if i[1] == 0:
                    log.info(f'所有签到消息已全部确认！')
                else:
                    log.info(f'部分签到消息确认失败！')
        else:
            log.warning(f'获取未确认签到消息列表失败！跳过确认')
        log.info(f'云原神签到消息确认完成！')

if __name__ == '__main__':
    pass
