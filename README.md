# R2-DiscordBot

A Discord bot with R2-D2 sound commands, music playback, and server utility
commands.

## Requirements

- Python 3.10 or newer
- FFmpeg installed and available on `PATH` (required for all audio playback)
- A Discord application/bot and a server where you can invite it
- Git, if you are cloning the repository

## 1. Create and configure the Discord bot

1. Open the [Discord Developer Portal](https://discord.com/developers/applications)
   and create an application.
2. Open **Bot**, create the bot user, and copy its token. Keep the token private.
   If it is exposed, reset it in the portal.
3. On the **Bot** page, enable **Message Content Intent** under **Privileged
   Gateway Intents**, then save the change. The bot uses message-prefix commands
   (the prefix is `;`), so this intent is required.
4. Invite the bot to your server from **OAuth2 > URL Generator**:
   - Select the `bot` scope.
   - Grant the permissions the bot needs: View Channels, Send Messages, Embed
     Links, Read Message History, Connect, Speak, Use Voice Activity, Manage
     Messages, Mute Members, and Deafen Members.
   - Open the generated URL and choose your server.

Commands that manage extensions require the caller to have Administrator
permissions. The `mute` and `fullmute` commands require the server role named
`Owner`, as well as the bot's Mute Members and Deafen Members permissions.

## 2. Get the project files

If you have not already downloaded the project, clone it and change to its
folder:

```sh
git clone https://github.com/AaronTarga/R2-DiscordBot.git
cd R2-DiscordBot
```

If you already have the project, open a terminal in its root folder (the folder
containing `main.py` and `requirements.txt`).

## 3. Install Python dependencies

Use a virtual environment so the packages are isolated from other Python
projects. The commands below install the pinned dependencies from
`requirements.txt`.

### Windows (PowerShell)

Install Python 3.10 or newer, then open PowerShell in the project folder:

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use the environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Linux

On Debian or Ubuntu, install Python, virtual-environment support, Git, and
FFmpeg:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git ffmpeg
python3 --version
```

Check that Python is 3.10 or newer. If your distribution's default Python is
older, install a newer Python version using that distribution's supported
packages before continuing. Then, in the project folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On other Linux distributions, install Python 3.10+, its `venv` support, Git,
and FFmpeg using the distribution's package manager, then run the same virtual
environment and pip commands.

## 4. Create `settings.py`

Create a file named `settings.py` in the project root, next to `main.py`, and
put your bot token and preferences in it:

```python
token = "paste-your-bot-token-here"
color = 0x333daa
error_color = 0xe8292c
bad_music = []
```

Do not share or commit your real bot token. If you previously exposed it, reset
it in the Discord Developer Portal and update `settings.py`.

## 5. Install and verify FFmpeg

The bot invokes FFmpeg to play both music and sound files. Installing the Python
packages does not install FFmpeg itself. Install it and make sure the `ffmpeg`
executable is on `PATH`.

### Windows

In PowerShell:

```powershell
winget install --id Gyan.FFmpeg.Shared --exact
```

Close and reopen PowerShell, then verify:

```powershell
ffmpeg -version
```

If PowerShell says `ffmpeg` is not recognized, add the directory containing
`ffmpeg.exe` (usually the installation's `bin` directory) to your Windows
`PATH`, open a new terminal, and try again.

### Debian or Ubuntu

```sh
sudo apt update
sudo apt install -y ffmpeg
ffmpeg -version
```

For another Linux distribution, install FFmpeg using its package manager and
verify that `ffmpeg -version` runs.

## 6. Start the bot

With the virtual environment active, run this from the project root:

```sh
python main.py
```

On Windows, if you did not activate the environment, run:

```powershell
.\.venv\Scripts\python.exe main.py
```

Keep the terminal open while the bot is running. A successful connection prints
`Bot is ready`. Type `;help` in a server channel to see available commands.

For example, join a voice channel and run `;r2_scream` for a sound, or use
`;play <YouTube URL>` to play music. The bot must have permission to view and
send messages in the channel, and to connect and speak in the voice channel.

## Troubleshooting

- **`PrivilegedIntentsRequired` or commands do not respond:** Enable **Message
  Content Intent** on the bot's page in the Developer Portal, save, and restart
  the bot.
- **`ffmpeg was not found`:** Install FFmpeg, ensure its executable is on
  `PATH`, open a new terminal, confirm `ffmpeg -version` works, and restart the
  bot.
- **The bot cannot join or speak:** Check the bot's server and channel
  permissions, including Connect and Speak.
- **`ModuleNotFoundError`:** Activate the project's virtual environment and
  install the dependencies with `python -m pip install -r requirements.txt`.

## Run with Docker

Docker Compose builds an image with FFmpeg and the Python dependencies, then
starts the bot using the `DISCORD_TOKEN` environment variable.

1. Copy `.env.example` to `.env` and set `DISCORD_TOKEN` to your Discord bot
   token.
2. In the Discord Developer Portal, enable **Message Content Intent** for the
   bot application. The bot uses `;`-prefixed commands, which require this
   privileged intent both in the application settings and in the bot code.
3. From the repository directory, run:

   ```sh
   docker compose up --build -d
   ```

4. Follow the bot logs with `docker compose logs -f` and stop it with
   `docker compose down`.

The token is not copied into the image. Keep `.env` private; it is excluded
from Git and the Docker build context. The Docker image uses
`settings.docker.py` for the container's settings, so the local `settings.py`
file is not required in the image.
