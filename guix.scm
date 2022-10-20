(define-module (guix)
  #:use-module (guix git-download)
  #:use-module (guix build-system python)
  #:use-module (guix gexp)
  #:use-module (guix packages)
  #:use-module (gnu packages base)          ;; for tar
  #:use-module (gnu packages bash)          ;; for bash
  #:use-module (gnu packages compression)   ;; for gzip
  #:use-module (gnu packages databases)     ;; for python-tortoise-orm
  #:use-module (gnu packages python)
  #:use-module (gnu packages python-web)    ;; for python-tweepy
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

(define mobilizon-reshare-git-origin-with-setup.py
  (computed-file "source"
                 (with-imported-modules '((guix build utils)
                                          (ice-9 string-fun))
                   #~(begin
                       (let ((bash (string-append #$bash "/bin/bash"))
                             (gzip (string-append #$gzip "/bin/gzip"))
                             (poetry (string-append #$poetry "/bin/poetry"))
                             (sed (string-append #$sed "/bin/sed"))
                             (tar (string-append #$tar "/bin/tar"))
                             (tests-script "./scripts/run_pipeline_tests.sh")
                             (origin #$mobilizon-reshare-git-origin))
                         (use-modules (guix build utils)
                                      (ice-9 string-fun))
                         (copy-recursively origin ".")
                         ;; This is an hack to obtain poetry's setup.py.
                         (setenv "POETRY_VIRTUALENVS_CREATE" "false")
                         (invoke poetry "build" "-f" "sdist")
                         (invoke bash "-c"
                                 (string-append "cd dist && "
                                                gzip " -cd ./*-`" poetry " version -s`.tar.gz > out.tar"))
                         (invoke bash "-c"
                                 (string-append
                                  tar " --wildcards -xvf dist/out.tar -O '*/setup.py' > setup.py"))
                         ;; Reduce source size.
                         (delete-file-recursively "dist")
                         (invoke sed "-i" "-E" (string-append "s/poetry/" (string-replace-substring poetry "/" "\\/") "/") tests-script)
                         (copy-recursively "." #$output))))))

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
      (source mobilizon-reshare-git-origin-with-setup.py)
      (native-inputs
       (modify-inputs (package-native-inputs mobilizon-reshare)
         (prepend python-httpx python-fastapi)))
      (propagated-inputs
       (modify-inputs (package-propagated-inputs mobilizon-reshare)
         (prepend python-asyncpg python-uvicorn)
         (replace "python-aerich"
                   python-aerich)
         (replace "python-click"
                   python-click)
         (replace "dynaconf"
                   dynaconf-3.1.11)
         (replace "python-facebook-sdk"
                   python-facebook-sdk)
         (replace "python-requests"
                   python-requests)
         (replace "python-tweepy"
                   python-tweepy)
         (replace "python-tortoise-orm"
                   python-tortoise-orm))))))

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

mobilizon-reshare.git
