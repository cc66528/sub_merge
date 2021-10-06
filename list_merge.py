import os
import shutil
from pathlib import Path
import time
import json
import yaml
import base64
from urllib.parse import quote
import requests
from requests.adapters import HTTPAdapter



with open('./sub/sub_list.json', 'r', encoding='utf-8') as f:
    raw_list = json.load(f)
sub_list = []
for index in range(len(raw_list)): 
    if raw_list[index]['enabled']:
        sub_list.append(raw_list[index]['url'])

class sub_convert():# 将订阅链接中YAML，Base64等内容转换为 Url 链接内容
    
    def __init__(self,sub_url,output_type):
        self.sub_url = sub_url
        self.output_type = output_type
        self.url_content = ''
    
    def yaml_decode(content): # YAML 转换为 Url 链接内容
        yaml_content = yaml.dump(content)
        return yaml_content
    def base64_decode(content): # Base64 转换为 Url 链接内容
        base64_content = base64.b64decode(content.encode('utf-8')).decode('ascii')
        return base64_content

    def url_encode(self):# 将订阅内容转化为 Url 链接内容

        """ i = 0
        while i < 3:
            try:
                resp = requests.get(self.sub_url, timeout=5)
                sub_content = str(resp.content.decode('utf-8'))# 获取其它编码（utf-8）文本https://developer.huaweicloud.com/hero/thread-69241-1-1.html
            except requests.exceptions.RequestException:
                i += 1 """
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))
        try:
            print('Downloading from:' + self.sub_url + '\n')
            resp = s.get(self.sub_url, timeout=5)
            sub_content = resp.content.decode('utf-8')

            if 'proxies:' in sub_content: # 判断字符串是否在文本中，是，判断为YAML。https://cloud.tencent.com/developer/article/1699719
                self.url_content = sub_convert.yaml_decode(sub_content)
                return self.url_content
            elif '://'  in sub_content: # 同上，是，判断为 Url 链接内容。
                self.url_content = sub_content
                return self.url_content
            else: # 判断 Base64.
                self.url_content = sub_convert.base64_decode(sub_content)
                self.url_content = base64.b64decode(sub_content.encode('utf-8')).decode('ascii')
                return self.url_content

        except requests.exceptions.RequestException as err:
            print(err)
        
    def yaml_encode(url_content):
        
        yaml_content = ''
        return yaml_content
    def base64_encode(url_content):

        base64_content = base64.b64encode(url_content.encode('utf-8')).decode('ascii')
        return base64_content

    def convert(self): # convert Url to YAML or Base64

        if self.output_type == 'YAML':
            return sub_convert.yaml_encode(self.url_content)
        elif self.output_type == 'Base64':
            return sub_convert.base64_encode(self.url_content)


class sub_merge(): # 将转换后的所有 Url 链接内容合并转换 YAML or Base64, ，并输出文件，输入订阅列表。

    def __init__(self,url_list):
        
        self.url_list = url_list

    def merge(self): # 将各自 Url 写入文件，并与内容生成字典

        content_list = []
        for index in range(len(self.url_list)):
            content_list.append(sub_convert(self.url_list[index],'').url_encode())
            file = open('./sub/list/' + str(index) + '.txt', 'w', encoding = 'utf-8')
            file.write(content_list[index])
            file.close
        
        print('Merging nodes...')
        content = ''.join(content_list) # https://python3-cookbook.readthedocs.io/zh_CN/latest/c02/p14_combine_and_concatenate_strings.html

        content_base64 = sub_convert.base64_encode(content)
        content_yaml = sub_convert.yaml_decode(content)
                   
        file = open('./sub/sub_merge.txt', 'w', encoding = 'utf-8')
        file.write(content)
        file.close

        file = open('./sub/sub_merge_base64.txt', 'w', encoding = 'utf-8')
        file.write(content_base64)
        file.close

        file = open('./sub/sub_merge_yaml.txt', 'w', encoding = 'utf-8')
        file.write(content_yaml)
        file.close

run = sub_merge(sub_list).merge()