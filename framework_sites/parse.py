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
 
 
def save_file(file_path, video_title, video, video_pbar):
    """
    保存文件
    :param file_path: 保存文件的路径
    :param video_title: 保存文件的名称
    :return:
    """
    with open(file_path, mode='wb') as f:
        for video_chunk in video.iter_content(1024 * 1024):
            f.write(video_chunk)
            video_pbar.set_description(f'正在下载{video_title}视频中。。。')
            video_pbar.update(1024 * 1024)
        video_pbar.set_description(f"{video_title}下载完成")
        video_pbar.close()
 
def geturlpath(url):
    # ParseResult(scheme='https', netloc='blog.xxx.net', path='/yilovexing/article/details/96432467', params='', query='', fragment='')
    all = urlparse(url)
    path = all.path
    return path
 
def bilibili_parse(link):
    """
    bilibili视频解析
    :param link: 链接
    :return:
    """
    # 创建文件夹
    bilibili_path ="bilibili"
    if not os.path.exists(bilibili_path):
        os.mkdir(bilibili_path)
    # 存放未合并的音视频
    bilibili_path_back = bilibili_path+'/back'
    if not os.path.exists(bilibili_path_back):
        os.mkdir(bilibili_path_back)
    # 请求头
    headers = {
        "referer":"https://search.bilibili.com/all?vt=63863998&keyword=%E8%8A%99%E8%95%96%E8%AF%B4&from_source=webtop_search&spm_id_from=333.1007&search_source=3",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": "buvid3=798D045B-044E-B159-D119-CE6F1D65290A26986infoc; b_nut=1676455526; CURRENT_FNVAL=4048; _uuid=D226F248-F6B10-104F9-787F-B381CD10F584D27359infoc; rpdid=|(Y|RJYkRuk0J'uY~YRlllk~; i-wanna-go-back=-1; b_ut=5; nostalgia_conf=-1; buvid4=9CB54975-CAAF-278A-801D-08D9FFA2746827622-023021518-lDPmqXPdj3j/FRGnEFCvXw==; buvid_fp_plain=undefined; header_theme_version=CLOSE; bp_video_offset_235693265=765160041876553700; DedeUserID=3493144259726260; DedeUserID__ckMd5=c6c4e098704df79c; CURRENT_QUALITY=120; home_feed_column=5; fingerprint=fcea116eb68fb1e1b7de3cdf436a86b4; PVID=1; bp_video_offset_3493144259726260=753287450881687600; buvid_fp=fcea116eb68fb1e1b7de3cdf436a86b4; b_lsid=9AAF8E7D_186F347EEB3; SESSDATA=214104d3,1694670823,e9fac*32; bili_jct=d2c3246d6115136ba6617d1597355664; sid=6rql2o0o; innersign=1"
    }
    html_text = requests.get(url=link, headers=headers).text
    response_json = re.findall('window.__playinfo__=(.*?)</script><script>', html_text)[0]
    print(response_json)
    video_url = json.loads(response_json)['data']['dash']['video'][0]['baseUrl']
    audio_url = json.loads(response_json)['data']['dash']['audio'][0]['baseUrl']
    # 视频简介标题
    description_text = parse.unquote(
        re.findall('<script>window.__INITIAL_STATE__=(.*?);\(function\(\)\{var s;', html_text)[0])
    print(description_text)
    description_json = json.loads(description_text)
    video_title = description_json['videoData']['title']
    video = requests.get(url=video_url, headers=headers, stream=True)
    video_file_size = int(video.headers.get("Content-Length"))
    video_pbar = tqdm(total=video_file_size)
    video_path = bilibili_path_back + '/' + video_title + '.mp4'
    print("正在下载视频。。。")
    save_file(file_path=video_path, video_title=video_title,
              video=video, video_pbar=video_pbar)
    audio = requests.get(url=audio_url, headers=headers, stream=True)
    audio_file_size = int(audio.headers.get("Content-Length"))
    audio_pbar = tqdm(total=audio_file_size)
    audio_path = bilibili_path_back + '/' + video_title + '.mp3'
    print("正在下载音频。。。")
    save_file(file_path=audio_path, video_title=video_title,
              video=audio, video_pbar=audio_pbar)
    is_merge = input("是否进行音视频合并？Y/n")
    if is_merge == 'Y' or is_merge == 'y':
        print("正在进行音视频合并。。")
        # 视频文件路径
        video_file = video_path
        # 音频文件路径
        audio_file = audio_path
        # 合并后输出文件路径
        output_file = bilibili_path + '/' + video_title + '.mp4'
        # 使用FFmpeg合并视频和音频
        subprocess.run(["/Users/liulu/ffmpeg/ffmpeg", "-i", video_file, "-i", audio_file, "-c:v", "copy", "-c:a", "copy", output_file])
        print("文件合并结束")
 
def douyin_parse(link):
    """
    抖音链接解析
    :param link: 链接
    :return:
    """
    # 创建文件夹
    douyin_path = "抖音"
    if not os.path.exists(douyin_path):
        os.mkdir(douyin_path)
    video_path = "视频"
    if not os.path.exists(douyin_path + '/' + video_path):
        os.mkdir(douyin_path + '/' + video_path)
    note_path = "图集"
    if not os.path.exists(douyin_path + '/' + note_path):
        os.mkdir(douyin_path + '/' + note_path)
    user_path = "个人主页视频"
    if not os.path.exists(douyin_path + '/' + user_path):
        os.mkdir(douyin_path + '/' + user_path)
 
    # 请求头
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": "ttwid=1%7C5grcQhcCKwqv-Xs9lsffIaLJcUnQcZ4xfprzwayDvQM%7C1676605769%7C255eb8db183847f6fd5f2cacf7d6549d63bf4969d381c3418e35995ac7b6a171; passport_csrf_token=a83047d9ee4fd31aba58f70e304335a0; passport_csrf_token_default=a83047d9ee4fd31aba58f70e304335a0; s_v_web_id=verify_le7zsch1_vrWqCyLv_4vsJ_4Wbu_8f9O_8uaRdVZujUR1; SEARCH_RESULT_LIST_TYPE=%22single%22; download_guide=%223%2F20230224%22; xgplayer_user_id=262468157771; douyin.com; strategyABtestKey=%221677545888.188%22; csrf_session_id=1b878a71d301ca0b9d1107a00a3237b2; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWNsaWVudC1jc3IiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLVxyXG5NSUlCRFRDQnRRSUJBREFuTVFzd0NRWURWUVFHRXdKRFRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxXHJcbllYSmtNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUV3Z21Gc3VDVHZESjZZeE11eVdXTEJUNGtcclxuUUtDSGpBdU9GeTV4Mno5QTFHMG9acTVuaVg0TzVPb2p5SFBVRnZBL0xOSzVaTWJ5bERtWmVhcWcwUnkzbjZBc1xyXG5NQ29HQ1NxR1NJYjNEUUVKRGpFZE1Cc3dHUVlEVlIwUkJCSXdFSUlPZDNkM0xtUnZkWGxwYmk1amIyMHdDZ1lJXHJcbktvWkl6ajBFQXdJRFJ3QXdSQUlnUG1rUzJQNUNBa1FRdU9GbnYraXFMZ0ZWNkxkMlBnQlA4VlZpRXgvNXVyc0NcclxuSUVMMnVuMkIzSjBSOTdUazJ0VjB5RGZsLzBLaFk0TmR1WTkxL0g3Z0h3RFFcclxuLS0tLS1FTkQgQ0VSVElGSUNBVEUgUkVRVUVTVC0tLS0tXHJcbiJ9; VIDEO_FILTER_MEMO_SELECT=%7B%22expireTime%22%3A1678152445204%2C%22type%22%3A1%7D; __ac_nonce=063fd5b3f0054f9ad1de6; __ac_signature=_02B4Z6wo00f011gMORgAAIDBHxoHtvE1a5tYLD2AALYJmzmLAnhJfJGYj6YrdcJ.GqhXaYlXaOHrARLl6HXYMHjHJ5EWjjeLDHp7exvMavnxqmZ1k5C4LKe.PSfjtAe7p4E8d.hBCkppHfice8; home_can_add_dy_2_desktop=%221%22; msToken=_zLGCd1OJcoYpZ-fRniWON1mH0QRLDV7QQDLZykyk-yi8iSN42r6xVyLhsC-yqr8O32mGA5d3TO1dLkHXF-BFdActIDv9RKjVe-yQORkllVOJqEkcJel5Q==; tt_scid=uk9.KTlPKHn.6qP2KcGIDFZUhII2O4vjDjErsTW866.w2Rux9NSFEVtnQ6ia9htH733a; msToken=nY0Gi1G71gNPaoixSC3WbdsEB1sz6dOm4H2crksAfDH5aSI3EY_YwcGZh9xnDaVlu3rzTXh7PFbWjEuepynneEMYisoZrzpTxovmnb3U1zM9gFTwG3_VSg=="
    }
    # 判断链接类型，主页链接还是视频链接
    print(link)
    link_type = re.findall('/share/(.*?)/', link)
    print(link_type)
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
            print('该链接为图集，开始解析。。。')
            note_title = video_json['aweme']['detail']['desc']
            if not os.path.exists(douyin_path + '/' + note_path + '/' + note_title):
                os.mkdir(douyin_path + '/' + note_path + '/' + note_title)
            music_url = video_json['aweme']['detail']['music']['playUrl']['uri']
            music = requests.get(music_url, stream=True)
            file_size = int(music.headers.get("Content-Length"))
            music_pbar = tqdm(total=file_size)
            save_file(file_path=douyin_path + '/' + note_path + '/' + note_title + '/' + note_title + '.mp3', video_title=note_title,
                      video=music, video_pbar=music_pbar)
            image_url_list = []
            for i in range(len(video_json['aweme']['detail']['images'])):
                img_url = video_json['aweme']['detail']['images'][i]['urlList'][0]
                image_url_list.append(img_url)
                image_response = requests.get(url=img_url).content
 
                path = douyin_path + '/' + note_path + '/' + note_title + '/' + str(i) + '.jpg'
                with open(path, 'wb') as f:
                    f.write(image_response)
                    f.close()
            print("下载完毕！")
            return
        video_title = video_json['aweme']['detail']['desc']
        video = requests.get(video_url, stream=True)
        file_size = int(video.headers.get("Content-Length"))
        video_pbar = tqdm(total=file_size)
        # print(video.url)
        try:
            save_file(file_path=douyin_path + '/' + video_path + '/' + video_title + '.mp4', video_title=video_title,
                  video=video, video_pbar=video_pbar)
        except:
            print("下载失败！")
 
 
    elif link_type and link_type[0] == 'user':
        # 链接为用户主页
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
 
def xhs_parse(link):
    """
    小红书解析
    :param link:
    :return:
    """
    # 创建文件夹
    xhs_path = "小红书"
    if not os.path.exists(xhs_path):
        os.mkdir(xhs_path)
    # 请求头
    headers = {
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/110.0.0.0",
        "cookie": "xhsTrackerId=7388abf6-2408-4e9a-8152-140ea8f5149f; xhsTrackerId.sig=Tpe1NCZ_pwRAXtm5IRfTK4Ie13LAhfn6cYScxV-IalE; a1=1866d900346b66jir33pjqgc03ropmfs02us1uchx10000135053; webId=f13d8bdb8bdc7da43646085bcc45045a; gid=yYKKfj88K082yYKKfj88qJ7S4KDKKV3FqqUV7xCAkS8qFMy8lU6iMy888yq282q8f2Y4S02J; gid.sign=bZspQsILDRcyjFKBcv/QLYXdSyo=; web_session=030037a4c042b15e5c1889508b244ad113e053; xhsTracker=url=noteDetail&xhsshare=WeixinSession; xhsTracker.sig=c7fp5QrY6HcoTDaS9n_cwgdBDxv0VfZzRSSSryslneA; extra_exp_ids=h5_2302011_origin,h5_1208_clt,h5_1130_clt,ios_wx_launch_open_app_exp,h5_video_ui_exp3,wx_launch_open_app_duration_origin,ques_clt2; extra_exp_ids.sig=CUGkGsXOyAfjUIy2Tj7J3xbdMjA_JzhGRdagzqYdnbg; webBuild=1.1.21; xsecappid=xhs-pc-web; websectiga=59d3ef1e60c4aa37a7df3c23467bd46d7f1da0b1918cf335ee7f2e9e52ac04cf; sec_poison_id=1249155d-9e9e-4392-8658-505c74a53135"
    }
    link = parse.unquote(link)
    link = geturlpath(link)
    video_id = re.findall(r'/explore/(\w+)', link)
    if not video_id:
        print('链接解析失败')
        return
    video_id = video_id[0]
    html_text = requests.get(url='https://www.xiaohongshu.com/discovery/item/'+video_id, headers=headers).text
    response_json = re.findall('window.__INITIAL_STATE__=(.*?)</script>', html_text)[0]
    response_json = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"),
                              response_json)
    print(response_json)
    response_json = json.loads(response_json)
    if not response_json['noteData']['data']['noteData']['type'] == 'video' and response_json['noteData']['data']['noteData']['type'] == 'normal':
        print('发现小红书图集，正在解析')
        # print(response_json)
        note_title = response_json['noteData']['data']['noteData']['title'] or response_json['noteData']['data']['noteData']['desc']
        if not os.path.exists(xhs_path+'/'+note_title):
            os.mkdir(xhs_path+'/'+note_title)
        for i in range(len(response_json['noteData']['data']['noteData']['imageList'])):
            image_url = 'https:'+response_json['noteData']['data']['noteData']['imageList'][i]['url']
 
            image_response = requests.get(url=image_url).content
            with open(xhs_path+'/'+note_title+'/'+str(i)+'.jpg', "wb") as f:
                f.write(image_response)
                f.close()
 
        return
 
    video_title = response_json['noteData']['data']['noteData']['title'] or response_json['noteData']['data']['noteData']['desc']
    video_url = response_json['noteData']['data']['noteData']['video']['url']
    video = requests.get(url=video_url, headers=headers, stream=True)
    video_file_size = int(video.headers.get("Content-Length"))
    video_pbar = tqdm(total=video_file_size)
    video_path = xhs_path + '/' + video_title + '.mp4'
    print("正在下载视频。。。")
    save_file(file_path=video_path, video_title=video_title,
              video=video, video_pbar=video_pbar)
 
 
 
 
 
 
if __name__ == '__main__':
    print('=====================================================')
    print('***************** 视频爬虫工具 ***********************')
    print('=====================================================')
    headers = {
        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
    }
    while True:
        # 输入解析链接
        linkInput = input('请输入解析链接：')
        # 对解析的链接进行提取
        link = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', linkInput)
        # 判断链接是否存在
        if not link:
            print("未找到有效链接,请重新输入!")
            continue
        link = link[0]
        print(link)
        # 对链接进行请求，查看是否有重定向
 
        if 'www.xiaohongshu.com' in link:
            link = link
        else:
            link = requests.get(url=link).url
        # bilibili
        if "www.bilibili.com" in link:
            bilibili_parse(link)
        elif 'douyin.com' in link or 'www.iesdouyin.com' in link:
            douyin_parse(link)
        elif 'www.xiaohongshu.com' in link:
            xhs_parse(link)
        else:
            print("暂时无法解析此链接")
