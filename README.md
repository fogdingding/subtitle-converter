## subtitle
透過付費 proxy [ipvanish](https://www.ipvanish.com/) 和 [＊＊＊]() 的免費額度進行影音文字轉字幕。


## 前置動作
* 已安裝docker

```bash
cd docker
docker-compose build
docker-compose up -d
```

## 使用方法
* 需要輸入 `影片路徑` 和 `檔案格式`
```bash
# 進入 docker container
docker ps
docker exec -it <container_id> bash
# 在 /root/project 路徑
python3 -m src.main --file_path /root/project/src/1.mp4 --filetype mp4
```