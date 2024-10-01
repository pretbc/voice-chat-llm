import threading
import numpy as np

from streamlit_webrtc import webrtc_streamer, WebRtcMode


class WebRTCHandler:
    def __init__(self):
        self.lock = threading.Lock()
        self._audio_buffer = []
        self._sample_rate = None
        self.webrtc_ctx = webrtc_streamer(
            key="voice-chat",
            mode=WebRtcMode.SENDONLY,
            audio_frame_callback=self.audio_frame_callback,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": False, "audio": True},
        )

    def audio_frame_callback(self, frame):
        self._sample_rate = 96_000 if frame.sample_rate < 96_000 else frame.sample_rate
        audio = frame.to_ndarray().flatten()
        with self.lock:
            self._audio_buffer.append(audio)
        return frame

    def clear_audio_buffer(self) -> None:
        self._audio_buffer.clear()
        return

    def mute_audio(self, mute: bool) -> None:
        if not mute:
            self.webrtc_ctx.audio_receiver._track.enabled = True
        else:
            self.webrtc_ctx.audio_receiver._track.enabled = False
        return None

    @property
    def is_playing(self):
        return self.webrtc_ctx.state.playing

    @property
    def audio_data(self):
        with self.lock:
            audio_data = np.concatenate(self._audio_buffer)
        return audio_data

    @property
    def sample_rate(self):
        return self._sample_rate
