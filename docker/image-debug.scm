(define-module (docker image-debug)
  #:use-module (gnu)
  #:use-module (gnu packages base)          ;; for coreutils
  #:use-module (gnu packages bash)          ;; for bash
  #:use-module (gnu packages gawk)          ;; for gawk
  #:use-module (gnu packages less)          ;; for less
  #:use-module (gnu services base)          ;; for special-file-service-type
  #:use-module (docker image))          ;; for special-file-service-type

(operating-system
  (inherit mobilizon-reshare-docker-image)
  (packages
   (list
    coreutils
    findutils
    less
    grep
    gawk
    sed))

  (services
    (append
     %mobilizon-reshare-services
     (list
      (service special-files-service-type
               `(("/bin/sh" ,(file-append bash "/bin/bash"))))))))
