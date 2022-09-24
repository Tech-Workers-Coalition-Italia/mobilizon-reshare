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

### Debian/Ubuntu/Linx Mint and derivatives

If you run Ubuntu 20.04, Linux Mint 20, Debian Bullseye or later (or one of their derivatives) installing Guix is achieved with:

```shell
$ sudo apt install guix
```

If you want to find out which version of Debian you are running you can use:

```shell
$ sudo cat /etc/debian_release
```

### Arch Linux

The Arch Wiki has a very good [article](https://wiki.archlinux.org/title/Guix).

### Other distributions

For every other distributions you can install Guix with the installer script. It will guide you through the process of installing Guix.

```shell
$ curl https://git.savannah.gnu.org/cgit/guix.git/plain/etc/guix-install.sh | sudo bash
```

Beware that piping to `sudo bash` is usually a *very* bad idea. Before running the above command please read the script and the Guix manual.

## Configuring Guix

To make Guix applications work out of the box you should add the following variables to your `.bash_profile` (or its equivalent for shells other than Bash):

```shell
GUIX_PROFILE="${HOME}/.guix-profile"
. "$GUIX_PROFILE/etc/profile"

export GUIX_LOCPATH="$GUIX_PROFILE/lib/locale"
export SSL_CERT_DIR="$GUIX_PROFILE/etc/ssl/certs"
export SSL_CERT_FILE="$GUIX_PROFILE/etc/ssl/certs/ca-certificates.crt"
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
$ guix install hello
The following package will be installed:
   hello 2.10

The following derivation will be built:
   /gnu/store/15s9gs89i6bf16skwb1c03bm4wj9h30a-profile.drv

building CA certificate bundle...
listing Emacs sub-directories...
building fonts directory...
building directory of Info manuals...
building database for manual pages...
building profile with 1 package...
hint: Consider setting the necessary environment variables by running:

     GUIX_PROFILE="~/.guix-profile/hello-profile"
     . "$GUIX_PROFILE/etc/profile"

Alternately, see `guix package --search-paths'.

$
```

when you see a message like that you can either run it to make the current shell work with the new packages installed by Guix or just close the current shell and spawn another, this way it'll put Guix packages in the right place in your `PATH`.
