(define-module (manifest)
  #:use-module (docker mobilizon-reshare)
  #:use-module (gnu packages)
  #:use-module (guix profiles))

(packages->manifest
 (append
  (list
   python-3.9-wrapper)
  (map specification->package+output
       '("meld" "git-cal" "man-db" "texinfo"
         "python-pre-commit" "poetry" "bzip2"
         "guix" "grep" "sed" "unzip" "bash" "ncurses"
         "findutils" "ripgrep" "python-semver"
         "util-linux" "python-black" "gawk" "fd"
         "coreutils" "less" "git" "git:credential-libsecret"
         "gitg" "direnv" "which" "vim" "emacs"
         "tar" "gzip" "openssh" "docker-cli" "docker-compose"))))
