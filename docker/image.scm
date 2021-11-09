(define-module (docker image)
  #:use-module (gnu)
  #:use-module (guix gexp)                  ;; for #$ and #~
  #:use-module (docker mobilizon-reshare)   ;; for mobilizon-reshare.git
  #:use-module (docker service)             ;; for mobilizon-reshare-service-type
  #:use-module (gnu services mcron))        ;; for mcron

(define mobilizon-reshare-job
  ;; Run mobilizon-reshare every 15th minute.
  #~(job "*/15 * * * *"
         (string-append
          #$mobilizon-reshare.git
          "/bin/mobilizon-reshare start > /proc/1/fd/1 2>/proc/1/fd/2")
         "mobilizon-reshare-start"
         #:user "root"))

(define-public %mobilizon-reshare-services
  (list
    (service mobilizon-reshare-service-type)
    (service mcron-service-type)
    (simple-service 'mobilizon-reshare-cron-jobs
                    mcron-service-type
                    (list mobilizon-reshare-job))))

(define-public mobilizon-reshare-docker-image
  (operating-system
    (locale "it_IT.utf8")
    (timezone "Europe/Rome")
    (keyboard-layout
     (keyboard-layout "it" "nodeadkeys"))

    (bootloader
     (bootloader-configuration
      (bootloader grub-bootloader)))

    (file-systems
     (list
      (file-system
        (mount-point "/")
        (device "/dev/fake")
        (type "ext4"))))

    (host-name "mobilizon-reshare-scheduler")

    (packages
     (list))

    (services
     %mobilizon-reshare-services)))

mobilizon-reshare-docker-image
