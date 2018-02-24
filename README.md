# Umineko no Naku Koro ni (Answer Arcs) - PS3 Voice and graphics patch

This patch aims to modify the newest release of Umineko by MangaGamer, changing its assets to replicate the PS3 version of the game.
It is compatible with the Steam version ***and*** the MangaGamer DRM-free download. See the roadmap below for current patch status.

# Warning - Steam Updates

Recent steam updates have been breaking patch installations. If you are an existing user, please read the below.

It is **mandatory** that you download the new .exe. 
When steam updates Umineko, it overwrites the game script which can cause your save files to lose their position, **potentially skipping you forward in the game (causing spoilers)**. Additionally, you may need to re-download the patch to fix any files overwritten by the steam update.
The new .exe prevents files being overwritten, and also prevents you loading your saves if steam does overwrite important files. 

## Instructions

If you're not sure if your 0.utf has been overwritten, start a new game (do NOT load a save). If voices play, your script is OK, follow the `Instructions if your 0.utf is OK`. If no voices play, follow `Instructions if your 0.utf has been overwritten`

### Instructions if your 0.utf has been overwritten by a steam update:
1. Go to the [Getting Started Guide](https://github.com/07th-mod/guide/wiki/Umineko-Getting-started), select your game version, then download the .exe only.
2. Overwrite your old .exe with the downloaded one
3. Overwrite your old `0.utf` with the downloaded one
4. Rename your `0.utf` to `0.u`
5. Rename the save folder from 'saves' to 'mysav'
6. Keep a backup of the .exe file and 0.u file in case it gets overwritten by steam.
7. Note that for Chiru, **your saves may be shifted forward slightly (maybe 5-10 lines of dialogue)** when you update your script from v1.0!! To counteract this, please load a fairly old save, then skip forward until reaching your original point in the game. You are affected by this if the save thumbnail doesn't match what is shown when you load the save.

### Instructions if your 0.utf is OK / has not been overwritten:
1. Go to the [Getting Started Guide](https://github.com/07th-mod/guide/wiki/Umineko-Getting-started), select your game version, then download the .exe only.
2. Overwrite your old .exe with the new one
3. Rename your `0.utf` to `0.u`
4. Rename the save folder from 'saves' to 'mysav'
5. Keep a backup of the .exe file and 0.u file in case it gets overwritten by steam.

### Steam Updates - Troubleshooting

If you find that your saves are suddenly missing, then 
 - you forgot to rename the 'saves' directory to 'mysav' 
 - your .exe was overwritten by steam - you need to replace it again

If you get a 'No game script found' error, likely you didn't rename `0.utf` to `0.u`

If your opening videos (there are two different ones) play very small and are the old sprites, likely your opening video was overriden by steam. If you wish you can re-download the graphics patch and apply it to get the videos. This will be fixed in future releases by renaming those videos.

## Latest Release / Install Instructions

See the Getting Started guide: https://github.com/07th-mod/guide/wiki/Umineko-Getting-started

## Feedback and bug reports

We now have a discord server: https://discord.gg/acSbBtD . If you have a formal issue to report, please still raise a gihub issue as it helps us keep track of issues. For small problems/questions however you can just ask on discord.

The patch is still in progress, and all we want is to kill all the bugs. If you find anything, first check if the bug has already been reported. If you've found a new bug, open a new issue and please include as much information as you can in the ['Issues'](https://github.com/07th-mod/umineko-answer/issues) section. The [Wiki](https://github.com/07th-mod/umineko-answer/wiki) also contains some bug information.

We really appreciate your help!

## Roadmap

The patch is currently **playable** but still in development.

- [x] Voices
- [x] Sprites
- [x] Backgrounds
- [x] Effects
- [x] CGs
- [x] Menus
