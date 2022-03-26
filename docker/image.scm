(define-module (docker image)
  #:use-module (guix build-system python)
  #:use-module (guix gexp)                  ;; for #$ and #~
  #:use-module (guix packages)
  #:use-module (docker mobilizon-reshare)   ;; for mobilizon-reshare.git
  #:use-module (gnu packages python))

(define-public mobilizon-reshare-scheduler
 (package (inherit mobilizon-reshare.git)
   (name "mobilizon-reshare-scheduler")
   (build-system python-build-system)
   (arguments
    `(#:phases
      (modify-phases %standard-phases
        (delete 'configure)
        (delete 'build)
        (delete 'check)
        (replace 'install
          (lambda* (#:key outputs #:allow-other-keys)
            (let ((bin (string-append (assoc-ref outputs "out")
                                      "/bin")))
              (mkdir-p bin)
              (install-file "scripts/scheduler.py" bin)))))))
   (propagated-inputs (list mobilizon-reshare.git
                            python-apscheduler))
   (synopsis "Mobilizon Reshare's scheduler")
   (description "This script is intended to start a scheduler
running @code{mobilizon-reshare}.")))
