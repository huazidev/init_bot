import re
import json
import requests
import logging
import random
from urllib import parse

from framework_sites.cookie import Cookies

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"


class Douyin:

    def __init__(self, url: str):
        self.url = url

    def generate_random_str(self, randomlength=107):
        """
        根据传入长度产生随机字符串
        """
        random_str = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
        length = len(base_str) - 1
        for _ in range(randomlength):
            random_str += base_str[random.randint(0, length)]
        return random_str

    def get_ttwid(self):
        ttwid = r'ttwid=1%7CWBuxH_bhbuTENNtACXoesI5QHV2Dt9-vkMGVHSRRbgY%7C1677118712%7C1d87ba1ea2cdf05d80204aea2e1036451dae638e7765b8a4d59d87fa05dd39ff'
        ttwid_url = 'https://ttwid.bytedance.com/ttwid/union/register/'
        data = {"region": "cn", "aid": 1768, "needFid": False, "service": "www.ixigua.com", "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": True}
        headers = {'Content-Type': 'application/json'}
        logging.info(ttwid_url)
        response = requests.post(ttwid_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            logging.info(f'ttwid succ: {response.json()}')
            logging.info(response.json())
            cookies = response.headers.get("Set-Cookie")
            ttwid = cookies.split(";")[0]
        else:
            logging.info(f'ttwid failed, code: {response.status_code}')
        logging.info(ttwid)
        return ttwid

    def run(self):
        r = requests.get(url=self.url)
        logging.info(str(r.url))
        self.key = re.findall('video/(\d+)?', str(r.url))[0]
        logging.info(self.key)

        return self.get_video_info()

    def get_video_info(self):
        xbogus_url = 'https://tiktok.iculture.cc/X-Bogus'
        url = f'https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={self.key}&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333'
        data = {
                "url": url,
                "user_agent": USER_AGENT,
        }
        headers = {'Content-Type': 'application/json'}
        logging.info(url)
        response = requests.post(xbogus_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            logging.info(response.json())
        else:
            logging.info(f'status: {response.status_code}')
        xbogus = response.json()
        url = xbogus['param']  # json.loads(xbogus)
        logging.info(url)
        # return js

        ms_token = self.generate_random_str()
        odin_tt = r'odin_tt=324fb4ea4a89c0c05827e18a1ed9cf9bf8a17f7705fcc793fec935b637867e2a5a9b8168c885554d029919117a18ba69; '
        ttwid = self.get_ttwid()
        bd_ticket_guard_client_data = r'bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWNsaWVudC1jc3IiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLVxyXG5NSUlCRFRDQnRRSUJBREFuTVFzd0NRWURWUVFHRXdKRFRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxXHJcbllYSmtNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVKUDZzbjNLRlFBNUROSEcyK2F4bXAwNG5cclxud1hBSTZDU1IyZW1sVUE5QTZ4aGQzbVlPUlI4NVRLZ2tXd1FJSmp3Nyszdnc0Z2NNRG5iOTRoS3MvSjFJc3FBc1xyXG5NQ29HQ1NxR1NJYjNEUUVKRGpFZE1Cc3dHUVlEVlIwUkJCSXdFSUlPZDNkM0xtUnZkWGxwYmk1amIyMHdDZ1lJXHJcbktvWkl6ajBFQXdJRFJ3QXdSQUlnVmJkWTI0c0RYS0c0S2h3WlBmOHpxVDRBU0ROamNUb2FFRi9MQnd2QS8xSUNcclxuSURiVmZCUk1PQVB5cWJkcytld1QwSDZqdDg1czZZTVNVZEo5Z2dmOWlmeTBcclxuLS0tLS1FTkQgQ0VSVElGSUNBVEUgUkVRVUVTVC0tLS0tXHJcbiJ9'
        cookie = f'msToken={ms_token};{odin_tt}{ttwid};{bd_ticket_guard_client_data}'
        logging.info(cookie)
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": "https://www.douyin.com/",
            "Cookie": cookie,
        }
        # headers = Cookies().dyheaders
        logging.info(headers)
        response = requests.get(url=url, headers=headers)
        i = 1
        while response.status_code != 200 and i > 0:
            logging.info(f"failed: {i}, code: {response.status_code}")
            response = requests.get(url=url, headers=headers)
            i -= 1

        video_url = f'原始链接：{self.url}'
        if response.status_code == 200:
            logging.info(response.content)
            logging.info(response.text)
            js = json.loads(response.content)
            try:
                video_url = str(js['aweme_detail']['video']['play_addr']
                                ['url_list'][2])  # .replace('playwm', 'play')  # 去水印后链接
            except:
                print('[  提示  ]:视频链接获取失败\r')
        else:
            logging.info('接口调用失败')

        return video_url
        # return res['item_list'][0]['video']['play_addr']['url_list'][0].replace('playwm', 'play').replace('720p', '9999')


def get_douyin(url):
    if re.match(r'http[s]?://v.douyin.com/\S+', url):
        dy = Douyin(url)
        url_judged = dy.run()

        return url_judged
    else:
        return '请检查你输入的链接是否正确，例如：https://v.douyin.com/6kAoWvc/'

def douyin_parse(link):
    """
    抖音链接解析
    :param link: 链接
    :return:
    """
    # 请求头
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": "ttwid=1%7C5grcQhcCKwqv-Xs9lsffIaLJcUnQcZ4xfprzwayDvQM%7C1676605769%7C255eb8db183847f6fd5f2cacf7d6549d63bf4969d381c3418e35995ac7b6a171; passport_csrf_token=a83047d9ee4fd31aba58f70e304335a0; passport_csrf_token_default=a83047d9ee4fd31aba58f70e304335a0; s_v_web_id=verify_le7zsch1_vrWqCyLv_4vsJ_4Wbu_8f9O_8uaRdVZujUR1; SEARCH_RESULT_LIST_TYPE=%22single%22; download_guide=%223%2F20230224%22; xgplayer_user_id=262468157771; douyin.com; strategyABtestKey=%221677545888.188%22; csrf_session_id=1b878a71d301ca0b9d1107a00a3237b2; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWNsaWVudC1jc3IiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLVxyXG5NSUlCRFRDQnRRSUJBREFuTVFzd0NRWURWUVFHRXdKRFRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxXHJcbllYSmtNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUV3Z21Gc3VDVHZESjZZeE11eVdXTEJUNGtcclxuUUtDSGpBdU9GeTV4Mno5QTFHMG9acTVuaVg0TzVPb2p5SFBVRnZBL0xOSzVaTWJ5bERtWmVhcWcwUnkzbjZBc1xyXG5NQ29HQ1NxR1NJYjNEUUVKRGpFZE1Cc3dHUVlEVlIwUkJCSXdFSUlPZDNkM0xtUnZkWGxwYmk1amIyMHdDZ1lJXHJcbktvWkl6ajBFQXdJRFJ3QXdSQUlnUG1rUzJQNUNBa1FRdU9GbnYraXFMZ0ZWNkxkMlBnQlA4VlZpRXgvNXVyc0NcclxuSUVMMnVuMkIzSjBSOTdUazJ0VjB5RGZsLzBLaFk0TmR1WTkxL0g3Z0h3RFFcclxuLS0tLS1FTkQgQ0VSVElGSUNBVEUgUkVRVUVTVC0tLS0tXHJcbiJ9; VIDEO_FILTER_MEMO_SELECT=%7B%22expireTime%22%3A1678152445204%2C%22type%22%3A1%7D; __ac_nonce=063fd5b3f0054f9ad1de6; __ac_signature=_02B4Z6wo00f011gMORgAAIDBHxoHtvE1a5tYLD2AALYJmzmLAnhJfJGYj6YrdcJ.GqhXaYlXaOHrARLl6HXYMHjHJ5EWjjeLDHp7exvMavnxqmZ1k5C4LKe.PSfjtAe7p4E8d.hBCkppHfice8; home_can_add_dy_2_desktop=%221%22; msToken=_zLGCd1OJcoYpZ-fRniWON1mH0QRLDV7QQDLZykyk-yi8iSN42r6xVyLhsC-yqr8O32mGA5d3TO1dLkHXF-BFdActIDv9RKjVe-yQORkllVOJqEkcJel5Q==; tt_scid=uk9.KTlPKHn.6qP2KcGIDFZUhII2O4vjDjErsTW866.w2Rux9NSFEVtnQ6ia9htH733a; msToken=nY0Gi1G71gNPaoixSC3WbdsEB1sz6dOm4H2crksAfDH5aSI3EY_YwcGZh9xnDaVlu3rzTXh7PFbWjEuepynneEMYisoZrzpTxovmnb3U1zM9gFTwG3_VSg=="
    }
    # 判断链接类型，主页链接还是视频链接
    link = requests.get(url=link).url
    link_type = re.findall('/share/(.*?)/', link)
    # print(link_type)
    if link_type and link_type[0] == 'video':
        # 链接为视频链接
        # 获取视频的链接中的ID
        logging.info(link)
        video_link_id = re.findall('/video/(.*?)/\?', link)[0]
        response = requests.get(url=f'https://www.douyin.com/video/{video_link_id}', headers=headers)
        render_data = re.findall('id="RENDER_DATA" type="application/json">(.*?)</script>', response.text)[0]
        # print(parse.unquote(render_data))
        # 将JSON字符串转换为Python字典对象
        data = json.loads(parse.unquote(render_data))
        # 删除字典中的第一个键值对
        del data[list(data.keys())[0]]
        video_json = list(data.items())[0][1]
        video_url = "https:" + video_json['aweme']['detail']['video']['playApi']
        if not video_json['aweme']['detail']['video']['playApi']:
            logging.info('该链接为图集，开始解析。。。')
            note_title = video_json['aweme']['detail']['desc']
            image_url_list = []
            for i in range(len(video_json['aweme']['detail']['images'])):
                img_url = video_json['aweme']['detail']['images'][i]['urlList'][0]
                image_url_list.append(img_url)
            return image_url_list
        return [video_url]


    elif link_type and link_type[0] == 'user':
        # 链接为用户主页
        return [link]
        parse_control = input("当前链接为个人主页链接，是否下载个人主页全部视频？按Y键继续，按任意键退出。（Y/n）")
        if parse_control == 'Y' or parse_control == 'y':
            # 获取个人主页链接ID
            user_id = re.findall('share/user/(.*?)\?', link)[0]
            response = requests.get(url=f'https://www.douyin.com/user/{user_id}', headers=headers)
            render_data = re.findall('id="RENDER_DATA" type="application/json">(.*?)</script>', response.text)[0]
            # print(parse.unquote(render_data))
            # 将JSON字符串转换为Python字典对象
            data = json.loads(parse.unquote(render_data))
            # 删除字典中的第一个键值对
            del data[list(data.keys())[0]]
            data = list(data.items())[0][1]
            dl_path = douyin_path + '/' + user_path + '/' + data['user']['user']['nickname']
            if not os.path.exists(dl_path):
                os.mkdir(dl_path)
            for i in range(len(data['post']['data'])):
                video_link = "https:" + data['post']['data'][i]["video"]["playApi"]

                if not data['post']['data'][i]["video"]["playApi"]:
                    print('发现图集，开始解析')
                    note_title = data['post']['data'][i]["desc"]
                    if not os.path.exists(dl_path + '/' + note_title):
                        os.mkdir(dl_path+ '/' + note_title)
                    music_url = data['post']['data'][i]['music']['playUrl']['uri']
                    music = requests.get(music_url, stream=True)
                    file_size = int(music.headers.get("Content-Length"))
                    music_pbar = tqdm(total=file_size)
                    save_file(file_path=dl_path + '/' + note_title + '/' + note_title + '.mp3',
                              video_title=note_title,
                              video=music, video_pbar=music_pbar)
                    image_url_list = []
                    for x in range(len(data['post']['data'][i]['images'])):
                        img_url = data['post']['data'][i]['images'][x]['urlList'][0]
                        image_url_list.append(img_url)
                        image_response = requests.get(url=img_url).content

                        path = dl_path + '/' + note_title + '/' + str(x) + '.jpg'
                        with open(path, 'wb') as f:
                            f.write(image_response)
                            f.close()
                    continue
                video_title = data['post']['data'][i]["desc"]
                video = requests.get(video_link, stream=True)
                file_size = int(video.headers.get("Content-Length"))
                video_pbar = tqdm(total=file_size)
                try:
                    save_file(file_path=dl_path + "/" + f'{video_title}.mp4', video_title=video_title, video=video,video_pbar=video_pbar)
                except:
                    continue


    else:
        logging.info("无法解析此链接")
        return [link]
