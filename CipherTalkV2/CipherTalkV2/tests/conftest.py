# tests/conftest.py
import sys, os

# insert the parent folder of tests/ into sys.path so pytest can find your modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
