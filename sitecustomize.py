"""Runtime patch for Streamlit iframe permission warnings.

Python automatically imports `sitecustomize` at startup (when available in
`sys.path`). This allows us to patch Streamlit static JS before the server
starts serving frontend assets.
"""

from pathlib import Path


def _patch_streamlit_iframe_permissions() -> None:
    unsupported = (
        "ambient-light-sensor",
        "battery",
        "document-domain",
        "layout-animations",
        "legacy-image-formats",
        "oversized-images",
        "vr ",
        "wake-lock",
    )
    try:
        import streamlit as st  # Imported lazily at startup
    except Exception:
        return

    try:
        streamlit_root = Path(st.__file__).resolve().parent
        js_dir = streamlit_root / "static" / "static" / "js"
        if not js_dir.exists():
            return
        # Streamlit may keep this list in different hashed JS bundles.
        for js_file in js_dir.glob("*.js"):
            content = js_file.read_text(encoding="utf-8")
            if not any(feature in content for feature in unsupported):
                continue
            patched = content
            for feature in unsupported:
                patched = patched.replace(f"`{feature}`,", "")
                patched = patched.replace(f"`{feature}`", "")
            if patched != content:
                js_file.write_text(patched, encoding="utf-8")
    except Exception:
        # Keep startup resilient even if filesystem is read-only.
        return


_patch_streamlit_iframe_permissions()
