# Cryptochat client

## Colabs

- Šárka Chwastková - [sarkaaa](https://github.com/sarkaaa)
- Ondřej Gajdušek - [ogajduse](https://github.com/ogajduse)
- Roman Ligocki - [rligocki](https://github.com/rligocki)
- Roland Dávidík - [RolandDavidik](https://github.com/RolandDavidik)

## Installation

Clone this repository

```
git clone https://github.com/sarkaaa/cryptochat-client.git && cd cryptochat-client
```

**Fedora**

Install dependencies for the Python packages

```
dnf install gcc gobject-introspection-devel cairo-devel cairo-gobject-devel pkg-config python3-devel gtk3
```

**Debian**

```
apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0
```

Make sure you have installed pipenv and pip

**Fedora**

```
dnf install python3-pip pipenv
```

**Debian**

Install the pipenv using this doc: https://pipenv.readthedocs.io/en/latest/install/#pragmatic-installation-of-pipenv



Then install the dependencies inside the venv by

```
pipenv --three install
```

Create `.data` directory for the client cache

```
mkdir .data
```

Run the app:

```
pipenv run python cryptochat_client.py
```

**Note** that this is client side only. You need to have running the server piece before running the client. Install the server according to the instructions of the server repository. https://github.com/ogajduse/cryptochat-server/

## About

School project focused on encrypted chat.
