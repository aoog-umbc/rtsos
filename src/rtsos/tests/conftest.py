from pytest import fixture

from zhai_rt import rt_PHMX


@fixture(scope="session")
def phmx_cache_dir(pytestconfig):
    return pytestconfig.cache.mkdir("phmx")


@fixture(scope="session")
def phmx_tmp_default(phmx_cache_dir):
    path = phmx_cache_dir / "default.nc"
    rt_PHMX.main(["--pre", str(path)])
    yield path
    path.unlink()


@fixture(scope="session")
def phmx_cache_output(phmx_tmp_default):
    path = phmx_tmp_default.parent / "output.nc"
    if not path.exists():
        rt_PHMX.main(
            [
                str(phmx_tmp_default),
                str(path),
            ],
        )
        for item in path.parent.glob("**/*.infile.txt"):
            item.unlink()
    return path
