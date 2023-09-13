import os
import signal
import platform
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import ConnectEvent
from TikTokLive.types import VideoQuality

client = TikTokLiveClient("@parkergetajob")

@client.on("connect")
async def on_connect(_: ConnectEvent):
    """
    Download the livestream video from TikTok directly!
    """
    client.download(
        path="./mp4s/stream.avi",
        duration=None,
        quality=VideoQuality.ORIGIN
    )

def stop_download():
    """
    Stop the download process gracefully based on the platform.
    """
    if platform.system() == "Windows":
        # Windows-specific code
        os.kill(client.ffmpeg.ffmpeg.process.pid, signal.CTRL_BREAK_EVENT)
    else:
        # Unix-like systems (Linux, macOS)
        os.kill(client.ffmpeg.ffmpeg.process.pid, signal.SIGTERM)

    # Print that we stopped
    print("Stopped download!")

if __name__ == '__main__':
    """
    Note: "ffmpeg" MUST be installed on your machine to run this program
    """
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    client.run()
