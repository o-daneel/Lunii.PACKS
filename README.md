# Lunii - Pack Manager (CLI)

Lunii Pack Manager is a Proof of Concept application to demonstrate management of stories in a Lunii Storyteller.

This is a simple CLI application that allows basic operations like export/import/remove.


📣 **[Communauté Discord autour de Lunii](https://discord.com/invite/jg9MjHBWQC)**

## TODO
*(nothing)*

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
    - [Removing a story](#removing-a-story)
    - [Importing a story](#importing-a-story)
- [Links / Similar repos](#links--similar-repos)
- [Story Packs](#story-packs)

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

# Links / Similar repos
* [Lunii - Reverse Engineering](https://github.com/o-daneel/Lunii.RE)
* [STUdio - Story Teller Unleashed](https://marian-m12l.github.io/studio-website/)
* [(GitHub) STUdio, Story Teller Unleashed](https://github.com/marian-m12l/studio)
* [Studio-Pack-Generator](https://github.com/jersou/studio-pack-generator)
* [Lunii Admin](https://github.com/olup/lunii-admin) (a GO implementation to create custom stories)

# Story Packs
You can enjoy some packs [here](packs/packs.links).   
Feel free to share new packs.