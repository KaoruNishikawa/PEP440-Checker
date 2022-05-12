def _import_dependencies():
    from poetry.core.version import pep440
    from poetry.core.version.exceptions import InvalidVersion
    return pep440, InvalidVersion

async def import_dependencies():
    try:
        return _import_dependencies()
    except ImportError:
        import micropip
        await micropip.install(["poetry==1.2.0b1"])
        return _import_dependencies()


class PEP440:
    def __init__(self):
        pass

    async def validate_version(self, version):
        pep440, InvalidVersion = await import_dependencies()
        try:
            pep440.PEP440Version.parse(version)
            return True
        except InvalidVersion:
            return False


async def test_version(event):
    version = Element("version-to-test").element.value
    is_valid = await PEP440().validate_version(version)
    pyscript.write(
        "version-test-result",
        f"{version} is" + (" " if is_valid else " not ") + "valid version",
    )

async def main():
    _ = await import_dependencies()

    from js import document
    document.getElementById("loading").style.display = "none"

import asyncio
loop = asyncio.get_event_loop()
_ = loop.run_until_complete(main())