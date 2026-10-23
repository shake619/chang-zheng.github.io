# -*- coding: utf-8 -*-
"""pytest 配置：确保无论从哪个目录运行测试，项目根目录都在导入路径上。"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
