# Pygot-Mods
Python tool for auto-updating plugins on spigot based Minecraft servers with a single command

## Requirements
- ftplib
- argparse
- requests
- bs4
- urllib
- tld

## How to use

Pygot-Mods requires two files:
- credentials file - This is a file containing your Spigot servers FTP credentials. Password is base64'd because I'm too lazy to implement AES. To create this file, simply run:
```bash
python pygot-mods.py --create_creds
```
- mods file - This is a text file containing **dynamic** links to your mods. (Do not put in static links to a mod, or you'll only ever get **THAT** version). An example file looks like the following:
```
https://github.com/rutgerkok/BlockLocker/releases/latest
https://www.iani.de/jenkins/job/LogBlock/lastStableBuild/artifact/target/LogBlock.jar
https://github.com/EssentialsX/Essentials/releases/latest
https://ci.lucko.me/job/LuckPerms/lastStableBuild/
https://github.com/Ghost-chu/QuickShop-Reremake/releases/latest
https://github.com/MilkBowl/Vault/releases/latest
https://github.com/mastercake10/TimeIsMoney/releases/latest
https://dev.bukkit.org/projects/worldedit
https://dev.bukkit.org/projects/worldguard
```

Once these two files are set-up, run the following command:

```bash
python pygot-mods --credfile [Path to credentials file] --modsfile [path to mods file]
```

The tool will then automatically download and update plugins on your spigot server. 
**NOTE**: The plugin will ask you whether you wish to delete certain .jar files in your /plugins/ directory.  If you wish to skip this and delete them all, use the --autorm flag.
