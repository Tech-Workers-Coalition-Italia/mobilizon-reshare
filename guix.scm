(define-module (guix)
  #:use-module (guix git-download)
  #:use-module (guix build-system python)
  #:use-module (guix gexp)
  #:use-module (guix packages)
  #:use-module (guix utils)
  #:use-module (gnu packages markup)     ;; for python-markdownify
  #:use-module (gnu packages python-web) ;; for python-fastapi-pagination-minimal and uvicorn
  #:use-module (gnu packages python-xyz) ;; for python-apscheduler
  #:use-module (mobilizon-reshare package)
  #:use-module (mobilizon-reshare dependencies)
  #:use-module (ice-9 rdelim)
  #:use-module (ice-9 popen))

(define %source-dir (getcwd))

(define mobilizon-reshare-git-origin
  (local-file %source-dir
              #:recursive? #t
              #:select? (git-predicate %source-dir)))

(define mobilizon-reshare.git
  (let ((source-version (with-input-from-file
                            (string-append %source-dir
                                           "/mobilizon_reshare/VERSION")
                          read-line))
        (revision "0")
        (commit (read-line
                 (open-input-pipe "git show HEAD | head -1 | cut -d ' ' -f 2"))))
    ((package-input-rewriting/spec `(("python-fastapi" . ,(const python-fastapi))
                                     ("python-dotenv" . ,(const python-dotenv-0.13.0))
                                     ("python-uvicorn" . ,(const python-uvicorn))))
     (package (inherit mobilizon-reshare)
       (name "mobilizon-reshare.git")
       (version (git-version source-version revision commit))
       (source mobilizon-reshare-git-origin)
       (propagated-inputs
        (modify-inputs (package-propagated-inputs mobilizon-reshare)
          (replace "python-uvicorn" python-uvicorn)
          (replace "python-fastapi" python-fastapi)
          (replace "python-fastapi-pagination-minimal"
            (package
              (inherit python-fastapi-pagination-minimal)
              (propagated-inputs
               (modify-inputs (package-propagated-inputs python-fastapi-pagination-minimal)
                 (replace "python-fastapi" python-fastapi)))))
          (replace "python-markdownify" python-markdownify)))))))

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
