# Tekken-7-primitive-mod-manager
So...
This program is what happens when person who knows little python asks chatGPT to write entire program for them.
I've wrote max 10 lines and glued everything together.
Now it only works on linux.

## Usage
```python ./TMMTEST-with-multi.py (path to archive mod to add)``` when downloading .py file
or
```./NT7PMM (path to archive of mod to add )```

## How it's working / What can it do
- It's enabling and disabling mods just by coping and pasting files to correct folders.
 -It supports not only .pak mods that are stored in `~mods` but also applies .csv files for [TKDataPatcher](https://tekkenmods.com/mod/2301/tkdatapatcher) support (Right now .csv files are not managable via this script and you can only add them).
- You can add mods that are archived in `.7z` `.zip` `.rar` formats (and just plain .pak file) by giving archive's location as first argument (You can also do that inside the program of course).
- You can remove mods.

## Contribution
if you are someone with more python experience feel free to do whatever you want with this. If you have any idea write it in issues. (I don't promise anything)
