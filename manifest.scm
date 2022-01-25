(define-module (manifest)
  #:use-module (docker mobilizon-reshare)
  #:use-module (gnu packages)
  #:use-module (guix packages)
  #:use-module (guix profiles))

(packages->manifest
  (append
    (map cadr (package-direct-inputs mobilizon-reshare.git))
    (list poetry/pinned)
    (map specification->package+output
       '("git-cal" "man-db" "texinfo"
         "python-pre-commit"
         "ripgrep" "python-semver"
         "fd" "docker-compose"))))
