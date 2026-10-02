# Human Flatpak package test checklist

No manifest content is provided in this checklist.

- Re-check the latest Flathub-hosted GNOME runtime and SDK immediately before packaging.
- Confirm that every dependency source is available offline, version-pinned, license-reviewed, and hash-verified. Include all transitive dependencies.
- Verify the upstream source archive and its SHA-256 against the actual tagged release.
- Confirm that the MIT license is installed and visible to the runtime metadata validator.
- Build with network unavailable and confirm that the build does not fetch dependencies.
- Use minimal finish permissions; do not request network or broad filesystem access. Check portal access for export.
- Build and install on x86_64; verify aarch64 too if supported by the selected runtime and package sources.
- Run the application through `flatpak-builder` and `flatpak run`; test GUI, CLI, exports, clipboard, and offline operation.
- Run Flathub's current manifest linter and repository linter, then inspect every warning.
- Keep all Flathub submission and reviewer communication human-authored and human-operated.
