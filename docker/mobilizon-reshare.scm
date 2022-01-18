(define-module (docker mobilizon-reshare)
  #:use-module (guix download)
  #:use-module (guix gexp)
  #:use-module (guix git-download)
  #:use-module (guix packages)
  #:use-module (guix utils)
  #:use-module ((guix licenses) #:prefix license:)
  #:use-module (guix build-system python)
  #:use-module (gnu packages check)
  #:use-module (gnu packages databases)
  #:use-module (gnu packages markup)
  #:use-module (gnu packages openstack)
  #:use-module (gnu packages python-build)
  #:use-module (gnu packages python-check)
  #:use-module (gnu packages python-crypto)
  #:use-module (gnu packages python-web)
  #:use-module (gnu packages python-xyz)
  #:use-module (gnu packages qt)
  #:use-module (gnu packages time)
  #:use-module (ice-9 popen)
  #:use-module (ice-9 rdelim)
  #:use-module (srfi srfi-1))

(define %source-dir (getcwd))

(define coopyleft
  (let ((license (@@ (guix licenses) license)))
    (license "Coopyleft"
             "https://wiki.coopcycle.org/en:license"
             "Coopyleft License")))

;; This comes from Guix commit ef347195278eb160ec725bbdccf71d67c0fa4271
(define python-asynctest-from-the-past
  (package
    (name "python-asynctest")
    (version "0.13.0")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "asynctest" version))
       (sha256
        (base32
         "1b3zsy7p84gag6q8ai2ylyrhx213qdk2h2zb6im3xn0m5n264y62"))))
    (build-system python-build-system)
    (arguments
     '(#:tests? #f))
    (home-page "https://github.com/Martiusweb/asynctest")
    (synopsis "Extension of unittest for testing asyncio libraries")
    (description
     "The package asynctest is built on top of the standard unittest module
and cuts down boilerplate code when testing libraries for asyncio.")
    (license license:asl2.0)))

;; After core-updates-freeze merge poetry stopped building.
;; We pin the version based on old master until it'll be fixed.
(define python-os-testr/fixed
  (package
    (inherit python-os-testr)
    (native-inputs
     (modify-inputs (package-native-inputs python-os-testr)
       (prepend python-testrepository)))))

(define python-msgpack-transitional/fixed
  (package
    (inherit python-msgpack-transitional)
    (arguments
     (substitute-keyword-arguments (package-arguments python-msgpack-transitional)
      ((#:phases phases)
       `(modify-phases ,phases
          (delete 'check)))))))

(define-public poetry/pinned
  (let ((transform
         (package-input-rewriting/spec `(("python-msgpack-transitional" .
                                          ,(const python-msgpack-transitional/fixed))
                                         ("python-os-testr" .
                                          ,(const python-os-testr/fixed))))))
    (transform poetry)))

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
           (lambda* (#:key tests? #:allow-other-keys)
             (when tests?
               (invoke "python" "-m" "unittest")))))))
    (propagated-inputs
     (list python-aiohttp python-requests python-requests-oauthlib))
    (native-inputs
     (list python-coveralls python-tox python-vcrpy))
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

(define-public python-ddlparse
  (package
    (name "python-ddlparse")
    (version "1.10.0")
    (source
      (origin
        (method url-fetch)
        (uri (pypi-uri "ddlparse" version))
        (sha256
          (base32 "1nh8m6rxslwk05daxshxmgk41qfp18yynydba49b13l4m8dnh634"))))
    (build-system python-build-system)
    (arguments
      ;; Tests depend on network access.
      `(#:tests? #false))
    (propagated-inputs (list python-pyparsing))
    (home-page "http://github.com/shinichi-takii/ddlparse")
    (synopsis "DDL parase and Convert to BigQuery JSON schema")
    (description "DDL parase and Convert to BigQuery JSON schema")
    (license #f)))

(define-public python-dictdiffer/fixed
  (package (inherit python-dictdiffer)
    (arguments
     (substitute-keyword-arguments (package-arguments python-send2trash)
      ((#:phases phases)
       `(modify-phases ,phases
          (delete 'check)))))))

(define-public python-aerich
  (package
    (name "python-aerich")
    (version "0.6.1")
    (source
      (origin
        (method url-fetch)
        (uri (pypi-uri "aerich" version))
        (sha256
          (base32 "19bvx5icsmmf9ylxyqrxw4wjv77shg5r8pjgdg7plzhn937bzlch"))))
    (build-system python-build-system)
    (propagated-inputs
      (list python-asyncmy
            python-asyncpg
            python-click
            python-ddlparse
            python-dictdiffer/fixed
            python-tomlkit
            python-tortoise-orm))
    (home-page "https://github.com/tortoise/aerich")
    (synopsis "A database migrations tool for Tortoise ORM.")
    (description
      "This package provides a database migrations tool for Tortoise ORM.")
    (license #f)))

(define-public python-pytest-tornado5
  (package
    (name "python-pytest-tornado5")
    (version "2.0.0")
    (source
      (origin
        (method url-fetch)
        (uri (pypi-uri "pytest-tornado5" version))
        (sha256
          (base32 "0qb62jw2w0xr6y942yp0qxiy755bismjfpnxaxjjm05gy2pymr8d"))))
    (build-system python-build-system)
    (propagated-inputs (list python-pytest python-tornado))
    (home-page "https://github.com/vidartf/pytest-tornado")
    (synopsis
      "Fixtures and markers to simplify testing of Tornado applications")
    (description
      "This package provides a @code{py.test} plugin providing fixtures and markers to
simplify testing of asynchronous tornado applications.")
    (license license:asl2.0)))

(define-public python-rethinkdb
  (package
    (name "python-rethinkdb")
    (version "2.4.8")
    (source
      (origin
        (method url-fetch)
        (uri (pypi-uri "rethinkdb" version))
        (sha256
          (base32 "1vmap0la5j8xpigyp5bqph9cb6dskyw76y37n3vb16l9rlmsfxcz"))))
    (build-system python-build-system)
    (arguments
     `(#:tests? #f))
    (propagated-inputs (list python-six))
    (home-page "https://github.com/RethinkDB/rethinkdb-python")
    (synopsis "Python driver library for the RethinkDB database server.")
    (description "Python driver library for the RethinkDB database server.")
    (license #f)))

(define-public python-apscheduler
  (package
    (name "python-apscheduler")
    (version "3.8.1")
    (source
      (origin
        (method url-fetch)
        (uri (pypi-uri "APScheduler" version))
        (sha256
          (base32 "0m93bz9qpw6iwhay68bwljjcfyzcbh2rq0lc2yp4iamxrzml9wsw"))))
    (build-system python-build-system)
    (arguments
     `(#:phases
       (modify-phases %standard-phases
         (replace 'check
           (lambda* (#:key tests? #:allow-other-keys)
             (when tests?
               ;; FIXME: Currently python-kazoo fails to build.
               (delete-file "tests/test_jobstores.py")
               (invoke "pytest")))))))
    (propagated-inputs
      (list python-pytz
            python-setuptools
            python-six
            python-tzlocal))
    (native-inputs
      (list python-mock
            python-pyqt
            python-twisted
            python-gevent
            python-setuptools-scm
            python-sqlalchemy
            python-redis
            python-pymongo
            python-rethinkdb
            python-pytest
            python-pytest-asyncio
            python-pytest-cov
            python-pytest-tornado5))
    (home-page "https://github.com/agronholm/apscheduler")
    (synopsis "In-process task scheduler with Cron-like capabilities")
    (description "In-process task scheduler with Cron-like capabilities")
    (license license:expat)))

(define-public python-apscheduler-3.6.3
  (package (inherit python-apscheduler)
   (version "3.6.3")
   (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "APScheduler" version))
       (sha256
         (base32 "0i72qpqgrgq6bb9vwsac46m7bqb6mq92g5nf2gydmfvgxng25d9v"))))))

(define-public python-telegram-bot
  (package
    (name "python-telegram-bot")
    (version "13.10")
    (source
      (origin
        (method url-fetch)
        (uri (pypi-uri "python-telegram-bot" version))
        (sha256
          (base32 "0ghyq044s0zi67hxwxdjjfvh37wr86pi5kmpq7harx11311mbifj"))))
    (build-system python-build-system)
    (arguments
     ;; FIXME: Most tests require network access. Some of them can
     ;; be run from the git repository but many still fail due
     ;; to vendoring of a seemingly heavily patched urllib3.
     `(#:tests? #f))
    (native-inputs
     (list python-beautifulsoup4
           python-pytest
           python-flaky))
    (propagated-inputs
      (list python-apscheduler-3.6.3
            python-cachetools
            python-certifi
            python-pytz
            python-tornado-6))
    (home-page "https://python-telegram-bot.org/")
    (synopsis "We have made you a wrapper you can't refuse")
    (description "We have made you a wrapper you can't refuse")
    (license #f)))

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
       `(#:phases
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
                         ;; of toml from dynaconf.
                         "-k" "not test_get_settings_failure_invalid_toml"))))
           (add-before 'sanity-check 'set-dummy-config
             (lambda _
               ;; This is needed to prevent the tool from
               ;; crashing at startup during the sanity check.
               (setenv "SECRETS_FOR_DYNACONF"
                       (string-append (getcwd)
                                      "/mobilizon_reshare/.secrets.toml")))))))
      (native-inputs
       ;; This is needed until we switch to tortoise 0.18.*
       (list python-asynctest-from-the-past
             python-iniconfig
             poetry/pinned
             python-pytest
             python-pytest-cov
             python-pytest-asyncio
             python-pytest-lazy-fixture
             python-responses))
      (propagated-inputs
       (list python-aerich
             python-aiosqlite
             python-appdirs
             python-arrow
             python-beautifulsoup4
             python-click
             dynaconf
             python-facebook-sdk.git
             python-jinja2
             python-markdownify
             python-requests
             python-telegram-bot
             python-tweepy
             python-tortoise-orm))
      (home-page
       "https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare")
      (synopsis
       "Publish Mobilizon events to your social networks")
      (description
       "This package provides a CLI application to publish Mobilizon
events to your social media.")
      (license coopyleft))))
