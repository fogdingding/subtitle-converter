import asyncio
import aiohttp
import random
from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
from .base import Base


class Crawler(Base):
    def __init__(self, thread=4):
        self.config = self.get_config()
        self.connector = self.__change_connector()
        self.data = []
        self.thread = thread

    def __change_socks5_setting(self, city=None):
        setting = {}
        try:
            all_city = self.config['root']['config']['ipvanish']['city']
            if city is None:
                city = random.choice(all_city)
                # 預設台北, 後續測過才提供多選
                # city = 'tpe.socks.ipvanish.com'
                setting['city'] = city
            else:
                setting['city'] = city
        except Exception as err:
            self.raise_error(err=f'爬蟲改變 socks5 設定出現異常 {err}', err_code=1)
        else:
            return setting
        
    def __change_connector(self):
        try:
            ipvanish = self.config['root']['config']['ipvanish']
            accounts = ipvanish['accounts']
            password = ipvanish['password']
            port = ipvanish['port']
            socks5_setting = self.__change_socks5_setting()
            city = socks5_setting['city']
            url = f'socks5://{accounts}:{password}@{city}:{port}'
            connector = ProxyConnector.from_url(url)
        except Exception as err:
            self.raise_error(err=f'爬蟲改變 connector 時出現異常{err}', err_code=1)
        else:
            return connector

    async def __download(self, session, queue) -> None:
        while True:
            try:
                item = queue.get_nowait()
                download_url = item['url']
                filename = item['filename']
                file_path = item['file_path']
                # TODO 製作真正的串流
                async with session.get(url=download_url, allow_redirects=True) as session_res:
                    data = await session_res.read()
                    with open(f"{file_path}/{filename}", 'wb') as f:
                        f.write(data)
            except asyncio.QueueEmpty:
                return
            except Exception as err:
                self.raise_error(err=f'爬蟲下載發生異常 {err}', err_code=4)
            else:
                print(f'{filename} 已經下載完畢')
    
    async def close(self):
        await self.connector.close()

    async def download(self, download_list) -> None:
        try:
            self.connector = self.__change_connector()
            async with aiohttp.ClientSession(connector=self.connector) as session:
                queue = asyncio.Queue()
                for i in download_list:
                    queue.put_nowait(i)

                tasks = []
                for _ in range(self.thread):
                    task = self.__download(session=session, queue=queue)
                    tasks.append(task)
                await asyncio.wait(tasks)
        except Exception as err:
            self.raise_error(err=f'爬蟲下載放入佇列時發生異常 {err}', err_code=1)
    
    async def get(self, url, is_json=False) -> None:
        try:
            self.connector = self.__change_connector()
            flag = True
            while flag:
                async with aiohttp.ClientSession(connector=self.connector) as session:
                    async with session.get(url=url, allow_redirects=True) as session_res:
                        if session_res.status == 200:
                            flag = False
                        if is_json:
                            session_res_data = {}
                            session_res_data = await session_res.json()
                        else:
                            session_res_data = ''
                            session_res_data = await session_res.text()
        except Exception as err:
            self.raise_error(err=f'爬蟲取得網頁資訊時發生異常 {err}', err_code=1)
        else:
            return session_res_data
