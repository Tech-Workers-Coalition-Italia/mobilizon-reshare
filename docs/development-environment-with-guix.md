# Hacking with Guix on Mobilizon Reshare
To setup a development environment to hack on `mobilizon-reshare` you can use [Guix](https://guix.gnu.org/) and [direnv](https://direnv.net/).

If you already have `guix` and `direnv` installed on your system, the development environment setup is as easy as:

```shell
$ git clone https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare
$ cd mobilizon-reshare/
direnv: error .envrc is blocked. Run `direnv allow` to approve its content.
$ direnv allow
direnv: loading .envrc

[...]

direnv: export +CPLUS_INCLUDE_PATH +C_INCLUDE_PATH +LIBRARY_PATH ~GUIX_LOCPATH ~PATH ~PYTHONPATH
$
```

Hurray 🎉 ! Now you can hack on `mobilizon-reshare` without worrying about dependencies.

## Installing Guix

*Caveat:* Guix currently runs only on Linux, if you run a different OS you're probably better off with something like [poetry](https://python-poetry.org/). Just beware that you may end up with slightly different behavior, since `poetry` only locks Python dependencies.

### Debian Bullseye/Ubuntu/Linux Mint

If you run Debian Bullseye (or one of its derivatives) installing Guix is achieved with:

```shell
$ sudo apt install guix
```

If you want to find out if your distribution is a derivative of Debian Bullseye you can run:

```shell
$ sudo cat /etc/debian_release
```

### Fedora

### Arch Linux

### Other distributions

For all other distributions you can install Guix with the installer script. It will guide you through the process of installing Guix.

```shell
$ curl https://git.savannah.gnu.org/cgit/guix.git/plain/etc/guix-install.sh | sudo bash
```

Beware that piping to `sudo bash` is usually a *very* bad idea. Before running the above command please read the script and the Guix manual.

## Configuring Guix

To make Guix applications work out of the box you should add the following variables to your `.bash_profile` (or its equivalent for shells other than Bash):

```shell
GUIX_PROFILE="${HOME}/.guix-profile"
. "$GUIX_PROFILE/etc/profile"

export GUIX_LOCPATH="$1/lib/locale"
export SSL_CERT_DIR="$1/etc/ssl/certs"
export SSL_CERT_FILE="$1/etc/ssl/certs/ca-certificates.crt"
export GIT_SSL_CAINFO="$SSL_CERT_FILE"
export CURL_CA_BUNDLE="$SSL_CERT_FILE"
export INFOPATH="$GUIX_PROFILE${INFOPATH:+:}${INFOPATH}"
export MANPATH="$GUIX_PROFILE${MANPATH:+:}${MANPATH}"

GUIX_PROFILE="$XDG_CONFIG_HOME/guix/current"
. "$GUIX_PROFILE/etc/profile"
```

and then run **in a new shell**

```shell
$ guix install nss-certs
$ sudo -i guix install glibc-locales
```

## Installing direnv

Once you have Guix properly setup, you can install `direnv` with:

```shell
$ guix install direnv
```

then you should [hook it](https://direnv.net/docs/hook.html) into your shell.

## Troubleshooting

Guix sometimes prints somewhat scary messages like:

```shell

```

when you see a message like that you can either run it to make the current shell work with the new packages installed by Guix or just close the current shell and spawn another, this way it'll put Guix packages in the right plache in your `PATH`.