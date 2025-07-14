# statz

**statz** is a cross-platform Python package that fetches **real-time system usage** and **hardware specs** — all wrapped in a simple, clean API.

Works on **macOS**, **Linux**, and **Windows**, and handles OS-specific madness under the hood so you don’t have to.

---

## ✨ Features

- 📊 Get real-time CPU, RAM, and disk usage
- 💻 Fetch detailed system specifications (CPU, RAM, OS, etc.)
- 🧠 Automatically handles platform-specific logic
- 🧼 Super clean API — just two functions, no fluff

---

## 📦 Installation

```bash
pip install statz
```

## 📝 Changelog

### v0.3.0 – Command Line Mode 💻

- ✨ Added command-line interface (CLI) support!
  - Run `statz` from your terminal after install
  - Available flags:
    - `--specs` → show all specs
    - `--usage` → show all usage
    - `--json` → output result in a clean JSON format
  - Example: `statz --specs --json`

- 📄 Prep for more CLI functionality in the future, such as getting dedicated specs for CPU, RAM, etc..

