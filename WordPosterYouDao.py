import datetime
import glob
import json
import os
import shutil
import time
import urllib

import requests


class WordPosterYouDao:
    def __init__(self, file_prefix, ):
        self.file_prefix = os.path.splitext(os.path.basename(file_prefix))[0]
        # 绝对路径
        self.a_file_path = os.path.join(os.getcwd(), 'words', 'log', self.file_prefix) + '_.txt'
        self.b_file_path = os.path.join(os.getcwd(), 'words', 'unfinished', self.file_prefix) + '.txt'
        self.log_file_path = os.path.join(os.getcwd(), 'words', 'log', self.file_prefix) + '.log'
        self.line_num = 0

    def log_to_file_and_console(self, message):
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ': ' + message)
        with open(self.log_file_path, 'a+', encoding='utf-8') as log_file:
            log_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ': ' + message + '\n')

    def replace_fran(self, string):
        fr_en = [['é', 'e'], ['ê', 'e'], ['è', 'e'], ['ë', 'e'], ['à', 'a'], ['â', 'a'], ['ç', 'c'], ['î', 'i'],
                 ['ï', 'i'],
                 ['ô', 'o'], ['ù', 'u'], ['û', 'u'], ['ü', 'u'], ['ÿ', 'y']
                 ]
        for i in fr_en:
            string = string.replace(i[0], i[1])
        return string

    def post_json_to_url(self, url, data):
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        proxy = {"http": None, "https": None}
        try:
            response = requests.post(url, data=data, headers=headers, proxies=proxy)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            self.log_to_file_and_console(f"POST request failed: {e}")
            return None

    # 移动文件
    def move_file(self):
        # 确定目标目录
        target_directory = os.path.join(os.getcwd(), 'words', 'finished')

        # 如果目标目录不存在，则创建它
        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
            except OSError as error:
                self.log_to_file_and_console(f"Error: 创建目标目录 {target_directory} 失败。{error}")
                return  # 退出函数

        # 构建要移动的文件列表
        files_to_move = glob.glob(self.b_file_path)

        # 移动文件
        for file_path in files_to_move:
            try:
                # 目标文件路径
                target_file_path = os.path.join(target_directory, os.path.basename(file_path))
                # 移动文件
                shutil.move(file_path, target_file_path)
                self.log_to_file_and_console(f"文件 {file_path} 已成功移动到 {target_directory}")
            except (IOError, OSError) as e:
                self.log_to_file_and_console(f"Error: 移动文件 {file_path} 失败。{e}")

    def read_words_and_post(self, post_url):
        if not os.path.isfile(self.b_file_path):
            self.log_to_file_and_console(f"Error: File {self.b_file_path} does not exist.")
            return None
        # 存在文件
        if not os.path.isfile(self.a_file_path):
            with open(self.a_file_path, 'w', encoding='utf-8') as a_file:
                a_file.write('0')
        # 读取起始行号
        with open(self.a_file_path, 'r') as a_file:
            self.line_num = int(a_file.readline().strip())

        words = []
        b_can_move = False
        with open(self.b_file_path, 'r', encoding='utf-8') as b_file:
            lines = b_file.readlines()
            A_NUM = self.line_num
            BATCH_SIZE = 10
            # 确保开始行号不大于文件总行数
            if self.line_num <= len(lines):
                # 从第start_line_number行开始读取
                for i in range(0, len(lines[A_NUM:]), BATCH_SIZE):
                    batch_lines = lines[A_NUM:][i:i + BATCH_SIZE]
                    batch_words = [line.strip() for line in batch_lines if len(line.strip()) > 0 and '#' not in line]
                    # words.extend([self.replace_fran(line) for line in batch_lines])
                    words.extend(batch_words)
                    self.log_to_file_and_console(f"Starting to send words from line {self.line_num + 1}.")
                    data = urllib.parse.quote('{"wordlist":[' + ','.join(words) + ']}')
                    # gg = json.loads(data)
                    # 重试POST请求最多3次
                    b_success = False
                    for attempt in range(100):
                        time.sleep(5)
                        response = self.post_json_to_url(post_url, data)
                        if response is not None:
                            body = response.get('result', {})
                            code = body.get('code', 0)
                            if code == 0:
                                # 更新起始行号
                                self.line_num += len(batch_lines)
                                with open(self.a_file_path, 'w', encoding='utf-8') as a_file:
                                    a_file.write(str(self.line_num))
                                b_success = True
                                words.clear()
                                self.log_to_file_and_console(
                                    f"该文件 {self.file_prefix} 成功: {self.line_num} /{len(lines)}行")
                                break  # 请求成功，跳出重试循环
                            else:
                                self.log_to_file_and_console(f"POST response with non-zero code: {body}")
                                time.sleep(5)  # 休眠10秒后再重试
                        else:
                            self.log_to_file_and_console(f"POST request failed (attempt: {attempt + 1}次).")
                            time.sleep(5)  # 休眠10秒后再重试
                    if not b_success:
                        # 失败则退出
                        self.log_to_file_and_console(
                            f"program exit,max tried {attempt + 1}times from start num: {self.line_num + 1} to end num: {self.line_num + 10 + 1}.")
                        return
            # 处理完的文件挪到finished文件夹
            self.log_to_file_and_console("文件处理完成，准备挪到finished文件夹.")
            b_can_move = True
        b_can_move = True
        self.log_to_file_and_console(f"file line {len(lines)} is less than {self.line_num}.")
        if b_can_move:
            self.move_file()

# 示例使用场景
if __name__ == "__main__":
    post_url = "https://tcb-df22zhkzi34p4nm-4cvje34891ec.service.tcloudbase.com/add_update_words_youdao"  # 替换为实际的URL
    word_poster = WordPosterYouDao("all.txt")
    word_poster.read_words_and_post(post_url)
