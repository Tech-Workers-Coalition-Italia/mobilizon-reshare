(define-module (docker service)
  #:use-module (gnu services)
  #:use-module (gnu system shadow)
  #:use-module (gnu packages admin)
  #:use-module (guix records)
  #:use-module (guix gexp)
  #:use-module (docker mobilizon-reshare)
  #:export (mobilizon-reshare-service-type
            mobilizon-reshare-configuration
            mobilizon-reshare-configuration?))

(define-record-type* <mobilizon-reshare-configuration>
  mobilizon-reshare-configuration make-mobilizon-reshare-configuration
  mobilizon-reshare-configuration?
  (mobilizon-reshare mobilizon-reshare-configuration-mobilizon-reshare (default mobilizon-reshare.git))
  (datadir mobilizon-reshare-datadir (default "/var/lib/mobilizon-reshare")))

(define %mobilizon-reshare-accounts
  (list (user-group
         (name "mobilizon-reshare")
         (system? #t))
        (user-account
                (name "mobilizon-reshare")
                (comment "Mobilizon Reshare's Service Account")
                (group "mobilizon-reshare")
                (supplementary-groups '("tty"))
                (system? #t)
                (home-directory "/var/empty")
                (shell (file-append shadow "/sbin/nologin")))))

(define (%mobilizon-reshare-activation config)
  "Return an activation gexp for Mobilizon Reshare."
  (let ((datadir (mobilizon-reshare-datadir config)))
    #~(begin
        (use-modules (guix build utils))
        (let* ((user    (getpwnam "mobilizon-reshare"))
               (uid     (passwd:uid user))
               (gid     (passwd:gid user))
               (datadir #$datadir))
          (mkdir-p datadir)
          (chown datadir uid gid)))))

(define mobilizon-reshare-service-type
  (service-type
   (name 'mobilizon-reshare)
   (extensions
    (list (service-extension profile-service-type
                             (compose list mobilizon-reshare-configuration-mobilizon-reshare))
          (service-extension account-service-type
                             (const %mobilizon-reshare-accounts))
          (service-extension activation-service-type
                             %mobilizon-reshare-activation)))
   (default-value (mobilizon-reshare-configuration))))
