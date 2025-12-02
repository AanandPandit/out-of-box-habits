# HackerOS - Hybrid PyQt5 + C++ Desktop App

A cyberpunk-themed productivity OS with an integrated Perplexity AI chatbot.
Built with Python (PyQt5) for the UI and C++ (PyBind11) for performance-critical modules.

## 🚀 Features
- **Dashboard**: Real-time stats and matrix rain effect (C++ powered).
- **AI Uplink**: Perplexity API chatbot with sliding panel.
- **Task Manager**: To-do list with local persistence.
- **Project Overwatch**: Project tracking with progress bars.
- **Strategy**: Long-term goal planning.

## 🛠️ Prerequisites
- Python 3.8+
- C++ Compiler (MSVC on Windows, GCC/Clang on Linux/Mac)
- CMake 3.10+

## 📦 Installation & Build

### 1. Create Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
pip install pybind11
```

### 3. Build C++ Module
This step compiles the `hacker_utils` C++ module.

```bash
# Create build directory
mkdir build
cd build

# Configure and Build
cmake ..
cmake --build . --config Release

# Verify the .pyd (Windows) or .so (Linux) file is in src/core/
```
*Note: If the build fails, the app will automatically fallback to Python implementations.*

### 4. Run the App
```bash
# Return to root
cd ..
python main.py
```

## 🔑 API Key
The app uses a placeholder Perplexity API key. To use your own:
1. Open `python/perplexity_chatbot.py`
2. Replace `API_KEY` or set `PERPLEXITY_API_KEY` environment variable.

## 📂 Project Structure
- `src/ui`: PyQt5 widgets and styles.
- `src/core`: Data management and C++ bridge.
- `src/cxx`: C++ source code.
- `python`: Standalone Python modules (Chatbot).
