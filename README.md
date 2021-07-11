<img src="/assets/logo.png">

# Maroon Lines
### Introduction

Maroon Lines is a source code editor with in-built version controlling.    
    
"Why not just use Git? That's the holy grail for version controlling!" - This is true. I believe so too. However, Git is more suited for projects. Maroon Lines tries to solve the problem of versioning for standalone files.     
    
Say you fire up your unregistered Sublime Text to solve a LeetCode or Kattis problem set. You write code to solve it, submit it and see it spectacularly fail. You go back to the drawing board to change your logic, and submit again. Fails again.   
  
You realise that the previous version was on the right track and just needed a little change. Unfortunately, you can't just jump back to a previous version - unless you had initialised a git repo, which you did not. Who would initialise a repository for a single file?    
    
Maroon Lines solves this problem by saving a version every time one saves his/her file. In addition, it also provides a intuitive way for the programmer to jump between versions easily - paving a way for one to store and view multiple solutions to a problem set in a single file.  

### Usage  
Download the installer for either Windows/MacOS [here](https://github.com/jaivigneshvenugopal/maroon-lines/releases) before beginning to use the software.  
  
The application opens like any other text-editor, however, its specialty raises its head when it starts saving content. Using the 'Save' or 'Save As' functionality implicitly saves a snapshot of the current state of the file.  
  
  
Every node represents a version of the file, and no two nodes are alike.  

#### Saving versions
A file has to be in storage before versioning could begin. Using the 'Save' or 'Save As' functionality implicitly saves a snapshot of the current state of the file.
 
![](assets/1.gif)

#### Accessing versions
To access specific/previous versions, click on respective nodes or use the following shortcuts:
###### Windows
```
Alt + Up/Down/Right/Down 
```
###### MacOS
```
Option + Up/Down/Right/Down
```
![](assets/2.gif)

#### Branching
To branch off from a file's edit history, move to a specific version and start editing. Follow the aforementioned instructions to save the new version.

![](assets/3.gif)

#### Implicit Features
The versions are saved offline, which means that the versions exist even after the application is closed. Therefore, it is possible to leave the code on a certain node and come back later on to work on it. All versions will be retained.

#### Bottlenecks
Due to the way the application is designed, it is necessary to change the file's name or location only through the application. If not, renaming the file or moving it to a different location will break the link between the file and its history.

### Development
#### Install Pyenv
###### Ubuntu/Debian
```
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

curl https://pyenv.run | bash
```

###### MacOS
```
brew install openssl readline sqlite3 xz zlib
curl https://pyenv.run | bash
```

###### Additional
The output will be based on your shell. But you should follow the instructions to add pyenv to your path and to initialize pyenv/pyenv-virtualenv auto completion. Once you’ve done this, you need to reload your shell:
```
exec "$SHELL" # Or just restart your terminal
```

#### Install Python 3.6.8
```
CONFIGURE_OPTS=--enable-shared pyenv install 3.6.8
```

#### Configure a new Virtual Environment
```
pyenv virtualenv 3.6.8 fbs
cd maroon-lines
pyenv local fbs
```

#### Install Pip Packages
```
pip install IPython wheel fbs pyqode.core pyqode.python networkx grave matplotlib==3.2.2 PyQt5==5.9.2 numpy==1.19.3
```

#### Generate Installer (on respective OS platforms)
```
fbs run
fbs freeze
fbs installer
```
### Credits
This desktop application was built using the following technologies:
1. [**PyQt5**](https://pypi.org/project/PyQt5/) - Qt is set of cross-platform C++ libraries that implement high-level APIs for accessing many aspects of modern desktop and mobile systems. PyQt provides python bindings for Qt.
2. [**pyQode**](https://github.com/pyQode) - Source code editor widget for PyQt/PySide
3. [**NetworkX**](https://networkx.org/) - Python package for the creation, manipulation, and study of the structure, dynamics, and functions of complex networks.
4. [**Grave**](https://github.com/networkx/grave) - Graph Visualization Package
