import json


class Base:
    def raise_error(self, err, err_code, is_raise=True, is_exit=False):
        '''
        0: deBug專用
        1: 基礎設定異常
        2: 程式碼錯誤異常
        3: 資料庫錯誤異常
        4: 爬蟲過程中異常
        '''
        if is_raise:
            print({
                "錯誤代碼": err_code,
                "錯誤訊息": err,
            })
            if is_exit:
                exit(0)

    def get_config(self):
        try:
            data = None
            with open('./src/lib/config.json', 'r') as f:
                data = json.load(f)
        except Exception as err:
            self.raise_error(err=err, err_code=1)
        else:
            return data
