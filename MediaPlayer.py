import os, platform

# 設置VLC庫路徑，需在import vlc之前
os.environ['PYTHON_VLC_MODULE_PATH'] = "./vlc_player"

import vlc

class Player:
    '''
        args:設置 options
    '''

    def __init__(self, *args):
        if args:
            instance = vlc.Instance(*args)
            self.media = instance.media_player_new()
        else:
            self.media = vlc.MediaPlayer()

    # 設置待播放的url地址或本地文件路徑，每次調用都會重新加載資源
    def set_uri(self, uri):
        self.media.set_mrl(uri)

    # 播放 成功返回0，失敗返回-1
    def play(self, path=None):
        if path:
            self.set_uri(path)
            return self.media.play()
        else:
            return self.media.play()

    # 暫停
    def pause(self):
        self.media.pause()

    # 恢復
    def resume(self):
        self.media.set_pause(0)

    # 停止
    def stop(self):
        self.media.stop()

    # 釋放資源
    def release(self):
        return self.media.release()

    # 是否正在播放
    def is_playing(self):
        return self.media.is_playing()

    # 已播放時間，返回毫秒值
    def get_time(self):
        return self.media.get_time()

    # 拖動指定的毫秒值處播放。成功返回0，失敗返回-1 (需要注意，只有當前多媒體格式或流媒體協議支持纔會生效)
    def set_time(self, ms):
        return self.media.get_time()

    # 音視頻總長度，返回毫秒值
    def get_length(self):
        return self.media.get_length()

    # 獲取當前音量（0~100）
    def get_volume(self):
        return self.media.audio_get_volume()

    # 設置音量（0~100）
    def set_volume(self, volume):
        return self.media.audio_set_volume(volume)

    # 返回當前狀態：正在播放；暫停中；其他
    def get_state(self):
        state = self.media.get_state()
        if state == vlc.State.Playing:
            return 1
        elif state == vlc.State.Paused:
            return 0
        else:
            return -1

    # 當前播放進度情況。返回0.0~1.0之間的浮點數
    def get_position(self):
        return self.media.get_position()

    # 拖動當前進度，傳入0.0~1.0之間的浮點數(需要注意，只有當前多媒體格式或流媒體協議支持纔會生效)
    def set_position(self, float_val):
        return self.media.set_position(float_val)

    # 獲取當前文件播放速率
    def get_rate(self):
        return self.media.get_rate()

    # 設置播放速率（如：1.2，表示加速1.2倍播放）
    def set_rate(self, rate):
        return self.media.set_rate(rate)

    # 設置寬高比率（如"16:9","4:3"）
    def set_ratio(self, ratio):
        self.media.video_set_scale(0)  # 必須設置爲0，否則無法修改屏幕寬高
        self.media.video_set_aspect_ratio(ratio)

    # 設置窗口句柄
    def set_window(self, wm_id):
        if platform.system() == 'Windows':
            self.media.set_hwnd(wm_id)
        else:
            self.media.set_xwindow(wm_id)

    # 註冊監聽器
    def add_callback(self, event_type, callback):
        self.media.event_manager().event_attach(event_type, callback)

    # 移除監聽器
    def remove_callback(self, event_type, callback):
        self.media.event_manager().event_detach(event_type, callback)