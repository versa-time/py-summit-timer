import platform
import plistlib
import subprocess
from pathlib import Path

APP_NAME = "SummitLink"
MAC_BUNDLE_ID = "com.versatime.summitlink"
APPLE_EVENTS_USAGE = (
    "Summit Link needs permission to control Microsoft Excel so it can write "
    "timing records into the selected workbook live."
)


def main() -> int:
    command = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onedir",
        "--name",
        APP_NAME,
    ]
    if platform.system() == "Darwin":
        command.extend(["--osx-bundle-identifier", MAC_BUNDLE_ID])
    command.append("src/summit_link/launcher.py")

    subprocess.run(command, check=True)

    if platform.system() == "Darwin":
        patch_macos_bundle()

    return 0


def patch_macos_bundle():
    plist_path = Path("dist") / f"{APP_NAME}.app" / "Contents" / "Info.plist"
    with plist_path.open("rb") as plist_file:
        plist = plistlib.load(plist_file)

    plist["NSAppleEventsUsageDescription"] = APPLE_EVENTS_USAGE
    plist["CFBundleIdentifier"] = MAC_BUNDLE_ID

    with plist_path.open("wb") as plist_file:
        plistlib.dump(plist, plist_file)

    subprocess.run(
        [
            "codesign",
            "--force",
            "--deep",
            "--sign",
            "-",
            str(plist_path.parents[1]),
        ],
        check=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
