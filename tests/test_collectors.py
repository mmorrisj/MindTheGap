from mindthegap.cli import parse_requirements
from mindthegap.collectors import depsdev, github, pypi


def test_find_github_repo_normalizes():
    assert pypi.find_github_repo(["https://github.com/psf/requests.git"]) == "https://github.com/psf/requests"
    assert pypi.find_github_repo(["https://github.com/psf/requests/issues"]) == "https://github.com/psf/requests"
    assert pypi.find_github_repo(["https://github.com/sponsors/bob", "https://docs.x.io"]) is None


def test_pypi_parse_ignores_yanked_and_prefers_source_url():
    payload = {
        "info": {
            "name": "x",
            "version": "2.0",
            "summary": None,
            "home_page": "https://github.com/wrong/home",
            "project_urls": {"Homepage": "https://x.dev", "Source": "https://github.com/right/x"},
        },
        "releases": {
            "1.0": [{"upload_time_iso_8601": "2020-01-01T00:00:00.000000Z"}],
            "2.0": [{"upload_time_iso_8601": "2024-01-01T00:00:00.000000Z", "yanked": True}],
            "empty": [],
        },
    }
    s = pypi.parse(payload)
    assert s.last_release_at.year == 2020
    assert s.release_count == 2
    assert s.repo_url == "https://github.com/right/x"


def test_github_parse_concentration():
    s = github.parse({"pushed_at": "2025-01-01T00:00:00Z", "archived": True}, [{"contributions": 9}, {"contributions": 1}])
    assert s.archived and s.contributor_count == 2 and s.top_contributor_share == 0.9


def test_depsdev_parse():
    assert depsdev.parse({"dependentCount": 12}) == 12
    assert depsdev.parse({}) is None


def test_parse_requirements():
    text = "requests>=2\n# c\n-r other.txt\nFoo_Bar[extra]==1 ; python_version>'3'\ngit+https://x\nrequests\n"
    assert parse_requirements(text) == ["requests", "foo-bar"]
