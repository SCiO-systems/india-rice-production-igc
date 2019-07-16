# Developer Installation

1. Install necessary requirements.

```bash
$ sudo add-apt-repository ppa:ubuntugis/ppa
$ sudo apt update
$ sudo apt install git python3 python3-dev python3-pip
$ pip3 install virtualenv # NO sudo
$ sudo apt install gdal-bin
$ sudo apt install libgdal-dev
```

2. Clone repository locally.

```bash
$ git clone https://github.com/SCiO-systems/Internship-George-Chochlakis
$ cd Internship-George-Chochlakis
```

Thereafter, every command should be executed from within the `Internship-George-Chochlakis` directory

3. Add the pre-commit hooks.

```bash
$ cp etc/pre-commit .git/hooks/pre-commit
$ chmod +x .git/hooks/pre-commit
```

4. Create a new virtual environment, `.venv`, and activate it.

```bash
$ ~/.local/bin/virtualenv .venv
$ . .venv/bin/activate # OR source .venv/bin/activate
```

5. Install remaining project dependencies

```bash
$ pip install -e .[dev]
```
