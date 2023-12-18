# Lunii - Pack Manager (CLI)

Lunii Pack Manager is a Proof of Concept application to demonstrate management of stories in a Lunii Storyteller.

This is a simple CLI application that allows basic operations like export/import/remove.


📣 **[Communauté Discord autour de Lunii](https://discord.com/invite/jg9MjHBWQC)**

## TODO
*(nothing)*
* update structure with v2 v3 support
* ~~validate cipher / decipher on v2~~
* v3 specifics
  * read keys from bin file (optionnal)
  * validate keys
* validate cipher / decipher on v3
  * import pycryptdome
  
* ~~update all exports to .mp3 .bmp .plain (v2 only) -> .plain.pk~~
* ~~update import to support directory~~
* update import to cipher
  * ~~v2 : with xxxtea~~
  * validate plain.pk before import
    * ri, si, li, ni present
    * check contents (rf sf files present)
    * check rf sf sizes ?
  * v3 : with aes using .md_bt
  * add support for .v2.pk
  * ~~add support for prev .zip~~
* if v3 bin key file, allow
  * export for v3 (if keys available), as plain ?
  * check story
* ADD CHECK stories
  * for v2, check bt, parse ri si, check all files present, check bmp size, check mp3 size
* update official db file, fetch db in homedir if not present + flag to refresh on demand


## Summary
- [Lunii - Pack Manager (CLI)](#lunii---pack-manager-cli)
  - [TODO](#todo)
  - [Summary](#summary)
  - [Usage - Command Line Interface](#usage---command-line-interface)
    - [App Version](#app-version)
    - [Help](#help)
  - [HowTo](#howto)
    - [Prepare env](#prepare-env)
    - [Build CLI executable](#build-cli-executable)
  - [Examples](#examples)
    - [Finding my Storyteller](#finding-my-storyteller)
    - [Getting info](#getting-info)
    - [Getting installed contents](#getting-installed-contents)
    - [Exporting a story](#exporting-a-story)
    - [Exporting ALL stories](#exporting-all-stories)
    - [Removing a story](#removing-a-story)
    - [Importing a story](#importing-a-story)
- [Links / Similar repos](#links--similar-repos)

## Usage - Command Line Interface

### App Version
````
$ python .\src\lunii-pm.py --version
Lunii Storyteller - Pack Manager (CLI), version 1.1.0
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
  -i, --info               Prints informations about the storyteller
  -l, --list               List all stories available in Lunii Storyteller
  -pe, --pack-export TEXT  Export selected story to an archive (or use ALL)
  -pi, --pack-import FILE  Import a story archive in the Lunii
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

## Examples

### Finding my Storyteller
```
> .\lunii-pm.exe -f
Found 1 connected device(s)
  "D:\" - 15 stories
```

### Getting info
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

**NOTE** : No need to type full ID given in list command. Just enough to avoid confusion.

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

# Links / Similar repos
* [Lunii - Reverse Engineering](https://github.com/o-daneel/Lunii.RE)
* [STUdio - Story Teller Unleashed](https://marian-m12l.github.io/studio-website/)
* [(GitHub) STUdio, Story Teller Unleashed](https://github.com/marian-m12l/studio)
* [Studio-Pack-Generator](https://github.com/jersou/studio-pack-generator)
* [Lunii Admin](https://github.com/olup/lunii-admin) (a GO implementation to create custom stories)
