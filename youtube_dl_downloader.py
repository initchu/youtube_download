import os
import sys
import yt_dlp  # yt-dlp 是维护活跃且功能强大的 YouTube 下载库
import threading
import time
from yt_dlp.utils import DownloadError

# 进度条回调函数

def progress_hook(d):
    if d['status'] == 'downloading':
        # 计算百分比
        percent = d.get('_percent_str', '').strip()
        speed = d.get('_speed_str', '').strip()
        eta = d.get('_eta_str', '').strip()
        print(f"\r进度: {percent} 速度: {speed} 剩余时间: {eta}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\n下载完成！")

# 获取视频信息

def get_video_info(url):
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except DownloadError as e:
            print(f"获取视频信息失败: {e}")
            return None
        except Exception as e:
            print(f"发生未知错误: {e}")
            return None

# 显示视频信息

def print_video_info(info):
    print(f"标题: {info.get('title')}")
    print(f"时长: {int(info.get('duration', 0))//60} 分钟 {int(info.get('duration', 0))%60} 秒")
    print("可用格式:")
    formats = info.get('formats', [])
    format_list = []
    # 首先添加自动合并选项
    print("[0] 自动合并最佳视频和音频（推荐，需本地有 ffmpeg）")
    format_list.append({'format_id': 'bestvideo+bestaudio', 'desc': '自动合并最佳视频和音频'})
    for idx, f in enumerate(formats, start=1):
        # 只显示有分辨率的视频或音频
        if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
            desc = f"[{idx}] {f.get('ext')} {f.get('format_note', '')} {f.get('resolution', '')} {f.get('abr', '')}kbps"
            print(desc)
            format_list.append(f)
    return format_list

# 下载视频/音频

def download_video(url, format_id, output_path):
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # 支持中文路径和标题
        'progress_hooks': [progress_hook],
        'noplaylist': True,
        'continuedl': True,  # 断点续传
        'retries': 10,
        'fragment_retries': 10,
        'consoletitle': False,
        'encoding': 'utf-8',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except DownloadError as e:
        print(f"下载失败: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

# 命令行主流程

def main():
    print("欢迎使用 YouTube 视频下载器！by Chuchengzhi\n仅供下载有权限的视频。\n")
    url = input("请输入 YouTube 视频 URL: ").strip()
    if not url:
        print("URL 不能为空！")
        return
    info = get_video_info(url)
    if not info:
        return
    formats = print_video_info(info)
    if not formats:
        print("未找到可用格式！")
        return
    idx = input("请选择要下载的格式编号（0 为自动合并最佳视频和音频）: ").strip()
    try:
        idx = int(idx)
        format_id = formats[idx]['format_id']
    except (ValueError, IndexError):
        print("格式编号无效！")
        return
    output_path = input("请输入保存路径（留空为当前目录）: ").strip()
    if not output_path:
        output_path = os.getcwd()
    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path)
        except Exception as e:
            print(f"创建目录失败: {e}")
            return
    print("开始下载...")
    download_video(url, format_id, output_path)

if __name__ == '__main__':
    main() 