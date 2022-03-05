(define-module (docker mobilizon-reshare)
  #:use-module (guix download)
  #:use-module (guix gexp)
  #:use-module (guix git-download)
  #:use-module (guix packages)
  #:use-module (guix transformations)
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

(define-public python-pypika-tortoise-0.1.3
  (package (inherit python-pypika-tortoise)
   (version "0.1.3")
   (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "pypika-tortoise" version))
       (sha256
         (base32 "066jb88f3hk42sks69gv6w7k5irf6r0ssbly1n41a3pb19p2vpzc"))))))

(define-public python-tortoise-orm-0.18.1
  (package (inherit python-tortoise-orm)
   (version "0.18.1")
   (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "tortoise-orm" version))
       (sha256
         (base32 "1c8xq3620z04i1yp8n6bfshi98qkjjydkbs3zld78a885p762wsk"))))
   (arguments
    `(#:tests? #f
      #:phases
      (modify-phases %standard-phases
        (delete 'sanity-check))))
   (propagated-inputs
    (modify-inputs (package-propagated-inputs python-tortoise-orm)
     (replace "python-pypika-tortoise" python-pypika-tortoise-0.1.3)))))

(define-public python-aerich
  (package
    (name "python-aerich")
    (version "0.6.2")
    (source
      (origin
        (method url-fetch)
        (uri (pypi-uri "aerich" version))
        (sha256
          (base32 "1r4xqw9x0fvdjbd36riz72n3ih1p7apv2p92lq1h6nwjfzwr2jvq"))))
    (build-system python-build-system)
    (propagated-inputs
      (list python-asyncmy
            python-asyncpg
            python-click
            python-ddlparse
            python-dictdiffer/fixed
            python-pytz
            python-pypika-tortoise-0.1.3
            python-tomlkit
            python-tortoise-orm-0.18.1))
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

(define-public python-apscheduler-for-telegram-bot
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
      (list python-apscheduler-for-telegram-bot
            python-cachetools
            python-certifi
            python-pytz
            python-tornado-6))
    (home-page "https://python-telegram-bot.org/")
    (synopsis "We have made you a wrapper you can't refuse")
    (description "We have made you a wrapper you can't refuse")
    (license #f)))

(define-public python-requests-2.25
 (package (inherit python-requests)
  (version "2.25.1")
  (source
   (origin
     (method url-fetch)
     (uri (pypi-uri "requests" version))
     (sha256
       (base32 "015qflyqsgsz09gnar69s6ga74ivq5kch69s4qxz3904m7a3v5r7"))))))

(define-public python-click-8.0
 (package (inherit python-click)
  (version "8.0.3")
  (source
   (origin
     (method url-fetch)
     (uri (pypi-uri "click" version))
     (sha256
       (base32 "0nybbsgaff8ihfh74nhmng6qj74pfpg99njc7ivysphg0lmr63j1"))))))

(define click-8-instead-of-click-7
  (package-input-rewriting/spec `(("python-click" . ,(const python-click-8.0)))))

(define requests-2.25-instead-of-requests-2.26
  (package-input-rewriting/spec `(("python-requests" . ,(const python-requests-2.25)))))

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
                       "tar --wildcards -xvf dist/*-`poetry version -s`.tar.gz -O '*/setup.py' > setup.py")))
           (replace 'check
             (lambda* (#:key tests? inputs outputs #:allow-other-keys)
               (when tests?
                 (setenv "POETRY_VIRTUALENVS_CREATE" "false")
                 (invoke "./scripts/run_pipeline_tests.sh"))))
           (add-before 'sanity-check 'set-dummy-config
             (lambda _
               ;; This is needed to prevent the tool from
               ;; crashing at startup during the sanity check.
               (setenv "SECRETS_FOR_DYNACONF"
                       (string-append (getcwd)
                                      "/mobilizon_reshare/.secrets.toml")))))))
      (native-inputs
       (list python-iniconfig
             poetry
             python-pytest
             python-pytest-cov
             python-pytest-asyncio
             python-pytest-lazy-fixture
             python-responses))
      (propagated-inputs
       (list (click-8-instead-of-click-7 python-aerich)
             python-aiosqlite
             python-appdirs
             python-arrow
             python-beautifulsoup4
             python-click-8.0
             (click-8-instead-of-click-7 dynaconf)
             (requests-2.25-instead-of-requests-2.26 python-facebook-sdk)
             python-jinja2
             python-markdownify
             python-requests-2.25
             python-telegram-bot
             (requests-2.25-instead-of-requests-2.26 python-tweepy)
             python-tortoise-orm-0.18.1))
      (home-page
       "https://github.com/Tech-Workers-Coalition-Italia/mobilizon-reshare")
      (synopsis
       "Publish Mobilizon events to your social networks")
      (description
       "This package provides a CLI application to publish Mobilizon
events to your social media.")
      (license coopyleft))))
