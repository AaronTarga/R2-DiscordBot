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
- **yt-dlp says "Sign in to confirm you're not a bot":** Export your YouTube
  cookies in Netscape format to a `.txt` file as described in the
  [yt-dlp cookie instructions](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp).
  The export must contain a current signed-in YouTube session; a stale, logged-out,
  or unsupported export will not bypass the check. Keep this file private; it can
  grant access to your account. For a direct run, set `YOUTUBE_COOKIES_FILE` to
  the file's path before starting the bot:

  ```powershell
  $env:YOUTUBE_COOKIES_FILE = "C:\path\to\cookies.txt"
  python main.py
  ```

  With Docker Compose, put the file at `cookies/cookies.txt` and set
  `YOUTUBE_COOKIES_FILE=/run/secrets/youtube-cookies/cookies.txt` in `.env`.
  The Compose service mounts the `cookies` directory read-only. After changing
  `.env`, recreate the container so it receives the updated environment:

  ```sh
  docker compose up -d --force-recreate
  ```

  To check that the configured path exists and is readable inside the container
  without displaying the cookie contents, run:

  ```sh
  docker compose exec bot python -c "import os,pathlib; value=os.getenv('YOUTUBE_COOKIES_FILE'); p=pathlib.Path(value) if value else None; print('configured:', bool(value), 'file:', bool(p and p.is_file()), 'readable:', bool(p and p.is_file() and os.access(p, os.R_OK)), 'bytes:', p.stat().st_size if p and p.is_file() else 0)"
  ```

  If the file is missing, empty, or unreadable, check the host file location,
  `.env` value, and container configuration. If it is readable but YouTube still
  rejects requests, create a fresh Netscape-format export from a browser session
  signed in to YouTube and try again; cookies do not guarantee that YouTube will
  allow the request. Leave the variable unset when cookies are not needed.
- **yt-dlp says "Requested format is not available":** YouTube extraction may
  require a JavaScript runtime to solve its challenges. The Docker image includes
  Deno; rebuild and recreate it after updating:

  ```sh
  docker compose up -d --build --force-recreate
  ```

  For a direct run, install a supported JavaScript runtime such as Deno and make
  sure it is available on `PATH`. If the error persists, yt-dlp may not be able
  to access formats for that video or YouTube may require additional verification.
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
