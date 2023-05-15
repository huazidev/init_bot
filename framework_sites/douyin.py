import re
import json
import requests
import logging
import random
from urllib import parse


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
