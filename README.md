# statz

**statz** is a cross-platform Python package that fetches **real-time system usage** and **hardware specs** — all wrapped in a simple, clean API.

Works on **macOS**, **Linux**, and **Windows**, and handles OS-specific madness under the hood so you don’t have to.

![statz logo](img/logo.png)

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

## 🗂️ Links
[PyPi Project 🐍](https://pypi.org/project/statz/)

[Github Repository 🧑‍💻](https://github.com/hellonearth311/Statz)

## 📝 Changelog

### v0.4.0 – Temperatures, Top Processes, and Bug Squashing 🔥

- 🌡️ Added temperature monitoring
  - Run ```stats.get_system_temps()``` to get a detailed dictionary of sensors

  - Run ```statz --temp``` to get temps out in the console like this:
    
    ```
    TEMPERATURE Info:
    Actuator: 31.2°C
    Airflow Left: 39.0°C
    Airflow Right: 39.3°C
    Airport: 39.5°C
    Airport 1: 39.5°C
    Battery 1: 33.4°C
    Battery 2: 33.4°C
    Battery 3: 33.4°C
    CPU Efficiency Core 1: 46.8°C
    CPU Efficiency Core 2: 46.3°C
    CPU Efficiency Core 4: 46.1°C
    CPU Performance Core 1: 2.2°C
    CPU Performance Core 2: 1.5°C
    CPU Performance Core 3: 2.2°C
    CPU Performance Core 4: 1.5°C
    CPU Performance Core 5: 2.2°C
    CPU Performance Core 6: 1.5°C
    CPU Performance Core 7: 2.2°C
    CPU Performance Core 8: 1.5°C
    DCIn Air Flow: 8.3°C
    Drive 0 OOBv3 Absolute Raw A: 34.7°C
    Drive 0 OOBv3 Absolute Raw B: 34.9°C
    Drive 0 OOBv3 Max: 34.9°C
    GPU 1: 47.1°C
    GPU 2: 40.3°C
    GPU 3: 40.4°C
    GPU Heatsink 1: 33.0°C
    NAND: 34.9°C
    NAND CH0 temp: 35.0°C
    PMU tcal: 51.82°C
    etc...
    ```
- 🧪 Added top ```n``` processes monitoring
  - Get top ```n``` processes using ```get_top_n_proccesses(n, type)``` where ```type``` = ```"cpu"``` or ```"mem"```.
  - Run ```statz --processes --process-count {process count} --process-type {"cpu", "mem"}``` to get an output like this
    ```
    PROCESSES Info:
      Device 1: {'pid': 107, 'name': 'Python', 'usage': 0.0}
      Device 2: {'pid': 383, 'name': 'loginwindow', 'usage': 0.0}
      Device 3: {'pid': 559, 'name': 'distnoted', 'usage': 0.0}
      Device 4: {'pid': 560, 'name': 'cfprefsd', 'usage': 0.0}
      Device 5: {'pid': 563, 'name': 'UserEventAgent', 'usage': 0.0}
    ```
- 🐞 Squashed some bugs
  - Fixed storage calculation bugs on macOS and Linux
  - Added better exception handling to the program
## 📝 Side Note
If you find any errors on Linux, please report them to me with as much detail as possible as I do not have a Linux machine.
