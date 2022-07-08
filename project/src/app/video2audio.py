import ffmpeg
from ..lib.base import Base


class Video2Audio(Base):
    def __init__(self) -> None:
        self.config = self.get_config()
        self.videos_config = {
            "file_path": self.config['root']['config']['ffmpeg']['file_path'],
            "is_quiet": self.config['root']['config']['ffmpeg']['is_quiet'],
            "segment_time": str(self.config['root']['config']['ffmpeg']['segment_time']),
            "segment_filename_list": self.config['root']['config']['ffmpeg']['segment_filename_list']
        }
    
    def convert(self, file_path) -> dict:
        path = self.videos_config['file_path']
        is_quiet = self.videos_config['is_quiet']
        segment_time = self.videos_config['segment_time']
        segment_filename_list = self.videos_config['segment_filename_list']
        
        out, err = (
            ffmpeg
            .input(file_path)
            .output(
                f'{path}/output%03d.mp4',
                vn=None,
                f='segment',
                acodec='copy',
                segment_time=segment_time,
                segment_start_number='1',
                segment_list=f'{path}/{segment_filename_list}',
                individual_header_trailer='1',
                break_non_keyframes='1',
                reset_timestamps='1',
            ).run(quiet=is_quiet, overwrite_output=True)
        )
        return {
            "out": out,
            "err": err,
        }
