# Upstream release checklist

- [ ] Review the user-visible change and update `CHANGELOG.md`.
- [ ] Keep the version consistent across `pyproject.toml`, AppStream releases, and Snap metadata.
- [ ] Run `python -m unittest discover -s tests -v`, `python -m build`, desktop-file validation, and AppStream validation.
- [ ] For GUI or export changes, run Linux GUI/AT-SPI QA and review the saved CSV/HTML. Verify offline behavior for changes to core operations.
- [ ] Review current AppStream copy and screenshot freshness. Retake Linux window captures when visible UI or decoration changes.
- [ ] Review dependency license, immutable source URL, checksum, and runtime assumptions when dependencies change.
- [ ] Commit the reviewed release state, create the matching `vX.Y.Z` tag, and verify tag CI.
- [ ] Publish GitHub release notes that describe actual user-visible changes and link the source archive.
- [ ] Update factual installation and website preparation notes only when the corresponding distribution or page is live.
