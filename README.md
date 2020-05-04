# obs-key-listener
A keyboard listener to maintain a state of game of Magic: the Gathering

**NOTE**: Please note this application has to be executed as "root" in linux (sudo) or with Administrator priviledges in Windows. This is due to the use of the [keyboard Python module](https://pypi.org/project/keyboard/) which requires escalation to tap into the keyboard input device.

## Windows Installation

Suggested Windows mode of installation is through a setup wizard that can be obtainer from the [releases page](https://github.com/mtg-to/obs-key-listener/releases).

Please download the `obs-key-listener-setup.exe` and run to install on your machine. The shortcut will be configured to use the default bindings with the format chosen during the installation.

## Usage with OBS

Using the captured shortcuts will cause the software to flush the state into a file on the hard drive. (On Windows this will be usually `c:\ProgramData\OBS Key Listener\obs.txt` by default). The output path can be chosen as a commandline parameter (for example in the Desktop shortcut).

The file written by the key listener can be used as a source for a `Text GDI+` group in OBS and thrown into the scene.

## Power usage

The script can be executed from the command line and there's quite

```
usage: cli.py [-h] [-f FMT] [-o PATH] [-c PATH]

Use keyboard shortcuts to maintain the global state counters in Magic: the Gathering

optional arguments:
  -h, --help            show this help message and exit
  -f FMT, --format FMT  selects the format of the game
  -o PATH, --output PATH
                        file to write the game state to (e.g. for OBS)
  -c PATH, --config PATH
                        path to the yaml config file
```

## Development

### Pre-requisites

* pyenv
* pipenv

### Running from source

To run from source, please ensure you have the pre-requisites installed and then:

```
pipenv install
pipenv run python cli.py -h
```

This will display the basic usage help.

### Packaging for Windows

To create a Windows one-file executable one needs to obtain [pyinstaller](https://pypi.org/project/PyInstaller/) and use it on this project on a Windows machine with appropriate Python setup and dependencies installed.

Recommended usage:
```
pyinstaller cli.py --onefile --name listener
```

The wizard installation is created using [Inno Setup](https://jrsoftware.org/isinfo.php). Installation script config is available under `innosetup/setup.iss`.

