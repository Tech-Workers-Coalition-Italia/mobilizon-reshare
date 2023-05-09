(define-module (guix)
  #:use-module (guix git-download)
  #:use-module (guix build-system python)
  #:use-module (guix gexp)
  #:use-module (guix packages)
  #:use-module (guix utils)
  #:use-module (gnu packages databases)     ;; for python-tortoise-orm
  #:use-module (gnu packages markup)        ;; for python-markdownify
  #:use-module (gnu packages python)
  #:use-module (gnu packages python-web)    ;; for python-uvicorn
  #:use-module (gnu packages python-xyz)    ;; for dynaconf
  #:use-module (mobilizon-reshare package)
  #:use-module (mobilizon-reshare dependencies)
  #:use-module (ice-9 rdelim)
  #:use-module (ice-9 popen))

(define %source-dir (getcwd))

(define mobilizon-reshare-git-origin
  (local-file %source-dir
              #:recursive? #t
              #:select? (git-predicate %source-dir)))

(use-modules (guix download)
             (guix transformations))
(define-public python-tweepy-4.13
  (package
    (inherit python-tweepy)
    (version "4.13.0")
    (source (origin
              (method url-fetch)
              (uri (pypi-uri "tweepy" version))
              (sha256
               (base32
                "123cikpmp2m360pxh2qarb4kkjmv8wi2prx7df178rlzbwrjax09"))))
    (arguments
     `(#:tests? #f))))

(define-public python-oauthlib-3.2
  (package
   (inherit python-oauthlib)
   (version "3.2.2")
   (source (origin
             (method url-fetch)
             (uri (pypi-uri "oauthlib" version))
             (sha256
              (base32
               "066r7mimlpb5q1fr2f1z59l4jc89kv4h2kgkcifyqav6544w8ncq"))))))

(define-public mobilizon-reshare.git
  (let ((source-version (with-input-from-file
                            (string-append %source-dir
                                           "/mobilizon_reshare/VERSION")
                          read-line))
        (revision "0")
        (commit (read-line
                 (open-input-pipe "git show HEAD | head -1 | cut -d ' ' -f 2"))))
    (package (inherit mobilizon-reshare)
      (name "mobilizon-reshare.git")
      (version (git-version source-version revision commit))
      (source mobilizon-reshare-git-origin)
      (arguments
       (substitute-keyword-arguments (package-arguments mobilizon-reshare)
         ((#:phases phases)
          #~(modify-phases #$phases
              (delete 'patch-pyproject.toml)))))
      (native-inputs
       (modify-inputs (package-native-inputs mobilizon-reshare)
         (prepend python-httpx python-fastapi python-fastapi-pagination)))
      (propagated-inputs
       (modify-inputs (package-propagated-inputs mobilizon-reshare)
         (prepend python-asyncpg python-uvicorn)
         (replace "python-tweepy"
                   python-tweepy-4.13)
         (replace "dynaconf"
                   dynaconf-3.1.11)
         (replace "python-markdownify"
                   python-markdownify))))))

(define-public mobilizon-reshare-scheduler
 (package (inherit mobilizon-reshare.git)
   (name "mobilizon-reshare-scheduler")
   (build-system python-build-system)
   (arguments
    (list
     #:phases
     #~(modify-phases %standard-phases
         (delete 'configure)
         (delete 'build)
         (delete 'check)
         (replace 'install
           (lambda _
             (let ((bin (string-append #$output "/bin")))
               (mkdir-p bin)
               (install-file "scripts/scheduler.py" bin)))))))
   (propagated-inputs (list mobilizon-reshare.git
                            python-apscheduler))
   (synopsis "Mobilizon Reshare's scheduler")
   (description "This script is intended to start a scheduler
running @code{mobilizon-reshare}.")))

(define-public patch-for-mobilizon-reshare-0.3.3
  (package-input-rewriting/spec `(("python-oauthlib" . ,(const python-oauthlib-3.2))
                                  ("python-beautifulsoup4" . ,(const python-beautifulsoup4))
                                  ("python-tortoise-orm" . ,(const python-tortoise-orm)))))

(patch-for-mobilizon-reshare-0.3.3 mobilizon-reshare.git)
