# Please Read!

If you a **user**, just download the pre-patched binaries from here: https://github.com/07th-mod/guide/wiki/Umineko-Getting-started

This page is only for developers.

## Important
The default resolution has been set to 1920 x 1080 (original game was 1280x960).

## Notes:
- When the python script patches the game .exe, it does not apply a diff, instead it searches for the instruction to set the width and height, then changes the value which is set. So in theory, even if the game is updated, it should still work.

## Notes - Linux:
- For the Linux executable, use the windows patcher (`patchUminekoToWidescreen.py`) followed by the Linux patcher (`patchUminekoVideoLinux.py`). The linux patcher is the same as the MAC patcher, but has a slight adjustment to ignore the first match in the executuable.