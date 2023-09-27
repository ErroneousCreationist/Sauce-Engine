from . import sauce
import webview

def OpenFileBrowser():
    file = None
    def open_file_dialog(w):
        nonlocal file
        try:
            file = w.create_file_dialog(webview.OPEN_DIALOG)[0]
        except TypeError:
            pass  # user exited file dialog without picking
        finally:
            w.destroy()
    window = webview.create_window("", hidden=True)
    webview.start(open_file_dialog, window)
    # file will either be a string or None
    return file
