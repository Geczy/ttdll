import os
import signal
import platform
import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import ConnectEvent, DisconnectEvent, LiveEndEvent
from TikTokLive.types import VideoQuality
import datetime

# Define the usernames to monitor
usernames_to_monitor = ["@parkergetajob", "@itsdeaann", "@kmohrz"]

# Create a dictionary to store client instances for each username
clients = {}

# Create dictionaries to track recording and waiting status for each username
recording = {username: False for username in usernames_to_monitor}
waiting_for_online = {username: True for username in usernames_to_monitor}

# Function to start recording for a specific username
def start_recording(username):
    recording[username] = True

    # Define the folder for user recordings
    user_folder = f"./recordings/{username}"
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
    clients[username].download(path=recording_path, duration=None, quality=VideoQuality.ORIGIN)
    print(f"Recording for {username} started and saved to {recording_path}")

# Function to stop recording for a specific username
def stop_recording(username):
    recording[username] = False

    # Stop the download process gracefully based on the platform
    if platform.system() == "Windows":
        # Windows-specific code
        os.kill(clients[username].ffmpeg.ffmpeg.process.pid, signal.CTRL_BREAK_EVENT)
    else:
        # Unix-like systems (Linux, macOS)
        os.kill(clients[username].ffmpeg.ffmpeg.process.pid, signal.SIGTERM)

    # Print that we stopped recording
    print(f"Recording for {username} stopped!")

# Initialize client instances and event handlers for each username
for username in usernames_to_monitor:
    clients[username] = TikTokLiveClient(username)

    @clients[username].on("connect")
    async def on_connect_client(event: ConnectEvent, username=username):
        global waiting_for_online
        print(f"Connected to Room ID for {username}:", clients[username].room_id)

        if waiting_for_online[username]:
            waiting_for_online[username] = False
            print(f"User {username} is now online. Starting recording...")
            start_recording(username)

    @clients[username].on("disconnect")
    async def on_disconnect_client(event: DisconnectEvent, username=username):
        global waiting_for_online
        print(f"Disconnected for {username}. Going back into waiting mode.")

        if recording[username]:
            stop_recording(username)

        waiting_for_online[username] = True

    @clients[username].on("live_end")
    async def on_live_end_client(event: LiveEndEvent, username=username):
        global recording
        print(f"Livestream for {username} ended :(")

        if recording[username]:
            stop_recording(username)

        waiting_for_online[username] = True

async def main():
    # Create tasks for each client and run them concurrently
    tasks = [clients[username].start() for username in usernames_to_monitor]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    """
    Note: "ffmpeg" MUST be installed on your machine to run this program
    """
    asyncio.run(main())
