# Windows Packaging

This project is developed on macOS, but production users need a Windows-friendly package.

The recommended delivery format is a portable Windows zip:

```text
LyricsConverter-Windows-Portable.zip
  启动歌词转换工具.bat
  使用说明.txt
  python/
  app.py
  convert.py
  lyrics_converter/
  requirements.txt
  test_data/
```

Production users only need to unzip the package and double-click:

```text
启动歌词转换工具.bat
```

## Why GitHub Actions

Windows Python packages should be built on Windows. Building a Windows executable or portable runtime directly on macOS is unreliable for this project because several dependencies include platform-specific wheels.

The workflow at `.github/workflows/build-windows-portable.yml` uses a Windows runner to:

1. Download the official Windows embeddable Python runtime.
2. Install project dependencies into that runtime.
3. Copy the application files.
4. Add the double-click launcher and instructions.
5. Upload `LyricsConverter-Windows-Portable.zip` as a GitHub Actions artifact.

## How To Build

1. Push the project to GitHub.
2. Open the repository on GitHub.
3. Go to `Actions`.
4. Choose `Build Windows Portable Package`.
5. Click `Run workflow`.
6. Download the artifact named `LyricsConverter-Windows-Portable`.

## Local Windows Build

If you are already on Windows, the same workflow steps can be followed manually:

```powershell
python -m pip install -r requirements.txt
python convert.py --list-modes
streamlit run app.py
```

For production delivery, prefer the GitHub Actions package so users do not need to install Python.
