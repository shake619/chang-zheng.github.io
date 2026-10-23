# -*- coding: utf-8 -*-
"""三维展厅资源内联打包器。

将 three.js 与场景 JS 全部内联为单个自包含 HTML 文档，
通过 st.components.v1.html 嵌入——不依赖 Streamlit 静态目录、
不依赖 st.iframe（旧版本 Streamlit 也可用）、无外部请求，离线可用。

three.js（MIT 许可证）来源：static/lib/three.module.min.js（r160）。
处理方式：剥离其 ESM export 语句，并生成 `const THREE = {...}` 命名空间，
使场景代码（原本 import THREE）无需改动模块体系即可运行。
"""
import functools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "static" / "lib" / "three.module.min.js"


def _three_as_global() -> str:
    """读取 three.module.min.js：剥离 export，返回 `源码 + const THREE={...}`。"""
    src = LIB.read_text(encoding="utf-8")
    pairs = []

    def _grab(m: re.Match) -> str:
        for part in m.group(1).split(","):
            part = part.strip()
            if not part:
                continue
            if " as " in part:
                internal, name = [x.strip() for x in part.split(" as ", 1)]
            else:
                internal = name = part
            pairs.append(f"{name}:{internal}")
        return ""

    src = re.sub(r"export\s*\{([^}]*)\}\s*;?", _grab, src)
    return src + "\nconst THREE={" + ",".join(pairs) + "};\n"


def _clean_app_js(js: str) -> str:
    """移除场景代码中对 three 的模块导入（THREE 已由内联代码提供）。"""
    js = re.sub(r"^\s*import\s+\*\s+as\s+THREE.*?;\s*$", "", js, flags=re.M)
    js = re.sub(r"^\s*const\s+THREE\s*=\s*await\s+import\([^)]*\)\s*;\s*$",
                "", js, flags=re.M)
    return js


def _safe_for_inline(code: str) -> str:
    """防止内联代码意外终止 <script> 标签。"""
    return code.replace("</script", "<\\/script")


@functools.lru_cache(maxsize=4)
def _lib_code() -> str:
    return _safe_for_inline(_three_as_global())


def _build_page(html_tpl: str, app_js: str) -> str:
    code = _lib_code() + "\n" + _safe_for_inline(_clean_app_js(app_js))
    if "<script type=\"module\" src=\"./" not in html_tpl:
        raise ValueError("模板中未找到场景脚本引用")
    html_tpl = html_tpl.replace(
        "</head>",
        "<script>window.__THREE_INLINE__=1;</script>\n</head>")
    return re.sub(
        r"<script type=\"module\" src=\"\./[^\"]+\"></script>",
        lambda _: "<script type=\"module\">\n" + code + "\n</script>",
        html_tpl)


@functools.lru_cache(maxsize=4)
def globe_html() -> str:
    """自包含的交互地球仪页面（含 Canvas2D 降级，全部内联）。"""
    tpl = (ROOT / "static" / "globe" / "globe.html").read_text(encoding="utf-8")
    app = (ROOT / "static" / "globe" / "globe.js").read_text(encoding="utf-8")
    g2d = (ROOT / "static" / "globe" / "globe2d.js").read_text(encoding="utf-8")
    # 2D 降级脚本改为经典内联脚本，提前定义 window.initGlobe2D
    tpl = tpl.replace(
        "</head>",
        "<script>\n" + _safe_for_inline(g2d) + "\n</script>\n</head>")
    return _build_page(tpl, app)


@functools.lru_cache(maxsize=4)
def bridge_html() -> str:
    """自包含的泸定桥三维模型页面。"""
    tpl = (ROOT / "static" / "bridge" / "bridge.html").read_text(encoding="utf-8")
    app = (ROOT / "static" / "bridge" / "bridge.js").read_text(encoding="utf-8")
    return _build_page(tpl, app)
