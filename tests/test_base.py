import os
import sys
import time
from decimal import Decimal
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base import Course, LoginException, Scraper, Udemy  # noqa: E402


def test_course_url_normalization():
    c = Course("Test", "https://www.udemy.com/course/python-basics?couponCode=ABC")
    assert c.slug == "python-basics"
    assert c.coupon_code == "ABC"
    assert c.url == "https://www.udemy.com/course/python-basics/?couponCode=ABC"
    assert c.status is False


def test_course_without_coupon():
    c = Course("Test", "https://www.udemy.com/course/django/")
    assert c.coupon_code is None
    assert c.is_coupon_valid is False


def test_course_equality_and_hash():
    a = Course("A", "https://www.udemy.com/course/x/")
    b = Course("B", "https://www.udemy.com/course/x/")
    assert a == b
    assert len({a, b}) == 1


def test_course_invalid_url_slug():
    c = Course("Test", "https://www.udemy.com/")
    assert c.slug in (None, "")


def test_compare_versions():
    u = Udemy("cli")
    assert u.compare_versions("2.3.6", "2.3.6") == 0
    assert u.compare_versions("2.3.5", "2.3.6") == -1
    assert u.compare_versions("2.3.7", "2.3.6") == 1
    assert u.compare_versions("2.4", "2.3.9") == 1
    assert u.compare_versions("2.3", "2.3.0") == 0


def test_cleanup_link_udemy():
    s = Scraper([])
    assert s.cleanup_link("https://www.udemy.com/course/x/") == "https://www.udemy.com/course/x/"


def test_cleanup_link_linksynergy():
    s = Scraper([])
    url = "https://click.linksynergy.com/deeplink?id=abc&mid=123&murl=https%3A%2F%2Fwww.udemy.com%2Fcourse%2Fpython%2F"
    assert s.cleanup_link(url) == "https://www.udemy.com/course/python/"


def test_cleanup_link_unknown_returns_empty():
    s = Scraper([])
    assert s.cleanup_link("https://example.com/whatever") == ""


def test_scraper_skips_unknown_sites():
    s = Scraper(["Real Discount", "Fake Site"])
    assert "Real Discount" in s.sites
    assert "Fake Site" not in s.sites


def test_manual_login_csrf_missing_raises():
    u = Udemy("cli")
    resp = Mock()
    resp.cookies = {}
    resp.text = "blocked"
    with patch("base.requests.Session.get", return_value=resp):
        try:
            u.manual_login("a@b.c", "pw")
            assert False, "should have raised"
        except LoginException as e:
            assert "CSRF" in str(e)


def test_get_session_info_blocked_raises_login_exception():
    u = Udemy("cli")
    u.cookie_dict = {"client_id": "x", "access_token": "y", "csrf_token": "z"}
    resp = Mock()
    resp.status_code = 403
    resp.headers = {"Content-Type": "text/html"}
    with patch("base.requests.Session.get", return_value=resp):
        try:
            u.get_session_info()
            assert False, "should have raised"
        except LoginException as e:
            assert "403" in str(e)


def test_keyword_exclusion_case_insensitive():
    u = Udemy("cli")
    u.settings = {}
    u.title_exclude = ["keyword", "NoT_CaSe"]
    c = Course("Learn KEYWORD One today", "https://www.udemy.com/course/x/")
    u.course = c
    assert u.is_keyword_excluded() is True
    c2 = Course("Learn Crypto trading", "https://www.udemy.com/course/y/")
    u.course = c2
    assert u.is_keyword_excluded() is False


def test_check_course_network_failure_marks_invalid_no_crash():
    u = Udemy("cli")
    u.client = Mock()
    u.client.get.side_effect = RuntimeError("network down")
    c = Course("Test", "https://www.udemy.com/course/x/")
    c.course_id = "1234"
    c.is_free = False
    u.course = c
    with patch("base.time.sleep"):
        u.check_course()
    assert c.is_valid is False
    assert c.error


def test_check_course_coupon_validation():
    u = Udemy("cli")
    u.client = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "purchase": {
            "data": {
                "list_price": {"amount": 89.99},
                "pricing_result": {"discount_percent": 100},
            }
        },
        "redeem_coupon": {"discount_attempts": [{"status": "applied"}]},
    }
    u.client.get.return_value = response
    c = Course("Test", "https://www.udemy.com/course/x/?couponCode=GOOD")
    c.course_id = "1234"
    u.course = c
    u.check_course()
    assert c.is_coupon_valid is True
    assert c.price == Decimal("89.99")


def test_check_course_expired_coupon():
    u = Udemy("cli")
    u.client = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "purchase": {
            "data": {
                "list_price": {"amount": 89.99},
                "pricing_result": {"discount_percent": 0},
            }
        },
        "redeem_coupon": {"discount_attempts": [{"status": "invalid"}]},
    }
    u.client.get.return_value = response
    c = Course("Test", "https://www.udemy.com/course/x/?couponCode=BAD")
    c.course_id = "1234"
    u.course = c
    u.check_course()
    assert c.is_coupon_valid is False


def test_verify_enrollment():
    u = Udemy("cli")
    u.client = Mock()
    enrolled = Mock()
    enrolled.status_code = 200
    enrolled.json.return_value = {"_class": "course"}
    not_enrolled = Mock()
    not_enrolled.status_code = 404
    u.client.get.side_effect = [enrolled, not_enrolled]
    c = Course("Test", "https://www.udemy.com/course/x/")
    c.course_id = "1234"
    assert u.verify_enrollment(c) is True
    assert u.verify_enrollment(c) is False


def test_free_checkout_503_verifies_instead_of_assume_success():
    u = Udemy("cli")
    u.client = Mock()
    five_oh_three = Mock()
    five_oh_three.status_code = 503
    five_oh_three.headers = {}
    u.client.get.return_value = five_oh_three
    c = Course("Test", "https://www.udemy.com/course/x/")
    c.course_id = "1234"
    u.course = c
    with patch.object(u, "verify_enrollment", return_value=False) as verify:
        u.free_checkout()
        assert c.status is False
        verify.assert_called_once()


def test_free_checkout_503_verified_enrolled():
    u = Udemy("cli")
    u.client = Mock()
    five_oh_three = Mock()
    five_oh_three.status_code = 503
    five_oh_three.headers = {}
    u.client.get.return_value = five_oh_three
    c = Course("Test", "https://www.udemy.com/course/x/")
    c.course_id = "1234"
    u.course = c
    with patch.object(u, "verify_enrollment", return_value=True):
        u.free_checkout()
        assert c.status is True


def test_bulk_checkout_504_verifies_and_no_exit():
    u = Udemy("cli")
    u.client = Mock()
    u.currency = "usd"
    u.settings = {"save_txt": False}
    five_oh_four = Mock()
    five_oh_four.status_code = 504
    five_oh_four.headers = {}
    five_oh_four.text = "timeout"
    u.client.post.return_value = five_oh_four
    c = Course("Test", "https://www.udemy.com/course/x/?couponCode=C")
    c.course_id = "1234"
    c.price = 99.99
    c.is_free = False
    u.valid_courses = [c]
    u.enrolled_courses = {}
    with patch.object(u, "verify_enrollment", return_value=True) as verify:
        u.bulk_checkout()
        verify.assert_called_once()
    assert u.successfully_enrolled_c == 1
    assert u.expired_c == 0


def test_bulk_checkout_504_unverified_counts_expired():
    u = Udemy("cli")
    u.client = Mock()
    u.currency = "usd"
    u.settings = {"save_txt": False}
    five_oh_four = Mock()
    five_oh_four.status_code = 504
    five_oh_four.headers = {}
    five_oh_four.text = "timeout"
    u.client.post.return_value = five_oh_four
    c = Course("Test", "https://www.udemy.com/course/x/?couponCode=C")
    c.course_id = "1234"
    c.price = 99.99
    c.is_free = False
    u.valid_courses = [c]
    u.enrolled_courses = {}
    with patch.object(u, "verify_enrollment", return_value=False):
        u.bulk_checkout()
    assert u.successfully_enrolled_c == 0
    assert u.expired_c == 1


def test_bulk_checkout_retry_after_waits_not_exits():
    u = Udemy("cli")
    u.client = Mock()
    u.currency = "usd"
    u.settings = {"save_txt": False}
    throttled = Mock()
    throttled.status_code = 429
    throttled.headers = {"retry-after": "1"}
    throttled.text = "slow down"
    ok = Mock()
    ok.status_code = 200
    ok.headers = {}
    ok.json.return_value = {"status": "succeeded"}
    ok.text = ""
    u.client.post.side_effect = [throttled, ok]
    c = Course("Test", "https://www.udemy.com/course/x/?couponCode=C")
    c.course_id = "1234"
    c.price = 10
    c.is_free = False
    u.valid_courses = [c]
    u.enrolled_courses = {}
    with patch("base.time.sleep"):
        u.bulk_checkout()
    assert u.successfully_enrolled_c == 1


def test_start_new_enroll_survives_course_errors():
    u = Udemy("cli")
    u.settings = {"save_txt": False, "discounted_only": False}
    u.enrolled_courses = {}
    u.currency = "usd"
    bad = Course("Bad", "https://www.udemy.com/course/bad/")
    bad.course_id = "1"
    good = Course("Good", "https://www.udemy.com/course/good/")
    good.course_id = "2"
    good.is_free = True
    good.status = True
    u.scraped_data = [bad, good]
    u.total_courses = 2

    def fake_get_course_id(course=None):
        if course is not None and course.title == "Bad":
            raise RuntimeError("boom")

    with patch.object(u, "get_course_id", side_effect=fake_get_course_id):
        with patch.object(u, "free_checkout"):
            u.start_new_enroll()
    assert u.successfully_enrolled_c == 1
    assert u.excluded_c == 1
    assert u.expired_c == 0


def test_start_new_enroll_sorts_most_enrolled_first():
    u = Udemy("cli")
    u.settings = {"save_txt": False, "discounted_only": False}
    u.enrolled_courses = {}
    u.currency = "usd"
    u.min_students = 100
    u.max_students = 0
    u.min_reviews = 0
    u.max_reviews = 0
    low = Course("Low", "https://www.udemy.com/course/low/")
    low.course_id = "1"
    low.students = 100
    low.is_free = True
    low.status = True
    high = Course("High", "https://www.udemy.com/course/high/")
    high.course_id = "2"
    high.students = 99999
    high.is_free = True
    high.status = True
    u.scraped_data = [low, high]
    u.total_courses = 2
    processed = []

    def spy_free_checkout():
        processed.append(u.course.title)

    def fake_get_course_id(course=None):
        pass

    with patch.object(u, "get_course_id", side_effect=fake_get_course_id):
        with patch.object(u, "free_checkout", side_effect=spy_free_checkout):
            with patch.object(u, "is_already_enrolled", return_value=False):
                u.start_new_enroll()
    assert u.successfully_enrolled_c == 2
    assert processed == ["High", "Low"]


def test_get_date_from_utc():
    u = Udemy("cli")
    assert u.get_date_from_utc("2026-08-17T07:30:00Z") == "August 17, 2026"


def test_students_filter_min_max():
    u = Udemy("cli")
    u.min_students = 100
    u.max_students = 5000
    c = Course("Test", "https://www.udemy.com/course/x/")
    c.course_id = "1234"
    c.students = 50
    u.course = c
    assert u.students_in_range() is False
    c.students = 100
    assert u.students_in_range() is True
    c.students = 5000
    assert u.students_in_range() is True
    c.students = 5001
    assert u.students_in_range() is False


def test_students_filter_off():
    u = Udemy("cli")
    u.min_students = 0
    u.max_students = 0
    u.min_reviews = 0
    u.max_reviews = 0
    c = Course("Test", "https://www.udemy.com/course/x/")
    u.course = c
    assert u.students_in_range() is True
    assert u.reviews_in_range() is True


def test_reviews_filter_min_max():
    u = Udemy("cli")
    u.min_reviews = 10
    u.max_reviews = 1000
    c = Course("Test", "https://www.udemy.com/course/x/")
    c.course_id = "1234"
    c.reviews = 5
    u.course = c
    assert u.reviews_in_range() is False
    c.reviews = 10
    assert u.reviews_in_range() is True
    c.reviews = 1000
    assert u.reviews_in_range() is True
    c.reviews = 1001
    assert u.reviews_in_range() is False


def test_stats_fetch_failure_does_not_exclude():
    u = Udemy("cli")
    u.min_students = 100
    u.max_students = 0
    u.min_reviews = 0
    u.max_reviews = 0
    u.client = Mock()
    resp = Mock()
    resp.status_code = 403
    u.client.get.return_value = resp
    c = Course("Test", "https://www.udemy.com/course/x/")
    c.course_id = "1234"
    u.course = c
    assert u.students_in_range() is True
    assert c.students is None


def test_stats_fetch_success():
    u = Udemy("cli")
    u.min_students = 100
    u.max_students = 0
    u.min_reviews = 0
    u.max_reviews = 0
    u.client = Mock()
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = {"num_subscribers": 12345, "num_reviews": 678}
    u.client.get.return_value = resp
    c = Course("Test", "https://www.udemy.com/course/x/")
    c.course_id = "1234"
    u.course = c
    assert u.students_in_range() is True
    assert c.students == 12345
    assert c.reviews == 678


def test_students_filter_excludes_via_is_course_excluded():
    u = Udemy("cli")
    u.min_students = 1000
    u.max_students = 0
    u.min_reviews = 0
    u.max_reviews = 0
    u.min_rating = 0.0
    u.title_exclude = []
    u.instructor_exclude = []
    u.categories = ["Development"]
    u.languages = ["English"]
    u.settings = {"course_update_threshold_months": 24}
    u.course = Course("Test", "https://www.udemy.com/course/x/")
    u.course.rating = 4.5
    u.course.last_update = "2026-08-01"
    u.course.category = "Development"
    u.course.language = "English"
    u.course.students = 500
    with patch.object(u, "fetch_course_stats"):
        u.is_course_excluded()
    assert u.course.is_excluded is True


def test_settings_migration_adds_filter_defaults():
    u = Udemy("cli")
    u.settings = {
        "sites": {"Courson": True},
        "languages": {"English": True},
        "categories": {"Development": True},
    }
    u.load_settings()
    for key in ("min_students", "max_students", "min_reviews", "max_reviews"):
        assert u.settings.get(key) == 0, key
    assert u.settings["sites"].get("FreebiesGlobal") is True
    assert u.settings["sites"].get("Online Courses") is True


class FakeResp:
    def __init__(self, body):
        self.content = body.encode("utf-8")


OC_PAGE = """
<html><body>
<h2>Python for Beginners</h2>
<a href="https://www.udemy.com/course/python-for-beginners/?couponCode=ABC123">Get Deal</a>
<h2>Django Masterclass</h2>
<a href="https://www.udemy.com/course/django-masterclass/?couponCode=DEF456">Get Deal</a>
<h2>Free Course No Coupon</h2>
<a href="https://www.udemy.com/course/free-course/">Get Deal</a>
</body></html>
"""


def test_oc_scraper_extracts_coupon_links():
    s = Scraper(["Online Courses"])
    with patch.object(s, "fetch_page", return_value=FakeResp(OC_PAGE)):
        s.oc()
    titles = [c.title for c in s.oc_data]
    assert titles == ["Python for Beginners", "Django Masterclass"]
    assert s.oc_data[0].coupon_code == "ABC123"
    assert s.oc_data[1].coupon_code == "DEF456"


def _u_with_dead_cache(u, entries):
    u._dead_cache = entries
    return u


def test_dead_coupon_cache_skips_only_same_slug_and_code():
    u = _u_with_dead_cache(Udemy("cli"), {"x|BAD": 9999999999.0})
    same = Course("A", "https://www.udemy.com/course/x/?couponCode=BAD")
    new_code = Course("A", "https://www.udemy.com/course/x/?couponCode=NEW")
    other_slug = Course("B", "https://www.udemy.com/course/y/?couponCode=BAD")
    no_code = Course("C", "https://www.udemy.com/course/x/")
    assert u._is_dead_coupon_cached(same) is True
    assert u._is_dead_coupon_cached(new_code) is False
    assert u._is_dead_coupon_cached(other_slug) is False
    assert u._is_dead_coupon_cached(no_code) is False


def test_dead_coupon_cache_expires_after_ttl():
    u = _u_with_dead_cache(
        Udemy("cli"), {"x|OLD": time.time() - 25 * 3600}
    )
    c = Course("A", "https://www.udemy.com/course/x/?couponCode=OLD")
    assert u._is_dead_coupon_cached(c) is False


def test_prepare_course_caches_confirmed_dead_only():
    u = Udemy("cli")
    u.enrolled_courses = {}

    def fake_get_course_id(course=None):
        course = course or u.course
        course.course_id = "1234"
        course.is_valid = True

    with patch.object(u, "get_course_id", side_effect=fake_get_course_id):
        u.client = Mock()
        dead_resp = Mock()
        dead_resp.status_code = 200
        dead_resp.json.return_value = {
            "purchase": {
                "data": {
                    "list_price": {"amount": 89.99},
                    "pricing_result": {"discount_percent": 0},
                }
            },
            "redeem_coupon": {"discount_attempts": [{"status": "invalid"}]},
        }
        u.client.get.return_value = dead_resp
        c = Course("Test", "https://www.udemy.com/course/x/?couponCode=BAD")
        with patch("base.time.sleep"):
            u._prepare_course(c)
        assert c.is_valid is True and c.is_coupon_valid is False
        assert u._is_dead_coupon_cached(c) is True

        # network failure must NOT be cached (course just marked invalid)
        u2 = Udemy("cli")
        u2.enrolled_courses = {}
        with patch.object(u2, "get_course_id", side_effect=fake_get_course_id):
            u2.client = Mock()
            u2.client.get.side_effect = RuntimeError("network down")
            c2 = Course("Test", "https://www.udemy.com/course/x/?couponCode=BAD")
            with patch("base.time.sleep"):
                u2._prepare_course(c2)
        assert c2.is_valid is False
        assert u2._is_dead_coupon_cached(c2) is False


def test_start_new_enroll_skips_cached_dead_coupons():
    u = Udemy("cli")
    u.scraped_data = [
        Course("A", "https://www.udemy.com/course/x/?couponCode=DEAD1"),
        Course("B", "https://www.udemy.com/course/y/?couponCode=LIVE1"),
    ]
    u._dead_cache = {"x|DEAD1": 9999999999.0}
    u.enrolled_courses = {}
    u.client = Mock()
    u.settings = {"save_txt": False}
    with patch.object(u, "setup_txt_file"), patch.object(u, "_save_dead_cache"):
        u.start_new_enroll()
    assert u.dead_cache_skipped == 1
    assert u.total_courses == 1


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"\n{len(tests)} tests passed")
