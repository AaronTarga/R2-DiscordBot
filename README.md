# R2-DiscordBot
a simple discord bot that plays music and r2d2 sounds

# Requirements

- At least Python3.6 or newer
    - with pip modules youtube-dl, discord.py, requests
    Best way to install dependencies is by using a virtual enviroment.
    I used Python3.8 and not 3.9 because that is causing problems with discord.py and created a virtual enviroment.

    Then you can import all dependencies by calling:
    ```
    pip install -r requirements.txt
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
