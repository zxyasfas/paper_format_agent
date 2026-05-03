from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


def update_fields_with_libreoffice(docx_path: str | Path, timeout: int = 60) -> bool:
    """Open DOCX in headless LibreOffice, update fields/indexes/TOC, and store it.

    Returns False when LibreOffice/UNO is unavailable; caller can still deliver the DOCX
    because Word will update the TOC on open when updateFields is enabled.
    """
    path = Path(docx_path).resolve()
    try:
        sys.path.append('/usr/lib/python3/dist-packages')
        import uno  # type: ignore
        from com.sun.star.beans import PropertyValue  # type: ignore
    except Exception:
        return False

    profile = Path('/tmp/lo-profile-paper-format-agent')
    profile.mkdir(exist_ok=True)
    port = 2017
    cmd = [
        'libreoffice', '--headless', '--nologo', '--nofirststartwizard', '--norestore', '--nodefault',
        f'-env:UserInstallation=file://{profile}',
        f'--accept=socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext',
    ]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False

    def prop(name, value):
        p = PropertyValue(); p.Name = name; p.Value = value; return p

    try:
        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local_ctx)
        ctx = None
        start = time.time()
        while time.time() - start < timeout:
            try:
                ctx = resolver.resolve(f'uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext')
                break
            except Exception:
                time.sleep(0.3)
        if ctx is None:
            return False
        desktop = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
        url = uno.systemPathToFileUrl(str(path))
        doc = desktop.loadComponentFromURL(url, '_blank', 0, (prop('Hidden', True), prop('UpdateDocMode', 3)))
        if doc is None:
            return False
        try:
            doc.TextFields.refresh()
        except Exception:
            pass
        try:
            indexes = doc.getDocumentIndexes()
            for i in range(indexes.getCount()):
                indexes.getByIndex(i).update()
        except Exception:
            pass
        doc.store()
        doc.close(True)
        return True
    except Exception:
        return False
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
