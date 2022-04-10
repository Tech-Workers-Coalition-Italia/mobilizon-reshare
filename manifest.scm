(define-module (manifest)
  #:use-module (docker mobilizon-reshare)
  #:use-module (gnu packages)
  #:use-module (guix channels)
  #:use-module (guix inferior)
  #:use-module (guix packages)
  #:use-module (guix profiles)
  #:use-module (srfi srfi-1))

(define channels
  ;; This is the old revision from which we want to
  ;; extract docker-compose.
  (list (channel
         (name 'guix)
         (url "https://git.savannah.gnu.org/git/guix.git")
         (commit
          "07f55a361e23152b48f34425f116a725cce39e48"))))

(define inferior
  ;; An inferior representing the above revision.
  (inferior-for-channels channels))

;; Now create a manifest with the current packages
;; and the old "docker-compose" package.
(packages->manifest
  (append
    ;; docker-compose fails to build on current master, hence this hack.
    (list (first (lookup-inferior-packages inferior "docker-compose")))
    (map cadr (package-direct-inputs mobilizon-reshare.git))
    (map specification->package+output
       '("git-cal" "man-db" "texinfo"
         "python-pre-commit" "cloc"
         "ripgrep" "python-semver"
         "fd"))))
