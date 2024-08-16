from flask import Flask, render_template, request , send_file
import threading,webbrowser
import time
import os
import shutil
from zipfile import ZipFile
import requests
import subprocess




# flaskアプリの明示
templates_path = "templates/"
static_path = "static/"
app = Flask(__name__ , template_folder=templates_path, static_folder=static_path)



def read_html_file_to_string(html_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_string = file.read()
    return html_string


# パスの定義
media_path = static_path + "media/"
txt_folder = media_path + "txt/"
txt_from_audio_path = txt_folder + "audio.txt"
input_audio_folder = media_path + "in_audio/"
ouput_audio_folder = media_path + "audio/" 
ouput_video_folder = media_path + "video/"
ffmpeg_path = media_path + "tool/ffmpeg_win"
yt_dlp_path = media_path + "tool/yt-dlp"
input_video_folder = media_path + "in_video/"
input_video_path = input_video_folder + "input.mp4"
output_csv_path_from_static = "/csv/scraping.csv"
output_csv_path = static_path + output_csv_path_from_static



@app.route('/', methods=['GET', 'POST'])
def dlc_video_page():
    if request.method == 'POST':
        video_url = request.form['video_url']
        video_url_list = [url.strip() for url in video_url.split('\n')]
        video_url_list = [url for url in video_url_list if "https://" in url]  # 文字列"https://"が含まれている要素だけを残す
        print(video_url_list)

        video_file_path_list = []
        for index, video_url in enumerate(video_url_list):     
            # 動画のmp4を取得
            video_file_path = ouput_video_folder + str(index) + ".mp4"

            # Web上からyt-dlpをダウンロードしなおす
            url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
            if os.path.exists(yt_dlp_path):
                os.remove(yt_dlp_path)
            time.sleep(1)
            urlData = requests.get(url).content
            with open(yt_dlp_path , mode='wb') as f:
                f.write(urlData)
            time.sleep(1)
            
            # yt-dlpを実行
            subprocess.run(["chmod" , "+x , yt_dlp_path])
            subprocess.run([yt_dlp_path , "-o" , video_file_path , video_url])
            
            video_file_path_list.append(video_file_path)
            
        return render_template(
            "dlc_video.html" ,
            video_file_path_list = video_file_path_list ,
            video_url_list = video_url_list ,
        )
    
    # 動画フォルダの中を空にする（削除自体が数秒時間がかかるのでページ開いた直後に実行すべき）
    video_folder = media_path + "video/"
    shutil.rmtree(video_folder)  # フォルダごと削除
    os.makedirs(video_folder)

    video_file_path_list = []
    return render_template(
        "dlc_video.html" ,
        video_file_path_list = video_file_path_list ,
    )


@app.route('/csv_download')
def csv_download():
    directory = os.path.join(app.root_path, 'files') 
    return send_file(os.path.join(directory, output_csv_path), as_attachment=True)


@app.route('/download/<id>')
def download(id):
    directory = os.path.join(app.root_path, 'files')
    video_file_path = ouput_video_folder + str(id) + ".mp4"
    return send_file(os.path.join(directory, video_file_path), as_attachment=True)

@app.route('/all_download')
def all_download():
    video_files = [os.path.join(media_path, 'video', filename) for filename in os.listdir(os.path.join(media_path, 'video'))]
    zip_file_path = os.path.join(media_path, 'video', 'all_videos.zip')
    with ZipFile(zip_file_path, 'w') as zipf:
        for video_file_path in video_files:
            if os.path.isfile(video_file_path):
                zipf.write(video_file_path, os.path.basename(video_file_path))
    return send_file(zip_file_path, as_attachment=True)


"""
https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp
"""

if __name__ == "__main__":
    port_number = 6487
    app.run(port = port_number , debug=False)

        



