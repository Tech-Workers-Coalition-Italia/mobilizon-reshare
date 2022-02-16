(use-modules (guix channels))

(list
 (channel
  (name 'guix)
  (url "https://git.savannah.gnu.org/git/guix.git")
  (commit
   "1121fa432f0e6422d5f9ebb96fb0014c4d5231f5")
  (introduction
   (make-channel-introduction
    "41000d16c5c1586482a76d856c3152a6b8fcce8a"
    (openpgp-fingerprint
     "BBB0 2DDF 2CEA F6A8 0D1D  E643 A2A0 6DF2 A33A 54FA")))))
