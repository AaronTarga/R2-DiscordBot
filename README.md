# R2-DiscordBot
a simple discord bot that plays music and r2d2 sounds

# Requirements

- Python 3.10 or newer
    - with pip modules yt-dlp, py-cord, requests
    Best way to install dependencies is by using a virtual enviroment.
    Python 3.10 is required by the pinned dependencies.

    Then you can import all dependencies by calling:
    ```
    pip install -r requirements.txt
    ```

    The bot uses py-cord's message content intent. Enable the Message Content
    Intent for the bot in the Discord Developer Portal.

- settings.py file where the colors of messages can be set and the discord bot token:
  ```python
  token = 'your-discord-bot-token'
  #the colors I used
  color = 0x333daa
  error_color = 0xe8292c
  #if you have friends with bad music taste :D
  bad_music = ['music','to','block']
  ```
