from datetime import datetime, timedelta
from typing import List, Tuple

from api.tools.utils import frames_diff, get_time, get_mask

TIME_MASK = "%H:%M:%S,%f"

class Handler(object):
    def __init__(self):
        self.end = False
        self.video_info = {}

        self.texts = []
        self.times = []
        self.current_frame = None
        self.current_text = None

    def start(self, video_path: str):
        reader = None # VideoReader(video_path, batch_size=32, buffer_size=1024)
        self.video_info = reader.info
        self.video_info['current_frame'] = 0
        # Using Tesseracts wrapper
        with PyTessBaseAPI(path=r'C:\Users\n.shamankov\AppData\Local\Programs\Tesseract-OCR\tessdata') as api:
            while True:
                flag, frames = reader.get()
                self.end = not flag
                if not flag:
                    break
                texts, times = self.__handle(frames, api)  # Obtaining new data from image by tesserOcr
                self.texts += texts
                self.times += times

    @staticmethod
    def __check_text_seq(texts, times):  # Get optimal text /cod block
        def get_optimal_text(subseq_texts, subseq_times):
            counter = {}
            for i in range(len(subseq_texts)):
                if subseq_texts[i] not in counter:
                    counter[subseq_texts[i]] = 0
                counter[subseq_texts[i]] += subseq_times[i]
            return max(counter, key=counter.get)


        texts_neighborhood, times_len_neighborhood = [], []
        start_time_neighborhood, end_time_neighborhood = times[0][0], times[0][1]
        result_texts, result_times = [], []
        for i in range(len(texts)):
            flag_passed = True
            for text in texts_neighborhood:
                dist = Levenshtein.distance(texts[i], text)
                if dist > 10:
                    flag_passed = False
                    break
            if flag_passed:
                texts_neighborhood.append(texts[i])
                times_len_neighborhood.append(
                    (
                            datetime.strptime(times[i][1], TIME_MASK) - datetime.strptime(times[i][0], TIME_MASK)
                    ).total_seconds()
                )
                end_time_neighborhood = times[i][1]
            else:
                result_texts.append(get_optimal_text(texts_neighborhood, times_len_neighborhood))
                result_times.append((start_time_neighborhood, end_time_neighborhood))
                texts_neighborhood, times_len_neighborhood = [], []
                start_time_neighborhood, end_time_neighborhood = times[i][0], times[i][1]

        return result_texts, result_times

    # get result text from samples
    def __merge_result(self):
        def cut_time(time):
            time_split = time.split(',')
            time_split[-1] = time_split[-1][:3]
            return ','.join(time_split)
        texts, times = self.texts, self.times
        it = 0
        result_texts, result_times = [], []
        for i in range(1, len(texts)):
            if texts[it] != texts[i]:
                text = texts[it]
                if text != '':
                    start_time, end_time = times[it] / 1000, times[i - 1] / 1000
                    start_time, end_time = datetime.fromtimestamp(start_time), datetime.fromtimestamp(end_time)
                    start_time, end_time = start_time - timedelta(hours=3), end_time - timedelta(hours=3)
                    start_time, end_time = start_time.strftime(TIME_MASK), end_time.strftime(TIME_MASK)
                    start_time, end_time = cut_time(start_time), cut_time(end_time)
                    result_texts.append(text)
                    result_times.append((start_time, end_time))
                it = i
        result_texts, result_times = Handler.__check_text_seq(result_texts, result_times)
        return '\n'.join([
            f'{i + 1}\n{result_times[i][0]} --> {result_times[i][1]}\n{result_texts[i]}'
            for i in range(len(result_texts))
        ])

    def get_result(self):
        return self.__merge_result()

    def get_status(self):
        return '', self.video_info['current_frame'], self.video_info['num_frames']

    def __handle(self, frames: List, api) -> Tuple:

        batch_times = [
            get_time(self.video_info['current_frame'] + i, self.video_info['fps']) for i in range(len(frames))
        ]

        texts, times = [], []
        for i in range(0, len(frames), 5):
            frame = frames[i]
            if self.current_frame is None:
                self.current_frame = frame
                diff = float('inf')
                mask = get_mask(frame)
            else:
                current_mask, mask = get_mask(self.current_frame), get_mask(frame)
                diff = frames_diff(np.array(current_mask), np.array(mask))
            if diff > 3000:
                self.current_frame = frame
                api.SetImage(mask)  # capture the image and then get text
                text = api.GetUTF8Text()
                self.current_text = text
            texts.append(self.current_text)
            times.append(batch_times[i])

        self.video_info['current_frame'] += len(frames)

        return texts, times
