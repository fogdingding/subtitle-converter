import aeidon
from ..lib.base import Base


class Subtitle(Base):
    def __init__(self) -> None:
        self.config = self.get_config()
        self.subtitle_config = {
            "file_path": self.config['root']['config']['csubtitle']['file_path'],
            "encoding": self.config['root']['config']['subtitle']['encoding'],
            "segment_time": int(self.config['root']['config']['ffmpeg']['segment_time'])
        }

    def merge_subtitles(self, in_filename1, in_filename2, out_filename, times):
        encoding = self.subtitle_config['encoding']
        segment_time = self.subtitle_config['segment_time']
        acc_segment_time = segment_time * times

        # create aeidon project
        project1 = aeidon.Project()
        project2 = aeidon.Project()
        project1.open_main(f"{in_filename1}", encoding)
        project2.open_main(f"{in_filename2}", encoding)

        # setup output format
        out_format = aeidon.files.new(aeidon.formats.WEBVTT, f"{out_filename}", encoding)

        # motify event entries
        for subtitle in project1.subtitles:
            subtitle.main_text = subtitle.main_text.replace('\n', ' ')
            subtitle.ssa.style = 'Top'
        for subtitle in project2.subtitles:
            subtitle.main_text = subtitle.main_text.replace('\n', ' ')
            subtitle.ssa.style = 'Bot'

        project2.shift_positions(None, aeidon.as_seconds(acc_segment_time))
        project1.subtitles.extend(project2.subtitles)
        project1.save_main(out_format)

    def main(self, segment_filename_list):
        path = self.subtitle_config['file_path']
        if len(segment_filename_list) > 1:
            last_file = None
            for idx, item in enumerate(segment_filename_list):
                item = f"{item}.vtt"
                out_filename = 'output.vtt'
                if idx == 0:
                    last_file = item
                    continue
                self.merge_subtitles(
                    in_filename1=f"{path}/{last_file}",
                    in_filename2=f"{path}/{item}",
                    out_filename=f"{path}/{out_filename}",
                    times=int(idx)
                )
                last_file = out_filename
