This thing lets you mount your Google Drive as a network drive on Windows. I
built this mostly so I could watch movies in original quality with embedded sub
on my Surface Go.

It's a happy-path-only proof-of-concept I did during a "hack day" at
[work][work]. To be honest you can achieve all this (and more) with rclone
alone (which I did) but I needed an excuse to try developing and packaging PyQt
software on Windows.

# Windows usage

![drivein-demo](https://user-images.githubusercontent.com/1446315/67615703-b0677b80-f7f9-11e9-8150-ae8c0e55b281.gif)

- Download & install [winfsp][1]
- Download latest [DriveIn Windows build][2], extract and run **launch.bat**:
  + click Authorize, a browser tab should automatically open asking you to give
    DriveIn full access to your Google Drive. You only need to do this once so
    it can generate an **rclone.conf** file.
  + click Mount
  + profit

# Under the hood

This is just a very dumb wrapper around [rclone][3].

The `rclone.exe` and `python.exe` executables are included along with a zippapp
built using [shiv][4]. I should probably use pynsist instead.

# In retrospect

Developing on Windows is not that painful: I got comfortable fast with
[scoop][scoop] and [VS Code][vsc].

Developing _for_ Windows, on the other hand, is not that nice. See, when I try
to gracefully kill the `rclone` subprocess, problems cropped up:

- `subprocess.kill(p.pid, signal.SIGINT)` won't work because Windows doesn't
  speak SIGINT.
- sending a ctrl c interrupt signal somehow leaked to the main process?
- `taskkill` without `/f` doesn't work
- so I ended with Windows-specific, kill-on-sight `taskkill /f`. What could
  possibly go wrong?

Packaging is not ideal. Although `shiv` produces a single zipapp file, the
"embeddable python" distribution has files all over the place.

# Possily better alternatives

- Use [pexpect][pexpect] to manage the `rclone` process
- Distribution alternatives:
  + Make an installer using pynsist. Does it support bundling another arbitrary
    installer (winfsp)?
  + Compile using [nuitka][nuitka]
- Maaaaaaybe PyQt is too fat a dependency. Tk may be a better choice, but then
  I'd lose `QDesktopServices.openUrl()` (python's `webbrowser.open()` results
  in an annoying "Firefox is already running" dialog).

In the meantime I'll keep using plain naked `rclone` for daily use.

[1]: http://www.secfs.net/winfsp/
[2]: https://ci.appveyor.com/project/nhanb/drivein/build/artifacts
[3]: https://rclone.org/
[4]: https://shiv.readthedocs.io/en/latest/
[work]: https://www.parcelperform.com/about-us
[scoop]: https://scoop.sh/
[vsc]: https://code.visualstudio.com/
[pexpect]: https://pexpect.readthedocs.io/en/stable/
[nuitka]: https://nuitka.net/
