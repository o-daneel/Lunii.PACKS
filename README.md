# Lunii - Pack Manager (CLI)

Lunii Pack Manager is a Proof of Concept application to demonstrate management of stories in a Lunii Storyteller.

This is a simple CLI application that allows basic operations like export/import/remove.


📣 **[Communauté Discord autour de Lunii](https://discord.com/invite/jg9MjHBWQC)**

## TODO
*(nothing)*
* ~~update official db file, fetch db in homedir if not present + flag to refresh on demand~~
* ~~update structure with v2 v3 support~~
* ~~validate cipher / decipher on v2~~
* ~~v3 specifics~~
  * ~~read keys from bin file (optionnal)~~
  * ~~validate keys~~
* ~~validate cipher / decipher on v3~~
  * ~~import pycryptdome~~
* ~~update all exports to .mp3 .bmp .plain (v2 only) -> .plain.pk~~
* ~~update import to support directory~~
* ~~update import to cipher~~
  * ~~v2 : with xxxtea~~
  * ~~v3 : with aes using .md_bt~~
  * ~~add support for .v2.pk~~
  * ~~add support for prev .zip~~
* ~~if v3 bin key file, allow~~
  * ~~export for v3 (if keys available), as plain ?~~
* ADD CHECK stories
  * for v2, check bt, parse ri si, check all files present, check bmp size, check mp3 size
  * validate plain.pk before import
    * ri, si, li, ni present
    * check contents (rf sf files present)
    * check rf sf sizes ?


## Summary
- [Lunii - Pack Manager (CLI)](#lunii---pack-manager-cli)
  - [TODO](#todo)
  - [Summary](#summary)
  - [Usage - Command Line Interface](#usage---command-line-interface)
    - [App Version](#app-version)
    - [Help](#help)
  - [HowTo](#howto)
    - [Prepare env](#prepare-env)
    - [Install linux bash wrapper](#install-linux-bash-wrapper)
    - [Build CLI executable](#build-cli-executable)
  - [Formats supported](#formats-supported)
    - [.plain.pk](#plainpk)
    - [.v1.pk / .v2.pk](#v1pk--v2pk)
    - [zip](#zip)
    - [7z](#7z)
  - [Examples](#examples)
    - [Finding my Storyteller](#finding-my-storyteller)
    - [Getting info](#getting-info)
    - [Getting installed contents](#getting-installed-contents)
    - [Exporting a story](#exporting-a-story)
    - [Exporting a genuine story from a v3](#exporting-a-genuine-story-from-a-v3)
    - [Exporting ALL stories](#exporting-all-stories)
    - [Removing a story](#removing-a-story)
    - [Importing a story](#importing-a-story)
    - [Importing multiple stories](#importing-multiple-stories)
- [Links / Similar repos](#links--similar-repos)

## Usage - Command Line Interface

### App Version
````
$ python .\src\lunii-pm.py --version
Lunii Storyteller - Pack Manager (CLI), version 2.0.2
````

### Help
````
$ python .\src\lunii-pm.py --help   
Usage: lunii-pm.py [OPTIONS]

Options:
  --version                Show the version and exit.
  -v, --verbose            Verbose mode
  -f, --find               Identifying all Lunii storytellers connected
  -d, --dev DIRECTORY      Specifies which drives letter to use for Lunii
                           Storyteller
  -r, --refresh            Refresh official db from Lunii
  -i, --info               Prints informations about the storyteller
  -l, --list               List all stories available in Lunii Storyteller
  -k, --key FILE           Device Key file for Lunii v3
  -pe, --pack-export TEXT  Export selected story to an archive (or use ALL)
  -pi, --pack-import PATH  Import a story archive in the Lunii
  -pr, --pack-remove TEXT  Remove a story from the Lunii
  --help                   Show this message and exit.
````

## HowTo

### Prepare env

Prepare a Vitrual environment for your project and install requirements
```
$ python -m venv venv
```

Switch to your venv 
* on Linux   
   `$ source venv/bin/activate`
* on Windows   
  `$ .\venv\Scripts\activate.bat`

Install dependencies
```
$ python -m pip install -r requirements.txt
```

### Build CLI executable
```
$ pyinstaller lunii-pm.spec
...
$ dist\lunii-pm.exe
```

### Install linux bash wrapper

A bash wrapper for Linux systems exists in this `Lunii.Packs` repository. It is located at the root of this project and is named `lunii-packs`.
This wrapper takes care of the activation and deactivation of the virtual environment, but you have to have followed the previous `Prepare env` paragraph.

You can either directly use it from the command line in this directory:

```bash
$ cd Lunii.PACKS/
$ lunii-packs --version
Lunii Storyteller - Pack Manager (CLI), version 2.1.0
``` 

Or, you can add the following alias in your `.bashrc` file if tou want to use it from anywhere:

```bash
# Custom aliases to run lunii-packs
alias lunii-packs='LUNII_REPO_PATH=/home/my-user/development/Lunii.PACKS /home/my-user/development/Lunii.PACKS/lunii-packs'
```

## Supported archive formats (Lunii)
**NOTE :** Flam stories are not yet supported
### .plain.pk
**Filename** :  `story_name.8B_UUID.plain.pk`  
**Ciphering** : None / Plain  
**Structure** :  

      uuid.bin
      ni
      li.plain
      ri.plain
      si.plain
      rf/000/XXYYXXYY.bmp
      sf/000/XXYYXXYY.mp3
### .v1.pk / .v2.pk
**Filename** :  
* `LONG_UUID.v2.pk`  
* `LONG_UUID.v2.pk`  
* `LONG_UUID.pk`  
  
**Ciphering** : Generic Key  
**Structure** :  

      00000000000000000000000000000000/ni
      00000000000000000000000000000000/li
      00000000000000000000000000000000/ri
      00000000000000000000000000000000/si
      00000000000000000000000000000000/rf/000/XXYYXXYY
      00000000000000000000000000000000/sf/000/XXYYXXYY
### ZIP (old Lunii.QT)
**Filename** :  `8B_UUID - story_name.zip`  
**Ciphering** : Generic Key  
**Structure** :  

      uuid.bin
      ni
      li
      ri
      si
      rf/000/XXYYXXYY
      sf/000/XXYYXXYY

### ZIP (alternate)
**Filename** :  `AGE+] story_title DASHED_UUID.zip`  
**Ciphering** : Generic Key  
**Structure** : (same as [.v1.pk / .v2.pk](#v1pk--v2pk))

      00000000-0000-0000-0000-000000000000/ni
      00000000-0000-0000-0000-000000000000/li
      00000000-0000-0000-0000-000000000000/ri
      00000000-0000-0000-0000-000000000000/si
      00000000-0000-0000-0000-000000000000/rf/000/XXYYXXYY
      00000000-0000-0000-0000-000000000000/sf/000/XXYYXXYY

### 7z
**Filename** : `AGE+] story_title DASHED_UUID.7z`  
**Ciphering** : Generic Key  
**Structure** :  

      00000000-0000-0000-0000-000000000000/ni
      00000000-0000-0000-0000-000000000000/li
      00000000-0000-0000-0000-000000000000/ri
      00000000-0000-0000-0000-000000000000/si
      00000000-0000-0000-0000-000000000000/rf/000/XXYYXXYY
      00000000-0000-0000-0000-000000000000/sf/000/XXYYXXYY

### STUdio (ZIP / 7z)
**Filename** : `AGE+] story_title DASHED_UUID.zip .7z`  
**Ciphering** : None  

**Structure** :  

        assets/
        stroy.json
        thumbnail.png

## Examples

### Finding my Storyteller
```
> .\lunii-pm.exe -f
Found 1 connected device(s)
  "D:\" - 15 stories
```

### Getting info
#### on v2
```
> .\lunii-pm.exe -i
INFO : using Lunii device on D:\
Lunii device on "D:\"
- firmware : v2.22
- snu      : b'00 11 22 33 44 55 66 77'
- dev key  : b'00 11 22 33 44 55 66 77 00 11 22 33 44 55 66 77'
- stories  : 4x
```

Or with device specified :
```
> .\lunii-pm.exe -d D:\ -i
Lunii device on "D:\"
- firmware : v2.22
- snu      : b'00 11 22 33 44 55 66 77'
- dev key  : b'00 11 22 33 44 55 66 77 00 11 22 33 44 55 66 77'
- stories  : 4x
```

#### on v3
```
> .\lunii-pm.exe -i
Lunii device on "D:\"
- firmware : v3.1.3
- snu      : b'23 02 30 11 22 33 44'
- dev key  : b''
- dev iv   : b''
- stories  : 4x
```

### Getting installed contents
```
> .\lunii-pm.exe -l
INFO : using Lunii device on D:\
Lunii device on "D:\"
- firmware : v2.22
- snu      : b'00 11 22 33 44 55 66 77'
- dev key  : b'00 11 22 33 44 55 66 77 00 11 22 33 44 55 66 77'
- stories  : 4x

> 4058B612 - Oh les pirates !
> 4CDF38C6 - Suzanne et Gaston
> B4D11DC9 - Panique aux 6 Royaumes
> FFB5D68A - Suzanne et Gaston fêtent Pâques
```

Or using vebose mode 

```
> .\lunii-pm.exe -l -v 
INFO : using Lunii device on D:\
Lunii device on "D:\"
- firmware : v2.22
- snu      : b'00 11 22 33 44 55 66 77'
- dev key  : b'00 11 22 33 44 55 66 77 00 11 22 33 44 55 66 77'
- stories  : 4x

UUID                                 | Name                                                         | Source
------------------------------------ | ------------------------------------------------------------ | ------
D56A4975-417E-4D04-AEB3-21254058B612 | Oh les pirates !                                             |
C4139D59-872A-4D15-8CF1-76D34CDF38C6 | Suzanne et Gaston                                            |
03933BA4-4FBF-475F-9ECC-35EFB4D11DC9 | Panique aux 6 Royaumes                                       |
9D9521E5-84AC-4CC8-9B09-8D0AFFB5D68A | Suzanne et Gaston fêtent Pâques                              |
```


### Exporting a story
```
> .\lunii-pm.exe -pe FFB
INFO : using Lunii device on D:\
[FFB5D68A - Suzanne et Gaston fêtent Pâques]
> Zipping story ...
Processing sf\000\FC9905BB: 100%|██████████████████████████████████████| 81/81 [00:08<00:00]
> Adding UUID ...
Successfully exported to :
  FFB5D68A - Suzanne et Gaston fêtent Pâques.zip
```

### Exporting a genuine story from a v3
```
> python .\src\lunii-pm.py -d D:\ -pe CF1
[6C8D9CF1 - Les Aventures de Zoé – Les 6 Royaumes]
   ERROR: Lunii v3 requires Device Key for genuine story export.
   ERROR: Failed to export
> python .\src\lunii-pm.py -d D:\ -pe CF1 -k .\test\_v3\odaneel.keys
[6C8D9CF1 - Les Aventures de Zoé – Les 6 Royaumes]
> Zipping story ...
Processing rf\000\1475EA27: 100%|███████████████████████████████████████| 65/65 [00:07<00:00]
> Adding UUID ...
Successfully exported to :
  Les Aventures de Zoe  Les 6 Royaumes.6C8D9CF1.plain.pk
```

### Exporting ALL stories
```
> .\lunii-pm.exe -pe all
INFO : using Lunii device on D:\
 1/3 [FFB5D68A - Suzanne et Gaston fêtent Pâques]
> Zipping story ...
Processing sf\000\FC9905BB: 100%|██████████████████████████████████████| 33/33 [00:00<00:00]
> Adding UUID ...
 2/3 [9A2D7E89 - Au Pays des Loups]
> Zipping story ...
Processing sf\000\EAC43510: 100%|██████████████████████████████████████| 65/65 [00:01<00:00] 
> Adding UUID ...
 3/3 [4CDF38C6 - Suzanne et Gaston]
> Zipping story ...
Processing sf\000\43FA0451: 100%|██████████████████████████████████████| 32/32 [00:00<00:00] 
> Adding UUID ...
Successfully exported to :
  FFB5D68A - Suzanne et Gaston fêtent Pâques.zip
  9A2D7E89 - Au Pays des Loups.zip
  4CDF38C6 - Suzanne et Gaston.zip
```

### Removing a story
```
> .\lunii-pm.exe -pr FFB
INFO : using Lunii device on D:\
Removing ffb5d68a - Suzanne et Gaston fêtent Pâques...
Are you sure ? [y/N] y
Story removed.                                                    
```
**NOTE** : No need to type full ID given in list command. Just enough to avoid confusion.

### Importing a story
```
> .\lunii-pm.exe -pi '.\FFB5D68A - Suzanne et Gaston fêtent Pâques.zip'
INFO : using Lunii device on D:\
Processing sf/000/FC9905BB: 100%|██████████████████████████████████████| 82/82 [00:29<00:00]
INFO : Authorization file creation...
Story imported.
```

If a story already exists, import will fail

```
> .\lunii-pm.exe -pi '.\FFB5D68A - Suzanne et Gaston fêtent Pâques.zip'
INFO : using Lunii device on D:\
ERROR: This story is already loaded, aborting !
ERROR: Failed to import
```

### Importing multiple stories
```
> .\lunii-pm.exe -pi ./packs
INFO : using Lunii device on D:\
Importing 4 archives...
 1/4 > U:\Lunii\plain.pk\1+\Promenons-nous avec les chiffres !.70FFDD7E.plain.pk
Processing sf/000/E3E6340F.mp3: 100%|██████████████████████████████████| 31/31 [00:00<00:00]
   INFO : Authorization file creation...
 2/4 > U:\Lunii\plain.pk\1+\Promenons-nous dans les bruits - L'intégrale.75F16A2F.plain.pk
Processing sf/000/FBB8714C.mp3: 100%|████████████████████████████████| 120/120 [00:02<00:00]
   INFO : Authorization file creation...
 3/4 > U:\Lunii\plain.pk\1+\Promenons-nous dans l’hiver !.FF6364AF.plain.pk
Processing sf/000/ED6CF27E.mp3: 100%|██████████████████████████████████| 35/35 [00:00<00:00]
   INFO : Authorization file creation...
 4/4 > U:\Lunii\plain.pk\1+\Promenons-nous à la ferme !.43019489.plain.pk
Processing sf/000/F9C27A67.mp3: 100%|██████████████████████████████████| 35/35 [00:00<00:00]
   INFO : Authorization file creation...
Stories imported.
```

# Links / Similar repos
* [Lunii v3 - Reverse Engineering](https://github.com/o-daneel/Lunii_v3.RE)
* [STUdio - Story Teller Unleashed](https://marian-m12l.github.io/studio-website/)
* [(GitHub) STUdio, Story Teller Unleashed](https://github.com/marian-m12l/studio)
* [Studio-Pack-Generator](https://github.com/jersou/studio-pack-generator)
* [Lunii Admin](https://github.com/olup/lunii-admin) (a GO implementation to create custom stories)
