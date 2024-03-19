(define-module (channels-lock)
  #:use-module (guix channels))

(list
 (channel
  (name 'mobilizon-reshare)
  (url "https://git.sr.ht/~fishinthecalculator/mobilizon-reshare-guix")
  (branch "main"))
 (channel
  (name 'guix)
  (url "https://git.savannah.gnu.org/git/guix.git")
  (commit
   "b7eb1a8116b2caee7acf26fb963ae998fbdb4253")
  (introduction
   (make-channel-introduction
    "afb9f2752315f131e4ddd44eba02eed403365085"
    (openpgp-fingerprint
     "BBB0 2DDF 2CEA F6A8 0D1D  E643 A2A0 6DF2 A33A 54FA")))))
