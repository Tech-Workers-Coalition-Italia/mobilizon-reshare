(define-module (manifest)
  #:use-module (mobilizon-reshare package)
  #:use-module (gnu packages)
  #:use-module (guix channels)
  #:use-module (guix inferior)
  #:use-module (guix packages)
  #:use-module (guix profiles)
  #:use-module (srfi srfi-1))

(packages->manifest
  (append
    (map cadr (package-direct-inputs mobilizon-reshare))
    (map specification->package+output
       '("git-cal" "man-db" "texinfo"
         "python-pre-commit" "cloc"
         "ripgrep" "python-semver"
         "fd" "docker-compose" "poetry"))))
