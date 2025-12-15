# -*- coding: utf-8 -*-

import re


# =====================================================
# Platform Hint Sets
# =====================================================

ELECTRON_MAIN_HINTS = [
    "BrowserWindow",
    "ipcMain",
    "protocol.register",
    "session.defaultSession",
    "require('electron').app",
    "require(\"electron\").app",
]

ELECTRON_RENDERER_HINTS = [
    "ipcRenderer",
    "window.",
    "document.",
    "fetch(",
    "XMLHttpRequest",
]

ELECTRON_CODE_LOAD_HINTS = [
    "require(",
    "import(",
    "loadURL(",
    "loadFile(",
    "eval(",
    "new Function",
]


NATIVE_PRIVILEGE_HINTS = [
    "CreateProcess",
    "ShellExecute",
    "execve",
    "fork",
    "sudo",
    "SetTokenInformation",
    "Impersonate",
]

NATIVE_CODE_LOAD_HINTS = [
    "LoadLibrary",
    "dlopen",
    ".dll",
    ".so",
    ".dylib",
]


MOBILE_IPC_HINTS = [
    "intent://",
    "ACTION_VIEW",
    "startActivity",
    "openURL",
    "deeplink",
]

MOBILE_CODE_LOAD_HINTS = [
    "loadUrl(",
    "WebView",
    "evaluateJavascript",
]

MOBILE_PRIVILEGE_HINTS = [
    "WRITE_SETTINGS",
    "SYSTEM_ALERT_WINDOW",
    "ACCESS_FINE_LOCATION",
]


# =====================================================
# Execution Context Inference
# =====================================================

def infer_execution_context(surface, platform):
    value = surface.get("value", "") or ""
    file = surface.get("file", "") or ""

    if surface.get("source") == "url":
        return "remote"

    if platform == "electron":
        for h in ELECTRON_MAIN_HINTS:
            if h in value or h in file:
                return "main"

        for h in ELECTRON_RENDERER_HINTS:
            if h in value or h in file:
                return "renderer"

        if "ipc" in value.lower():
            return "ipc"

    if platform == "native":
        if "pipe" in value.lower() or "socket" in value.lower():
            return "local-service"
        return "native-process"

    if platform == "mobile":
        if "webview" in value.lower():
            return "webview"
        return "mobile-app"

    return "unknown"


# =====================================================
# Boundary Inference
# =====================================================

def infer_boundary(surface, context):
    if context == "remote":
        return "client->server"

    if context == "ipc":
        return "renderer->main"

    if context == "renderer":
        return "renderer-only"

    if context == "main":
        return "local-only"

    if context == "local-service":
        return "client->service"

    if context == "webview":
        return "webview->native"

    if context == "mobile-app":
        return "app->os"

    if context == "native-process":
        return "local->os"

    return "unknown"


# =====================================================
# Execution Risk Inference
# =====================================================

def infer_execution_risk(surface, platform):
    value = surface.get("value", "") or ""

    if platform == "electron":
        for h in ELECTRON_CODE_LOAD_HINTS:
            if h in value:
                return "code-loading"

    if platform == "native":
        for h in NATIVE_CODE_LOAD_HINTS:
            if h.lower() in value.lower():
                return "code-loading"
        for h in NATIVE_PRIVILEGE_HINTS:
            if h.lower() in value.lower():
                return "privileged"

    if platform == "mobile":
        for h in MOBILE_CODE_LOAD_HINTS:
            if h.lower() in value.lower():
                return "code-loading"
        for h in MOBILE_PRIVILEGE_HINTS:
            if h.lower() in value.lower():
                return "privileged"

    if surface.get("auth_context"):
        return "state-change"

    return "read-only"


# =====================================================
# Public Entry Point
# =====================================================

def apply_execution_context(surfaces, platform="electron"):
    """
    Annotate surfaces with execution context metadata.

    platform:
        - electron
        - native
        - mobile
    """

    for s in surfaces:
        context = infer_execution_context(s, platform)
        boundary = infer_boundary(s, context)
        risk = infer_execution_risk(s, platform)

        s["execution_context"] = context
        s["boundary"] = boundary
        s["execution_risk"] = risk

    return surfaces
