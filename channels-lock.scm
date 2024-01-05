(define-module (channels-lock)
  #:use-module (guix channels))

;; Build history

;; 11068:d513d4ca532f376a47a1fc018736292601c81539 -> NOT OK (dependencies)
;; 16604:06cd4e761ef5f17fe7c9471f4834fd4893e730cc -> NOT OK (dependencies)
;; 19372:df5a358f67e729116e8176b8489092cd9e499bf5 -> OK
;; 22139:79a3cd34c0318928186a04b6481c4d22c0051d04 -> OK

(list
 (channel
  (name 'mobilizon-reshare)
  (url "https://git.sr.ht/~fishinthecalculator/mobilizon-reshare-guix")
  (branch "main"))
 (channel
  (name 'guix)
  (url "https://git.savannah.gnu.org/git/guix.git")
  (commit
   "df5a358f67e729116e8176b8489092cd9e499bf5")
  (introduction
   (make-channel-introduction
    "afb9f2752315f131e4ddd44eba02eed403365085"
    (openpgp-fingerprint
     "BBB0 2DDF 2CEA F6A8 0D1D  E643 A2A0 6DF2 A33A 54FA")))))
