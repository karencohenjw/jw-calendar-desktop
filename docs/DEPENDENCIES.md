# Dependency inventory

This inventory records upstream sources for a future human packager. It is not a generated package or Flatpak dependency manifest.

## Python application dependency

| Package | Version | License | Source | Source archive | Runtime dependencies |
|---|---:|---|---|---|---|
| `jwcalendar-calendrical` | `0.1.0` | MIT | [Upstream repository](https://github.com/karencohenjw/jwcalendar-calendrical) | [PyPI source archive](https://files.pythonhosted.org/packages/9c/f9/8976f49cc64457dedbe2d1f5b34f785f7dee97875d83ac44b5cf83b60a4b/jwcalendar_calendrical-0.1.0.tar.gz), SHA-256 `fa4530bfe70d0b54f62bde0a0ad871efe6b730d41e4e658166177fd1f87e1881` | None declared for the base package; optional development/test extras are not runtime dependencies. |

PyPI also published a pure-Python wheel for this exact version. Its SHA-256 is `5b7a7f07bb8d03bdc5800d14397e3e0a0886fe0eea7e8907f7ac73b5b1ca0f99`. PyPI does not permit replacing uploaded distribution files for an existing release. The application currently declares only the pinned engine package; Python standard-library modules have no separate package source.

The dependency is not expected to be included in a GNOME runtime and must be provided from its verified source. A future packager must independently verify the archive and license.

## Desktop stack

| Component | Version used by this project | License | Upstream | Expected runtime availability |
|---|---|---|---|---|
| Python | 3.10+ | PSF-2.0 | [python.org](https://www.python.org/) | Common GNOME base component; verify the selected runtime. |
| PyGObject (`gi`) | GTK bindings supplied by the OS | LGPL-2.1-or-later | [GNOME PyGObject](https://gitlab.gnome.org/GNOME/pygobject) | Availability varies by runtime. The Snap uses the core24 `python3-gi` package plus the GNOME extension. A Flatpak packager must verify or build a compatible binding. |
| GTK | GTK 4.10+; Ubuntu 24.04 CI uses GTK 4.14 series | LGPL-2.1-or-later | [GTK](https://gitlab.gnome.org/GNOME/gtk) | GTK 4.10 provides the asynchronous `Gtk.FileDialog` API used for export. GTK 4 is supplied by the GNOME platform runtime. |
| libadwaita | 1.4+ | LGPL-2.1-or-later | [libadwaita](https://gitlab.gnome.org/GNOME/libadwaita) | Supplied by a compatible GNOME runtime. |
| GLib / GIO | OS/runtime version | LGPL-2.1-or-later | [GLib](https://gitlab.gnome.org/GNOME/glib) | Supplied by GTK/GNOME runtime. |

There are no network calls in the calendar core. GUI toolkit libraries are not Python package dependencies in `pyproject.toml`; they are installed from the Linux distribution or supplied by the desktop runtime.

## Flathub Python source workflow research

Flathub maintains the `flatpak-builder-tools` project, which includes `flatpak-pip-generator` for translating Python package inputs into offline build sources. A human packager should select and read the current tool documentation, review every resolved source, version, license and hash, and ensure the eventual build works with network disabled. The AI did not run the generator and did not create a dependency manifest.
