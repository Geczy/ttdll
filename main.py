import os
import signal
import platform
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import ConnectEvent, DisconnectEvent
from TikTokLive.types import VideoQuality
import datetime

client = TikTokLiveClient("@parkergetajob")

# Flag to track if we are waiting for the user to go online
waiting_for_online = True

@client.on("connect")
async def on_connect(_: ConnectEvent):
    global waiting_for_online
    print("Connected to Room ID:", client.room_id)

    # Check if we were waiting for the user to go online
    if waiting_for_online:
        waiting_for_online = False
        print("User is now online. Starting recording...")
        start_recording()

@client.on("disconnect")
async def on_disconnect(event: DisconnectEvent):
    global waiting_for_online
    print("Disconnected. Going back into waiting mode.")
    waiting_for_online = True

def start_recording():
    # Define the folder for user recordings
    user_folder = f"./recordings/{client.unique_id}"
    os.makedirs(user_folder, exist_ok=True)

    # Get today's date as a string (e.g., "2023-09-13")
    today_date = datetime.date.today().strftime("%Y-%m-%d")

    # Check for existing files and add a postfix if necessary
    filename = f"{today_date}.avi"
    file_count = 1
    while os.path.exists(os.path.join(user_folder, filename)):
        filename = f"{today_date}_{file_count}.avi"
        file_count += 1

    # Start recording with the unique filename
    recording_path = os.path.join(user_folder, filename)
    client.download(path=recording_path, duration=None, quality=VideoQuality.ORIGIN)
    print(f"Recording started and saved to {recording_path}")

def stop_recording():
    # Stop the download process gracefully based on the platform
    if platform.system() == "Windows":
        # Windows-specific code
        os.kill(client.ffmpeg.ffmpeg.process.pid, signal.CTRL_BREAK_EVENT)
    else:
        # Unix-like systems (Linux, macOS)
        os.kill(client.ffmpeg.ffmpeg.process.pid, signal.SIGTERM)

    # Print that we stopped recording
    print("Recording stopped!")

if __name__ == '__main__':
    """
    Note: "ffmpeg" MUST be installed on your machine to run this program
    """
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    client.run()
