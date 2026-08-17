# Changelog

## v2.3.9
- Major speedup: course data (ids, metadata, stats, coupon validity) is now
  pre-fetched in parallel (8 workers) before enrollment instead of sequentially
  per course. Measured: ~8x faster enrollment prep (6.5 min -> 49 s for 300
  courses at 0.4s/request latency)
- Scraping tuned: more workers on detail-fetch sites + dead sites removed.
  Measured: 2.9x faster full scrape (92 s -> 32 s) with 64% more courses
  (1070 -> 1755)
- Trending focus: when student-count filters are active, most-enrolled
  (best-selling) courses are enrolled first
- Live progress in CLI/GUI during the pre-fetch phase

## v2.3.8
- Added FreebiesGlobal coupon site (verified working, ~290 coupons per run)
- Added student count filters (min/max students enrolled, 0 = off)
- Added review count filters (min/max reviews, 0 = off)
- New filters fetch stats via Udemy API; if stats can't be fetched the course is NOT excluded
- Confirmed settings list covers all 13 official Udemy categories
- GUI: new "Student Count Filter" and "Review Count Filter" panels in Advanced tab

## v2.3.7
- Fixed 504/503 responses being falsely counted as enrollment success (now verifies via API)
- Removed `exit()` calls that killed the whole app on Udemy throttling; retry-after is now respected
- One failing course no longer stops the entire enrollment run
- Fixed `check_course` crash when course data fetch fails
- Fixed E-next scraper crash on missing enroll link
- Fixed `fetch_page` returning None and crashing scrapers
- Fixed broken case-insensitive title exclusion filter
- Fixed GUI category/language checkboxes being dropped from layout
- Fixed GUI pending counter showing 0/20 instead of actual batch size 5
- Fixed log file being wiped on every start (mode=a for rotation)
- Removed hardcoded cookies from Course Joiner scraper
- Fixed stale Course Joiner category id (74 -> 1000)
- Disabled dead scrapers (Course Vania, IDownloadCoupons) - sites no longer expose public coupons
- Removed Tutorial Bar from settings (scraper disabled)
- Fixed update check hanging at startup; added timeouts everywhere
- Added clean LoginException when Udemy blocks login
- Deleted dead old_cli.py and colors.py
- Added unit tests (tests/test_base.py)

## v2.3.6
- Fix settings and log file not saving

## v2.3.5
- Fixed `IDownloadCoupons`


## v2.3.4

- Remove unnecessary key bindings from login window
- Fixed Some scrappers
- Fixed Errors during enrollment
- Optimized enrollment process
- Fixed few edge cases where the course was already enrolled but not detected

## v2.3.3

- Improved all scrapers for better performance.
- Added `Courson` as a new coupon source
- Added `Course Joiner` as a new coupon source
- Added Course class for better course management
- Added better error handling and logging
- Added Vietnamese language support
- Implemented bulk checkout for more efficient enrollment
- Improved CLI with rich text interface and live progress displays
- Enhanced GUI with detailed enrollment statistics
- Fixed RealDiscount again
- Fixed minor bugs and optimizations

## v2.3.2

- Fixed `RealDiscount`
- Tried to reduce throttling


## v2.3.1

- Fixed missing color in print
- Improve update checker
- Improved Already enrolled course detection


## v2.3

- Removed getting settings from github is file not found. Default settings will be included in exe.
- Changed Manual Login API
- Fixed `TutorialBar`
- Fixed Error for Courses that are no longer accepting new enrollments
- Refactored some code

## v2.2

- Fixed `CourseVania`
- Refactored code
- Added Course last Updated filter

## v2.1

- Fixed Scrappers
- Optimized some code
- Fixed multiple issues
- Hopefully all known errors are fixed
- CLI now supports Browser Cookie Login (Can be changed in settings)

## v2.0

- Fix Retrying error

## v1.9

- Potential fix for Manual Login
- Fixed error on encountering free course with coupons
- Fixed IDownloadCoupons
- Added support for Urdu and Nepali language

## v1.8

- Refactored code
- Fixed Course not enrolling
- Fixed real discount
- Fixed enext
- Fixed coursevania
- Fixed Manual Login
- Fixed scrapers
- Fixed a lot of things
- Removed Colab Version because Login not possible

## v1.7

- Fixed Auto-Login

## v1.6

- Fixed Login issues
- Fixed `CourseVania`
- Fixed Enrolling
- Some minor fixes

## v1.5

- Fixed login problem.
- Fixed my ego.

## v1.4

- Added `e-next.in`
- Added Discounted only filter
- Hopeful fix for `Amount saved` not showing
- Hopeful fix for Manual login
- Fixed not saving courses to file on unexpected exit.
- Simplified some logic

## v1.3

- Added Save to txt file option in CLI and GUI
- Fixed some logic

## v1.2

- Fixed RealDiscount and CourseVania

## v1.1

- Fixed RealDiscount and CourseVania
- Added Russian Language filter

## v1.0

- Fresh start
