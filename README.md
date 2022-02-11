# R2-DiscordBot
a simple discord bot that plays music and r2d2 sounds

# Requirements

- At least Python3.6 or newer
    - with pip modules youtube-dl, discord.py, requests
    Best way to install dependencies is by using a virtual enviroment.
    I use Python3.9 currently.

    Then you can import all dependencies by calling:
    ```
    pip install -r requirements.txt
    ```

    With the requirements.txt file the exact version I used in the last commit gets used
    and it could be that for example youtube-dl is not up to date and music cannot be loaded anymore.
    If this happens packages can be updated like this:

    ```
    pip install --upgrade youtube_dl
    ```

- settings.py file where the colors of messages can be set and the discord bot token:
  ```python
  token = 'your-discord-bot-token'
  #the colors I used
  color = 0x333daa
  error_color = 0xe8292c
  #if you have friends with bad music taste :D
  bad_music = ['music','to','block']
  ```
