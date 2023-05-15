import logging
import json
import os
import re
import subprocess
import sys
from urllib import parse
from urllib.parse import urlparse

import requests
from tqdm import tqdm



def geturlpath(url):
    # ParseResult(scheme='https', netloc='blog.xxx.net', path='/yilovexing/article/details/96432467', params='', query='', fragment='')
    all = urlparse(url)
    path = all.path
    return path


def xhs_parse(link):
    """
    小红书解析
    :param link:
    :return:
    """

    link = requests.get(url=link).url
    logging.info(link)
    if 'redirectPath=' in link:
        link = link.split("redirectPath=")[1]
        logging.info(link)
    # 请求头
    headers = {
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/110.0.0.0",
        "cookie": "xhsTrackerId=7388abf6-2408-4e9a-8152-140ea8f5149f; xhsTrackerId.sig=Tpe1NCZ_pwRAXtm5IRfTK4Ie13LAhfn6cYScxV-IalE; a1=1866d900346b66jir33pjqgc03ropmfs02us1uchx10000135053; webId=f13d8bdb8bdc7da43646085bcc45045a; gid=yYKKfj88K082yYKKfj88qJ7S4KDKKV3FqqUV7xCAkS8qFMy8lU6iMy888yq282q8f2Y4S02J; gid.sign=bZspQsILDRcyjFKBcv/QLYXdSyo=; web_session=030037a4c042b15e5c1889508b244ad113e053; xhsTracker=url=noteDetail&xhsshare=WeixinSession; xhsTracker.sig=c7fp5QrY6HcoTDaS9n_cwgdBDxv0VfZzRSSSryslneA; extra_exp_ids=h5_2302011_origin,h5_1208_clt,h5_1130_clt,ios_wx_launch_open_app_exp,h5_video_ui_exp3,wx_launch_open_app_duration_origin,ques_clt2; extra_exp_ids.sig=CUGkGsXOyAfjUIy2Tj7J3xbdMjA_JzhGRdagzqYdnbg; webBuild=1.1.21; xsecappid=xhs-pc-web; websectiga=59d3ef1e60c4aa37a7df3c23467bd46d7f1da0b1918cf335ee7f2e9e52ac04cf; sec_poison_id=1249155d-9e9e-4392-8658-505c74a53135"
    }
    link = parse.unquote(link)
    logging.info(link)
    link = geturlpath(link)
    video_id = re.findall(r'/explore/(\w+)', link)
    if not video_id:
        logging.info('链接解析失败')
        return []
    video_id = video_id[0]
    html_text = requests.get(url='https://www.xiaohongshu.com/discovery/item/'+video_id, headers=headers).text
    response_json = re.findall('window.__INITIAL_STATE__=(.*?)</script>', html_text)[0]
    response_json = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"),
                           response_json)
    # logging.info(response_json)
    response_json = json.loads(response_json)
    note_data = response_json['noteData']
    if not note_data:
        logging.info("no data")
        return []
    urls = []
    if not response_json['noteData']['data']['noteData']['type'] == 'video' and response_json['noteData']['data']['noteData']['type'] == 'normal':
        logging.info('发现小红书图集，正在解析')
        for i in range(len(response_json['noteData']['data']['noteData']['imageList'])):
            image_url = 'https:'+response_json['noteData']['data']['noteData']['imageList'][i]['url']
            urls.append(image_url)
        return urls

    video_title = response_json['noteData']['data']['noteData']['title'] or response_json['noteData']['data']['noteData']['desc']
    video_url = response_json['noteData']['data']['noteData']['video']['url']
    logging.info(video_url)
    urls.append(video_url)
    return urls
