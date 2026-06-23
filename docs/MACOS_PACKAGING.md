# macOS Packaging

There are two macOS launch options:

1. `packaging/macos/启动歌词转换工具.command`
   - Uses a local `.venv`.
   - Requires `python3` on the Mac.

2. `歌词转换工具.app`
   - Built by GitHub Actions with PyInstaller.
   - Includes the Python runtime and project dependencies.
   - Does not require users to install Python.

## Build The App Package

1. Open the GitHub repository.
2. Go to `Actions`.
3. Run `Build macOS App Package`.
4. Download `LyricsConverter-macOS-App`.
5. Unzip it and send the resulting package to Mac users.

Production users open:

```text
歌词转换工具.app
```

## macOS Security Notice

The app is not signed or notarized. On first open, macOS may warn that it cannot verify the developer.

Users can usually open it by:

1. Right-clicking the app.
2. Choosing `Open`.
3. Confirming `Open` again.

For a stricter production environment, the next step would be Apple Developer signing and notarization.
