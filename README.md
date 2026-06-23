<a id="readme-top"></a>

<div align="center">
  <h3 align="center">type-4-me</h3>

  <p align="center">
    Small Python app that types pasted code into another window.
    <br />
    <a href="https://github.com/hsmith56/type-4-me">View Project</a>
    ·
    <a href="https://github.com/hsmith56/type-4-me/issues">Report Bug</a>
  </p>
</div>

## About The Project

type-4-me is a lightweight Tkinter desktop tool for typing text/code into a focused target window. It can format Python or JSON, manage multiple tabs, control typing speed, and stop when focus changes.

### Built With

* Python
* Tkinter
* Windows `SendInput`
* uv

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

* Windows
* Python 3.14+
* [uv](https://docs.astral.sh/uv/)

### Installation

```sh
git clone https://github.com/hsmith56/type-4-me.git
cd type-4-me
uv sync
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

Run app:

```sh
uv run type-4-me
```

Or:

```sh
uv run python main.py
```

Basic flow:

1. Paste text or code into editor.
2. Choose `python` or `json` if formatting is needed.
3. Set typing speed with CPS slider.
4. Click **Start Typing**.
5. Focus target window within 3 seconds.
6. Click **Stop** or switch focus to cancel.

Shortcuts:

* `Ctrl+N` — new tab
* `Ctrl+W` — close tab
* `Ctrl+Tab` — next tab
* `Ctrl+Shift+Tab` — previous tab

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap

- [x] Tabbed editor
- [x] Python/JSON formatting
- [x] Adjustable typing speed
- [ ] Package Windows executable

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

1. Fork project
2. Create branch (`git checkout -b feature/my-feature`)
3. Commit changes (`git commit -m "Add my feature"`)
4. Push branch (`git push origin feature/my-feature`)
5. Open pull request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Project Link: [https://github.com/hsmith56/type-4-me](https://github.com/hsmith56/type-4-me)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
