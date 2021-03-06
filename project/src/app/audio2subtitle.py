import re
import asyncio
from ..lib.base import Base
from ..lib.crawler import Crawler
from .tusclient import client


class Audio2Subtitle(Base):
    def __init__(self, filename, filetype):
        self.Crawler = Crawler()
        self.config = self.get_config()
        self.crawler_config = {
            "filename": filename,
            "video_file_path": f"{self.config['root']['config']['ffmpeg']['file_path']}",
            "subtitle_file_path": f"{self.config['root']['config']['csubtitle']['file_path']}",
            "filetype": filetype,
            "csub_subtitle_url": self.config['root']['url']['csubtitle']['text'],
            "csub_upload_url": self.config['root']['url']['csubtitle']['upload_file'],
            "csub_rstatus_file": self.config['root']['url']['csubtitle']['rstatus_file'],
            "csub_download_file": self.config['root']['url']['csubtitle']['download_file'],
            "all_type": self.config['root']['config']['csubtitle']['file_format'],
            "ip": '',
            "uidvalue": '',
            "filenumvalue": '1',
            "languageoption": 'language=zh-TW',
            "keycode": "keycode=none",
            "opt": "opt=text",
            "filedeep": '',
            "umiscoption": "[none]",
        }
        self.crawler_config['filedeep'] = f"{self.crawler_config['languageoption']}|{self.crawler_config['keycode']}|{self.crawler_config['opt']}"
    
    def __parser_csubtitle(self, res_text) -> None:
        try:
            re_uidvalue = re.search('var uidvalue = ".[a-zA-Z0-9]{0,64}";', res_text)
            if re_uidvalue is not None:
                uidvalue = re.search('[0-9a-zA-Z]{32,36}', re_uidvalue.group(0))
                uidvalue = uidvalue.group(0) if uidvalue is not None else ''
                self.crawler_config['uidvalue'] = uidvalue
            re_ip = re.search(r'var ip = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}";', res_text)
            if re_ip is not None:
                ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', re_ip.group(0))
                ip = ip.group(0) if ip is not None else ''
                self.crawler_config['ip'] = ip
            if self.crawler_config['uidvalue'] == '' or self.crawler_config['ip'] == '':
                self.raise_error(err=f"?????? CSUB ???????????? ip or uidvalue", err_code=4)
        except Exception as err:
            self.raise_error(err=f"?????? CSUB ???????????????????????? {err}", err_code=2)

    async def get_csubtitle(self):
        try:
            url = self.crawler_config['csub_subtitle_url']
            res_text = await self.Crawler.get(url=url)
            self.__parser_csubtitle(res_text)
        except Exception as err:
            self.raise_error(err=f"?????? CSUB ??????????????????????????? {err}", err_code=4)
        else:
            return res_text
    
    def upload_file(self):
        try:
            url = self.crawler_config['csub_upload_url']
            filename = self.crawler_config['filename']
            video_file_path = self.crawler_config['video_file_path']
            metadata = {
                'filename': self.crawler_config['filename'],
                'filetype': self.crawler_config['filetype'],
                'uid': self.crawler_config['uidvalue'],
                'filenum': self.crawler_config['filenumvalue'],
                'deep': self.crawler_config['filedeep'],
                'ip': self.crawler_config['ip'],
                'miscoption': self.crawler_config['umiscoption']
            }
            tus_client = client.TusClient(url=url)
            # print(url, metadata)
            with open(f"{video_file_path}/{filename}", 'rb') as f:
                uploader = tus_client.uploader(file_stream=f, metadata=metadata)
                uploader.upload()
        except Exception as err:
            self.raise_error(err=f"??????????????? CSUB ????????????????????? {err}", err_code=4)
    
    async def check_upload_file(self):
        try:
            url = self.crawler_config['csub_rstatus_file']
            uidvalue = self.crawler_config['uidvalue']
            data = {
                "file_id": None,
                "msg": '',
            }
            flag = True
            while flag:
                session_res_json = await self.Crawler.get(f'{url}{uidvalue}', is_json=True)
                if session_res_json is None:
                    continue
                if 'msg' in session_res_json:
                    flag = False
                    data['msg'] = session_res_json['msg']
                    print(data['msg'])
                    if data['msg'].find('????????????') != -1:
                        data['file_id'] = session_res_json['finalfile']
                    if data['msg'].find('?????????????????????????????????????????????') != -1:
                        data['file_id'] = -1
                    if data['msg'].find('????????????????????????') != -1:
                        data['file_id'] = -2
        except Exception as err:
            self.raise_error(err=f"???????????????????????????????????? {err}", err_code=4)
        else:
            return data

    async def main(self):
        try:
            # ????????????????????????
            print('????????????????????????...')
            await self.get_csubtitle()
            csub_download_file = self.crawler_config['csub_download_file']
            all_type = self.crawler_config['all_type']
            
            # ????????????????????????????????????TODO ???????????????session
            print('???????????????...')
            self.upload_file()
            upload_flag = True
            print('???????????????...')
            while upload_flag:
                check_file_status = await self.check_upload_file()
                if check_file_status['file_id'] is not None:
                    if check_file_status['file_id'] == -1:
                        upload_flag = False
                        print('???????????????????????????')
                        continue
                    if check_file_status['file_id'] == -2:
                        await self.get_csubtitle()
                        print(f"????????????????????????????????????????????????IP???{self.crawler_config['ip']}")
                        self.upload_file()
                        upload_flag = True
                        print('?????????????????????...')
                        continue
                    upload_flag = False
                await asyncio.sleep(5)
            
            print('??????????????????...')
            # ?????????????????????????????????
            if check_file_status['file_id'] is not False:    
                download_list = []
                filename = self.crawler_config['filename']
                subtitle_file_path = self.crawler_config['subtitle_file_path']
                for out_type in all_type:
                    download_list.append({
                        "url": f"{csub_download_file}id={check_file_status['file_id']}&ext={out_type}",
                        "file_path": subtitle_file_path,
                        "filename": f"{filename}.{out_type}",
                    })
            
                # ????????????
                await self.Crawler.download(download_list=download_list)
            
            # ????????????
            print('??????????????????...')
            await self.Crawler.close()
        except Exception as err:
            self.raise_error(err=f"????????????????????? {err}", err_code=2)
        else:
            return {
                'config': self.crawler_config,
            }
