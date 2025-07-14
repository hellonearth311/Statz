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

### v0.3.1 – CLI Options and Cool Colors 🖥️ 🎨

- ⌨️ Added more CLI Options!
  - Run `statz` from your terminal after install
  - Available flags:
    - `--specs` → show all specs
    - `--usage` → show all usage

    - `--cpu` → show cpu usage/specs
    - `--gpu` → show gpu usage/specs
    - `--ram` → show ram usage/specs
    - `--os` → show os usage/specs
    - `--disk` → show disk usage/specs
    - `--network` → show network usage/specs
    - `--battery` → show battery usage/specs
    
    - `--json` → output result in a clean JSON format
    - `--out` → output result into a JSON file
  - Example: `statz --specs --cpu --gpu --out`
  - Output:
    ```
    File: statz_export_(date)_(time)
    {
      "cpu": {
        "processor": "arm",
        "coreCountPhysical": 12,
        "coreCountLogical": 12,
        "cpuName": "Apple M4 Pro",
        "cpuFrequency": "Unknown"
      },
      "gpu": {
        "error": "GPU information not available on Darwin"
      }
    }
    ```

- 🎨 Colored error mesages!
  - For unsupported types, such as GPU information on MacOS, errors will be printed in red!

