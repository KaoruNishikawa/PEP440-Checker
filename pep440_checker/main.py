import asyncio
from typing import Union

# Pre-loaded objects, reloading them can cause error.
pyscript = pyscript  # noqa: F821
Element = Element  # noqa: F821


def _import_dependencies() -> None:
    global Version, parse_constraint, InvalidVersion, ParseConstraintError
    from poetry.core.semver.version import Version as _Version
    from poetry.core.semver.helpers import parse_constraint as _parse_constraint
    from poetry.core.version.exceptions import InvalidVersion as _InvalidVersion
    from poetry.core.semver.exceptions import (
        ParseConstraintError as _ParseConstraintError,
    )

    Version = _Version
    parse_constraint = _parse_constraint
    InvalidVersion = _InvalidVersion
    ParseConstraintError = _ParseConstraintError


async def import_dependencies() -> None:
    try:
        _import_dependencies()
    except ImportError:
        import micropip

        await micropip.install(["poetry==1.2.0b1"])
        _import_dependencies()


class PEP440:
    async def validate_version(self, version) -> bool:
        try:
            Version.parse(version)
            return True
        except InvalidVersion:
            return False

    async def is_in(self, version, version_range) -> Union[str, bool]:
        try:
            version = Version.parse(version)
            version_range = parse_constraint(version_range)
            return version_range.allows(version)
        except InvalidVersion:
            return f"Invalid version: <code>{version}</code>"
        except ParseConstraintError:
            return f"Invalid version range: <code>{version_range}</code>"


async def test_version(event) -> None:
    version = Element("version-to-test").element.value  # noqa: F821
    is_valid = await PEP440().validate_version(version)
    pyscript.write(
        "version-test-result",
        f"Version <code>{version}</code> is"
        + (" " if is_valid else " not ")
        + "valid versioning",
    )


async def test_version_range(event) -> None:
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


async def main() -> None:
    await import_dependencies()

    from js import document

    document.getElementById("loading").style.display = "none"


loop = asyncio.get_event_loop()
_ = loop.run_until_complete(main())
