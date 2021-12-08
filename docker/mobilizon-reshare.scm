(define-module (docker mobilizon-reshare)
  #:use-module (guix download)
  #:use-module (guix gexp)
  #:use-module (guix git-download)
  #:use-module (guix packages)
  #:use-module (guix utils)
  #:use-module ((guix licenses) #:prefix license:)
  #:use-module (guix build-system python)
  #:use-module (gnu packages)
  #:use-module (gnu packages check)
  #:use-module (gnu packages databases)
  #:use-module (gnu packages django)
  #:use-module (gnu packages python)
  #:use-module (gnu packages python-build)
  #:use-module (gnu packages python-check)
  #:use-module (gnu packages python-web)
  #:use-module (gnu packages python-xyz)
  #:use-module (gnu packages serialization)
  #:use-module (gnu packages time)
  #:use-module (gnu packages web)
  #:use-module (ice-9 popen)
  #:use-module (ice-9 rdelim)
  #:use-module (srfi srfi-1))

(define %source-dir (getcwd))

(define coopyleft
  (let ((license (@@ (guix licenses) license)))
    (license "Coopyleft"
             "https://wiki.coopcycle.org/en:license"
             "Coopyleft License")))

(define wrap-python3
  (@@ (gnu packages python) wrap-python3))

(define-public python-3.9-wrapper
  (wrap-python3 python-3.9))

;; This is only for mobilizon-bots.git.
(define-public python-arrow-1.1
  (package (inherit python-arrow)
    (name "python-arrow")
    (version "1.1.0")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "arrow" version))
       (sha256
        (base32
         "1n2vzyrirfj7fp0zn6iipm3i8bch0g4m14z02nrvlyjiyfmi7zmq"))))))

;; This is only for mobilizon-bots.git.
(define-public python-tortoise-orm-0.17
  (package (inherit python-tortoise-orm)
    (name "python-tortoise-orm")
    (version "0.17.6")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "tortoise-orm" version))
       (sha256
        (base32
         "0viwmd8773b4bz8119d26wd3qxrdhmafrqd4m8bdz3439gcpq67l"))))))

;; This is only for mobilizon-bots.git.
(define-public python-pytest-asyncio-0.15
  (package (inherit python-pytest-asyncio)
    (name "python-pytest-asyncio")
    (version "0.15.1")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "pytest-asyncio" version))
       (sha256
        (base32
         "0vrzsrg3j1cfd57m0b3r5xf87rslgcs42jya346mdg9bc6wwwr15"))))
    (arguments
     (substitute-keyword-arguments (package-arguments python-pytest-asyncio)
       ((#:tests? _ #f) #f)))))

(define-public python-markdownify
  (package
    (name "python-markdownify")
    (version "0.9.2")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "markdownify" version))
       (sha256
        (base32
         "0zfpzdwkf34spmfr2iwkqch3fi0nnll2v5nghvgnrmazjn4rcxdr"))))
    (build-system python-build-system)
    (arguments
     `(#:tests? #f))
    (native-inputs
     `(("python-pytest" ,python-pytest-6)))
    (propagated-inputs
     `(("python-flake8" ,python-flake8)
       ("python-beautifulsoup4" ,python-beautifulsoup4)
       ("python-six" ,python-six)))
    (home-page
     "http://github.com/matthewwithanm/python-markdownify")
    (synopsis "Convert HTML to markdown.")
    (description "Convert HTML to markdown.")
    (license license:expat)))

(define-public python-ipaddress
  (package
    (name "python-ipaddress")
    (version "1.0.23")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "ipaddress" version))
       (sha256
        (base32 "1qp743h30s04m3cg3yk3fycad930jv17q7dsslj4mfw0jlvf1y5p"))))
    (build-system python-build-system)
    (home-page "https://github.com/phihag/ipaddress")
    (synopsis "IPv4/IPv6 manipulation library")
    (description "IPv4/IPv6 manipulation library")
    (license #f)))

(define-public python-vcrpy
  (package
    (name "python-vcrpy")
    (version "4.1.1")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "vcrpy" version))
       (sha256
        (base32 "16gmzxs3lzbgf1828n0q61vbmwyhpvzdlk37x6gdk8n05zr5n2ap"))))
    (build-system python-build-system)
    (arguments
     `(#:phases
       (modify-phases %standard-phases
         (replace 'check
           (lambda* (#:key tests? outputs #:allow-other-keys)
             (when tests?
               (substitute* "tox.ini"
                 (("AWS_ACCESS_KEY_ID") "PYTHONPATH"))
               (setenv "PYTHONPATH" (string-append ".:" (getenv "PYTHONPATH")))
               ;; These tests require network access.
               (delete-file "tests/unit/test_stubs.py")
               (invoke "pytest" "tests/unit")))))))
    (native-inputs
     `(
       ("python-black" ,python-black)
       ("python-coverage" ,python-coverage)
       ("python-flake8" ,python-flake8)
       ("python-flask" ,python-flask)
       ("python-httplib2" ,python-httplib2)
       ("python-ipaddress" ,python-ipaddress)
       ("python-mock" ,python-mock)
       ("python-pytest" ,python-pytest)
       ("python-pytest-cov" ,python-pytest-cov)
       ("python-pytest-httpbin" ,python-pytest-httpbin)
       ("python-tox" ,python-tox)
       ("python-urllib3" ,python-urllib3)))

    (propagated-inputs
     `(("python-pyyaml" ,python-pyyaml)
       ("python-six" ,python-six)
       ("python-wrapt" ,python-wrapt)
       ("python-yarl" ,python-yarl)))
    (home-page "https://github.com/kevin1024/vcrpy")
    (synopsis
     "Automatically mock your HTTP interactions to simplify and speed up testing")
    (description
     "Automatically mock your HTTP interactions to simplify and speed up testing")
    (license license:expat)))

(define-public python-tweepy
  (package
    (name "python-tweepy")
    (version "4.1.0")
    (source
     (origin
       (method git-fetch)
       (uri
        (git-reference
         (url "https://github.com/tweepy/tweepy")
         (commit (string-append "v" version))))
       (file-name (git-file-name name version))
       (sha256
        (base32
         "1c0paxc38i5jq8i20f9xwv966sap4nnhgnbdxg3611pllnzg5wdv"))))
    (build-system python-build-system)
    (arguments
     `(#:phases
       (modify-phases %standard-phases
         (replace 'check
           (lambda* (#:key tests? inputs outputs #:allow-other-keys)
             (when tests?
               (invoke "python" "-m" "unittest")))))))
    (propagated-inputs
     `(("python-aiohttp" ,python-aiohttp)
       ("python-requests" ,python-requests)
       ("python-requests-oauthlib" ,python-requests-oauthlib)))
    (native-inputs
     `(("python-coveralls" ,python-coveralls)
       ("python-tox" ,python-tox)
       ("python-vcrpy" ,python-vcrpy)))
    (home-page "https://www.tweepy.org/")
    (synopsis "Twitter library for Python")
    (description "Twitter library for Python")
    (license license:expat)))

(define-public python-facebook-sdk
  (package
    (name "python-facebook-sdk")
    (version "3.1.0")
    (source
      (origin
        (method url-fetch)
        (uri (pypi-uri "facebook-sdk" version))
        (sha256
          (base32 "138grz0n6plzdqgi4h6hhszf58bsvx9v76cwj51g1nd3kvkd5g6a"))))
    (build-system python-build-system)
    (propagated-inputs `(("python-requests" ,python-requests)))
    (home-page "https://facebook-sdk.readthedocs.io")
    (synopsis
      "Facebook Graph API client in Python")
    (description
      "This client library is designed to support the Facebook Graph API and
the official Facebook JavaScript SDK, which is the canonical way to implement
Facebook authentication.")
    (license license:asl2.0)))

(define-public python-facebook-sdk.git
  (let ((version (package-version python-facebook-sdk))
        (revision "0")
        (commit "3fa89fec6a20dd070ccf57968c6f89256f237f54"))
      (package (inherit python-facebook-sdk)
        (name "python-facebook-sdk.git")
        (version (git-version version revision commit))
        (source
         (origin
           (method git-fetch)
           (uri
            (git-reference
             (url "https://github.com/mobolic/facebook-sdk")
             (commit commit)))
           (file-name (git-file-name name version))
           (sha256
            (base32
             "0vayxkg6p8wdj63qvzr24dj3q7rkyhr925b31z2qv2mnbas01dmg"))))
        (arguments
         ;; Tests depend on network access.
         `(#:tests? #false)))))

(define-public mobilizon-reshare.git
  (let ((source-version (with-input-from-file
                            (string-append %source-dir
                                           "/mobilizon_reshare/VERSION")
                          read-line))
        (revision "0")
        (commit (read-line
                 (open-input-pipe "git show HEAD | head -1 | cut -d ' ' -f 2"))))
    (package
      (name "mobilizon-reshare.git")
      (version (git-version source-version revision commit))
      (source (local-file %source-dir
                          #:recursive? #t
                          #:select? (git-predicate %source-dir)))
      (build-system python-build-system)
      (arguments
       `(#:python ,python-3.9
         #:phases
         (modify-phases %standard-phases
           (add-after 'unpack 'generate-setup.py
             (lambda* (#:key inputs outputs #:allow-other-keys)
               ;; This is a hack needed to get poetry's
               ;; setup.py.
               (setenv "POETRY_VIRTUALENVS_CREATE" "false")
               (invoke "poetry" "build" "-f" "sdist")
               (invoke "bash" "-c"
                       "tar --wildcards -xvf dist/*-`poetry version -s`.tar.gz -O '*/setup.py' > setup.py")
               (substitute* "setup.py"
                 (("'install_requires': install_requires,") ""))))
           (replace 'check
             (lambda* (#:key tests? inputs outputs #:allow-other-keys)
               (when tests?
                 (invoke "python" "-m" "pytest"
                         ;; This test fails because of the unvendoring
                         ;; of toml from dynaconf and
                         ;; because they depend on system timezone.
                         "-k" "not test_get_settings_failure_invalid_toml and not test_format_event")))))))
      (native-inputs
       `(("python-asynctest" ,python-asynctest)
         ("python-iniconfig" ,python-iniconfig)
         ("poetry" ,poetry)
         ("python-pytest" ,python-pytest-6)
         ("python-pytest-cov" ,python-pytest-cov)
         ("python-pytest-asyncio" ,python-pytest-asyncio-0.15)
         ("python-pytest-lazy-fixture"
          ,python-pytest-lazy-fixture)
         ("python-responses" ,python-responses)
         ("python-wrapper" ,python-3.9-wrapper)))
      (propagated-inputs
       `(("python-aiosqlite" ,python-aiosqlite)
         ("python-appdirs" ,python-appdirs)
         ("python-arrow" ,python-arrow-1.1)
         ("python-beautifulsoup4" ,python-beautifulsoup4)
         ("python-click" ,python-click)
         ("dynaconf" ,dynaconf)
         ("python-facebook-sdk" ,python-facebook-sdk.git)
         ("python-jinja2" ,python-jinja2)
         ("python-markdownify" ,python-markdownify)
         ("python-requests" ,python-requests)
         ("python-tweepy" ,python-tweepy)
         ("python-tortoise-orm" ,python-tortoise-orm-0.17)))
      (home-page
       "https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare")
      (synopsis
       "Publish Mobilizon events to your social networks")
      (description
       "This package provides a CLI application to publish Mobilizon
events to your social media.")
      (license coopyleft))))
