import asyncio
from argparse import ArgumentParser
from .lib.base import Base
from .app.audio2subtitle import Audio2Subtitle
from .app.video2audio import Video2Audio
from .app.subtitle import Subtitle


async def pack_Audio2Subtitle(ffmpeg_convete_list, filetype):
    # tasks = []
    # for idx, i in enumerate(ffmpeg_convete_list):
    #     locals()['Audio2Subtitle_' + str(idx)] = Audio2Subtitle(filename=i, filetype=filetype)
    #     tasks.append(locals()['Audio2Subtitle_' + str(idx)].main())
    # await asyncio.wait(tasks)

    for idx, i in enumerate(ffmpeg_convete_list):
        print(f'目前進行第{idx + 1}個檔案轉換字幕')
        await Audio2Subtitle(filename=i, filetype=filetype).main()


if __name__ == '__main__':
    # 參數驗證
    parser = ArgumentParser()
    parser.add_argument("--file_path", type=str, default=None)
    parser.add_argument("--filetype", type=str, default=None)
    args = parser.parse_args()
    filename = args.file_path
    filetype = args.filetype
    if filename is None or filetype is None:
        print("請給予指定參數, file_path: 影片絕對路徑, filetype: 影片格式，\n如：python3 -m src.main --file_path /root/project/src/1.mp4 --filetype mp4")
        exit(0)

    # init
    Subtitle = Subtitle()
    Video2Audio = Video2Audio()
    Base = Base()
    config = Base.get_config()

    # convert video
    print('準備開始進行轉換檔案(video -> audio), (音源檔案目前還是mp4，但沒有影像)')
    Video2Audio.convert(file_path=filename)
    path = config['root']['config']['ffmpeg']['file_path']
    segment_filename_list = config['root']['config']['ffmpeg']['segment_filename_list']
    with open(f'{path}/{segment_filename_list}', 'r') as f:
        ffmpeg_convete_list = f.read().splitlines()
    print(f'完成轉換原始檔案，目前已轉換了{len(ffmpeg_convete_list)}個音源檔案')

    # convert subtitle
    print('準備開始進行音源轉字幕，請耐心等候至全部分流完成')
    loop = asyncio.get_event_loop()
    tmp = loop.run_until_complete(pack_Audio2Subtitle(ffmpeg_convete_list=ffmpeg_convete_list, filetype=filetype))
    print('完成所有音源轉字幕任務')

    # merge subtitle
    print('開始合併字幕任務')
    Subtitle.main(segment_filename_list=ffmpeg_convete_list)
    print('完成合併字幕任務')

    
