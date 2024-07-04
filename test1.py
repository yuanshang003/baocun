import logging
import requests
import js2py

date = 123
msg = ""
a = 0
hz = ".rcits.cn"
failed_accounts = []  # 记录失败的账号
deleted_count = 0  # 删除的账号密码对的数量
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
max_retries = 5  # 每个账号的最大重试次数

# 正确地读取账号并尝试登录
with open("1zh.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()  # 读取所有行到列表

# 遍历账号列表
for line in lines:
    date = line.strip()  # 去除两端的空白字符和换行符
    date1 = date + "123456"  # 拼接账号和密码
    retries = 0  # 当前账号的重试次数

    while retries < max_retries:
        try:
            # 登录
            url = "https://" + date.strip('\n') + hz + "/user/ajax.php?act=login"
            payload = "user=" + date.strip('\n') + "&pass=" + date1.strip('\n')
            headers = {
                'Origin': "https://" + date.strip('\n') + hz,
                'Referer': "https://" + date.strip('\n') + hz + "/user/login.php",
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            response = requests.post(url, headers=headers, data=payload)
            a += 1
            logger.info("账号: %s", "第{}个   ".format(a) + date.strip('\n'))
            logger.info("响应内容: %s", response.text)

            login_fail = response.text.find("用户名或密码不正确！")
            if login_fail != -1:
                logger.info("登录失败: %s", date)
                failed_accounts.append(date)  # 记录失败的账号
                deleted_count += 1  # 增加删除计数
                break
            else:
                # 获取基本cookie
                cookie = response.cookies
                PHPSESSID = list(cookie.values())[0]
                user_token = list(cookie.values())[1]
                mysid = list(cookie.values())[2]

                url = "https://" + date.strip('\n') + hz + "/user/qiandao.php"

                payload = {}
                headers = {
                    'authority': date.strip('\n') + hz,
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                    'cache-control': 'no-cache',
                    'pragma': 'no-cache',
                    'referer': "https://" + date.strip('\n') + hz + "/user/",
                    'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
                }

                response = requests.get(url, headers=headers, data=payload)
                print(response)
                start_index = response.text.find(',(') + 1
                end_index = response.text.find(');', start_index)

                if start_index != -1 and end_index != -1:
                    string = response.text[start_index:end_index]
                    cookiess = string
                    sec_defend = js2py.eval_js(cookiess)

                # sec_defend有效化
                url = "https://" + date.strip('\n') + hz + "/user/qiandao.php"

                headers[
                    'cookie'] = "mysid=" + mysid + "; user_token=" + user_token + "; PHPSESSID=" + PHPSESSID + "; sec_defend=" + sec_defend + "; counter=1; _aihecong_chat_visibility=true"

                response = requests.get(url, headers=headers, data=payload)

                # 签到
                url = "https://" + date.strip('\n') + hz + "/user/ajax_user.php?act=qiandao"
                headers['Referer'] = "https://" + date.strip('\n') + hz + "/user/qiandao.php"

                response = requests.get(url, headers=headers, data=payload)

                logger.info("签到状态: %s", response.json())
                msg = msg + "\n" + str(a) + "   " + date
                break  # 成功退出重试循环

        except requests.exceptions.RequestException as e:
            retries += 1
            logger.info("运行状态: %s", f"Request failed: {e}. Retrying {retries}/{max_retries}")
            if retries == max_retries:
                logger.error("连续5次请求失败，停止运行")
                exit()

# 删除失败的账号
with open("1zh.txt", 'r', encoding='utf-8') as file:
    lines = [line for line in file if line.strip() not in failed_accounts]

# 重写文件，只包含成功的账号
with open("1zh.txt", 'w', encoding='utf-8') as file:
    file.writelines(lines)

logger.info("处理完成，失败的账号已被删除。")

msg = msg + "\n" + "共删除了 {} 个账号密码对".format(deleted_count)
# print(msg)


def post_weichat_2():
    url = 'http://www.pushplus.plus/send'
    # post发送的字典参数
    data_dict = {
        'token': "6e2a636fa73f4437ab92f48417111e46",  # 一对多、一对一的token值
        'title': 'Github Action签到',  # 微信接收到显示的标题
        'template': 'txt',  # 指定微信接收到显示的类型
        'content': msg
    }
    r = requests.post(url, data=data_dict)  # 发起请求，可以不设置请求头
    print(r.text)
    logger.info("推送状态: %s", r.text)


if __name__ == '__main__':
    post_weichat_2()
