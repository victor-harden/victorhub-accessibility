# victorhub-accessibility

A pragmatic accessibility checker for static HTML. It catches the issues that are
cheap to fix and expensive to miss: missing `lang`, missing `<title>`, images
without `alt`, form fields without labels, empty links and skipped heading levels.

## Features

- Checks `lang`, `<title>`, `img[alt]`, `label`/`aria-label` for inputs,
  heading level jumps, and link text quality.
- Human report with line-independent element paths, or JSON.
- Exit code `1` when errors exist, so it can gate a build.
- Tests with both good and deliberately broken fixtures.

## Installation

```bash
git clone https://github.com/victor-harden/victorhub-accessibility.git
cd victorhub-accessibility
```

## Usage

```bash
python3 a11y.py demo-good.html
python3 a11y.py demo-bad.html --json
python3 a11y.py site/ --recursive
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT — see [LICENSE](LICENSE).
