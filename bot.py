import os
import subprocess
import sys

if __name__ == "__main__":
    bot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "detailing_bot")
    subprocess.run([sys.executable, "bot.py"], cwd=bot_dir)
