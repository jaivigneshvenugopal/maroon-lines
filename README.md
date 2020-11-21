# maroon-lines

### Install Pyenv
##### Ubuntu/Debian
```
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

curl https://pyenv.run | bash
```

##### MacOS
```
brew install openssl readline sqlite3 xz zlib
curl https://pyenv.run | bash
```

##### Additional
The output will be based on your shell. But you should follow the instructions to add pyenv to your path and to initialize pyenv/pyenv-virtualenv auto completion. Once you’ve done this, you need to reload your shell:
```
exec "$SHELL" # Or just restart your terminal
```



### Install Python 3.6.8
```
CONFIGURE_OPTS=--enable-shared pyenv install 3.6.8
```

### Configure a new Virtual Environment
```
pyenv virtualenv 3.6.8 fbs
cd maroon-lines
pyenv local fbs
```

### Install Pip Packages
```
pip install IPython wheel fbs pyqode.core pyqode.python networkx grave matplotlib==3.2.2 PyQt5==5.9.2 numpy==1.19.3
```

### Generate installer
```
fbs run
fbs freeze
fbs installer
```