<a id="readme-top"></a>

<div align="center">
  <h3 align="center">type-4-me</h3>

  <p align="center">
    Windows desktop helper that types prepared text or code into another app.
    <br />
    <a href="https://github.com/hsmith56/type-4-me">View Project</a>
    ·
    <a href="https://github.com/hsmith56/type-4-me/issues">Report Bug</a>
  </p>

  [![MIT License][license-shield]][license-url]
  [![Python][python-shield]][python-url]
</div>

## About The Project

type-4-me is a small Tkinter app for pasting code into one window, then typing it into another window with native Windows keystrokes. It is useful when direct paste is unavailable, blocked, or unreliable.

Current capabilities:

- Tabbed text editor with line numbers
- Python and JSON formatting
- Adjustable characters-per-second typing speed
- Native Windows `SendInput` keystrokes
- Optional smart-tab support for editors that auto-indent
- Stop button plus focus-change cancellation

### Built With

- [![Python][python-shield]][python-url]
- Tkinter
- Windows `SendInput`
- [uv](https://docs.astral.sh/uv/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

- Windows
- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

### Installation

```sh
git clone https://github.com/hsmith56/type-4-me.git
cd type-4-me
uv sync
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Start app:

```sh
uv run type-4-me
```

Alternate entry point:

```sh
uv run python main.py
```

Typical workflow:

1. Paste text or code into editor.
2. Select `python` or `json` when formatting is needed.
3. Click **Format** if needed.
4. Set typing speed with CPS slider.
5. Enable **target supports smart-tab** only when target editor auto-indents after blocks.
6. Click **Start Typing**.
7. Focus target window within 3 seconds.
8. Click **Stop** or switch focus to cancel typing.

Keyboard shortcuts:

- `Ctrl+N`: New tab
- `Ctrl+W`: Close tab
- `Ctrl+Tab`: Next tab
- `Ctrl+Shift+Tab`: Previous tab

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Notes

- Native typing works on Windows only.
- Non-ASCII characters are not supported by current keystroke mapper.
- Tabs are converted to four spaces before typing.
- Typing stops if foreground window changes after typing begins.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Development

Run app during development:

```sh
uv run python main.py
```

Install dependencies from lockfile:

```sh
uv sync
```

No test suite is currently defined in project metadata.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

- [x] Tabbed editor
- [x] Python and JSON formatting
- [x] Adjustable typing speed
- [x] Focus-change cancellation
- [ ] Package Windows executable
- [ ] Add automated tests

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

1. Fork project.
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add my feature"`
4. Push branch: `git push origin feature/my-feature`
5. Open pull request.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Project Link: [https://github.com/hsmith56/type-4-me](https://github.com/hsmith56/type-4-me)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

[license-shield]: https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge
[license-url]: LICENSE
[python-shield]: https://img.shields.io/badge/Python-3.14+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white
[python-url]: https://www.python.org/
