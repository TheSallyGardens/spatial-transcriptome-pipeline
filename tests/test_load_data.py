from __future__ import annotations

# tests/test_load_data.py
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "workflow" / "scripts"))

# Test cases require real data - write placeholder tests
def test_platform_detection():
    """测试平台检测逻辑"""
    pass

def test_10x_loader_signature():
    """测试10x loader函数签名"""
    from load_data import load_10x_visium
    assert callable(load_10x_visium)

def test_stereo_seq_loader_signature():
    """测试Stereo-seq loader函数签名"""
    from load_data import load_stereo_seq
    assert callable(load_stereo_seq)