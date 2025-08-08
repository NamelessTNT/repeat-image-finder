[![Python](https://img.shields.io/badge/python-3.12-green)](https://www.python.org/doc/versions/)

### Introduction
This is a script that finds repeated images in a folder and shows it on a window for you to pick which ones to keep and which ones to delete.
This script uses **imagehash** to identify different pictures. It's only sensitive to pictures with similar overall structure so this is only used to find **highly similar pictures** (often different copies of a single picture).

### How to use
- Open command line in the script folder and run `python window.py`.
- Set `image path` to be your picture folder. The script will automatically find every picture under the directory.
- Set `hash record path` and `repeat record path` to be previous output json files or some new empty json files
- Click the entry to refresh the window. The start button will only be activated when all three entrys are not empty.
- Progress will be shown in the command line. When it's finished, click refresh button to get outputs.
- Use "Prev" and "Next" button to navigate through the results. Compare picture info in the right. If you want to delete a photo, **check the checkbox on the right and click "Confirm"**. The script will remember your decisions.
- When you reach the last record in all repeated images, click "Confirm" would move all the pictures selected into recycle bin.
