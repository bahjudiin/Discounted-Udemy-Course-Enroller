"""Scrape smoke test: runs all coupon-site scrapers, fails if any site is broken.

Used by the scheduled GitHub Actions job to detect sites that changed their
HTML (scrapers silently return 0 courses otherwise). Read-only: makes no
commits and needs no Udemy credentials.
"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base import Scraper, scraper_dict  # noqa: E402


def main():
    sites = list(scraper_dict.keys())
    s = Scraper(sites)
    threads = [
        threading.Thread(target=getattr(s, scraper_dict[site]), daemon=True)
        for site in sites
    ]
    t0 = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    failures = []
    total = 0
    for site in sites:
        code = scraper_dict[site]
        n = len(getattr(s, f"{code}_data"))
        err = getattr(s, f"{code}_error")
        total += n
        print(f"{site:18s} {n:5d} courses   error={err!r}")
        if err or n == 0:
            failures.append(site)

    print(f"total: {total} courses in {time.time() - t0:.1f}s")
    if failures:
        print(f"FAILED SITES: {', '.join(failures)}")
        return 1
    if total == 0:
        print("FAILED: no courses scraped from any site")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
