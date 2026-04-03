import yt_dlp
import threading
import os
import re

class DownloaderEngine:
    def __init__(self, progress_callback, completion_callback, error_callback):
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
        self.error_callback = error_callback

    def ytdlp_hook(self, d):
        if d['status'] == 'downloading':
            # Extract percentage safely
            percent_str = d.get('_percent_str', '0.0%').replace('%', '').strip()
            try:
                # Remove ANSI color codes that yt-dlp might output
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                percent_str = ansi_escape.sub('', percent_str)
                percent = float(percent_str)
                self.progress_callback(percent)
            except Exception:
                pass
        elif d['status'] == 'finished':
            self.progress_callback(100.0)
    
    def download_in_thread(self, url, format_type, file_ext, save_path):
        def _download():
            try:
                # Setup yt_dlp options
                ydl_opts = {
                    'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [self.ytdlp_hook],
                    'quiet': True,
                    'no_warnings': True,
                }
                
                if format_type == 'Audio':
                    ydl_opts['format'] = 'bestaudio/best'
                    if file_ext != 'Best (Auto)':
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': file_ext.lower(),
                            'preferredquality': '192',
                        }]
                else:
                    if file_ext == 'Best (Auto)':
                        ydl_opts['format'] = 'best'
                    else:
                        extStr = file_ext.lower()
                        ydl_opts['format'] = f'bestvideo[ext={extStr}]+bestaudio/best[ext={extStr}]'
                        ydl_opts['merge_output_format'] = extStr
                    
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                self.completion_callback()
            except Exception as e:
                self.error_callback(str(e))
                
        # Start the background thread
        thread = threading.Thread(target=_download)
        thread.start()
