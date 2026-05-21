#!/usr/bin/env python3
"""
Test script to verify health check functions work correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit session state for testing
import streamlit as st
if not hasattr(st, 'session_state'):
    st.session_state = {}

# Import the health check functions from complex_dash
from complex_dash import check_fred_api, check_stablecoins_api, check_yfinance_api

def test_health_checks():
    print("Testing health check functions...")
    
    # Test FRED API check
    try:
        fred_ok, fred_msg = check_fred_api()
        print(f"FRED API Check: {'PASS' if fred_ok else 'FAIL'} - {fred_msg}")
    except Exception as e:
        print(f"FRED API Check: ERROR - {e}")
    
    # Test Stablecoins API check
    try:
        stablecoins_ok, stablecoins_msg = check_stablecoins_api()
        print(f"Stablecoins API Check: {'PASS' if stablecoins_ok else 'FAIL'} - {stablecoins_msg}")
    except Exception as e:
        print(f"Stablecoins API Check: ERROR - {e}")
        
    # Test Yahoo Finance API check
    try:
        yahoo_ok, yahoo_msg = check_yfinance_api()
        print(f"Yahoo Finance Check: {'PASS' if yahoo_ok else 'FAIL'} - {yahoo_msg}")
    except Exception as e:
        print(f"Yahoo Finance Check: ERROR - {e}")

if __name__ == "__main__":
    test_health_checks()