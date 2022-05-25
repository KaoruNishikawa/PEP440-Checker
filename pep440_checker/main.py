import asyncio

pyscript = pyscript  # noqa: F821
Element = Element  # noqa: F821


def _import_dependencies():
    from poetry.core.semver.version import Version
    from poetry.core.semver.helpers import parse_constraint
    from poetry.core.version.exceptions import InvalidVersion
    from poetry.core.semver.exceptions import ParseConstraintError
    return Version, parse_constraint, InvalidVersion, ParseConstraintError


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
        Version, _, InvalidVersion, _ = await import_dependencies()
        try:
            Version.parse(version)
            return True
        except InvalidVersion:
            return False

    async def is_in(self, version, version_range):
        (
            Version, parse_constraint, InvalidVersion, ParseConstraintError
        ) = await import_dependencies()
        try:
            version = Version.parse(version)
            version_range = parse_constraint(version_range)
            return version_range.allows(version)
        except InvalidVersion:
            return f"Invalid version: '{version}'"
        except ParseConstraintError:
            return f"Invalid version range: '{version_range}'"


async def test_version(event):
    version = Element("version-to-test").element.value  # noqa: F821
    is_valid = await PEP440().validate_version(version)
    pyscript.write(
        "version-test-result",
        f"Version <code>{version}</code> is"
        + (" " if is_valid else " not ")
        + "valid versioning",
    )


async def test_version_range(event):
    version = Element("version-specification").element.value
    version_range = Element("version-range").element.value
    is_in = await PEP440().is_in(version, version_range)
    if isinstance(is_in, str):
        pyscript.write("version-range-result", is_in)
    else:
        pyscript.write(
            "version-range-result",
            f"Version <code>{version}</code> is"
            + (" " if is_in else " not ")
            + f"in range <code>{version_range}</code>",
        )


async def main():
    _ = await import_dependencies()

    from js import document
    document.getElementById("loading").style.display = "none"


loop = asyncio.get_event_loop()
_ = loop.run_until_complete(main())
