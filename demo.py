# -*- coding: utf-8 -*-`n# ============================================================
# MediVoice v2.0 — PINK THEME EDITION (Stable Build)
# Voice Alerts • AI • Inventory • Appointments • Tools
# ============================================================

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import hashlib, os, tempfile, requests, re, mimetypes, json, smtplib, threading
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import altair as alt
from PIL import Image
from email.mime.text import MIMEText
from collections import deque
# Voice modules
from voice_input import get_voice_input
from voice_alert import speak
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="Hello from MediVoice!", ln=True, align="C")

pdf.output("medivoice_test.pdf")


# ============================================================
# STREAMLIT CONFIG + THEME CSS
# ============================================================
st.set_page_config(page_title="MediVoice App - Your health companion", layout="wide")

# Initialize theme in session state
st.session_state.setdefault("dark_theme", False)

def get_css():
    if st.session_state.dark_theme:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Manrope:wght@400;600;700&display=swap');
        :root {
            --bg:#1a1a2e;
            --panel:#16213e;
            --card:#0f3460;
            --pink:#e94560;
            --pink-dark:#d32f4d;
            --yellow:#f9a826;
            --text:#e6e6e6;
            --muted:#b8b8b8;
        }
        html, body, [class*="css"]  {
            font-family:'Manrope','Segoe UI',sans-serif;
            color:var(--text);
            background:var(--bg);
        }
        .stApp {
            background:var(--bg);
            background-image:
                radial-gradient(circle at 10% 20%, rgba(40,40,70,0.45), transparent 35%),
                radial-gradient(circle at 90% 10%, rgba(249,168,38,0.25), transparent 40%),
                radial-gradient(circle at 50% 80%, rgba(233,69,96,0.35), transparent 35%);
            background-repeat:no-repeat;
        }
        .main .block-container {
            padding: 1.8rem 2.2rem 4rem;
        }
        .section-header {
            background:var(--card);
            border-radius:28px;
            padding:1.1rem 1.3rem;
            display:flex;
            align-items:center;
            gap:0.8rem;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 25px 60px rgba(233,69,96,0.15);
            margin-bottom:1.5rem;
        }
        .section-icon {
            width:60px;
            height:60px;
            border-radius:20px;
            background:linear-gradient(145deg,var(--pink),var(--pink-dark));
            color:#fff;
            font-size:28px;
            display:flex;
            align-items:center;
            justify-content:center;
        }
        .section-header h2 {
            margin:0;
            font-family:'Playfair Display', serif;
        }
        .section-header p {
            margin:0;
            color:var(--muted);
        }
        .filter-panel {
            background:linear-gradient(145deg,#1e2a4a,#16213e);
            border-radius:30px;
            padding:1.7rem;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 20px 50px rgba(233,69,96,0.12);
        }
        .filter-panel h3 {
            font-family:'Playfair Display', serif;
            margin-top:0;
        }
        .kpi-row {
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
            gap:1.2rem;
            margin:1.4rem 0 1.6rem;
        }
        .kpi-card {
            background:linear-gradient(145deg,#1e2a4a,#16213e);
            border-radius:26px;
            padding:1rem 1.2rem;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 18px 45px rgba(233,69,96,0.15);
        }
        .kpi-card small {
            color:var(--muted);
            font-weight:600;
            text-transform:uppercase;
            letter-spacing:0.08em;
        }
        .kpi-value {
            font-size:1.6rem;
            font-weight:700;
            margin-top:0.4rem;
        }
        .kpi-sub {
            font-size:0.95rem;
            color:var(--muted);
        }
        .kpi-delta {
            font-size:0.88rem;
            font-weight:600;
        }
        .kpi-delta.positive { color:#4cd964; }
        .kpi-delta.negative { color:#ff3b30; }
        .chart-card {
            background:var(--card);
            border-radius:30px;
            padding:1.5rem;
            border:1px solid rgba(233,69,96,0.25);
            box-shadow:0 25px 60px rgba(233,69,96,0.12);
        }
        .chart-card h3 {
            margin-top:0;
            font-family:'Playfair Display', serif;
        }
        .stTextInput>label, .stSelectbox>label, .stMultiSelect>label, .stTextArea>label {
            font-weight:600;
            color:var(--muted);
        }
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"]>div,
        .stMultiSelect div[data-baseweb="select"]>div,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input {
            border-radius:18px !important;
            border:1px solid rgba(233,69,96,0.4) !important;
            background:#1e2a4a !important;
            color:var(--text) !important;
        }
        .stButton>button, .stDownloadButton>button {
            border-radius:999px;
            border:none;
            padding:0.55rem 1.6rem;
            background:linear-gradient(135deg,var(--pink),var(--pink-dark));
            color:#fff;
            font-weight:600;
            box-shadow:0 12px 25px rgba(233,69,96,0.25);
            transition:transform 0.2s ease, box-shadow 0.2s ease;
        }
        .stButton>button:hover,
        .stDownloadButton>button:hover {
            transform:translateY(-2px);
            box-shadow:0 18px 30px rgba(233,69,96,0.32);
        }
        .stButton>button:active,
        .stDownloadButton>button:active {
            transform:translateY(1px);
            box-shadow:0 8px 16px rgba(233,69,96,0.18);
        }
        .stButton>button:focus-visible,
        .stDownloadButton>button:focus-visible {
            outline:3px solid rgba(233,69,96,0.6);
            outline-offset:3px;
        }
        .stTabs [role="tablist"] {
            gap:0.65rem;
            border-bottom:none;
            padding:0.4rem 0 0.8rem;
            flex-wrap:wrap;
        }
        .stTabs [role="tab"] {
            border:none !important;
            background:linear-gradient(135deg,rgba(30,42,74,0.9),rgba(22,33,62,0.75)) !important;
            font-weight:600;
            color:var(--muted) !important;
            padding:0.35rem 1rem;
            border-radius:999px;
            position:relative;
            box-shadow:0 10px 25px rgba(233,69,96,0.12);
            border:1px solid rgba(233,69,96,0.3);
            transition:all 0.25s ease;
        }
        .stTabs [role="tab"] span {
            display:flex;
            align-items:center;
            gap:0.4rem;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            color:#fff !important;
            background:linear-gradient(120deg,var(--pink),var(--pink-dark)) !important;
            box-shadow:0 18px 32px rgba(233,69,96,0.3);
            border-color:transparent;
        }
        .stTabs [role="tab"][aria-selected="true"]::after {
            display:none;
        }
        [data-testid="stSidebar"]>div:first-child {
            background:linear-gradient(180deg,#1e2a4a,#16213e);
            border-radius:26px;
            border:1px solid rgba(233,69,96,0.25);
        }
        .tool-tablet {
            background:rgba(30,42,74,0.8);
            padding:0.4rem;
            border-radius:26px;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 12px 30px rgba(233,69,96,0.15);
        }
        .tool-tablet.active {
            background:linear-gradient(135deg,var(--pink),var(--pink-dark));
            box-shadow:0 22px 40px rgba(233,69,96,0.35);
        }
        .tool-tablet .stButton>button {
            width:100%;
            border:none;
            background:transparent;
            color:var(--text);
            font-weight:600;
            font-size:0.95rem;
        }
        .tool-tablet.active .stButton>button {
            color:#fff;
        }
        .mobile-shell {
            max-width: 300px;
            margin: 0.5rem auto 1.4rem;
            padding: 1rem 0 1.6rem;
        }
        .mobile-card {
            background:linear-gradient(145deg,#1e2a4a,#16213e);
            border-radius:30px;
            padding:1.2rem 1.4rem;
            box-shadow:0 28px 50px rgba(233,69,96,0.15);
            border:1px solid rgba(233,69,96,0.3);
        }
        .accent-pill {
            width:60px;
            height:60px;
            border-radius:24px;
            background:linear-gradient(145deg,var(--pink),var(--pink-dark));
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:26px;
            color:#fff;
            margin-bottom:0.7rem;
        }
        .stAlert {
            border-radius:22px;
            border-left:6px solid var(--pink);
            background:linear-gradient(135deg,#1e2a4a,#16213e);
        }
        .ai-shell {
            background:linear-gradient(160deg,#1e2a4a,#16213e);
            border-radius:34px;
            padding:1.5rem;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 30px 65px rgba(233,69,96,0.15);
            min-height:420px;
            max-height:520px;
            overflow-y:auto;
        }
        .chat-timeline {
            display:flex;
            flex-direction:column;
            gap:0.9rem;
        }
        .chat-bubble {
            padding:0.85rem 1rem;
            border-radius:20px;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 12px 25px rgba(230,230,230,0.08);
        }
        .chat-bubble p {
            margin:0.2rem 0 0;
        }
        .bubble-label {
            font-size:0.82rem;
            letter-spacing:0.02em;
            font-weight:600;
            text-transform:uppercase;
            color:var(--muted);
        }
        .user-bubble {
            background:#0f3460;
            align-self:flex-end;
        }
        .ai-bubble {
            background:linear-gradient(145deg,#1e2a4a,#16213e);
        }
        .quick-card {
            background:linear-gradient(145deg,#1e2a4a,#16213e);
            border-radius:26px;
            padding:1.2rem;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 22px 45px rgba(233,69,96,0.15);
        }
        .quick-card h4 {
            margin-top:0;
            font-family:'Playfair Display', serif;
        }
        .prompt-note {
            font-size:0.85rem;
            color:var(--muted);
            margin-bottom:0.6rem;
        }
        .voice-card {
            margin-top:1rem;
            background:linear-gradient(145deg,#1e2a4a,#16213e);
        }
        .voice-card .stButton>button {
            margin-bottom:0;
        }
        .quick-card button {
            width:100%;
            margin-bottom:0.4rem;
            border-radius:999px !important;
            border:none !important;
            background:rgba(15,52,96,0.95) !important;
            color:var(--pink) !important;
            font-weight:600 !important;
            box-shadow:none !important;
        }
        .quick-card button:hover {
            background:#0f3460 !important;
        }
        .blue-box {
            background:linear-gradient(135deg,#1e2a4a,#16213e);
            border-radius:24px;
            padding:1.2rem;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 20px 40px rgba(233,69,96,0.12);
        }
        .status-chip {
            display:inline-flex;
            align-items:center;
            font-size:0.85rem;
            font-weight:600;
            padding:0.35rem 0.85rem;
            border-radius:999px;
            background:rgba(230,230,230,0.15);
            color:var(--text);
            text-transform:uppercase;
            letter-spacing:0.06em;
        }
        .status-chip.chip-upcoming { background:rgba(0,201,167,0.2); color:#00c9a7; }
        .status-chip.chip-soon { background:rgba(249,168,38,0.3); color:#f9a826; }
        .status-chip.chip-now { background:rgba(233,69,96,0.3); color:#e94560; }
        .status-chip.chip-overdue { background:rgba(255,63,106,0.3); color:#ff3f6a; }
        .reminder-chip.chip-upcoming { background:rgba(0,201,167,0.2); color:#00c9a7; }
        .reminder-chip.chip-soon { background:rgba(249,168,38,0.3); color:#f9a826; }
        .reminder-chip.chip-now { background:rgba(233,69,96,0.3); color:#e94560; }
        .reminder-chip.chip-overdue { background:rgba(255,63,106,0.3); color:#ff3f6a; }
        .reminder-card .reminder-top {
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            gap:1rem;
        }
        .reminder-card .reminder-time {
            font-weight:600;
            color:var(--muted);
            margin-top:0.25rem;
        }
        .reminder-card .reminder-med {
            margin:0;
            font-size:1.05rem;
            font-weight:700;
            color:var(--text);
        }
        .reminder-card .reminder-time {
            font-weight:600;
            color:var(--muted);
            margin-top:0.15rem;
        }
        .reminder-card .reminder-meta {
            display:flex;
            flex-wrap:wrap;
            gap:0.75rem;
            margin-top:0.8rem;
            font-size:0.92rem;
            color:var(--muted);
        }
        .reminder-card .reminder-meta span {
            display:inline-flex;
            align-items:center;
            gap:0.35rem;
        }
        .day-grid {
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(120px,1fr));
            gap:0.9rem;
            margin:1rem 0 1.5rem;
        }
        .day-card {
            background:linear-gradient(145deg,#1e2a4a,#16213e);
            border-radius:20px;
            padding:0.85rem 0.9rem;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 12px 28px rgba(233,69,96,0.15);
            text-align:center;
        }
        .day-card--today {
            border-color:var(--pink);
            box-shadow:0 18px 45px rgba(233,69,96,0.25);
        }
        .day-card__date {
            font-weight:700;
            font-size:0.95rem;
            color:var(--text);
        }
        .day-card__day {
            font-size:0.8rem;
            letter-spacing:0.08em;
            color:var(--muted);
            text-transform:uppercase;
        }
        .day-card__count {
            font-weight:600;
            color:var(--pink);
            margin-top:0.4rem;
        }
        .day-card__meds {
            margin-top:0.35rem;
            font-size:0.8rem;
            color:var(--muted);
            min-height:1.6rem;
        }
        .weekly-grid {
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
            gap:1.1rem;
            margin:1.1rem 0 1.8rem;
        }
        .weekly-card {
            background:linear-gradient(145deg,#0f3460,#1e2a4a);
            border-radius:26px;
            padding:1.2rem 1.3rem;
            border:1px solid rgba(233,69,96,0.25);
            box-shadow:0 20px 45px rgba(233,69,96,0.12);
            display:flex;
            flex-direction:column;
            gap:0.85rem;
        }
        .weekly-card__top {
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
        }
        .weekly-card__day {
            font-size:0.8rem;
            text-transform:uppercase;
            color:var(--muted);
            letter-spacing:0.08em;
        }
        .weekly-card__date {
            font-size:1.15rem;
            font-weight:700;
        }
        .weekly-card__badge {
            font-size:0.85rem;
            font-weight:700;
            padding:0.25rem 0.75rem;
            border-radius:999px;
            background:rgba(233,69,96,0.2);
            color:var(--pink);
        }
        .weekly-card__stats {
            display:grid;
            grid-template-columns:repeat(2,minmax(0,1fr));
            gap:0.75rem;
        }
        .weekly-card__stat {
            background:rgba(15,52,96,0.85);
            border-radius:18px;
            padding:0.6rem 0.7rem;
            border:1px solid rgba(233,69,96,0.3);
        }
        .weekly-card__stat .label {
            font-size:0.75rem;
            text-transform:uppercase;
            color:var(--muted);
            letter-spacing:0.08em;
        }
        .weekly-card__stat .value {
            font-size:1.35rem;
            font-weight:700;
        }
        .weekly-card__progress {
            position:relative;
            height:8px;
            border-radius:999px;
            background:rgba(233,69,96,0.3);
            overflow:hidden;
        }
        .weekly-card__progress .fill {
            position:absolute;
            top:0;
            left:0;
            bottom:0;
            border-radius:999px;
            background:linear-gradient(135deg,var(--pink),var(--pink-dark));
        }
        .weekly-card__progress-label {
            font-size:0.8rem;
            font-weight:600;
            color:var(--muted);
            margin-top:0.2rem;
        }
        .weekly-card__meds-title {
            font-size:0.78rem;
            text-transform:uppercase;
            letter-spacing:0.08em;
            color:var(--muted);
        }
        .weekly-card__meds {
            list-style:none;
            padding:0;
            margin:0;
            display:flex;
            flex-direction:column;
            gap:0.5rem;
        }
        .weekly-card__meds li {
            display:flex;
            justify-content:space-between;
            align-items:center;
            font-size:0.92rem;
            background:rgba(15,52,96,0.85);
            border-radius:14px;
            padding:0.35rem 0.6rem;
            border:1px solid rgba(233,69,96,0.25);
        }
        .weekly-card__meds li .status {
            font-size:0.78rem;
            font-weight:700;
            text-transform:uppercase;
        }
        .weekly-card__meds li .status.ok {
            color:#4cd964;
        }
        .weekly-card__meds li .status.miss {
            color:#ff6b6b;
        }
        .weekly-card__meds li.more {
            justify-content:flex-start;
            font-size:0.85rem;
            color:var(--muted);
        }
        .weekly-card__meds li.empty {
            justify-content:flex-start;
            font-size:0.85rem;
            color:var(--muted);
        }
        .weekly-card__more {
            margin-top:0.45rem;
        }
        .weekly-card__more summary {
            cursor:pointer;
            font-size:0.9rem;
            font-weight:600;
            color:var(--pink);
            list-style:none;
            border:1px solid rgba(233,69,96,0.4);
            border-radius:14px;
            padding:0.35rem 0.7rem;
            background:rgba(15,52,96,0.85);
        }
        .weekly-card__more summary::-webkit-details-marker {
            display:none;
        }
        .weekly-card__more[open] summary {
            background:rgba(233,69,96,0.15);
        }
        .weekly-card__more ul {
            list-style:none;
            padding:0.6rem 0.2rem 0;
            margin:0;
            display:flex;
            flex-direction:column;
            gap:0.45rem;
        }
        .weekly-chart-card {
            background:linear-gradient(145deg,#1e2a4a,#16213e);
            border-radius:26px;
            padding:1.2rem 1.4rem;
            border:1px solid rgba(233,69,96,0.3);
            box-shadow:0 18px 40px rgba(233,69,96,0.15);
            margin-top:0.5rem;
        }
        .weekly-chart-card__title {
            font-family:'Playfair Display', serif;
            font-size:1.1rem;
            margin-bottom:0.6rem;
            display:flex;
            align-items:center;
            gap:0.5rem;
        }
        .reminder-card {
            background:linear-gradient(145deg,#1e2a4a,#16213e);
            border-radius:24px;
            padding:1rem;
            border:1px solid rgba(233,69,96,0.4);
            box-shadow:0 12px 28px rgba(233,69,96,0.15);
            min-height:200px;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
            backdrop-filter:blur(6px);
            position:relative;
        }
        .reminder-chip {
            position:absolute;
            top:0.8rem;
            right:0.8rem;
            font-size:0.75rem;
            font-weight:600;
            padding:0.25rem 0.65rem;
            border-radius:999px;
            background:rgba(230,230,230,0.15);
            color:var(--text);
            text-transform:uppercase;
            letter-spacing:0.06em;
        }
        .reminder-card .reminder-top {
            display:flex;
            flex-direction:column;
            gap:0.2rem;
            margin-top:0.8rem;
        }
        .reminder-card .reminder-med {
            margin:0;
            font-size:1rem;
            font-weight:700;
            color:var(--text);
        }
        .reminder-card .reminder-time {
            font-weight:600;
            color:var(--muted);
        }
        .reminder-card .reminder-meta {
            margin-top:0.6rem;
            display:flex;
            flex-direction:column;
            gap:0.35rem;
            font-size:0.9rem;
            color:var(--muted);
        }
        .reminder-card .reminder-meta span {
            display:block;
            padding:0.4rem 0.65rem;
            border-radius:14px;
            background:rgba(15,52,96,0.7);
            border:1px solid rgba(233,69,96,0.3);
        }
        .tools-grid {
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
            gap:1rem;
        }
        </style>
        """
    else:
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Manrope:wght@400;600;700&display=swap');
        :root {
            --bg:#ffeaf0;
            --panel:#fff4f7;
            --card:#ffffff;
            --pink:#ff7aa2;
            --pink-dark:#ff4c91;
            --yellow:#ffd86f;
            --text:#3a2a33;
            --muted:#80616b;
        }
        html, body, [class*="css"]  {
            font-family:'Manrope','Segoe UI',sans-serif;
            color:var(--text);
            background:var(--bg);
        }
        .stApp {
            background:var(--bg);
            background-image:
                radial-gradient(circle at 10% 20%, rgba(255,255,255,0.45), transparent 35%),
                radial-gradient(circle at 90% 10%, rgba(255,216,111,0.35), transparent 40%),
                radial-gradient(circle at 50% 80%, rgba(255,148,184,0.45), transparent 35%);
            background-repeat:no-repeat;
        }
        .main .block-container {
            padding: 1.8rem 2.2rem 4rem;
        }
        .section-header {
            background:var(--card);
            border-radius:28px;
            padding:1.1rem 1.3rem;
            display:flex;
            align-items:center;
            gap:0.8rem;
            border:1px solid rgba(255,148,184,0.2);
            box-shadow:0 25px 60px rgba(255,74,145,0.12);
            margin-bottom:1.5rem;
        }
        .section-icon {
            width:60px;
            height:60px;
            border-radius:20px;
            background:linear-gradient(145deg,var(--pink),var(--pink-dark));
            color:#fff;
            font-size:28px;
            display:flex;
            align-items:center;
            justify-content:center;
        }
        .section-header h2 {
            margin:0;
            font-family:'Playfair Display', serif;
        }
        .section-header p {
            margin:0;
            color:var(--muted);
        }
        .filter-panel {
            background:linear-gradient(145deg,#fff7fb,#ffe0ea);
            border-radius:30px;
            padding:1.7rem;
            border:1px solid rgba(255,148,184,0.25);
            box-shadow:0 20px 50px rgba(255,74,145,0.15);
        }
        .filter-panel h3 {
            font-family:'Playfair Display', serif;
            margin-top:0;
        }
        .kpi-row {
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
            gap:1.2rem;
            margin:1.4rem 0 1.6rem;
        }
        .kpi-card {
            background:linear-gradient(145deg,#fff7fb,#ffeef5);
            border-radius:26px;
            padding:1rem 1.2rem;
            border:1px solid rgba(255,148,184,0.25);
            box-shadow:0 18px 45px rgba(255,74,145,0.18);
        }
        .kpi-card small {
            color:var(--muted);
            font-weight:600;
            text-transform:uppercase;
            letter-spacing:0.08em;
        }
        .kpi-value {
            font-size:1.6rem;
            font-weight:700;
            margin-top:0.4rem;
        }
        .kpi-sub {
            font-size:0.95rem;
            color:var(--muted);
        }
        .kpi-delta {
            font-size:0.88rem;
            font-weight:600;
        }
        .kpi-delta.positive { color:#2eaa66; }
        .kpi-delta.negative { color:#ff3f6a; }
        .chart-card {
            background:var(--card);
            border-radius:30px;
            padding:1.5rem;
            border:1px solid rgba(255,148,184,0.2);
            box-shadow:0 25px 60px rgba(255,74,145,0.15);
        }
        .chart-card h3 {
            margin-top:0;
            font-family:'Playfair Display', serif;
        }
        .stTextInput>label, .stSelectbox>label, .stMultiSelect>label, .stTextArea>label {
            font-weight:600;
            color:var(--muted);
        }
        .stTextInput input,
        .stSelectbox div[data-baseweb="select"]>div,
        .stMultiSelect div[data-baseweb="select"]>div,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input {
            border-radius:18px !important;
            border:1px solid rgba(255,148,184,0.4) !important;
            background:#fff !important;
        }
        .stButton>button, .stDownloadButton>button {
            border-radius:999px;
            border:none;
            padding:0.55rem 1.6rem;
            background:linear-gradient(135deg,var(--pink),var(--pink-dark));
            color:#fff;
            font-weight:600;
            box-shadow:0 12px 25px rgba(255,74,145,0.25);
            transition:transform 0.2s ease, box-shadow 0.2s ease;
        }
        .stButton>button:hover,
        .stDownloadButton>button:hover {
            transform:translateY(-2px);
            box-shadow:0 18px 30px rgba(255,74,145,0.32);
        }
        .stButton>button:active,
        .stDownloadButton>button:active {
            transform:translateY(1px);
            box-shadow:0 8px 16px rgba(255,74,145,0.18);
        }
        .stButton>button:focus-visible,
        .stDownloadButton>button:focus-visible {
            outline:3px solid rgba(255,148,184,0.6);
            outline-offset:3px;
        }
        .stTabs [role="tablist"] {
            gap:0.65rem;
            border-bottom:none;
            padding:0.4rem 0 0.8rem;
            flex-wrap:wrap;
        }
        .stTabs [role="tab"] {
            border:none !important;
            background:linear-gradient(135deg,rgba(255,255,255,0.9),rgba(255,244,247,0.75)) !important;
            font-weight:600;
            color:var(--muted) !important;
            padding:0.35rem 1rem;
            border-radius:999px;
            position:relative;
            box-shadow:0 10px 25px rgba(255,74,145,0.12);
            border:1px solid rgba(255,148,184,0.25);
            transition:all 0.25s ease;
        }
        .stTabs [role="tab"] span {
            display:flex;
            align-items:center;
            gap:0.4rem;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            color:#fff !important;
            background:linear-gradient(120deg,var(--pink),var(--pink-dark)) !important;
            box-shadow:0 18px 32px rgba(255,74,145,0.3);
            border-color:transparent;
        }
        .stTabs [role="tab"][aria-selected="true"]::after {
            display:none;
        }
        [data-testid="stSidebar"]>div:first-child {
            background:linear-gradient(180deg,#fff9fb,#ffe7ef);
            border-radius:26px;
            border:1px solid rgba(255,148,184,0.2);
        }
        .tool-tablet {
            background:rgba(255,255,255,0.8);
            padding:0.4rem;
            border-radius:26px;
            border:1px solid rgba(255,148,184,0.3);
            box-shadow:0 12px 30px rgba(255,74,145,0.18);
        }
        .tool-tablet.active {
            background:linear-gradient(135deg,var(--pink),var(--pink-dark));
            box-shadow:0 22px 40px rgba(255,74,145,0.35);
        }
        .tool-tablet .stButton>button {
            width:100%;
            border:none;
            background:transparent;
            color:var(--text);
            font-weight:600;
            font-size:0.95rem;
        }
        .tool-tablet.active .stButton>button {
            color:#fff;
        }
        .mobile-shell {
            max-width: 300px;
            margin: 0.5rem auto 1.4rem;
            padding: 1rem 0 1.6rem;
        }
        .mobile-card {
            background:linear-gradient(145deg,#fff7fb,#ffe0ec);
            border-radius:30px;
            padding:1.2rem 1.4rem;
            box-shadow:0 28px 50px rgba(255,74,145,0.15);
            border:1px solid rgba(255,148,184,0.25);
        }
        .accent-pill {
            width:60px;
            height:60px;
            border-radius:24px;
            background:linear-gradient(145deg,var(--pink),var(--pink-dark));
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:26px;
            color:#fff;
            margin-bottom:0.7rem;
        }
        .stAlert {
            border-radius:22px;
            border-left:6px solid var(--pink);
            background:linear-gradient(135deg,#fff3f8,#ffe2ea);
        }
        .ai-shell {
            background:linear-gradient(160deg,#fff8fd,#ffe0ec);
            border-radius:34px;
            padding:1.5rem;
            border:1px solid rgba(255,148,184,0.3);
            box-shadow:0 30px 65px rgba(255,74,145,0.18);
            min-height:420px;
            max-height:520px;
            overflow-y:auto;
        }
        .chat-timeline {
            display:flex;
            flex-direction:column;
            gap:0.9rem;
        }
        .chat-bubble {
            padding:0.85rem 1rem;
            border-radius:20px;
            border:1px solid rgba(255,148,184,0.25);
            box-shadow:0 12px 25px rgba(58,42,51,0.08);
        }
        .chat-bubble p {
            margin:0.2rem 0 0;
        }
        .bubble-label {
            font-size:0.82rem;
            letter-spacing:0.02em;
            font-weight:600;
            text-transform:uppercase;
            color:var(--muted);
        }
        .user-bubble {
            background:#fff;
            align-self:flex-end;
        }
        .ai-bubble {
            background:linear-gradient(145deg,#fff5fb,#ffe0ec);
        }
        .quick-card {
            background:linear-gradient(145deg,#fff7fb,#ffe0ec);
            border-radius:26px;
            padding:1.2rem;
            border:1px solid rgba(255,148,184,0.25);
            box-shadow:0 22px 45px rgba(255,74,145,0.15);
        }
        .quick-card h4 {
            margin-top:0;
            font-family:'Playfair Display', serif;
        }
        .prompt-note {
            font-size:0.85rem;
            color:var(--muted);
            margin-bottom:0.6rem;
        }
        .voice-card {
            margin-top:1rem;
            background:linear-gradient(145deg,#fff2fa,#ffdbe9);
        }
        .voice-card .stButton>button {
            margin-bottom:0;
        }
        .quick-card button {
            width:100%;
            margin-bottom:0.4rem;
            border-radius:999px !important;
            border:none !important;
            background:rgba(255,255,255,0.95) !important;
            color:var(--pink-dark) !important;
            font-weight:600 !important;
            box-shadow:none !important;
        }
        .quick-card button:hover {
            background:#fff !important;
        }
        .blue-box {
            background:linear-gradient(135deg,#fff6fb,#ffe6ef);
            border-radius:24px;
            padding:1.2rem;
            border:1px solid rgba(255,148,184,0.25);
            box-shadow:0 20px 40px rgba(255,74,145,0.12);
        }
        .status-chip {
            display:inline-flex;
            align-items:center;
            font-size:0.85rem;
            font-weight:600;
            padding:0.35rem 0.85rem;
            border-radius:999px;
            background:rgba(58,42,51,0.08);
            color:var(--text);
            text-transform:uppercase;
            letter-spacing:0.06em;
        }
        .status-chip.chip-upcoming { background:rgba(0,201,167,0.15); color:#008f74; }
        .status-chip.chip-soon { background:rgba(255,216,111,0.3); color:#a36a00; }
        .status-chip.chip-now { background:rgba(255,74,145,0.2); color:#c11263; }
        .status-chip.chip-overdue { background:rgba(255,63,106,0.25); color:#861135; }
        .reminder-chip.chip-upcoming { background:rgba(0,201,167,0.15); color:#008f74; }
        .reminder-chip.chip-soon { background:rgba(255,216,111,0.3); color:#a36a00; }
        .reminder-chip.chip-now { background:rgba(255,74,145,0.2); color:#c11263; }
        .reminder-chip.chip-overdue { background:rgba(255,63,106,0.25); color:#861135; }
        .reminder-card .reminder-top {
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
            gap:1rem;
        }
        .reminder-card .reminder-time {
            font-weight:600;
            color:var(--muted);
            margin-top:0.25rem;
        }
        .reminder-card .reminder-med {
            margin:0;
            font-size:1.05rem;
            font-weight:700;
            color:var(--text);
        }
        .reminder-card .reminder-time {
            font-weight:600;
            color:var(--muted);
            margin-top:0.15rem;
        }
        .reminder-card .reminder-meta {
            display:flex;
            flex-wrap:wrap;
            gap:0.75rem;
            margin-top:0.8rem;
            font-size:0.92rem;
            color:var(--muted);
        }
        .reminder-card .reminder-meta span {
            display:inline-flex;
            align-items:center;
            gap:0.35rem;
        }
        .day-grid {
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(120px,1fr));
            gap:0.9rem;
            margin:1rem 0 1.5rem;
        }
        .day-card {
            background:linear-gradient(145deg,#fff7fb,#ffe8ef);
            border-radius:20px;
            padding:0.85rem 0.9rem;
            border:1px solid rgba(255,148,184,0.25);
            box-shadow:0 12px 28px rgba(255,74,145,0.18);
            text-align:center;
        }
        .day-card--today {
            border-color:var(--pink);
            box-shadow:0 18px 45px rgba(255,74,145,0.28);
        }
        .day-card__date {
            font-weight:700;
            font-size:0.95rem;
            color:var(--text);
        }
        .day-card__day {
            font-size:0.8rem;
            letter-spacing:0.08em;
            color:var(--muted);
            text-transform:uppercase;
        }
        .day-card__count {
            font-weight:600;
            color:var(--pink-dark);
            margin-top:0.4rem;
        }
        .day-card__meds {
            margin-top:0.35rem;
            font-size:0.8rem;
            color:var(--muted);
            min-height:1.6rem;
        }
        .weekly-grid {
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
            gap:1.1rem;
            margin:1.1rem 0 1.8rem;
        }
        .weekly-card {
            background:linear-gradient(145deg,#fff,#ffeef5);
            border-radius:26px;
            padding:1.2rem 1.3rem;
            border:1px solid rgba(255,148,184,0.2);
            box-shadow:0 20px 45px rgba(255,74,145,0.15);
            display:flex;
            flex-direction:column;
            gap:0.85rem;
        }
        .weekly-card__top {
            display:flex;
            justify-content:space-between;
            align-items:flex-start;
        }
        .weekly-card__day {
            font-size:0.8rem;
            text-transform:uppercase;
            color:var(--muted);
            letter-spacing:0.08em;
        }
        .weekly-card__date {
            font-size:1.15rem;
            font-weight:700;
        }
        .weekly-card__badge {
            font-size:0.85rem;
            font-weight:700;
            padding:0.25rem 0.75rem;
            border-radius:999px;
            background:rgba(255,74,145,0.12);
            color:var(--pink-dark);
        }
        .weekly-card__stats {
            display:grid;
            grid-template-columns:repeat(2,minmax(0,1fr));
            gap:0.75rem;
        }
        .weekly-card__stat {
            background:rgba(255,255,255,0.85);
            border-radius:18px;
            padding:0.6rem 0.7rem;
            border:1px solid rgba(255,148,184,0.25);
        }
        .weekly-card__stat .label {
            font-size:0.75rem;
            text-transform:uppercase;
            color:var(--muted);
            letter-spacing:0.08em;
        }
        .weekly-card__stat .value {
            font-size:1.35rem;
            font-weight:700;
        }
        .weekly-card__progress {
            position:relative;
            height:8px;
            border-radius:999px;
            background:rgba(255,148,184,0.2);
            overflow:hidden;
        }
        .weekly-card__progress .fill {
            position:absolute;
            top:0;
            left:0;
            bottom:0;
            border-radius:999px;
            background:linear-gradient(135deg,var(--pink),var(--pink-dark));
        }
        .weekly-card__progress-label {
            font-size:0.8rem;
            font-weight:600;
            color:var(--muted);
            margin-top:0.2rem;
        }
        .weekly-card__meds-title {
            font-size:0.78rem;
            text-transform:uppercase;
            letter-spacing:0.08em;
            color:var(--muted);
        }
        .weekly-card__meds {
            list-style:none;
            padding:0;
            margin:0;
            display:flex;
            flex-direction:column;
            gap:0.5rem;
        }
        .weekly-card__meds li {
            display:flex;
            justify-content:space-between;
            align-items:center;
            font-size:0.92rem;
            background:rgba(255,255,255,0.85);
            border-radius:14px;
            padding:0.35rem 0.6rem;
            border:1px solid rgba(255,148,184,0.2);
        }
        .weekly-card__meds li .status {
            font-size:0.78rem;
            font-weight:700;
            text-transform:uppercase;
        }
        .weekly-card__meds li .status.ok {
            color:#2eaa66;
        }
        .weekly-card__meds li .status.miss {
            color:#d53c6c;
        }
        .weekly-card__meds li.more {
            justify-content:flex-start;
            font-size:0.85rem;
            color:var(--muted);
        }
        .weekly-card__meds li.empty {
            justify-content:flex-start;
            font-size:0.85rem;
            color:var(--muted);
        }
        .weekly-card__more {
            margin-top:0.45rem;
        }
        .weekly-card__more summary {
            cursor:pointer;
            font-size:0.9rem;
            font-weight:600;
            color:var(--pink-dark);
            list-style:none;
            border:1px solid rgba(255,148,184,0.35);
            border-radius:14px;
            padding:0.35rem 0.7rem;
            background:rgba(255,255,255,0.85);
        }
        .weekly-card__more summary::-webkit-details-marker {
            display:none;
        }
        .weekly-card__more[open] summary {
            background:rgba(255,74,145,0.08);
        }
        .weekly-card__more ul {
            list-style:none;
            padding:0.6rem 0.2rem 0;
            margin:0;
            display:flex;
            flex-direction:column;
            gap:0.45rem;
        }
        .weekly-chart-card {
            background:linear-gradient(145deg,#fff7fb,#ffe6ef);
            border-radius:26px;
            padding:1.2rem 1.4rem;
            border:1px solid rgba(255,148,184,0.25);
            box-shadow:0 18px 40px rgba(255,74,145,0.18);
            margin-top:0.5rem;
        }
        .weekly-chart-card__title {
            font-family:'Playfair Display', serif;
            font-size:1.1rem;
            margin-bottom:0.6rem;
            display:flex;
            align-items:center;
            gap:0.5rem;
        }
        .reminder-card {
            background:linear-gradient(145deg,#fff7fb,#ffe2ef);
            border-radius:24px;
            padding:1rem;
            border:1px solid rgba(255,148,184,0.35);
            box-shadow:0 12px 28px rgba(255,74,145,0.18);
            min-height:200px;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
            backdrop-filter:blur(6px);
            position:relative;
        }
        .reminder-chip {
            position:absolute;
            top:0.8rem;
            right:0.8rem;
            font-size:0.75rem;
            font-weight:600;
            padding:0.25rem 0.65rem;
            border-radius:999px;
            background:rgba(58,42,51,0.08);
            color:var(--text);
            text-transform:uppercase;
            letter-spacing:0.06em;
        }
        .reminder-card .reminder-top {
            display:flex;
            flex-direction:column;
            gap:0.2rem;
            margin-top:0.8rem;
        }
        .reminder-card .reminder-med {
            margin:0;
            font-size:1rem;
            font-weight:700;
            color:var(--text);
        }
        .reminder-card .reminder-time {
            font-weight:600;
            color:var(--muted);
        }
        .reminder-card .reminder-meta {
            margin-top:0.6rem;
            display:flex;
            flex-direction:column;
            gap:0.35rem;
            font-size:0.9rem;
            color:var(--muted);
        }
        .reminder-card .reminder-meta span {
            display:block;
            padding:0.4rem 0.65rem;
            border-radius:14px;
            background:rgba(255,255,255,0.7);
            border:1px solid rgba(255,148,184,0.25);
        }
        .tools-grid {
            display:grid;
            grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
            gap:1rem;
        }
        </style>
        """

# Apply CSS based on theme
st.markdown(get_css(), unsafe_allow_html=True)


def render_section_header(icon: str, title: str, subtitle: str = ""):
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    icon_text = icon if icon and icon.isascii() else ""
    icon_html = f'<div class="section-icon">{icon_text}</div>' if icon_text else ""
    html = (
        "<div class=\"section-header\">"
        f"{icon_html}"
        "<div class=\"section-text\">"
        f"<h2>{title}</h2>"
        f"{subtitle_html}"
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_pill(text: str, target=None):
    target = target or st
    target.markdown(f"<div class='pill'>{text}</div>", unsafe_allow_html=True)


BANGLA_DAY_NAMES = {
    "Mon": "সোম",
    "Tue": "মঙ্গল",
    "Wed": "বুধ",
    "Thu": "বৃহস্পতি",
    "Fri": "শুক্র",
    "Sat": "শনি",
    "Sun": "রবি",
}

BANGLA_MONTH_NAMES = {
    "Jan": "জানু",
    "Feb": "ফেব্রু",
    "Mar": "মার্চ",
    "Apr": "এপ্রিল",
    "May": "মে",
    "Jun": "জুন",
    "Jul": "জুলাই",
    "Aug": "আগস্ট",
    "Sep": "সেপ্টে",
    "Oct": "অক্টো",
    "Nov": "নভে",
    "Dec": "ডিসে",
}

BANGLA_DIGIT_MAP = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

BENGALI_TO_ASCII_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

BANGLA_MONTH_FULL = {
    "জানুয়ারি": "January",
    "ফেব্রুয়ারি": "February",
    "মার্চ": "March",
    "এপ্রিল": "April",
    "মে": "May",
    "জুন": "June",
    "জুলাই": "July",
    "আগস্ট": "August",
    "সেপ্টেম্বর": "September",
    "অক্টোবর": "October",
    "নভেম্বর": "November",
    "ডিসেম্বর": "December",
}

BANGLA_DATE_KEYWORDS = {
    "আজ": "today",
    "আগামীকাল": "tomorrow",
    "পরশু": "day after tomorrow",
    "গতকাল": "yesterday",
}


def to_local_digits(value: str):
    if st.session_state.get("ui_lang") == "bn":
        return str(value).translate(BANGLA_DIGIT_MAP)
    return str(value)


def localized_number(value):
    return to_local_digits(value) if st.session_state.get("ui_lang") == "bn" else str(value)


def localized_day_parts(day_obj):
    weekday = day_obj.strftime("%a")
    month = day_obj.strftime("%b")
    day_num = day_obj.strftime("%d").lstrip("0") or "0"
    if st.session_state.get("ui_lang") == "bn":
        weekday = BANGLA_DAY_NAMES.get(weekday, weekday)
        month = BANGLA_MONTH_NAMES.get(month, month)
        day_num = to_local_digits(day_num)
    return weekday, f"{month} {day_num}"

def normalize_voice_string(text: str):
    normalized = text.strip()
    for bn, en in BANGLA_MONTH_FULL.items():
        normalized = normalized.replace(bn, en)
    for bn, en in BANGLA_DATE_KEYWORDS.items():
        normalized = normalized.replace(bn, en)
    normalized = normalized.translate(BENGALI_TO_ASCII_DIGITS)
    return normalized

def parse_spoken_time(text: str):
    normalized = normalize_voice_string(text).lower()
    match = re.search(r"(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", normalized)
    if not match:
        return None
    hour = int(match.group(1))
    minute = match.group(2) or "00"
    ampm = match.group(3)
    if ampm == "pm" and hour != 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    hour %= 24
    return f"{hour:02}:{int(minute):02}"

def parse_spoken_date(text: str):
    normalized = normalize_voice_string(text).lower()
    today = datetime.now().date()
    if "today" in normalized:
        return today
    if "tomorrow" in normalized:
        return today + timedelta(days=1)
    if "day after tomorrow" in normalized:
        return today + timedelta(days=2)
    if "yesterday" in normalized:
        return today - timedelta(days=1)
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%b %d %Y",
        "%B %d %Y",
        "%b %d",
        "%B %d",
    ]
    normalized = normalized.replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
    for fmt in formats:
        try:
            dt = datetime.strptime(normalized, fmt)
            if "%Y" not in fmt:
                dt = dt.replace(year=today.year)
            return dt.date()
        except ValueError:
            continue
    return None

EN_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

BN_NUMBER_WORDS = {
    "এক": 1,
    "দুই": 2,
    "তিন": 3,
    "চার": 4,
    "পাঁচ": 5,
    "ছয়": 6,
    "সাত": 7,
    "আট": 8,
    "নয়": 9,
    "দশ": 10,
}

def parse_spoken_number(text: str):
    normalized = normalize_voice_string(text).lower()
    match = re.search(r"\d+(?:\.\d+)?", normalized)
    if match:
        value = match.group()
        return float(value) if "." in value else int(value)
    for word, value in EN_NUMBER_WORDS.items():
        if word in normalized:
            return value
    for word, value in BN_NUMBER_WORDS.items():
        if word in normalized:
            return value
    fractions = {
        ("half",): 0.5,
        ("one", "half"): 1.5,
    }
    words = normalized.split()
    for idx, word in enumerate(words):
        next_word = words[idx + 1] if idx + 1 < len(words) else ""
        if word == "half":
            return 0.5
        if word in EN_NUMBER_WORDS and next_word == "half":
            return EN_NUMBER_WORDS[word] + 0.5
        if word in BN_NUMBER_WORDS and next_word == "আধা":
            return BN_NUMBER_WORDS[word] + 0.5
    return None
    return None


def humanize_minutes(seconds):
    if seconds is None:
        return "0m"
    minutes = max(1, int(round(abs(seconds) / 60)))
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours}h"
    return f"{hours}h {mins}m"


def describe_reminder_status(diff_seconds):
    if diff_seconds < -120:
        return T("chip_due_in").format(time=humanize_minutes(diff_seconds)), "chip-upcoming"
    if diff_seconds < 0:
        return T("chip_due_soon"), "chip-soon"
    if diff_seconds < 300:
        return T("chip_due_now"), "chip-now"
    return T("chip_overdue").format(time=humanize_minutes(diff_seconds)), "chip-overdue"


def render_week_tracker(conn, user_id, start_date, days=5):
    if not user_id:
        return
    end_date = start_date + timedelta(days=days - 1)
    try:
        df = pd.read_sql_query(
            """
            SELECT date, medicine, is_taken
            FROM medicine
            WHERE user_id=? AND date BETWEEN ? AND ?
            ORDER BY date, reminder_time
            """,
            conn,
            params=(user_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        )
    except Exception:
        return
    if df.empty:
        st.info(T("week_tracker_none"))
        return
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    cards = []
    for offset in range(days):
        day = start_date + timedelta(days=offset)
        day_records = df[df["date"].dt.date == day]
        total = len(day_records)
        taken = int(day_records["is_taken"].sum()) if total else 0
        due = total - taken
        meds = sorted(
            {row["medicine"] for _, row in day_records.iterrows()}
        )
        meds_label = ", ".join(meds[:2]) if meds else T("week_tracker_no_meds")
        remaining = len(meds) - 2
        if remaining > 0:
            meds_label += " " + T("week_tracker_more").format(count=localized_number(remaining))
        card_class = "day-card day-card--today" if day == start_date else "day-card"
        weekday_label, date_label = localized_day_parts(day)
        cards.append(
            (
                f"<div class=\"{card_class}\">"
                f"<div class=\"day-card__day\">{weekday_label}</div>"
                f"<div class=\"day-card__date\">{date_label}</div>"
                f"<div class=\"day-card__count\">{T('week_tracker_due').format(count=localized_number(due))}</div>"
                f"<div class=\"day-card__count\" style=\"color:#2eaa66;\">"
                f"{T('week_tracker_taken').format(count=localized_number(taken))}</div>"
                f"<div class=\"day-card__meds\">{meds_label}</div>"
                "</div>"
            )
        )
    header_html = (
        "<div class=\"section-header\" style=\"margin-top:0;\">"
        "<div class=\"section-text\">"
        f"<h2 style=\"margin-bottom:0.2rem;\">{T('week_tracker_title')}</h2>"
        f"<p style=\"margin:0;\">{T('week_tracker_subtitle')}</p>"
        "</div>"
        "</div>"
    )
    grid_html = f"<div class=\"day-grid\">{''.join(cards)}</div>"
    st.markdown(header_html + grid_html, unsafe_allow_html=True)


def render_reminder_card(row, day_date, now, conn, user, user_email, family_lookup, allow_actions=True):
    notify_names, notify_emails = resolve_notification_targets(row, family_lookup)
    try:
        reminder_time = datetime.strptime(row["reminder_time"], "%H:%M").time()
    except (TypeError, ValueError):
        return
    dt = datetime.combine(day_date, reminder_time)
    diff = (now - dt).total_seconds()

    if allow_actions and row.get("voice_alerted", 0) and diff < 0:
        conn.execute("UPDATE medicine SET voice_alerted=0 WHERE id=?", (row["id"],))
        conn.commit()
        return

    status = T("taken") if row["is_taken"] else T("pending")

    if allow_actions:
        should_voice_alert = (
            -VOICE_ALERT_WINDOW_BEFORE <= diff <= VOICE_ALERT_WINDOW_AFTER
            and not row["is_taken"]
            and not row.get("voice_alerted", 0)
        )
        should_email_alert = diff >= -5 and not row.get("email_notified", 0)

        if should_voice_alert:
            play_voice_alert(row["medicine"], st.session_state.alert_lang)
            conn.execute("UPDATE medicine SET voice_alerted=1 WHERE id=?", (row["id"],))
            conn.commit()

        if should_email_alert and notify_emails:
            notes_text = row["instructions"] or T("notes_none")
            subject = f"MediVoice reminder: {row['medicine']} at {row['reminder_time']}"
            body = (
                f"Hello,\n\n"
                f"This is a reminder that {row['medicine']} is scheduled for {row['date']} at {row['reminder_time']}.\n"
                f"Dosage: {row['dosage'] or '-'}\n"
                f"{T('dose_quantity_label')}: {int(row.get('dose_quantity') or 1)}\n"
                f"Instructions: {notes_text}\n\n"
                "Please ensure the medicine is taken on time.\n\n"
                "Sent by MediVoice."
            )
            sent, sent_to = send_email_notification(notify_emails, subject, body)
            if sent:
                conn.execute("UPDATE medicine SET email_notified=1 WHERE id=?", (row["id"],))
                conn.commit()
                st.info(T("notification_sent").format(recipients=", ".join(sent_to)))
    else:
        should_voice_alert = False

    chip_label, chip_class = describe_reminder_status(diff)
    notify_html = ""
    if notify_names:
        notify_html = f"<span>{T('notify_recipients_label')}: {', '.join(notify_names)}</span>"

    card_html = (
        "<div class='reminder-card'>"
        f"<div class='reminder-chip {chip_class}'>{chip_label}</div>"
        "<div class='reminder-top'>"
        f"<p class='reminder-med'>{row['medicine']}</p>"
        f"<div class='reminder-time'>{row['reminder_time']}</div>"
        "</div>"
        "<div class='reminder-meta'>"
        f"<span>{T('status_label')}: {status}</span>"
        f"{notify_html}"
        "</div>"
        "</div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)

    if not allow_actions:
        return

    row1 = st.columns(2)
    if row1[0].button(T("taken"), key=f"tk{row['id']}", use_container_width=True):
        if not row["is_taken"]:
            conn.execute("UPDATE medicine SET is_taken=1 WHERE id=?", (row["id"],))
            conn.commit()
            dose_qty = int(row.get("dose_quantity") or 1)
            logged, remaining = record_inventory_usage(
                conn,
                user,
                row["medicine"],
                quantity=dose_qty,
                source="reminder"
            )
            if logged:
                record_notification(
                    T("inventory_log_success").format(
                        medicine=row["medicine"],
                        qty=dose_qty,
                        stock=remaining
                    )
                )
                process_inventory_alerts(conn, user, user_email, family_lookup, show_feedback=True)
        else:
            record_notification(T("inventory_no_match"))
        st.rerun()

    if row1[1].button(T("delete"), key=f"dl{row['id']}", use_container_width=True):
        conn.execute("DELETE FROM medicine WHERE id=?", (row["id"],))
        conn.commit()
        st.rerun()

    row2 = st.columns(2)
    if row2[0].button(T("voice_play_now"), key=f"pv{row['id']}", use_container_width=True):
        play_voice_alert(row["medicine"], st.session_state.alert_lang)

    if row2[1].button(T("snooze_btn"), key=f"sn{row['id']}", use_container_width=True):
        minutes = int(st.session_state.get("snooze_minutes", 10))
        new_dt = snooze_reminder(conn, row["id"], minutes)
        if new_dt:
            message = T("snooze_success").format(time=new_dt.strftime("%H:%M"))
            st.success(message)
            record_notification(message)
        else:
            st.error(T("snooze_failed"))
        st.rerun()

def configure_chart_fonts():
    if st.session_state.get("ui_lang") == "bn":
        font_choices = [
            "Nirmala UI",
            "Vrinda",
            "Noto Sans Bengali",
            "Siyam Rupali",
            "Segoe UI",
            "Arial Unicode MS",
            "DejaVu Sans"
        ]
        plt.rcParams["font.family"] = font_choices
        plt.rcParams["axes.unicode_minus"] = False
    else:
        plt.rcParams["font.family"] = "DejaVu Sans"


# ============================================================
# API KEYS
# ============================================================
GEMINI_KEY = "AIzaSyARtGA0hlF1tyTMDY0jTwOeVXzbSEbbXRo"

# Directory for storing uploaded prescriptions
PRESCRIPTION_DIR = Path("prescription_uploads")
PRESCRIPTION_DIR.mkdir(exist_ok=True)


# ============================================================
# SESSION DEFAULTS
# ============================================================
st.session_state.setdefault("logged", False)
st.session_state.setdefault("page", "login")
st.session_state.setdefault("ui_lang", "en")
st.session_state.setdefault("alert_lang", "en")
st.session_state.setdefault("notification_voice_lang_ref", {"value": st.session_state.alert_lang})
st.session_state.setdefault("notification_log", [])
st.session_state.setdefault("snooze_minutes", 10)
NOTIFICATION_POLL_SECONDS = 2
NOTIFICATION_QUEUE = deque(maxlen=50)
NOTIFICATION_LOCK = threading.Lock()
# Voice alert grace windows (in seconds)
VOICE_ALERT_WINDOW_BEFORE = 0     # no early alerts; wait until reminder time
VOICE_ALERT_WINDOW_AFTER = 7200   # keep trying up to 2 hours late
# Appointment alert window in seconds (1 minute)
APPOINTMENT_ALERT_WINDOW_SECONDS = 60
DASHBOARD_HISTORY_DAYS = 7
DASHBOARD_FUTURE_DAYS = 7
REMINDER_TILE_COLUMNS = 3
DASHBOARD_HISTORY_DAYS = 7
DASHBOARD_FUTURE_DAYS = 7


# ============================================================
# LANGUAGE TEXTS
# ============================================================
TEXT = {
    "en": {
        "login": "Login",
        "signup": "Signup",
        "dashboard": "Dashboard",
        "reminders": "Reminders",
        "reports": "Reports",
        "tools": "Tools",
        "ai": "AI Assistant",
        "logout": "Logout",
        "today_rem": "Today's Reminders",
        "no_today": "No reminders today.",
        "add_rem": "Add New Reminder",
        "ask": "Ask anything…",
        "med_name": "Medicine Name",
        "dos": "Dosage",
        "freq": "Frequency",
        "inst": "Instructions",
        "date": "Date",
        "time": "Time (HH:MM)",
        "save": "Save",
        "taken": "Taken",
        "delete": "Delete",
        "choose_tool": "Choose a Tool:",
        "inventory_tool": "Inventory Manager",
        "prescription_photos": "Prescription Photos",
        "interaction_checker": "Interaction Checker",
        "voice_commands": "Voice Commands",
        "doctor_appointments": "Doctor Appointment Reminders",
        "inventory_subtitle": "Track low stock medicines at a glance",
        "inventory_stock": "Stock",
        "inventory_threshold": "Low Stock Alert",
        "notes_label": "Notes",
        "notes_helper": "Add any instructions from your doctor.",
        "notes_optional": "Notes (optional)",
        "notes_optional_help": "Add a short reminder about dosage instructions or doctor comments.",
        "notes_none": "None",
        "inventory_saved": "Inventory saved!",
        "inventory_empty": "No inventory yet.",
        "low_stock_badge": "⚠️ LOW STOCK",
        "out_stock_badge": "🚨 OUT OF STOCK",
        "inventory_out_warning": "The following medicines are out of stock: {medicine}. Email alerts will be sent.",
        "inventory_out_subject": "MediVoice stock alert: {medicine} is out of stock",
        "inventory_out_body": "Hi,\n\n{medicine} has run out of stock. Notes: {notes}\n\nPlease restock it soon to avoid missed doses.\n\n- MediVoice",
        "inventory_out_no_email": "Add an email address to your profile to receive stock alerts.",
        "inventory_out_sent": "Out-of-stock alert sent for {medicine} to {recipients}",
        "inventory_low_subject": "MediVoice low stock alert: {medicine}",
        "inventory_low_body": "Hi,\n\n{medicine} is low on stock (below threshold). Notes: {notes}\n\nPlease restock soon.\n\n- MediVoice",
        "inventory_low_sent": "Low-stock alert sent for {medicine} to {recipients}",
        "appointment_email_subject": "Upcoming appointment: {doctor} on {date} at {time}",
        "appointment_email_body": "Hi,\n\nYou have an upcoming appointment with {doctor} at {hospital} on {date} at {time}. Notes: {notes}\n\n- MediVoice",
        "appointment_email_sent": "Appointment reminder sent for {doctor} to {recipients}",
        "inventory_log_title": "Log medicine intake",
        "inventory_log_helper": "Keep your stock accurate by recording doses taken.",
        "inventory_log_quantity": "Quantity taken",
        "inventory_log_button": "Log intake",
        "inventory_log_success": "Logged {qty} dose(s) for {medicine}. Remaining stock: {stock}",
        "inventory_no_match": "Add this medicine to inventory first to track usage.",
        "inventory_logged_label": "Doses logged",
        "inventory_last_logged": "Last logged",
        "inventory_notify_label": "Stock alert recipients",
        "inventory_notify_help": "Choose who should receive low/out-of-stock emails.",
        "inventory_notify_self": "Email me as well",
        "inventory_notify_self_label": "You",
        "inventory_recipients_label": "Alerts go to",
        "dose_quantity_label": "Dose quantity",
        "dose_quantity_help": "How many units are taken with each reminder.",
        "inventory_manage_tab": "Manage Stock",
        "inventory_log_tab": "Log Intake",
        "ok_badge": "✅ OK",
        "prescription_subtitle": "Securely store doctor's instructions and notes",
        "prescription_intro": "Store prescription snapshots safely for later review or sharing with your doctor.",
        "upload_prescription": "Upload prescription image",
        "save_prescription_btn": "Save Prescription Image",
        "prescription_read_error": "Could not read the uploaded file. Please try again.",
        "prescription_saved": "Prescription image saved!",
        "prescription_select_prompt": "No prescription selected yet. Choose an image to get started.",
        "saved_prescriptions": "Saved Prescriptions",
        "prescription_empty": "No prescription images have been saved yet.",
        "image_missing": "Image file missing on disk.",
        "download_image": "⬇️ Download Image",
        "interaction_subtitle": "Find potential conflicts instantly",
        "medicine_one": "Medicine 1",
        "medicine_two": "Medicine 2",
        "check": "Check",
        "interaction_ibuprofen_aspirin": "Increases bleeding risk",
        "interaction_warfarin_aspirin": "Severe bleeding risk",
        "interaction_metformin_alcohol": "Lactic acidosis danger",
        "interaction_paracetamol_alcohol": "Liver damage risk",
        "interaction_none": "No major interactions found.",
        "voice_subtitle": "Hands-free actions for your meds",
        "start_listening": "Start Listening",
        "voice_not_understood": "Not understood",
        "voice_you_said": "You said: {text}",
        "voice_added": "Added: {medicine} at {time}",
        "voice_listening_prompt": "Listening... Please speak now.",
        "voice_date_invalid": "Couldn't understand that date. Try saying 'November 18' or 'today'.",
        "voice_number_invalid": "Couldn't detect a number in your voice command.",
        "voice_delete_none": "No reminders to delete",
        "voice_deleted": "Deleted {medicine}",
        "voice_alert_msg": "It's time to take {medicine}.",
        "voice_play_now": "Play voice reminder",
        "snooze_btn": "Snooze 10 min",
        "snooze_success": "Reminder snoozed to {time}.",
        "snooze_failed": "Could not snooze this reminder.",
        "voice_med_missing": "Please mention the medicine name in your voice command.",
        "chip_due_in": "Due in {time}",
        "chip_due_soon": "Almost time",
        "chip_due_now": "Due now",
        "chip_overdue": "Overdue {time}",
        "speak_english_btn": "Play reminder (English)",
        "speak_bangla_btn": "Play reminder (Bangla)",
        "appointment_subtitle": "Plan visits and stay notified",
        "doctor_name_label": "Doctor Name",
        "hospital_label": "Hospital / Clinic",
        "save_appointment": "Save Appointment",
        "appointment_saved": "Appointment saved!",
        "invalid_time": "Invalid time format! Use HH:MM",
        "invalid_email": "Please enter a valid email address.",
        "voice_alert_sent": "Voice alert sent for {doctor} ({time}).",
        "snooze_length_label": "Snooze duration (minutes)",
        "snooze_length_help": "Choose how long reminders sleep when you hit Snooze.",
        "day_label_today": "Today · {date}",
        "day_label_other": "{weekday} · {date}",
        "history_section": "Previous reminders",
        "history_empty": "No previous reminders in this window.",
        "history_note": "Past reminders are read-only.",
        "week_tracker_title": "Week at a glance",
        "week_tracker_subtitle": "Each square shows the medicines due on that day.",
        "week_tracker_none": "No reminders scheduled",
        "week_tracker_due": "{count} due",
        "week_tracker_taken": "{count} taken",
        "week_tracker_no_meds": "No meds",
        "week_tracker_more": "+{count} more",
        "weekly_card_taken_label": "Taken",
        "weekly_card_missed_label": "Missed",
        "weekly_card_completion_label": "On track",
        "weekly_card_meds_label": "Medicines",
        "weekly_card_empty": "No medicines logged.",
        "weekly_card_more": "+{count} more",
        "weekly_card_badge": "{taken}/{total}",
        "tools_subtitle": "Quick utilities for your day",
        "sleep_insights": "Sleep_insights",
        "sleep_subtitle": "Log nightly rest, mood, and notes to understand trends.",
        "sleep_log_header": "Add a new sleep entry",
        "sleep_log_date": "Night of sleep.",
        "sleep_hours": "Hours slept (in hours)",
        "sleep_quality_label": "Sleep quality (1–5)",
        "sleep_mood_label": "Morning mood (1–5).",
        "sleep_save_entry": "Save sleep entry",
        "sleep_saved": "Sleep entry saved!",
        "sleep_empty": "No sleep entries yet. Add one using the form above.",
        "sleep_avg_hours": "Average hours (7 days).",
        "sleep_quality_trend": "Average quality (7 days)",
        "sleep_streak": "Logged nights.",
        "sleep_variability": "Consistency",
        "sleep_recent_entries": "Recent sleep records",
        "sleep_chart_title": "Recent 14 nights",
        "sleep_tip_positive": "Congrats! Keep going to bed at the same time.",
        "sleep_tip_negative": "Aim for 7–9 hours of sleep and cut back on late-night screen time.",
        "quick_prompt_summary": "Summarize today's reminders",
        "quick_prompt_motivation": "Suggest a gentle motivation message",
        "quick_prompt_family": "Draft a friendly message for my family",
        "reports_subtitle": "Insights and exports",
        "report_choose": "Choose Report:",
        "report_weekly": "Weekly Summary",
        "report_analytics": "Advanced Analytics",
        "report_monthly": "Monthly Report",
        "weekly_title": "Weekly Summary",
        "weekly_subtitle": "7-day adherence snapshot",
        "analytics_title": "Advanced Analytics",
        "analytics_subtitle": "Trend insights across your regimen",
        "monthly_title": "Monthly Report",
        "monthly_subtitle": "Export and share polished summaries",
        "app_title": "MediVoice App",
        "app_subtitle": "Your health companion",
        "signup_title": "Create Account",
        "signup_subtitle": "Join MediVoice to plan your care",
        "username": "Username",
        "password": "Password",
        "email": "Email",
        "create_account_btn": "Create Account",
        "back_to_login": "Back to Login",
        "fill_fields": "Fill all fields.",
        "account_created": "Account created!",
        "username_exists": "Username already exists",
        "user_not_found": "User not found",
        "incorrect_password": "Incorrect password",
        "dashboard_subtitle": "Live reminders & voice alerts",
        "reminders_subtitle": "Schedule medicines and keep them organized",
        "ai_subtitle": "Ask MediVoice anything",
        "ai_greeting": "Hello! I'm your MediVoice assistant. How can I help?",
        "ai_listen_header": "🔊 Listen to Answer",
        "ai_play_en": "🎧 Play in English",
        "ai_play_bn": "🎧 Listen in Bangla",
        "ai_thinking": "Thinking...",
        "ai_you_label": "You",
        "ai_bot_label": "AI",
        "settings_title": "⚙ Settings",
        "app_language_label": "App Language",
        "voice_language_label": "Voice Alert Language",
        "language_english": "English",
        "language_bangla": "Bangla",
        "intake_per_medicine": "Intake Per Medicine",
        "compliance_30_day": "30-Day Compliance",
        "missed_vs_taken": "Missed vs Taken",
        "top_meds_label": "Most Frequently Taken Medicines",
        "time_of_day_adherence": "Time-of-Day Adherence",
        "monthly_summary": "Monthly Performance Summary",
        "no_data": "No data available.",
        "analytics_empty": "No data available for analytics yet.",
        "monthly_empty": "No records available for this month.",
        "reminder_added": "Reminder added!",
        "status_label": "Status",
        "pending": "Pending",
        "missed": "Missed",
        "taken_vs_missed": "Taken vs Missed",
        "overall_compliance": "Overall Compliance",
        "monthly_compliance": "Monthly Compliance",
        "generate_pdf_btn": "📄 Generate Monthly PDF",
        "pdf_success": "PDF generated successfully!",
        "download_report": "📩 Download Report",
        "pdf_title": "MediVoice - Monthly Report",
        "pdf_user_line": "User: {user}",
        "pdf_summary_line": "Last 30 Days Summary",
        "pdf_total_line": "Total Reminders: {count}",
        "pdf_taken_line": "Taken: {count}",
        "pdf_missed_line": "Missed: {count}",
        "pdf_compliance_line": "Compliance: {percent}%",
        "pdf_top_meds": "Top Medicines:",
        "pdf_med_entry": "{medicine}: {count} doses",
        "preview": "Preview",
        "manage_family": "Family Members",
        "family_subtitle": "Track relatives and their health needs",
        "add_family_member": "Add Family Member",
        "member_name": "Member Name",
        "relationship": "Relationship",
        "relationship_mother": "Mother",
        "relationship_father": "Father",
        "relationship_wife": "Wife",
        "relationship_husband": "Husband",
        "relationship_son": "Son",
        "relationship_daughter": "Daughter",
        "relationship_brother": "Brother",
        "relationship_sister": "Sister",
        "relationship_grandfather": "Grandfather",
        "relationship_grandmother": "Grandmother",
        "relationship_other": "Other",
        "age": "Age",
        "health_conditions": "Health Conditions",
        "save_member": "Save Member",
        "member_saved": "Family member saved!",
        "member_name_required": "Member name is required.",
        "family_email_instructions": "Add their email so they can receive reminders.",
        "family_email_missing": "Email not provided",
        "notify_family_label": "Notify Family Members (optional)",
        "notify_family_help": "Select relatives who should receive reminder emails at this time.",
        "no_family_emails": "Add at least one family member with an email to send notifications.",
        "email_settings_missing": "Email settings are not configured. Set SMTP_* environment variables or Streamlit secrets.",
        "email_send_error": "Could not send email notification: {error}",
        "notification_sent": "Reminder email sent to: {recipients}",
        "notification_skipped": "No email recipients configured.",
        "notify_recipients_label": "Email alerts",
        "saved_family_members": "Saved Family Members",
        "no_family_members": "No family members added yet.",
        "delete_member": "Delete Member",
        "health_none": "No notes provided",
        "family_deleted": "Family member removed.",
        "forgot_password": "Forgot Password?",
        "recover_password": "Recover Password",
        "recovery_subtitle": "Enter your email to reset your password",
        "send_recovery": "Send Recovery Link",
        "recovery_sent": "Password recovery link sent to your email!",
        "reset_password": "Reset Password",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "password_mismatch": "Passwords do not match",
        "password_reset_success": "Password reset successfully!",
        "theme_toggle": "Theme",
        "dark_theme": "Dark Theme",
        "light_theme": "Light Theme"
    },
    "bn": {
        "login": "লগইন",
        "signup": "অ্যাকাউন্ট তৈরি",
        "dashboard": "ড্যাশবোর্ড",
        "reminders": "রিমাইন্ডার",
        "reports": "রিপোর্ট",
        "tools": "টুলস",
        "ai": "এআই সহকারী",
        "logout": "লগআউট",
        "today_rem": "আজকের রিমাইন্ডার",
        "no_today": "আজ কোনো রিমাইন্ডার নেই",
        "add_rem": "রিমাইন্ডার যোগ করুন",
        "ask": "যেকোনো কিছু জিজ্ঞাসা করুন…",
        "med_name": "ওষুধের নাম",
        "dos": "ডোজ",
        "freq": "ফ্রিকোয়েন্সি",
        "inst": "নির্দেশনা",
        "date": "তারিখ",
        "time": "সময় (HH:MM)",
        "save": "সেভ",
        "taken": "খাওয়া হয়েছে",
        "delete": "ডিলিট",
        "choose_tool": "টুল নির্বাচন করুন:",
        "inventory_tool": "মজুত ব্যবস্থাপনা সরঞ্জাম",
        "prescription_photos": "প্রেসক্রিপশনের ছবি",
        "interaction_checker": "ঔষধের পারস্পরিক ক্রিয়া যাচাইকারী",
        "voice_commands": "ভয়েসের মাধ্যমে নির্দেশ",
        "doctor_appointments": "ডাক্তারের সঙ্গে সাক্ষাতের সময়",
        "inventory_subtitle": "কম স্টকের ওষুধ এক নজরে দেখুন",
        "inventory_stock": "স্টক",
        "inventory_threshold": "কম স্টক সতর্কতা",
        "notes_label": "নোট",
        "notes_helper": "ডাক্তারের নির্দেশাবলী লিখে রাখুন।",
        "notes_optional": "নোট (ঐচ্ছিক)",
        "notes_optional_help": "ডোজ বা ডাক্তারের মন্তব্য নিয়ে একটি সংক্ষিপ্ত স্মরণিকা লিখুন।",
        "notes_none": "কিছুই নেই",
        "inventory_saved": "ইনভেন্টরি সংরক্ষিত!",
        "inventory_empty": "এখনও কোনো ইনভেন্টরি যোগ করা হয়নি।",
        "low_stock_badge": "⚠️ কম স্টক",
        "out_stock_badge": "🚨 ওষুধ শেষ",
        "inventory_out_warning": "এই ঔষধগুলো মজুত নেই: {medicine}। ইমেল সতর্কতা পাঠানো হবে।",
        "inventory_out_subject": "MediVoice সতর্কতা: {medicine} শেষ হয়ে গেছে",
        "inventory_out_body": "প্রিয় ব্যবহারী,\n\nআপনার {medicine} ঔষুধের স্টক শূন্য। নোট: {notes}\n\nদয়া করে দ্রুত ঔষুধ কিনুন যাতে ডোজ মিস না হয়।\n\n- MediVoice",
        "inventory_out_no_email": "স্টক সতর্কতার জন্য অ্যাকাউন্টে একটি ইমেল ঠিকানা যোগ করুন।",
        "inventory_out_sent": "{medicine} ঔষুধের স্টক সতর্কতা পাঠানো হয়েছে: {recipients}",
        "inventory_log_title": "ইনটেক লগ করুন",
        "inventory_log_helper": "ডোজ নেওয়ার সঙ্গে সঙ্গে স্টক হালনাগাদ রাখুন।",
        "inventory_log_quantity": "নেওয়া পরিমাণ",
        "inventory_log_button": "ইনটেক সংরক্ষণ",
        "inventory_log_success": "{medicine} এর {qty} ডোজ লগ হয়েছে। অবশিষ্ট স্টক: {stock}",
        "inventory_no_match": "ব্যবহার করতে হলে আগে ইনভেন্টরিতে ঔষুধটি যোগ করুন।",
        "inventory_logged_label": "লগ হওয়া ডোজ",
        "inventory_last_logged": "শেষ লগ",
        "inventory_notify_label": "স্টক সতর্কতার প্রাপক",
        "inventory_notify_help": "কোন সদস্যরা কম/ফুরিয়ে যাওয়া স্টকের ইমেল পাবেন তা নির্বাচন করুন।",
        "inventory_notify_self": "আমাকেও ইমেল করুন",
        "inventory_notify_self_label": "আপনি",
        "inventory_recipients_label": "সতর্কতা যাবে",
        "dose_quantity_label": "প্রতি ডোজে পরিমাণ",
        "dose_quantity_help": "প্রতিবার রিমাইন্ডারে কয়টি ইউনিট গ্রহণ করেন।",
        "ok_badge": "✔ ঠিক আছে",
        "prescription_subtitle": "ডাক্তারের নির্দেশ ও নোট নিরাপদে রাখুন",
        "prescription_intro": "ডাক্তারের সাথে ভাগ করার বা পরে দেখার জন্য প্রেসক্রিপশনের ছবি সংরক্ষণ করুন।",
        "upload_prescription": "প্রেসক্রিপশনের ছবি আপলোড করুন",
        "save_prescription_btn": "প্রেসক্রিপশন ছবি সংরক্ষণ করুন",
        "prescription_read_error": "আপলোড করা ফাইল পড়া যায়নি। আবার চেষ্টা করুন।",
        "prescription_saved": "প্রেসক্রিপশনের ছবি সংরক্ষিত হয়েছে!",
        "prescription_select_prompt": "এখনও কোনো প্রেসক্রিপশন নির্বাচন করা হয়নি। শুরু করতে একটি ছবি বেছে নিন।",
        "saved_prescriptions": "সংরক্ষিত প্রেসক্রিপশন",
        "prescription_empty": "কোনো প্রেসক্রিপশন ছবি এখনও সংরক্ষণ করা হয়নি।",
        "image_missing": "ডিস্কে ছবিটি পাওয়া যায়নি।",
        "download_image": "⬇️ ছবি ডাউনলোড করুন",
        "interaction_subtitle": "সম্ভাব্য সংঘাত দ্রুত খুঁজে নিন",
        "medicine_one": "ওষুধ ১",
        "medicine_two": "ওষুধ ২",
        "check": "পরীক্ষা করুন",
        "interaction_ibuprofen_aspirin": "রক্তক্ষরণের ঝুঁকি বাড়ায়",
        "interaction_warfarin_aspirin": "তীব্র রক্তক্ষরণের ঝুঁকি",
        "interaction_metformin_alcohol": "ল্যাকটিক অ্যাসিডোসিসের ঝুঁকি",
        "interaction_paracetamol_alcohol": "লিভার ক্ষতির ঝুঁকি",
        "interaction_none": "কোনো বড় মিথস্ক্রিয়া পাওয়া যায়নি।",
        "voice_subtitle": "ওষুধের কাজ হাত ছাড়া সেরে ফেলুন",
        "start_listening": "শুনতে শুরু করুন",
        "voice_not_understood": "বুঝতে পারিনি",
        "voice_you_said": "আপনি বলেছিলেন: {text}",
        "voice_added": "{time} সময় {medicine} যোগ করা হয়েছে",
        "voice_listening_prompt": "শুনছি... এখন কথা বলুন।",
        "voice_date_invalid": "তারিখ বোঝা যায়নি। বলুন 'নভেম্বর ১৮' বা 'আজ'।",
        "voice_number_invalid": "ভয়েস নির্দেশে কোনো সংখ্যা বোঝা যায়নি।",
        "voice_med_missing": "ভয়েস নির্দেশে অনুগ্রহ করে ওষুধের নাম বলুন।",
        "voice_delete_none": "মুছে ফেলার মতো কোনো রিমাইন্ডার নেই",
        "voice_deleted": "{medicine} মুছে ফেলা হয়েছে",
        "voice_alert_msg": "{medicine} খাওয়ার সময় হয়েছে।",
        "voice_play_now": "ভয়েস রিমাইন্ডার চালু করুন",
        "snooze_btn": "১০ মিনিট পিছিয়ে দিন",
        "snooze_success": "রিমাইন্ডার {time} পর্যন্ত স্থগিত হয়েছে।",
        "snooze_failed": "এই রিমাইন্ডার পিছানো গেল না।",
        "chip_due_in": "{time} বাকি",
        "chip_due_soon": "প্রায় সময়",
        "chip_due_now": "এখনই সময়",
        "chip_overdue": "{time} দেরি",
        "speak_english_btn": "ইংরেজিতে শুনুন",
        "speak_bangla_btn": "বাংলায় শুনুন",
        "appointment_subtitle": "চিকিৎসা ভিজিট পরিকল্পনা করুন ও সতর্ক থাকুন",
        "doctor_name_label": "ডাক্তারের নাম",
        "hospital_label": "হাসপাতাল / ক্লিনিক",
        "save_appointment": "অ্যাপয়েন্টমেন্ট সংরক্ষণ করুন",
        "appointment_saved": "অ্যাপয়েন্টমেন্ট সংরক্ষিত হয়েছে!",
        "invalid_time": "সময়ের ফরম্যাট সঠিক নয়! HH:MM ব্যবহার করুন",
        "invalid_email": "Please enter a valid email address.",
        "voice_alert_sent": "{doctor} ({time})-এর জন্য ভয়েস অ্যালার্ট পাঠানো হয়েছে।",
        "snooze_length_label": "স্নুজ সময় (মিনিট)",
        "snooze_length_help": "স্নুজ চাপলে কত মিনিট পরে বাজবে ঠিক করুন।",
        "day_label_today": "আজ · {date}",
        "day_label_other": "{weekday} · {date}",
        "history_section": "পূর্বের রিমাইন্ডার",
        "history_empty": "এই সময়সীমায় কোনো পুরোনো রিমাইন্ডার নেই।",
        "history_note": "পূর্বের রিমাইন্ডার শুধুমাত্র পড়া যাবে।",
        "week_tracker_title": "সাপ্তাহিক নজর",
        "week_tracker_subtitle": "প্রতিটি বাক্সে সেই দিনের ওষুধের সময় দেখানো হচ্ছে।",
        "week_tracker_none": "কোনো রিমাইন্ডার নেই",
        "week_tracker_due": "{count} বাকি",
        "week_tracker_taken": "{count} সম্পন্ন",
        "week_tracker_no_meds": "কোনো ওষুধ নেই",
        "week_tracker_more": "+{count} আরও",
        "weekly_card_taken_label": "খাওয়া হয়েছে",
        "weekly_card_missed_label": "মিস হয়েছে",
        "weekly_card_completion_label": "অগ্রগতি",
        "weekly_card_meds_label": "ওষুধ",
        "weekly_card_empty": "কোনো ওষুধ যোগ করা নেই",
        "weekly_card_more": "+{count} আরও",
        "weekly_card_badge": "{taken}/{total}",
        "tools_subtitle": "দৈনন্দিন দ্রুত টুলসমূহ",
        "sleep_insights": "ঘুমের বিশ্লেষণ",
        "sleep_subtitle": "রাতের ঘুম, মুড ও নোট থেকে প্রবণতা খুঁজুন",
        "sleep_log_header": "নতুন ঘুমের তথ্য যুক্ত করুন",
        "sleep_log_date": "ঘুমের রাত",
        "sleep_hours": "ঘুমের সময় (ঘণ্টা)",
        "sleep_quality_label": "ঘুমের মান (১-৫)",
        "sleep_mood_label": "সকালের মুড (১-৫)",
        "sleep_save_entry": "ঘুমের তথ্য সংরক্ষণ",
        "sleep_saved": "ঘুমের তথ্য সংরক্ষিত হয়েছে!",
        "sleep_empty": "এখনও কোনও ঘুমের তথ্য নেই। উপরে যোগ করুন।",
        "sleep_avg_hours": "গড় ঘণ্টা (৭ দিন)",
        "sleep_quality_trend": "গড় মান (৭ দিন)",
        "sleep_streak": "লগ করা রাত",
        "sleep_variability": "স্থিতিশীলতা",
        "sleep_recent_entries": "সাম্প্রতিক ঘুমের লগ",
        "sleep_chart_title": "শেষ ১৪ রাত",
        "sleep_tip_positive": "অভ্যাস চমৎকার! একই সময়ে বিশ্রাম নিন।",
        "sleep_tip_negative": "৭-৯ ঘণ্টা ঘুমের চেষ্টা করুন এবং স্ক্রিন সময় কমান।",
        "reports_subtitle": "ইনসাইট ও এক্সপোর্ট",
        "report_choose": "রিপোর্ট নির্বাচন করুন:",
        "report_weekly": "সাপ্তাহিক সারাংশ",
        "report_analytics": "উন্নত বিশ্লেষণ",
        "report_monthly": "মাসিক রিপোর্ট",
        "weekly_title": "সাপ্তাহিক সারাংশ",
        "weekly_subtitle": "৭ দিনের অনুসরণ অবস্থা",
        "analytics_title": "উন্নত বিশ্লেষণ",
        "analytics_subtitle": "ধারাবাহিকতার প্রবণতা দেখুন",
        "monthly_title": "মাসিক রিপোর্ট",
        "monthly_subtitle": "মাসিক ডাটা ও শেয়ারযোগ্য আউটপুট",
        "app_title": "মেডিভয়েস অ্যাপ",
        "app_subtitle": "আপনার স্বাস্থ্য সঙ্গী",
        "signup_title": "অ্যাকাউন্ট তৈরি করুন",
        "signup_subtitle": "আপনার যত্ন পরিকল্পনার জন্য মেডিভয়েসে যোগ দিন",
        "username": "ব্যবহারকারীর নাম",
        "password": "পাসওয়ার্ড",
        "email": "ইমেইল",
        "create_account_btn": "অ্যাকাউন্ট তৈরি করুন",
        "back_to_login": "লগইনে ফিরে যান",
        "fill_fields": "সব ঘর পূরণ করুন।",
        "account_created": "অ্যাকাউন্ট তৈরি হয়েছে!",
        "username_exists": "ব্যবহারকারীর নাম ইতিমধ্যে আছে",
        "user_not_found": "ব্যবহারকারী পাওয়া যায়নি",
        "incorrect_password": "ভুল পাসওয়ার্ড",
        "dashboard_subtitle": "লাইভ রিমাইন্ডার ও ভয়েস অ্যালার্ট",
        "reminders_subtitle": "ওষুধের সময়সূচি ঠিক রাখুন এবং গুছিয়ে রাখুন",
        "ai_subtitle": "মেডিভয়েসকে যেকোনো কিছু জিজ্ঞেস করুন",
        "ai_greeting": "হ্যালো! আমি আপনার মেডিভয়েস সহকারী। কীভাবে সাহায্য করতে পারি?",
        "ai_listen_header": "🔊 উত্তরের অডিও শুনুন",
        "ai_play_en": "🎧 ইংরেজিতে শুনুন",
        "ai_play_bn": "🎧 বাংলায় শুনুন",
        "ai_thinking": "ভাবা চলছে...",
        "ai_you_label": "আপনি",
        "ai_bot_label": "এআই",
        "settings_title": "⚙ সেটিংস",
        "app_language_label": "অ্যাপের ভাষা",
        "voice_language_label": "ভয়েস অ্যালার্ট ভাষা",
        "language_english": "ইংরেজি",
        "language_bangla": "বাংলা",
        "intake_per_medicine": "প্রতিটি ওষুধের গ্রহণ অবস্থা",
        "compliance_30_day": "৩০ দিনের অনুগত্য",
        "missed_vs_taken": "মিসড বনাম গ্রহণ",
        "top_meds_label": "সবচেয়ে বেশি নেওয়া ওষুধ",
        "time_of_day_adherence": "দিনের কোন সময়ে গ্রহণ",
        "monthly_summary": "মাসিক পারফরম্যান্স সারাংশ",
        "no_data": "কোনো ডাটা পাওয়া যায়নি।",
        "analytics_empty": "অ্যানালিটিক্সের জন্য এখনো কোনো ডাটা নেই।",
        "monthly_empty": "এই মাসের জন্য রেকর্ড নেই।",
        "reminder_added": "রিমাইন্ডার যোগ হয়েছে!",
        "status_label": "অবস্থা",
        "pending": "অপেক্ষমাণ",
        "missed": "মিসড",
        "taken_vs_missed": "খাওয়া হয়েছে বনাম মিসড",
        "overall_compliance": "মোট অনুগত্য",
        "monthly_compliance": "মাসিক অনুগত্য",
        "generate_pdf_btn": "📄 মাসিক পিডিএফ তৈরি করুন",
        "pdf_success": "পিডিএফ সফলভাবে তৈরি হয়েছে!",
        "download_report": "📩 রিপোর্ট ডাউনলোড করুন",
        "pdf_title": "মেডিভয়েস - মাসিক রিপোর্ট",
        "pdf_user_line": "ব্যবহারকারী: {user}",
        "pdf_summary_line": "গত ৩০ দিনের সারাংশ",
        "pdf_total_line": "মোট রিমাইন্ডার: {count}",
        "pdf_taken_line": "খাওয়া হয়েছে: {count}",
        "pdf_missed_line": "মিসড: {count}",
        "pdf_compliance_line": "অনুগত্য: {percent}%",
        "pdf_top_meds": "শীর্ষ ওষুধ:",
        "pdf_med_entry": "{medicine}: {count} ডোজ",
        "preview": "প্রিভিউ",
        "manage_family": "পরিবারের সদস্যরা",
        "family_subtitle": "পরিজনের তথ্য ও স্বাস্থ্য চাহিদা ট্র্যাক করুন",
        "add_family_member": "পরিবারের সদস্য যোগ করুন",
        "member_name": "সদস্যের নাম",
        "relationship": "সম্পর্ক",
        "relationship_mother": "মা",
        "relationship_father": "বাবা",
        "relationship_wife": "স্ত্রী",
        "relationship_husband": "স্বামী",
        "relationship_son": "ছেলে",
        "relationship_daughter": "মেয়ে",
        "relationship_brother": "ভাই",
        "relationship_sister": "বোন",
        "relationship_grandfather": "দাদা / নানা",
        "relationship_grandmother": "দাদি / নানি",
        "relationship_other": "অন্যান্য",
        "age": "বয়স",
        "health_conditions": "স্বাস্থ্য তথ্য",
        "save_member": "সদস্য সংরক্ষণ করুন",
        "member_saved": "সদস্যের তথ্য সংরক্ষণ হয়েছে!",
        "member_name_required": "সদস্যের নাম লিখুন।",
        "family_email_instructions": "তাদের ইমেইল যোগ করুন যাতে তারা রিমাইন্ডার পেতে পারে।",
        "family_email_missing": "ইমেইল প্রদান করা হয়নি",
        "notify_family_label": "পরিবারের সদস্যদের জানান (ঐচ্ছিক)",
        "notify_family_help": "এই সময়ে যেসব আত্মীয়কে রিমাইন্ডার ইমেইল পাঠানো উচিত তাদের নির্বাচন করুন।",
        "no_family_emails": "নোটিফিকেশন পাঠাতে অন্তত একজন পরিবারের সদস্যের ইমেইল যোগ করুন।",
        "email_settings_missing": "ইমেইল সেটিংস কনফিগার করা হয়নি। SMTP_* পরিবেশ ভেরিয়েবল বা Streamlit সিক্রেটস সেট করুন।",
        "email_send_error": "ইমেইল নোটিফিকেশন পাঠানো যায়নি: {error}",
        "notification_sent": "রিমাইন্ডার ইমেইল পাঠানো হয়েছে: {recipients}",
        "notification_skipped": "কোনো ইমেইল প্রাপক কনফিগার করা হয়নি।",
        "notify_recipients_label": "ইমেইল সতর্কতা",
        "saved_family_members": "সংরক্ষিত পরিবার সদস্য",
        "no_family_members": "এখনও কোনো সদস্য যোগ করা হয়নি।",
        "delete_member": "মুছে ফেলুন",
        "health_none": "কোনো নোট নেই",
        "family_deleted": "সদস্য মুছে ফেলা হয়েছে।",
        "forgot_password": "পাসওয়ার্ড ভুলে গেছেন?",
        "recover_password": "পাসওয়ার্ড পুনরুদ্ধার",
        "recovery_subtitle": "পাসওয়ার্ড রিসেট করতে আপনার ইমেইল দিন",
        "send_recovery": "পুনরুদ্ধার লিঙ্ক পাঠান",
        "recovery_sent": "পাসওয়ার্ড পুনরুদ্ধার লিঙ্ক আপনার ইমেইলে পাঠানো হয়েছে!",
        "reset_password": "পাসওয়ার্ড রিসেট",
        "new_password": "নতুন পাসওয়ার্ড",
        "confirm_password": "পাসওয়ার্ড নিশ্চিত করুন",
        "password_mismatch": "পাসওয়ার্ড মেলে না",
        "password_reset_success": "পাসওয়ার্ড সফলভাবে রিসেট হয়েছে!",
        "theme_toggle": "থিম",
        "dark_theme": "ডার্ক থিম",
        "light_theme": "লাইট থিম"
    }
}


def T(k): return TEXT[st.session_state.ui_lang].get(k, k)


FAMILY_RELATIONSHIPS = [
    "mother",
    "father",
    "wife",
    "husband",
    "son",
    "daughter",
    "brother",
    "sister",
    "grandfather",
    "grandmother",
    "other",
]


def relationship_label(code: str) -> str:
    key = f"relationship_{code}"
    return TEXT[st.session_state.ui_lang].get(key, TEXT[st.session_state.ui_lang].get("relationship_other", code.title()))


def render_kpi_cards(cards):
    html = "<div class='kpi-row'>"
    for card in cards:
        delta = card.get("delta")
        delta_class = ""
        delta_html = ""
        if delta is not None:
            delta_class = "positive" if card.get("delta_positive", True) else "negative"
            delta_html = f"<div class='kpi-delta {delta_class}'>{delta}</div>"

        html += f"""
            <div class='kpi-card'>
                <small>{card['label']}</small>
                <div class='kpi-value'>{card['value']}</div>
                <div class='kpi-sub'>{card.get('subtext','')}</div>
                {delta_html}
            </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def build_radar_chart(labels, values):
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    values = values + values[:1]
    angles = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color="#5f54d7", linewidth=2)
    ax.fill(angles, values, color="#5f54d7", alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticklabels([])
    ax.spines["polar"].set_color("#dedff2")
    ax.grid(color="#dedff2", linestyle="--", linewidth=0.6)
    fig.tight_layout()
    return fig


def build_method_pie(method_counts):
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    colors = ["#5f54d7", "#c27ade", "#f6b2c0", "#f9d8a7"]
    ax.pie(
        method_counts.values,
        labels=method_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors[: len(method_counts)],
        wedgeprops={"edgecolor": "white", "linewidth": 1},
        textprops={"color": "#2b2c34"},
    )
    fig.tight_layout()
    return fig


def get_email_config():
    secrets_obj = getattr(st, "secrets", None)

    def fetch(key, default=None):
        env_val = os.getenv(key)
        if env_val:
            return env_val
        if secrets_obj is not None:
            try:
                return secrets_obj.get(key, default)
            except Exception:
                return default
        return default

    host = fetch("SMTP_HOST")
    port = fetch("SMTP_PORT", "587")
    user = fetch("SMTP_USER")
    password = fetch("SMTP_PASSWORD")
    sender = fetch("SMTP_SENDER", user)
    use_tls = fetch("SMTP_USE_TLS", "true")

    try:
        port = int(port)
    except (TypeError, ValueError):
        port = 587

    if isinstance(use_tls, str):
        use_tls = use_tls.lower() not in ("0", "false", "no")
    else:
        use_tls = bool(use_tls)

    if not all([host, port, user, password, sender]):
        return None

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "sender": sender,
        "use_tls": use_tls
    }


def record_notification(message, use_session=True):
    if use_session:
        st.session_state.setdefault("notification_log", [])
        st.session_state["notification_log"].append(message)
        st.session_state["notification_log"] = st.session_state["notification_log"][-20:]
    else:
        with NOTIFICATION_LOCK:
            NOTIFICATION_QUEUE.append(message)


def send_email_notification(recipients, subject, body, show_feedback=True):
    recipients = [r.strip() for r in recipients if r and r.strip()]
    if not recipients:
        if show_feedback:
            st.info(T("notification_skipped"))
        return False, []

    config = get_email_config()
    if not config:
        if show_feedback and not st.session_state.get("email_config_missing_warned"):
            st.warning(T("email_settings_missing"))
            st.session_state["email_config_missing_warned"] = True
        return False, []
    if show_feedback:
        st.session_state["email_config_missing_warned"] = False

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = config["sender"]
    msg["To"] = ", ".join(recipients)

    try:
        if config["use_tls"]:
            server = smtplib.SMTP(config["host"], config["port"])
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(config["host"], config["port"])
        server.login(config["user"], config["password"])
        server.sendmail(config["sender"], recipients, msg.as_string())
        server.quit()
        return True, recipients
    except Exception as e:
        if show_feedback:
            st.error(T("email_send_error").format(error=str(e)))
        else:
            log_message = f"Email send error: {e}"
            print(log_message)
            record_notification(log_message, use_session=False)
        return False, []


def resolve_notification_targets(row, family_lookup):
    notify_names = []
    notify_emails = []
    raw_notify = row.get("notify_member_ids")
    member_ids = []
    if raw_notify:
        try:
            parsed = json.loads(raw_notify)
            if isinstance(parsed, list):
                for item in parsed:
                    try:
                        member_ids.append(int(item))
                    except (TypeError, ValueError):
                        continue
        except (TypeError, ValueError):
            member_ids = []
    if not member_ids:
        return [], []

    for mid in member_ids:
        info = family_lookup.get(mid)
        if not info:
            continue
        if info.get("name"):
            notify_names.append(info["name"])
        if info.get("email"):
            notify_emails.append(info["email"])

    notify_names = list(dict.fromkeys(notify_names))
    notify_emails = list(dict.fromkeys(notify_emails))
    return notify_names, notify_emails


def parse_inventory_notify_config(raw_value):
    member_ids = []
    include_self = False
    if not raw_value:
        return member_ids, include_self
    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, dict):
            raw_members = parsed.get("members")
            if isinstance(raw_members, list):
                member_ids = raw_members
            include_self = bool(parsed.get("include_self"))
        elif isinstance(parsed, list):
            member_ids = parsed
    except (TypeError, ValueError):
        member_ids = []
        include_self = False
    cleaned_ids = []
    for mid in member_ids:
        try:
            cleaned_ids.append(int(mid))
        except (TypeError, ValueError):
            continue
    return cleaned_ids, include_self


def resolve_inventory_recipient_emails(row, user_email, family_lookup):
    member_ids, include_self = parse_inventory_notify_config(row.get("notify_member_ids"))
    recipients = []
    if include_self and user_email:
        recipients.append(user_email)
    for mid in member_ids:
        info = family_lookup.get(mid)
        if not info:
            continue
        email = info.get("email")
        if email:
            recipients.append(email)
    recipients = [r for r in dict.fromkeys(recipients) if r]
    return recipients


def get_user_email(conn, user_id):
    try:
        row = conn.execute("SELECT email FROM users WHERE username=?", (user_id,))
        record = row.fetchone()
    except sqlite3.Error:
        return None
    return record[0] if record and record[0] else None


def process_inventory_alerts(conn, user_id, user_email, family_lookup, show_feedback=False):
    if not user_id:
        return
    try:
        df = pd.read_sql_query(
            """
            SELECT
                id,
                medicine,
                stock,
                threshold,
                notes,
                notify_member_ids,
                COALESCE(out_notified, 0) AS out_notified
                    , COALESCE(low_stock_notified, 0) AS low_stock_notified
                FROM inventory
            WHERE user_id=?
            """,
            conn,
            params=(user_id,)
        )
    except Exception:
        return
    if df.empty:
        return
    # Out of stock alerts
    alerts_out = df[(df["stock"] <= 0) & (df["out_notified"] == 0)]
    for _, row in alerts_out.iterrows():
        recipients = resolve_inventory_recipient_emails(row, user_email, family_lookup)
        if not recipients:
            message = T("inventory_out_no_email")
            if show_feedback:
                st.warning(message)
            else:
                record_notification(message, use_session=False)
            continue
        subject = T("inventory_out_subject").format(medicine=row["medicine"])
        notes_text = row["notes"] or T("notes_none")
        body = T("inventory_out_body").format(medicine=row["medicine"], notes=notes_text)
        sent, sent_to = send_email_notification(recipients, subject, body, show_feedback=show_feedback)
        if sent:
            conn.execute("UPDATE inventory SET out_notified=1 WHERE id=?", (row["id"],))
            conn.commit()
            message = T("inventory_out_sent").format(medicine=row["medicine"], recipients=", ".join(sent_to))
            if show_feedback:
                st.info(message)
            else:
                record_notification(message, use_session=False)

    # Low stock alerts (stock < 4 and not already notified)
    alerts_low = df[(df["stock"] > 0) & (df["stock"] < 4) & (df["low_stock_notified"] == 0)]
    for _, row in alerts_low.iterrows():
        recipients = resolve_inventory_recipient_emails(row, user_email, family_lookup)
        if not recipients:
            message = T("inventory_out_no_email")
            if show_feedback:
                st.warning(message)
            else:
                record_notification(message, use_session=False)
            continue
        subject = T("inventory_low_subject").format(medicine=row["medicine"])
        notes_text = row["notes"] or T("notes_none")
        body = T("inventory_low_body").format(medicine=row["medicine"], notes=notes_text)
        sent, sent_to = send_email_notification(recipients, subject, body, show_feedback=show_feedback)
        if sent:
            conn.execute("UPDATE inventory SET low_stock_notified=1 WHERE id=?", (row["id"],))
            conn.commit()
            message = T("inventory_low_sent").format(medicine=row["medicine"], recipients=", ".join(sent_to))
            if show_feedback:
                st.info(message)
            else:
                record_notification(message, use_session=False)


def record_inventory_usage(conn, user_id, medicine_name, quantity=1, source="manual"):
    """Deduct stock for the given medicine and log the event."""
    if not (user_id and medicine_name):
        return False, None
    med_name = medicine_name.strip()
    if not med_name:
        return False, None
    try:
        qty = max(1, int(quantity))
    except (TypeError, ValueError):
        qty = 1
    cursor = conn.cursor()
    row = cursor.execute(
        """
        SELECT id, stock
        FROM inventory
        WHERE user_id=? AND LOWER(medicine)=LOWER(?)
        ORDER BY last_updated DESC, id DESC
        LIMIT 1
        """,
        (user_id, med_name)
    ).fetchone()
    if not row:
        return False, None
    inventory_id, stock = row
    current_stock = int(stock or 0)
    new_stock = current_stock - qty
    if new_stock < 0:
        new_stock = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "UPDATE inventory SET stock=?, last_updated=? WHERE id=?",
        (new_stock, now, inventory_id)
    )
    cursor.execute(
        """
        INSERT INTO inventory_usage(inventory_id, user_id, medicine, quantity, source)
        VALUES (?, ?, ?, ?, ?)
        """,
        (inventory_id, user_id, med_name, qty, source)
    )
    conn.commit()
    return True, new_stock


def snooze_reminder(conn, reminder_id, minutes=10):
    """Push a reminder forward and reset notification flags."""
    try:
        row = conn.execute(
            "SELECT date, reminder_time FROM medicine WHERE id=?",
            (reminder_id,)
        ).fetchone()
    except sqlite3.Error:
        return None
    if not row:
        return None
    raw_dt = f"{row[0]} {row[1]}"
    try:
        current_dt = datetime.strptime(raw_dt, "%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return None
    new_dt = current_dt + timedelta(minutes=max(1, int(minutes)))
    conn.execute(
        """
        UPDATE medicine
        SET date=?, reminder_time=?, voice_alerted=0, email_notified=0
        WHERE id=?
        """,
        (new_dt.strftime("%Y-%m-%d"), new_dt.strftime("%H:%M"), reminder_id)
    )
    conn.commit()
    return new_dt


def get_voice_alert_message(medicine, lang_code):
    lang_dict = TEXT.get(lang_code, TEXT["en"])
    template = lang_dict.get("voice_alert_msg", TEXT["en"]["voice_alert_msg"])
    return template.format(medicine=medicine)


def play_voice_alert(medicine, lang_code):
    speak(get_voice_alert_message(medicine, lang_code), lang_code)


def process_voice_alerts(conn, user_id, alert_lang):
    if not user_id:
        return
    today = datetime.now().date()
    today_str = today.strftime("%Y-%m-%d")
    try:
        df = pd.read_sql_query(
            """
            SELECT id, medicine, reminder_time, date, is_taken, voice_alerted
            FROM medicine
            WHERE user_id=? AND date=?
            ORDER BY reminder_time
            """,
            conn,
            params=(user_id, today_str)
        )
    except Exception:
        return
    if df.empty:
        return
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    due_df = df[df["date"].dt.date == today]
    if due_df.empty:
        return
    now = datetime.now()
    for _, row in due_df.iterrows():
        try:
            reminder_time = datetime.strptime(row["reminder_time"], "%H:%M").time()
        except (TypeError, ValueError):
            continue
        dt = datetime.combine(today, reminder_time)
        diff = (now - dt).total_seconds()
        if row.get("voice_alerted", 0) and diff < 0:
            conn.execute("UPDATE medicine SET voice_alerted=0 WHERE id=?", (row["id"],))
            conn.commit()
            continue
        if (
            -VOICE_ALERT_WINDOW_BEFORE <= diff <= VOICE_ALERT_WINDOW_AFTER
            and not row.get("is_taken")
            and not row.get("voice_alerted", 0)
        ):
            play_voice_alert(row["medicine"], alert_lang)
            conn.execute("UPDATE medicine SET voice_alerted=1 WHERE id=?", (row["id"],))
            conn.commit()


def process_due_notifications(conn, user_id, family_lookup, alert_lang="en", show_feedback=False):
    if not user_id:
        return
    # Get current time once at the start (needed for both medicine and appointments)
    now = datetime.now()
    
    reminders = pd.read_sql_query(
        """
        SELECT *
        FROM medicine
        WHERE user_id=? AND (email_notified=0 OR voice_alerted=0)
        """,
        conn,
        params=(user_id,)
    )
    if reminders.empty:
        # Continue to check appointments even if no medicine reminders
        pass
    else:
        tolerance = max(1, NOTIFICATION_POLL_SECONDS)
        for _, r in reminders.iterrows():
            try:
                reminder_dt = datetime.strptime(f"{r['date']} {r['reminder_time']}", "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            diff = (reminder_dt - now).total_seconds()
            # Fire reminder only when time has arrived or just passed (within 10 seconds after, not before)
            if not (-10 <= diff <= 0):
                continue
            
            # Send email if not already sent
            if not r.get("email_notified"):
                notify_names, notify_emails = resolve_notification_targets(r, family_lookup)
                if notify_emails:
                    notes_text = r["instructions"] or (T("notes_none") if show_feedback else "None")
                    subject = f"MediVoice reminder: {r['medicine']} at {r['reminder_time']}"
                    body = (
                        f"Hello,\n\n"
                        f"This is a reminder that {r['medicine']} is scheduled for {r['date']} at {r['reminder_time']}.\n"
                        f"Dosage: {r['dosage'] or '-'}\n"
                        f"{T('dose_quantity_label')}: {int(r.get('dose_quantity') or 1)}\n"
                        f"Instructions: {notes_text}\n\n"
                        "Please ensure the medicine is taken on time.\n\n"
                        "Sent by MediVoice."
                    )
                    sent, sent_to = send_email_notification(notify_emails, subject, body, show_feedback=show_feedback)
                    if sent:
                        conn.execute("UPDATE medicine SET email_notified=1 WHERE id=?", (r["id"],))
                        conn.commit()
                        if show_feedback:
                            st.info(T("notification_sent").format(recipients=", ".join(sent_to)))
                        else:
                            log_message = f"Sent {r['medicine']} reminder to {', '.join(sent_to)}"
                            print(log_message)
                            record_notification(log_message, use_session=False)
            
            # Play voice alert if not already played
            if not r.get("voice_alerted"):
                try:
                    play_voice_alert(r["medicine"], alert_lang)
                    conn.execute("UPDATE medicine SET voice_alerted=1 WHERE id=?", (r["id"],))
                    conn.commit()
                    log_message = f"Played voice alert for {r['medicine']} in {alert_lang}"
                    record_notification(log_message, use_session=False)
                except Exception as e:
                    print(f"Voice alert error for {r['medicine']}: {e}")

    # Check appointments and send reminders at the exact scheduled time
    appts = pd.read_sql_query(
        "SELECT * FROM appointments WHERE user_id=? AND (email_notified=0 OR voice_notified=0)",
        conn,
        params=(user_id,)
    )
    if not appts.empty:
        for _, a in appts.iterrows():
            try:
                ap_dt = datetime.strptime(f"{a['date']} {a['time']}", "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            diff = (ap_dt - now).total_seconds()
            # Fire only when appointment time has arrived (within 10 seconds after, not before)
            if -10 <= diff <= 0:
                # Send email if not already sent
                if not a.get("email_notified"):
                    user_email = get_user_email(conn, user_id)
                    recipients = resolve_inventory_recipient_emails(a, user_email, family_lookup)
                    # Fallback: if no recipients configured, send to user's own email
                    if not recipients and user_email:
                        recipients = [user_email]
                    if recipients:
                        subject = f"Upcoming appointment: {a['doctor_name']} on {a['date']} at {a['time']}"
                        body = f"Hi,\n\nYou have an upcoming appointment with {a['doctor_name']} at {a.get('hospital', '')} on {a['date']} at {a['time']}. Notes: {a.get('notes', '')}\n\n- MediVoice"
                        sent, sent_to = send_email_notification(recipients, subject, body, show_feedback=show_feedback)
                        if sent:
                            conn.execute("UPDATE appointments SET email_notified=1 WHERE id=?", (a["id"],))
                            conn.commit()
                            log_message = f"Sent appointment reminder for {a['doctor_name']} to {', '.join(sent_to)}"
                            record_notification(log_message, use_session=False)
                
                # Play voice alert if not already played
                if not a.get("voice_notified"):
                    try:
                        # Create language-appropriate message
                        if alert_lang == "bn":
                            msg = f"{a['doctor_name']} এর সাথে ডাক্তার অ্যাপয়েন্টমেন্ট {a['time']} এ।"
                        else:
                            msg = f"You have a doctor appointment with {a['doctor_name']} at {a['time']}"
                        speak(msg, alert_lang)
                        conn.execute("UPDATE appointments SET voice_notified=1 WHERE id=?", (a["id"],))
                        conn.commit()
                        log_message = f"Played voice alert for appointment with {a['doctor_name']} in {alert_lang}"
                        record_notification(log_message, use_session=False)
                    except Exception as e:
                        print(f"Voice alert error for appointment with {a['doctor_name']}: {e}")

def run_due_notifications(user_id, alert_lang, show_feedback=False):
    if not user_id:
        return
    conn = sqlite3.connect("medicine.db")
    try:
        family_df = pd.read_sql_query(
            """
            SELECT id, member_name, email
            FROM family_members
            WHERE user_id=?
            """,
            conn,
            params=(user_id,)
        )
        family_lookup = {
            row["id"]: {"name": row["member_name"], "email": row["email"]}
            for _, row in family_df.iterrows()
        }
        user_email = get_user_email(conn, user_id)
        process_due_notifications(conn, user_id, family_lookup, alert_lang, show_feedback=show_feedback)
        process_inventory_alerts(conn, user_id, user_email, family_lookup, show_feedback=show_feedback)
        process_voice_alerts(conn, user_id, alert_lang)
    finally:
        conn.close()


def ensure_notification_worker(user_id):
    if not user_id:
        return
    
    # Always restart worker to ensure it's running
    stop_event = st.session_state.get("notification_worker_stop")
    if stop_event:
        stop_event.set()

    stop_event = threading.Event()
    st.session_state["notification_worker_stop"] = stop_event
    voice_ref = st.session_state.setdefault("notification_voice_lang_ref", {"value": st.session_state.alert_lang})

    def worker():
        while not stop_event.is_set():
            try:
                current_lang = voice_ref.get("value") or "en"
                run_due_notifications(user_id, current_lang, show_feedback=False)
            except Exception as e:
                print(f"Notification worker error: {e}")
            stop_event.wait(NOTIFICATION_POLL_SECONDS)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    st.session_state["notification_worker"] = thread
    st.session_state["notification_worker_user"] = user_id
    print(f"Started notification worker for user: {user_id}")


# ============================================================
# DATABASE INIT
# ============================================================
def init_db():
    conn = sqlite3.connect("medicine.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT,
            salt TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS medicine(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            medicine TEXT,
            reminder_time TEXT,
            date TEXT,
            is_taken INTEGER DEFAULT 0,
            dosage TEXT,
            instructions TEXT,
            notify_member_ids TEXT,
            email_notified INTEGER DEFAULT 0,
            voice_alerted INTEGER DEFAULT 0,
            dose_quantity INTEGER DEFAULT 1
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            medicine TEXT,
            stock INTEGER,
            threshold INTEGER,
            notes TEXT,
            out_notified INTEGER DEFAULT 0,
            low_stock_notified INTEGER DEFAULT 0,
            last_updated TEXT,
            notify_member_ids TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory_usage(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventory_id INTEGER,
            user_id TEXT NOT NULL,
            medicine TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (inventory_id) REFERENCES inventory(id)
        )
    """)
    try:
        columns = {
            row[1]
            for row in c.execute("PRAGMA table_info(inventory)")
        }
    except sqlite3.OperationalError:
        columns = set()
    if "notes" not in columns:
        c.execute("ALTER TABLE inventory ADD COLUMN notes TEXT")
    if "out_notified" not in columns:
        c.execute("ALTER TABLE inventory ADD COLUMN out_notified INTEGER DEFAULT 0")
    if "notify_member_ids" not in columns:
        c.execute("ALTER TABLE inventory ADD COLUMN notify_member_ids TEXT")
    if "low_stock_notified" not in columns:
        c.execute("ALTER TABLE inventory ADD COLUMN low_stock_notified INTEGER DEFAULT 0")

    c.execute("""
        CREATE TABLE IF NOT EXISTS appointments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            doctor_name TEXT,
            hospital TEXT,
            date TEXT,
            time TEXT,
            notes TEXT,
            notify_member_ids TEXT,
            email_notified INTEGER DEFAULT 0,
            voice_notified INTEGER DEFAULT 0
        )
    """)
    try:
        ap_columns = {row[1] for row in c.execute("PRAGMA table_info(appointments)")}
    except sqlite3.OperationalError:
        ap_columns = set()
    if "email_notified" not in ap_columns:
        c.execute("ALTER TABLE appointments ADD COLUMN email_notified INTEGER DEFAULT 0")
    if "voice_notified" not in ap_columns:
        c.execute("ALTER TABLE appointments ADD COLUMN voice_notified INTEGER DEFAULT 0")
    if "notify_member_ids" not in ap_columns:
        c.execute("ALTER TABLE appointments ADD COLUMN notify_member_ids TEXT")

    c.execute("""
        CREATE TABLE IF NOT EXISTS family_members(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            member_name TEXT NOT NULL,
            relationship TEXT NOT NULL,
            age INTEGER,
            health_conditions TEXT,
            email TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sleep_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            log_date TEXT NOT NULL,
            hours REAL,
            quality INTEGER,
            mood INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ensure backward compatibility with older databases
    med_cols = [col[1] for col in c.execute("PRAGMA table_info(medicine)").fetchall()]
    if "notify_member_ids" not in med_cols:
        c.execute("ALTER TABLE medicine ADD COLUMN notify_member_ids TEXT")
    if "email_notified" not in med_cols:
        c.execute("ALTER TABLE medicine ADD COLUMN email_notified INTEGER DEFAULT 0")
    if "voice_alerted" not in med_cols:
        c.execute("ALTER TABLE medicine ADD COLUMN voice_alerted INTEGER DEFAULT 0")
    if "dose_quantity" not in med_cols:
        c.execute("ALTER TABLE medicine ADD COLUMN dose_quantity INTEGER DEFAULT 1")

    fam_cols = [col[1] for col in c.execute("PRAGMA table_info(family_members)").fetchall()]
    if "email" not in fam_cols:
        c.execute("ALTER TABLE family_members ADD COLUMN email TEXT")

    conn.commit()
    conn.close()

init_db()


# ============================================================
# PASSWORD HASH
# ============================================================
def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt


# ============================================================
# PASSWORD RECOVERY PAGE
# ============================================================
def password_recovery_page():
    st.markdown(
        """
        <div class="mobile-shell">
        <div class="mobile-card login-card">
            <div class="accent-pill">🔑</div>
            <h1>Password Recovery</h1>
            <p>Enter your email to reset your password.</p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("recovery_form"):
        email = st.text_input(T("email"), placeholder="your@email.com")
        submit = st.form_submit_button(T("send_recovery"))

    if submit:
        if not email:
            st.error("Please enter your email address.")
            return
        
        conn = sqlite3.connect("medicine.db")
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE email=?", (email,))
        row = c.fetchone()
        conn.close()

        if row:
            # In a real app, you would send an email with a reset link
            # For this demo, we'll just show a success message
            st.success(T("recovery_sent"))
            st.info("In a real application, a password reset link would be sent to your email.")
        else:
            st.error("No account found with that email address.")

    st.markdown(
        """
            <div style="text-align:center;margin-top:1rem;color:var(--text-muted);">
                <small>Remember your password?</small>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(T("back_to_login")):
        st.session_state.page = "login"
        st.rerun()


# ============================================================
# RESET PASSWORD PAGE
# ============================================================
def reset_password_page():
    st.markdown(
        """
        <div class="mobile-shell">
        <div class="mobile-card login-card">
            <div class="accent-pill">🔄</div>
            <h1>Reset Password</h1>
            <p>Enter your new password.</p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("reset_form"):
        new_password = st.text_input(T("new_password"), type="password", placeholder="New password")
        confirm_password = st.text_input(T("confirm_password"), type="password", placeholder="Confirm password")
        submit = st.form_submit_button(T("reset_password"))

    if submit:
        if not new_password or not confirm_password:
            st.error("Please fill all fields.")
            return
        
        if new_password != confirm_password:
            st.error(T("password_mismatch"))
            return

        # In a real app, you would verify the reset token and update the password
        # For this demo, we'll just show a success message
        st.success(T("password_reset_success"))
        st.session_state.page = "login"
        st.rerun()

    st.markdown(
        """
            <div style="text-align:center;margin-top:1rem;color:var(--text-muted);">
                <small>Back to login?</small>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(T("back_to_login")):
        st.session_state.page = "login"
        st.rerun()


# ============================================================
# LOGIN PAGE
# ============================================================
def login_page():
    st.markdown(
        """
        <div class="mobile-shell">
        <div class="mobile-card login-card">
            <div class="accent-pill">💊</div>
            <h1> MediVoice</h1>
            <p>Plan doses, watch reminders, and share updates with family.</p>
            <div style="margin:0.6rem auto 0.9rem auto;width:90px;height:90px;border-radius:24px;background:rgba(255,255,255,0.75);display:flex;align-items:center;justify-content:center;box-shadow:0 12px 24px rgba(255,74,145,0.2);">
                <img src="https://cdn-icons-png.flaticon.com/512/2966/2966489.png"
                     style="width:60px;height:60px;" alt="App icon">
            </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        user = st.text_input(T("username"), placeholder="     ")
        pw = st.text_input(T("password"), type="password", placeholder="*********")
        submit = st.form_submit_button(T("login"))

    if submit:
        conn = sqlite3.connect("medicine.db")
        c = conn.cursor()
        c.execute("SELECT password, salt FROM users WHERE username=?", (user,))
        row = c.fetchone()
        conn.close()

        if not row:
            st.error(T("user_not_found"))
            return

        stored, salt = row
        entered, _ = hash_password(pw, salt)

        if stored == entered:
            st.session_state.logged = True
            st.session_state.user = user
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error(T("incorrect_password"))

    st.markdown(
        """
            <div style="text-align:center;margin-top:1rem;color:var(--text-muted);">
                <small>Don't have an account?</small>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button(T("signup")):
            st.session_state.page = "signup"
            st.rerun()
    with col2:
        if st.button(T("forgot_password")):
            st.session_state.page = "recovery"
            st.rerun()


# ============================================================
# SIGNUP PAGE
# ============================================================
def signup_page():
    st.markdown(
        """
        <div class="mobile-shell">
        <div class="mobile-card login-card">
            <div class="accent-pill">?</div>
            <h1>Create your account</h1>
            <p>Invite family members and coordinate reminders together.</p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("signup_form"):
        user = st.text_input(T("username"), placeholder="nabila")
        email = st.text_input(T("email"), placeholder="nabila@example.com")
        pw = st.text_input(T("password"), type="password", placeholder="Choose a strong password")
        submit = st.form_submit_button(T("create_account_btn"))

    if submit:
        if not user or not email or not pw:
            st.error(T("fill_fields"))
            return
        h, s = hash_password(pw)
        conn = sqlite3.connect("medicine.db")
        try:
            conn.execute("INSERT INTO users(username,email,password,salt) VALUES(?,?,?,?)",
                         (user, email, h, s))
            conn.commit()
            st.success(T("account_created"))
            st.session_state.page = "login"
            st.rerun()
        except:
            st.error(T("username_exists"))
        finally:
            conn.close()

    st.markdown(
        """
            <div style="text-align:center;margin-top:1rem;color:var(--text-muted);">
                <small>Already have an account?</small>
            </div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(T("back_to_login")):
        st.session_state.page = "login"
        st.rerun()


# ============================================================
# SIDEBAR CONTROLS
# ============================================================
def sidebar_controls():
    render_pill(T("settings_title"), target=st.sidebar)

    # Theme Toggle
    theme_options = [T("light_theme"), T("dark_theme")]
    current_theme = T("dark_theme") if st.session_state.dark_theme else T("light_theme")
    theme_choice = st.sidebar.selectbox(
        f"🎨 {T('theme_toggle')}",
        options=theme_options,
        index=theme_options.index(current_theme),
        key="theme_selector"
    )
    
    # Update theme based on selection
    new_dark_theme = (theme_choice == T("dark_theme"))
    if new_dark_theme != st.session_state.dark_theme:
        st.session_state.dark_theme = new_dark_theme
        st.rerun()

    lang_options = ["en", "bn"]
    lang = st.sidebar.selectbox(
        f"🌍 {T('app_language_label')}",
        options=lang_options,
        index=lang_options.index(st.session_state.ui_lang),
        format_func=lambda code: T("language_english") if code == "en" else T("language_bangla")
    )
    st.session_state.ui_lang = lang

    voice_choice = st.sidebar.selectbox(
        f"\U0001f50a {T('voice_language_label')}",
        options=lang_options,
        index=lang_options.index(st.session_state.alert_lang),
        format_func=lambda code: T("language_english") if code == "en" else T("language_bangla")
    )
    st.session_state.alert_lang = voice_choice
    voice_ref = st.session_state.setdefault("notification_voice_lang_ref", {"value": voice_choice})
    voice_ref["value"] = voice_choice

    snooze_val = st.sidebar.slider(
        f"⏱ {T('snooze_length_label')}",
        min_value=5,
        max_value=30,
        step=5,
        value=int(st.session_state.get("snooze_minutes", 10))
    )
    st.session_state.snooze_minutes = snooze_val
    st.sidebar.caption(T("snooze_length_help"))

    st.sidebar.markdown("---")
    st.sidebar.markdown("---")
    if st.sidebar.button(T("logout")):
        stop_event = st.session_state.get("notification_worker_stop")
        if stop_event:
            stop_event.set()
        st.session_state.pop("notification_worker_stop", None)
        st.session_state.pop("notification_worker", None)
        st.session_state.pop("notification_worker_user", None)
        st.session_state.logged = False
        st.session_state.page = "login"
        st.rerun()


# ============================================================
# DASHBOARD (Voice Alerts)
# ============================================================
def dashboard_page(conn):
    render_section_header("🏠", T("dashboard"), T("dashboard_subtitle"))

    user = st.session_state.user
    today_date = datetime.now().date()
    today_str = today_date.strftime("%Y-%m-%d")
    now = datetime.now()

    range_start = today_date - timedelta(days=DASHBOARD_HISTORY_DAYS)
    range_end = today_date + timedelta(days=DASHBOARD_FUTURE_DAYS)
    df = pd.read_sql_query(
        """
        SELECT *
        FROM medicine
        WHERE user_id=?
          AND date BETWEEN ? AND ?
        ORDER BY date, reminder_time
        """,
        conn,
        params=(user, range_start.strftime("%Y-%m-%d"), range_end.strftime("%Y-%m-%d"))
    )
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    family_df = pd.read_sql_query(
        """
        SELECT id, member_name, email
        FROM family_members
        WHERE user_id=?
        """,
        conn,
        params=(user,)
    )
    family_lookup = {
        row["id"]: {"name": row["member_name"], "email": row["email"]}
        for _, row in family_df.iterrows()
    }
    user_email = get_user_email(conn, user)
    process_due_notifications(conn, user, family_lookup, show_feedback=True)
    process_inventory_alerts(conn, user, user_email, family_lookup, show_feedback=True)

    render_week_tracker(conn, user, today_date)
    st.session_state.setdefault("notification_log", [])
    with NOTIFICATION_LOCK:
        while NOTIFICATION_QUEUE:
            st.session_state["notification_log"].append(NOTIFICATION_QUEUE.popleft())
        st.session_state["notification_log"] = st.session_state["notification_log"][-20:]
    if st.session_state["notification_log"]:
        st.info("Notifications: " + " | ".join(st.session_state["notification_log"][-3:]))

    # Show upcoming doctor appointments
    appts_df = pd.read_sql_query(
        """
        SELECT *
        FROM appointments
        WHERE user_id=? AND date >= ?
        ORDER BY date, time
        """,
        conn,
        params=(user, today_str)
    )
    if not appts_df.empty:
        st.markdown("### 🩺 " + T("doctor_appointments"))
        for _, appt in appts_df.iterrows():
            st.markdown(
                f"""
                <div class='blue-box'>
                    <b>{appt['doctor_name']}</b><br>
                    📍 {appt['hospital']}<br>
                    📅 {appt['date']} — ⏰ {appt['time']}<br>
                    <b>Notes:</b> {appt['notes'] or T('notes_none')}
                </div>
                """,
                unsafe_allow_html=True
            )

    if df.empty:
        st.info(T("no_today"))
        return

    upcoming_df = df[df["date"].dt.date >= today_date]
    history_df = df[df["date"].dt.date < today_date]

    if upcoming_df.empty:
        st.info(T("no_today"))
    else:
        for day in sorted(upcoming_df["date"].dt.date.unique()):
            day_df = upcoming_df[upcoming_df["date"].dt.date == day]
            weekday_label, date_label = localized_day_parts(day)
            label = (
                T("day_label_today").format(date=date_label)
                if day == today_date
                else T("day_label_other").format(
                    weekday=weekday_label,
                    date=date_label
                )
            )
            render_pill(label)
            tile_cols = None
            for idx, (_, row) in enumerate(day_df.iterrows()):
                if idx % REMINDER_TILE_COLUMNS == 0:
                    tile_cols = st.columns(REMINDER_TILE_COLUMNS)
                with tile_cols[idx % REMINDER_TILE_COLUMNS]:
                    render_reminder_card(
                        row,
                        day,
                        now,
                        conn,
                        user,
                        user_email,
                        family_lookup,
                        allow_actions=True
                    )

    history_dates = sorted(history_df["date"].dt.date.unique(), reverse=True)
    with st.expander(T("history_section"), expanded=False):
        if not history_dates:
            st.info(T("history_empty"))
        else:
            st.caption(T("history_note"))
            for day in history_dates:
                day_df = history_df[history_df["date"].dt.date == day]
                weekday_label, date_label = localized_day_parts(day)
                label = T("day_label_other").format(
                    weekday=weekday_label,
                    date=date_label
                )
                render_pill(label)
                tile_cols = None
                for idx, (_, row) in enumerate(day_df.iterrows()):
                    if idx % REMINDER_TILE_COLUMNS == 0:
                        tile_cols = st.columns(REMINDER_TILE_COLUMNS)
                    with tile_cols[idx % REMINDER_TILE_COLUMNS]:
                        render_reminder_card(
                            row,
                            day,
                            now,
                            conn,
                            user,
                            user_email,
                            family_lookup,
                            allow_actions=False
                        )


# ============================================================
# ADD REMINDER
# ============================================================
def reminders_page(conn):
    render_section_header("⏰", T("add_rem"), T("reminders_subtitle"))

    user = st.session_state.user
    notify_df = pd.read_sql_query(
        """
        SELECT id, member_name, email
        FROM family_members
        WHERE user_id=? AND email IS NOT NULL AND TRIM(email) != ''
        ORDER BY member_name
        """,
        conn,
        params=(user,)
    )
    notify_options = notify_df["id"].tolist()
    option_labels = {
        row["id"]: f"{row['member_name']} ({row['email']})"
        for _, row in notify_df.iterrows()
    }
    family_lookup = {
        row["id"]: {"name": row["member_name"], "email": row["email"]}
        for _, row in notify_df.iterrows()
    }
    user_email = get_user_email(conn, user)

    c1, c2 = st.columns(2)

    with c1:
        med = st.text_input(T("med_name"), key="reminder_med_field")
        dos = st.text_input(T("dos"), key="reminder_dos_field")
        dose_qty = st.number_input(
            T("dose_quantity_label"),
            min_value=1,
            value=1,
            step=1,
            help=T("dose_quantity_help"),
            key="reminder_dose_qty_field"
        )
        freq = ""
        inst = st.text_input(T("inst"), key="reminder_inst_field")

    with c2:
        date = st.date_input(T("date"), key="reminder_date_field")
        time = st.text_input(
            T("time"),
            value=datetime.now().strftime("%H:%M"),
            key="reminder_time_field"
        )
        if notify_options:
            notify_selection = st.multiselect(
                T("notify_family_label"),
                notify_options,
                default=[],
                format_func=lambda mid: option_labels.get(mid, str(mid)),
                key="notify_family_select",
                help=T("notify_family_help")
            )
        else:
            st.info(T("no_family_emails"))
            notify_selection = []

    if st.button(T("save")):
        try:
            datetime.strptime(time, "%H:%M")
        except:
            st.error(T("invalid_time")); return

        conn.execute("""
            INSERT INTO medicine(
                user_id,
                medicine,
                reminder_time,
                date,
                dosage,
                frequency,
                instructions,
                notify_member_ids,
                dose_quantity
            )
            VALUES(?,?,?,?,?,?,?,?,?)
        """, (
            user,
            med,
            time,
            date.strftime("%Y-%m-%d"),
            dos,
            freq,
            inst,
            json.dumps(notify_selection) if notify_selection else None,
            int(dose_qty)
        ))
        conn.commit()
        st.success(T("reminder_added"))
        st.rerun()


# ============================================================
# WEEKLY SUMMARY
# ============================================================
def weekly_summary(conn):
    render_section_header("📆", T("weekly_title"), T("weekly_subtitle"))

    user = st.session_state.user
    today = datetime.now().date()
    start = today - timedelta(days=6)

    df = pd.read_sql_query(
        f"SELECT * FROM medicine WHERE user_id='{user}' AND date BETWEEN '{start}' AND '{today}'",
        conn
    )

    if df.empty:
        st.info(T("no_data"))
        return

    df["date"] = pd.to_datetime(df["date"])

    def render_med_item(name, is_taken):
        status_label = T("taken") if is_taken else T("missed")
        status_class = "ok" if is_taken else "miss"
        return (
            f"<li><span>{name}</span>"
            f"<span class='status {status_class}'>{status_label}</span></li>"
        )

    cards = []
    max_meds = 3
    for day in sorted(df["date"].unique()):
        day_df = df[df["date"] == day]
        taken = int(day_df["is_taken"].sum())
        total = len(day_df)
        missed = max(0, total - taken)
        completion = int(round((taken / total) * 100)) if total else 0

        if day_df.empty:
            meds_html = f"<li class='empty'>{T('weekly_card_empty')}</li>"
            extra_html = ""
        else:
            visible_rows = day_df.head(max_meds)
            meds_html = "".join(
                render_med_item(row["medicine"], row["is_taken"])
                for _, row in visible_rows.iterrows()
            )
            remaining = max(0, len(day_df) - max_meds)
            extra_html = ""
            if remaining > 0:
                extra_rows = day_df.iloc[max_meds:]
                extra_items = "".join(
                    render_med_item(row["medicine"], row["is_taken"])
                    for _, row in extra_rows.iterrows()
                )
                extra_html = (
                    "<details class='weekly-card__more'>"
                    f"<summary>{T('weekly_card_more').format(count=localized_number(remaining))}</summary>"
                    f"<ul>{extra_items}</ul>"
                    "</details>"
                )

        badge_text = T("weekly_card_badge").format(
            taken=localized_number(taken),
            total=localized_number(total)
        )
        weekday_label, date_label = localized_day_parts(day)
        cards.append(
            "<div class='weekly-card'>"
            "<div class='weekly-card__top'>"
            "<div>"
            f"<div class='weekly-card__day'>{weekday_label}</div>"
            f"<div class='weekly-card__date'>{date_label}</div>"
            "</div>"
            f"<div class='weekly-card__badge'>{badge_text}</div>"
            "</div>"
            "<div class='weekly-card__stats'>"
            "<div class='weekly-card__stat'>"
            f"<div class='label'>{T('weekly_card_taken_label')}</div>"
            f"<div class='value'>{localized_number(taken)}</div>"
            "</div>"
            "<div class='weekly-card__stat'>"
            f"<div class='label'>{T('weekly_card_missed_label')}</div>"
            f"<div class='value'>{localized_number(missed)}</div>"
            "</div>"
            "</div>"
            "<div>"
            "<div class='weekly-card__progress'>"
            f"<div class='fill' style='width:{completion}%;'></div>"
            "</div>"
            f"<div class='weekly-card__progress-label'>"
            f"{localized_number(completion)}% {T('weekly_card_completion_label')}"
            "</div>"
            "</div>"
            f"<div class='weekly-card__meds-title'>{T('weekly_card_meds_label')}</div>"
            f"<ul class='weekly-card__meds'>{meds_html}</ul>"
            f"{extra_html}"
            "</div>"
        )

    if cards:
        st.markdown(f"<div class='weekly-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)

    stats = (
        df.groupby("medicine")["is_taken"]
        .sum()
        .reset_index()
    )
    stats.columns = [T("med_name"), T("taken")]
    if not stats.empty:
        chart = (
            alt.Chart(stats)
            .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
            .encode(
                x=alt.X(f"{T('med_name')}:N", sort='-y', title=T("med_name")),
                y=alt.Y(f"{T('taken')}:Q", title=T("taken")),
                color=alt.value("#ff6fa0")
            )
            .properties(width=320, height=200)
        )
        with st.container():
            st.markdown(
                (
                    "<div class='weekly-chart-card'>"
                    f"<div class='weekly-chart-card__title'>\U0001f4ca {T('intake_per_medicine')}</div>"
                ),
                unsafe_allow_html=True
            )
            st.altair_chart(chart, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

def analytics_page(conn):
    render_section_header("📊", T("analytics_title"), T("analytics_subtitle"))
    configure_chart_fonts()

    user = st.session_state.user

    df = pd.read_sql_query(
        f"SELECT * FROM medicine WHERE user_id='{user}'",
        conn
    )

    if df.empty:
        st.info(T("analytics_empty"))
        return

    df["date"] = pd.to_datetime(df["date"])
    df["hour"] = pd.to_datetime(df["reminder_time"], format="%H:%M").dt.hour

    # -------------------------------------------------------
    render_pill(f"📈 {T('compliance_30_day')}")
    # -------------------------------------------------------
    render_pill(f"📈 {T('compliance_30_day')}")

    last_30 = df[df["date"] >= (datetime.now() - timedelta(days=30))]
    total = len(last_30)
    taken = last_30["is_taken"].sum()

    compliance = int((taken / total) * 100) if total > 0 else 0

    st.metric(T("overall_compliance"), f"{compliance}%")

    # -------------------------------------------------------
    render_pill(f"⚖ {T('missed_vs_taken')}")
    # -------------------------------------------------------
    render_pill(f"⚖ {T('missed_vs_taken')}")

    taken_cnt = taken
    missed_cnt = total - taken_cnt

    chart_cols = st.columns(2)
    with chart_cols[0]:
        render_pill(f"🎯 {T('taken_vs_missed')}")
        fig, ax = plt.subplots(figsize=(2.4, 2.4))
        ax.pie(
            [taken_cnt, missed_cnt],
            labels=[T("taken"), T("missed")],
            autopct="%1.1f%%",
            colors=["#ff7aa2", "#ffd1e3"]
        )
        ax.set_title("")
        st.pyplot(fig)

    with chart_cols[1]:
        render_pill(f"⭐ {T('top_meds_label')}")
        med_rank = (
            last_30.groupby("medicine")["is_taken"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )

        med_rank_df = med_rank.reset_index()
        med_rank_df.columns = [T("med_name"), T("taken")]
        if not med_rank_df.empty:
            rank_chart = (
                alt.Chart(med_rank_df)
                .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
                .encode(
                    x=alt.X(f"{T('med_name')}:N", sort='-y', title=T("med_name")),
                    y=alt.Y(f"{T('taken')}:Q", title=T("taken")),
                    color=alt.value("#ffc2d9")
                )
                .properties(width=300, height=300)
            )
            st.altair_chart(rank_chart, use_container_width=False)

    # -------------------------------------------------------
    render_pill(f"\U0001F552 {T('time_of_day_adherence')}")  # clock emoji

    def _bucketize(hour: int) -> str:
        if 5 <= hour < 11:
            return "Morning (5am-11am)"
        if 11 <= hour < 17:
            return "Afternoon (11am-5pm)"
        if 17 <= hour < 22:
            return "Evening (5pm-10pm)"
        return "Night (10pm-5am)"

    df['time_bucket'] = df['hour'].apply(_bucketize)
    bucket_order = [
        "Morning (5am-11am)",
        "Afternoon (11am-5pm)",
        "Evening (5pm-10pm)",
        "Night (10pm-5am)",
    ]

    bucket_stats = (
        df.groupby('time_bucket')['is_taken']
        .mean()
        .mul(100)
        .reindex(bucket_order)
        .fillna(0)
    )

    bucket_df = bucket_stats.reset_index()
    bucket_df.columns = ['Period', 'OnTime']

    bucket_chart = (
        alt.Chart(bucket_df)
        .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
        .encode(
            x=alt.X('Period:N', sort=bucket_order, title='Day part'),
            y=alt.Y('OnTime:Q', title='Taken on time (%)'),
            color=alt.value('#ff9cc5')
        )
        .properties(width=320, height=250)
    )
    st.altair_chart(bucket_chart, use_container_width=False)

    emoji_map = {
        "Morning (5am-11am)": "\U0001F305",    # sunrise
        "Afternoon (11am-5pm)": "\U0001F31E",  # sun with face
        "Evening (5pm-10pm)": "\U0001F307",    # sunset
        "Night (10pm-5am)": "\U0001F303",      # night with stars
    }
    for period, value in bucket_stats.items():
        icon = emoji_map.get(period, "\U0001F552")
        st.write(f"{icon} {period}: {value:.0f}% of reminders taken on time.")

# ============================================================
# UPDATED MONTHLY REPORT (MULTI-COLOR + PDF)
# ============================================================
def monthly_report_page(conn):
    render_section_header("📄", T("monthly_title"), T("monthly_subtitle"))

    user = st.session_state.user

    df = pd.read_sql_query(
        """
        SELECT * FROM medicine
        WHERE user_id=?
        AND date >= date('now','-30 day')
        ORDER BY date ASC
        """,
        conn,
        params=(user,),
    )

    if df.empty:
        st.info(T("monthly_empty"))
        return

    df["date"] = pd.to_datetime(df["date"])
    month_label = df["date"].dt.strftime("%B %Y").iloc[-1]

    render_pill(f"📌 {month_label}")

    total = len(df)
    taken = df["is_taken"].sum()
    compliance = int((taken / total) * 100)

    st.metric(T("monthly_compliance"), f"{compliance}%")

    top_col, least_col = st.columns(2)

    with top_col:
        render_pill(f"🌟 {T('top_meds_label')}")
        top_meds = (
            df.groupby("medicine")["is_taken"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        top_df = top_meds.reset_index()
        top_df.columns = [T("med_name"), T("taken")]
        if not top_df.empty:
            chart = (
                alt.Chart(top_df)
                .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
                .encode(
                    x=alt.X(f"{T('med_name')}:N", sort='-y', title=T("med_name")),
                    y=alt.Y(f"{T('taken')}:Q", title=T("taken")),
                    color=alt.value("#ff7aa2")
                )
                .properties(width=260, height=200)
            )
            st.altair_chart(chart, use_container_width=False)

    with least_col:
        render_pill("🧊 Least Taken")
        least_meds = (
            df.groupby("medicine")["is_taken"]
            .sum()
            .sort_values(ascending=True)
            .head(5)
        )
        least_df = least_meds.reset_index()
        least_df.columns = [T("med_name"), T("taken")]
        if not least_df.empty:
            least_chart = (
                alt.Chart(least_df)
                .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
                .encode(
                    x=alt.X(f"{T('med_name')}:N", sort='-y', title=T("med_name")),
                    y=alt.Y(f"{T('taken')}:Q", title=T("taken")),
                    color=alt.value("#ffcce0")
                )
                .properties(width=260, height=200)
            )
            st.altair_chart(least_chart, use_container_width=False)
    # ---------------------------------------------------
    # PDF Generation Button
    # ---------------------------------------------------
    if st.button(T("generate_pdf_btn")):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt=T("pdf_title"), ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=T("pdf_user_line").format(user=user), ln=True)
        pdf.cell(200, 10, txt=T("pdf_summary_line"), ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", size=11)
        pdf.cell(200, 8, txt=T("pdf_total_line").format(count=total), ln=True)
        pdf.cell(200, 8, txt=T("pdf_taken_line").format(count=taken), ln=True)
        pdf.cell(200, 8, txt=T("pdf_missed_line").format(count=total - taken), ln=True)
        pdf.cell(200, 8, txt=T("pdf_compliance_line").format(percent=compliance), ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=T("pdf_top_meds"), ln=True)

        for med, count in top_meds.items():
            pdf.set_font("Arial", size=11)
            pdf.cell(200, 8, txt=T("pdf_med_entry").format(medicine=med, count=count), ln=True)

        # Save temp
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp.name)

        st.success(T("pdf_success"))

        with open(tmp.name, "rb") as f:
            st.download_button(
                label=T("download_report"),
                data=f.read(),
                file_name=f"{user}_MonthlyReport.pdf",
                mime="application/pdf"
            )




# ============================================================
# INVENTORY PAGE
# ============================================================
# ============================================================
# FIXED — INVENTORY PAGE (No duplicate keys)
# ============================================================

def inventory_page(conn):
    render_section_header("📦", T("inventory_tool"), T("inventory_subtitle"))

    user = st.session_state.user
    c = conn.cursor()
    user_email = get_user_email(conn, user)

    family_df = pd.read_sql_query(
        """
        SELECT id, member_name, email
        FROM family_members
        WHERE user_id=?
        ORDER BY member_name
        """,
        conn,
        params=(user,)
    )
    family_lookup = {
        int(row["id"]): {"name": row["member_name"], "email": row["email"]}
        for _, row in family_df.iterrows()
    }
    email_ready_df = family_df[
        family_df["email"].notna() & (family_df["email"].str.strip() != "")
    ]
    notify_options = [int(x) for x in email_ready_df["id"].tolist()]
    notify_labels = {
        int(row["id"]): f"{row['member_name']} ({row['email']})"
        for _, row in email_ready_df.iterrows()
    }

    df = pd.read_sql_query(
        f"SELECT * FROM inventory WHERE user_id='{user}'",
        conn
    )
    try:
        usage_df = pd.read_sql_query(
            """
            SELECT inventory_id, SUM(quantity) AS total_taken, MAX(created_at) AS last_taken
            FROM inventory_usage
            WHERE user_id=?
            GROUP BY inventory_id
            """,
            conn,
            params=(user,)
        )
    except Exception:
        usage_df = pd.DataFrame(columns=["inventory_id", "total_taken", "last_taken"])
    usage_lookup = {}
    if not usage_df.empty:
        usage_df["total_taken"] = usage_df["total_taken"].fillna(0).astype(int)
        usage_lookup = {
            row["inventory_id"]: {
                "total": row["total_taken"],
                "last": row["last_taken"]
            }
            for _, row in usage_df.iterrows()
        }
    zero_df = df[df["stock"] <= 0]
    if not zero_df.empty:
        names = ", ".join(zero_df["medicine"].tolist())
        st.warning(T("inventory_out_warning").format(medicine=names))

    tab_manage, tab_log = st.tabs([T("inventory_manage_tab"), T("inventory_log_tab")])

    with tab_manage:
        col1, col2 = st.columns(2)

        with col1:
            med = st.text_input(T("med_name"), key="inv_name_input")
            stock = st.number_input(T("inventory_stock"), min_value=0, key="inv_stock_input")
            thresh = st.number_input(T("inventory_threshold"), min_value=1, key="inv_thresh_input")

        with col2:
            notes = st.text_area(T("notes_label"), key="inv_notes_input")
            if notify_options:
                notify_selection = st.multiselect(
                    T("inventory_notify_label"),
                    notify_options,
                    default=[],
                    format_func=lambda mid: notify_labels.get(mid, str(mid)),
                    help=T("inventory_notify_help"),
                    key="inv_notify_select"
                )
            else:
                notify_selection = []
                st.info(T("no_family_emails"))
            include_self = st.checkbox(
                T("inventory_notify_self"),
                value=bool(user_email),
                key="inv_notify_self"
            )

        if st.button(T("save"), key="inv_save_btn"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            notify_payload = None
            if notify_selection or include_self:
                notify_payload = json.dumps({
                    "members": notify_selection,
                    "include_self": include_self
                })

            c.execute("SELECT id FROM inventory WHERE user_id=? AND medicine=?", (user, med))
            row = c.fetchone()

            if row:
                c.execute("""
                    UPDATE inventory
                    SET stock=?, threshold=?, notes=?, last_updated=?, notify_member_ids=?,
                        out_notified=CASE WHEN ? > 0 THEN 0 ELSE out_notified END,
                        low_stock_notified=CASE WHEN ? >= 4 THEN 0 ELSE low_stock_notified END
                    WHERE id=?
                """, (stock, thresh, notes, now, notify_payload, stock, stock, row[0]))
            else:
                c.execute("""
                    INSERT INTO inventory(user_id,medicine,stock,threshold,notes,last_updated,notify_member_ids)
                    VALUES (?,?,?,?,?,?,?)
                """, (user, med, stock, thresh, notes, now, notify_payload))

            conn.commit()
            st.success(T("inventory_saved"))
            process_inventory_alerts(conn, user, user_email, family_lookup, show_feedback=True)
            st.rerun()

    with tab_log:
        if df.empty:
            st.info(T("inventory_empty"))
        else:
            st.markdown("### " + T("inventory_log_title"))
            st.caption(T("inventory_log_helper"))
            med_options = df["medicine"].tolist()
            with st.form("inventory_log_form"):
                selected_med = st.selectbox(T("med_name"), med_options, key="inventory_log_med")
                qty_logged = st.number_input(
                    T("inventory_log_quantity"),
                    min_value=1,
                    value=1,
                    step=1,
                    key="inventory_log_qty"
                )
                submitted = st.form_submit_button(T("inventory_log_button"))

            if submitted:
                logged, remaining = record_inventory_usage(
                    conn,
                    user,
                    selected_med,
                    quantity=qty_logged,
                    source="manual"
                )
                if logged:
                    st.success(
                        T("inventory_log_success").format(
                            medicine=selected_med,
                            qty=int(qty_logged),
                            stock=remaining
                        )
                    )
                    process_inventory_alerts(conn, user, user_email, family_lookup, show_feedback=True)
                    st.rerun()
                else:
                    st.warning(T("inventory_no_match"))

            if not usage_df.empty:
                st.markdown("### " + T("intake_per_medicine"))
                summary_df = usage_df.merge(
                    df[["id", "medicine"]],
                    left_on="inventory_id",
                    right_on="id",
                    how="left"
                )
                summary_df = summary_df.rename(columns={
                    "medicine": T("med_name"),
                    "total_taken": T("inventory_logged_label"),
                    "last_taken": T("inventory_last_logged")
                })
                taken_col = T("inventory_logged_label")
                last_col = T("inventory_last_logged")
                summary_df[taken_col] = summary_df[taken_col].fillna(0).astype(int)
                summary_df[last_col] = pd.to_datetime(summary_df[last_col], errors="coerce")
                summary_df[last_col] = summary_df[last_col].dt.strftime("%b %d, %Y %H:%M")
                summary_df[last_col] = summary_df[last_col].fillna("-")
                st.dataframe(
                    summary_df[[T("med_name"), taken_col, last_col]],
                    use_container_width=True
                )

    st.markdown("---")

    if df.empty:
        st.info(T("inventory_empty"))
        return

    for _, r in df.iterrows():
        is_empty = r["stock"] <= 0
        low = r["stock"] <= r["threshold"]
        if is_empty:
            color = "#ffe1e9"
            label = T("out_stock_badge")
        elif low:
            color = "#ffdcdc"
            label = T("low_stock_badge")
        else:
            color = "#dcffdc"
            label = T("ok_badge")
        notes_value = r.get("notes", None)
        notes_display = notes_value or T("notes_none")
        usage_lines = ""
        usage_info = usage_lookup.get(r["id"])
        if usage_info:
            total_taken = usage_info.get("total")
            if total_taken:
                usage_lines += f"<br><b>{T('inventory_logged_label')}:</b> {total_taken}"
            last_logged = usage_info.get("last")
            if last_logged:
                try:
                    last_dt = datetime.strptime(last_logged, "%Y-%m-%d %H:%M:%S")
                    last_text = last_dt.strftime("%b %d, %Y %H:%M")
                except (TypeError, ValueError):
                    last_text = last_logged
                usage_lines += f"<br><b>{T('inventory_last_logged')}:</b> {last_text}"
        member_ids, include_self_flag = parse_inventory_notify_config(r.get("notify_member_ids"))
        recipient_names = []
        if member_ids or include_self_flag:
            if include_self_flag:
                recipient_names.append(T("inventory_notify_self_label"))
            for mid in member_ids:
                info = family_lookup.get(mid)
                if info and info.get("name"):
                    recipient_names.append(info["name"])
        else:
            if user_email:
                recipient_names.append(T("inventory_notify_self_label"))
            for info in family_lookup.values():
                if info.get("email") and info.get("name"):
                    recipient_names.append(info["name"])
        recipient_names = [name for i, name in enumerate(recipient_names) if name and name not in recipient_names[:i]]
        if recipient_names:
            usage_lines += f"<br><b>{T('inventory_recipients_label')}:</b> {', '.join(recipient_names)}"

        col_left, col_right = st.columns([5, 1])
        with col_left:
            st.markdown(
                f"""
                <div class='blue-box' style='background:{color};'>
                    <b>{r['medicine']} — {label}</b><br>
                    {T('inventory_stock')}: {r['stock']} | {T('inventory_threshold')}: {r['threshold']}<br>
                    {T('notes_label')}: {notes_display}{usage_lines}
                </div>
                """,
                unsafe_allow_html=True
            )
        with col_right:
            if st.button(T("delete"), key=f"inv_del_{r['id']}", use_container_width=True):
                cur = conn.cursor()
                try:
                    cur.execute("DELETE FROM inventory_usage WHERE inventory_id=?", (r["id"],))
                except Exception:
                    pass
                cur.execute("DELETE FROM inventory WHERE id=?", (r["id"],))
                conn.commit()
                st.success(T("voice_deleted").format(medicine=r['medicine']))
                st.rerun()


# ============================================================
# PRESCRIPTION IMAGE UPLOADS
# ============================================================
def _ensure_prescription_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            notes TEXT,
            uploaded_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def _build_prescription_filename(original_name: str) -> str:
    base_path = Path(original_name or "prescription.png")
    base = re.sub(r"[^A-Za-z0-9_-]", "", base_path.stem)
    if not base:
        base = "prescription"
    ext = base_path.suffix or ".png"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{base}{ext}"


def prescription_upload_page(conn):
    _ensure_prescription_table(conn)
    user = st.session_state.user

    render_section_header("📸", T("prescription_photos"), T("prescription_subtitle"))
    st.write(T("prescription_intro"))

    upload = st.file_uploader(T("upload_prescription"), type=["jpg", "jpeg", "png"])
    notes = st.text_area(
        T("notes_optional"),
        help=T("notes_optional_help")
    )

    if upload:
        st.image(upload, width=350, caption=T("preview"))
        if st.button(T("save_prescription_btn")):
            upload.seek(0)
            file_bytes = upload.read()
            if not file_bytes:
                st.error(T("prescription_read_error"))
            else:
                file_name = _build_prescription_filename(upload.name)
                dest_path = PRESCRIPTION_DIR / file_name
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dest_path, "wb") as f:
                    f.write(file_bytes)

                conn.execute(
                    """
                    INSERT INTO prescriptions(user_id, file_name, file_path, notes, uploaded_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user, file_name, str(dest_path), notes.strip() or None, datetime.now().isoformat(timespec="seconds")),
                )
                conn.commit()
                st.success(T("prescription_saved"))
                st.rerun()
    else:
        st.info(T("prescription_select_prompt"))

    render_pill(f"📥 {T('saved_prescriptions')}")
    df = pd.read_sql_query(
        """
        SELECT id, file_name, file_path, notes, uploaded_at
        FROM prescriptions
        WHERE user_id=?
        ORDER BY uploaded_at DESC
        """,
        conn,
        params=(user,),
    )

    if df.empty:
        st.info(T("prescription_empty"))
        return

    for _, row in df.iterrows():
        container = st.container()
        container.markdown(f"**{row['file_name']}** · {row['uploaded_at']}")
        if row["notes"]:
            container.write(row["notes"])

        path = Path(row["file_path"])
        if path.exists():
            container.image(str(path), width=320)
            mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            with open(path, "rb") as f:
                container.download_button(
                    label=T("download_image"),
                    data=f.read(),
                    file_name=row["file_name"],
                    mime=mime_type,
                    key=f"prescription_download_{row['id']}",
                )
        else:
            container.warning(T("image_missing"))

        container.markdown("---")


# ============================================================
# INTERACTION CHECKER
# ============================================================
def interaction_checker_page(conn):
    render_section_header("🔍", T("interaction_checker"), T("interaction_subtitle"))

    col1, col2 = st.columns(2)
    m1 = col1.text_input(T("medicine_one"))
    m2 = col2.text_input(T("medicine_two"))

    interactions = {
        ("ibuprofen", "aspirin"): T("interaction_ibuprofen_aspirin"),
        ("warfarin", "aspirin"): T("interaction_warfarin_aspirin"),
        ("metformin", "alcohol"): T("interaction_metformin_alcohol"),
        ("paracetamol", "alcohol"): T("interaction_paracetamol_alcohol")
    }

    if st.button(T("check")):
        a, b = m1.lower(), m2.lower()
        if (a, b) in interactions:
            st.error(interactions[(a, b)])
        elif (b, a) in interactions:
            st.error(interactions[(b, a)])
        else:
            st.success(T("interaction_none"))


# ============================================================
# VOICE COMMANDS
# ============================================================
def show_today(conn):
    user = st.session_state.user
    t = datetime.now().strftime("%Y-%m-%d")
    df = pd.read_sql_query(f"SELECT * FROM medicine WHERE user_id='{user}' AND date='{t}'", conn)

    if df.empty:
        st.info(T("no_today"))
    else:
        for _, r in df.iterrows():
            st.write(f"{r['medicine']} — {r['reminder_time']}")

def delete_last(conn):
    user = st.session_state.user
    c = conn.cursor()
    c.execute("SELECT id,medicine FROM medicine WHERE user_id=? ORDER BY id DESC LIMIT 1", (user,))
    row = c.fetchone()
    if not row:
        st.info(T("voice_delete_none"))
    else:
        c.execute("DELETE FROM medicine WHERE id=?", (row[0],))
        conn.commit()
        st.success(T("voice_deleted").format(medicine=row[1]))

VOICE_STOPWORDS = {
    "add", "set", "remind", "reminder", "me", "to", "please", "at", "for", "my",
    "medicine", "med", "today", "tonight", "this", "evening", "morning", "night",
    "afternoon", "noon", "pm", "am", "in", "the", "take", "schedule", "time",
    "give", "need", "and", "with", "after", "before", "make", "put", "around",
    "on", "tomorrow", "next", "day", "of"
}

DOSAGE_UNITS = {
    "mg": "mg",
    "milligram": "mg",
    "milligrams": "mg",
    "g": "g",
    "gram": "g",
    "grams": "g",
    "ml": "ml",
    "milliliter": "ml",
    "milliliters": "ml",
    "mcg": "mcg",
    "microgram": "mcg",
    "micrograms": "mcg",
    "units": "units",
    "drop": "drops",
    "drops": "drops"
}

QUANTITY_UNITS = {
    "tablet": "tablets",
    "tablets": "tablets",
    "tab": "tablets",
    "tabs": "tablets",
    "pill": "pills",
    "pills": "pills",
    "capsule": "capsules",
    "capsules": "capsules",
    "cap": "capsules",
    "caps": "capsules",
    "spoon": "spoons",
    "spoons": "spoons",
    "teaspoon": "teaspoons",
    "teaspoons": "teaspoons",
    "tablespoon": "tablespoons",
    "tablespoons": "tablespoons",
    "drop": "drops",
    "drops": "drops"
}

INSTRUCTION_PHRASES = [
    "after meal",
    "after meals",
    "before meal",
    "before meals",
    "after breakfast",
    "before breakfast",
    "after lunch",
    "before lunch",
    "after dinner",
    "before dinner",
    "before bed",
    "before sleep",
    "with food",
    "with water",
    "with milk"
]

FREQUENCY_MAP = [
    ("Three times a day", ["three times a day", "thrice a day", "3 times a day"]),
    ("Twice a day", ["twice a day", "two times a day", "2 times a day", "twice daily"]),
    ("Once a day", ["once a day", "once daily", "one time a day", "daily"]),
    ("Every morning", ["every morning", "each morning", "morning only"]),
    ("Every night", ["every night", "each night", "night only", "at night"]),
]


def parse_voice(text, conn):
    original = text.strip()
    cleaned = original.lower()

    def remove_span(source: str, span):
        return (source[: span[0]] + " " + source[span[1]:]).strip()

    time_value = None
    time_match = re.search(r"(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)", cleaned)
    if time_match:
        hour = int(time_match.group(1))
        minute = time_match.group(2) or "00"
        ampm = time_match.group(3)
        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        time_value = f"{hour:02}:{minute}"
        cleaned = remove_span(cleaned, time_match.span())
    else:
        twenty_four = re.search(r"(?:at\s*)?(\d{1,2}):(\d{2})", cleaned)
        if twenty_four:
            hour = int(twenty_four.group(1)) % 24
            minute = twenty_four.group(2)
            time_value = f"{hour:02}:{minute}"
            cleaned = remove_span(cleaned, twenty_four.span())
    if not time_value:
        time_value = "08:00"

    date_value = datetime.now().date()
    if "tomorrow" in cleaned:
        date_value += timedelta(days=1)
        cleaned = cleaned.replace("tomorrow", " ")

    dosage_value = ""
    dosage_match = re.search(r"(\d+(?:\.\d+)?)\s*(mg|milligrams?|g|grams?|ml|milliliters?|mcg|micrograms?|units|drops?)", cleaned)
    if dosage_match:
        amount = dosage_match.group(1)
        unit_key = dosage_match.group(2).lower()
        norm_unit = DOSAGE_UNITS.get(unit_key, unit_key)
        dosage_value = f"{amount} {norm_unit}"
        cleaned = remove_span(cleaned, dosage_match.span())

    dose_qty = 1
    quantity_match = re.search(r"(\d+)\s*(tablets?|tabs?|pills?|capsules?|caps?|spoons?|teaspoons?|tablespoons?|drops?)", cleaned)
    if quantity_match:
        dose_qty = int(quantity_match.group(1))
        unit_key = quantity_match.group(2).lower()
        if not dosage_value:
            norm_unit = QUANTITY_UNITS.get(unit_key, unit_key)
            dosage_value = f"{dose_qty} {norm_unit}"
        cleaned = remove_span(cleaned, quantity_match.span())

    freq_value = ""
    for label, keywords in FREQUENCY_MAP:
        if any(keyword in cleaned for keyword in keywords):
            freq_value = label
            for keyword in keywords:
                if keyword in cleaned:
                    cleaned = cleaned.replace(keyword, " ")
            break

    instruction_value = ""
    for phrase in INSTRUCTION_PHRASES:
        if phrase in cleaned:
            instruction_value = phrase.capitalize()
            cleaned = cleaned.replace(phrase, " ")
            break

    tokens = [tok for tok in re.split(r"[^a-z0-9]+", cleaned) if tok]
    med_tokens = [tok for tok in tokens if tok not in VOICE_STOPWORDS and not tok.isdigit()]
    med_name = " ".join(med_tokens).strip()
    if not med_name:
        st.error(T("voice_med_missing"))
        return
    med_name = med_name.title()

    instructions = instruction_value or "Added via voice"

    conn.execute(
        """
        INSERT INTO medicine(
            user_id,
            medicine,
            reminder_time,
            date,
            dosage,
            frequency,
            instructions,
            dose_quantity
        )
        VALUES (?,?,?,?,?,?,?,?)
        """,
        (
            st.session_state.user,
            med_name,
            time_value,
            date_value.strftime("%Y-%m-%d"),
            dosage_value,
            freq_value,
            instructions,
            int(dose_qty)
        )
    )
    conn.commit()
    st.success(T("voice_added").format(medicine=med_name, time=time_value))

    details = []
    if dosage_value:
        details.append(f"{T('dos')}: {dosage_value}")
    if dose_qty:
        details.append(f"{T('dose_quantity_label')}: {dose_qty}")
    if freq_value:
        details.append(f"{T('freq')}: {freq_value}")
    if instruction_value:
        details.append(f"{T('notes_label')}: {instruction_value.capitalize()}")
    if details:
        st.info(" · ".join(details))


# ============================================================
# DOCTOR APPOINTMENTS
# ============================================================
def appointment_page(conn):
    render_section_header("🩺", T("doctor_appointments"), T("appointment_subtitle"))

    user = st.session_state.user
    col1, col2 = st.columns(2)

    # Load family members for appointment notifications
    family_df = pd.read_sql_query(
        "SELECT id, member_name, email FROM family_members WHERE user_id=? ORDER BY member_name",
        conn,
        params=(user,)
    )
    family_lookup = {int(row["id"]): {"name": row["member_name"], "email": row["email"]} for _, row in family_df.iterrows()}
    email_ready_df = family_df[family_df["email"].notna() & (family_df["email"].str.strip() != "")]
    notify_options = [int(x) for x in email_ready_df["id"].tolist()]
    notify_labels = {int(row["id"]): f"{row['member_name']} ({row['email']})" for _, row in email_ready_df.iterrows()}

    with col1:
        doctor = st.text_input(T("doctor_name_label"), key="app_doc_name")
        hospital = st.text_input(T("hospital_label"), key="app_hosp_name")
        date = st.date_input(T("date"), key="app_date_input")

    with col2:
        time_val = st.time_input(T("time"), key="app_time_input", step=timedelta(minutes=1))
        notes = st.text_area(T("notes_label"), key="app_notes_input")
        if notify_options:
            notify_selection = st.multiselect(
                T("inventory_notify_label"),
                notify_options,
                default=[],
                format_func=lambda mid: notify_labels.get(mid, str(mid)),
                help=T("appointment_notify_help") if "appointment_notify_help" in TEXT[st.session_state.get("ui_lang","en")] else "",
                key="app_notify_select"
            )
        else:
            notify_selection = []
            st.info(T("no_family_emails"))
        include_self = st.checkbox(T("inventory_notify_self"), value=bool(get_user_email(conn, user)), key="app_notify_self")

    if st.button(T("save_appointment"), key="app_save_btn"):
        try:
            # Accept time object from st.time_input and format it
            if isinstance(time_val, str):
                datetime.strptime(time_val, "%H:%M")
                time_str = time_val
            else:
                time_str = time_val.strftime("%H:%M")

            notify_payload = None
            if notify_selection or include_self:
                notify_payload = json.dumps({"members": notify_selection, "include_self": include_self})

            conn.execute("""
                INSERT INTO appointments(user_id, doctor_name, hospital, date, time, notes, notify_member_ids)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user, doctor, hospital, date.strftime("%Y-%m-%d"), time_str, notes, notify_payload))

            conn.commit()
            st.success(T("appointment_saved"))
            st.rerun()

        except Exception:
            st.error(T("invalid_time"))

    st.markdown("---")

    df = pd.read_sql_query(
        f"SELECT * FROM appointments WHERE user_id='{user}' ORDER BY date, time",
        conn
    )

    now = datetime.now()

    for _, a in df.iterrows():
        st.markdown(
            f"""
            <div class='blue-box'>
                <b>🩺 {a['doctor_name']}</b><br>
                {a['hospital']}<br>
                📅 {a['date']} — ⏰ {a['time']}<br>
                <b>{T('notes_label')}:</b> {a['notes'] or T('notes_none')}
            </div>
            """,
            unsafe_allow_html=True
        )

        msg_en = f"You have a doctor appointment with {a['doctor_name']} at {a['time']}."
        msg_bn = f"{a['doctor_name']} এর সাথে ডাক্তার অ্যাপয়েন্টমেন্ট {a['time']}।"

        voice_cols = st.columns(2)
        with voice_cols[0]:
            if st.button(T("speak_english_btn"), key=f"appt_voice_en_{a['id']}"):
                speak(msg_en, "en")
        with voice_cols[1]:
            if st.button(T("speak_bangla_btn"), key=f"appt_voice_bn_{a['id']}"):
                speak(msg_bn, "bn")

        ap_dt = datetime.strptime(a["date"] + " " + a["time"], "%Y-%m-%d %H:%M")
        diff = (ap_dt - now).total_seconds()

        # Background worker handles automatic alerts at exact time
        # This section just shows status and allows manual actions

        # Delete appointment button
        if st.button(T("delete"), key=f"appt_del_{a['id']}"):
            conn.execute("DELETE FROM appointments WHERE id=?", (a['id'],))
            conn.commit()
            st.success(T("voice_deleted").format(medicine=a['doctor_name']))
            st.rerun()


# ============================================================
# FAMILY MEMBERS PAGE
# ============================================================
def family_members_page(conn):
    st.session_state.setdefault("reset_family_form", False)
    if st.session_state["reset_family_form"]:
        for key in ("family_member_name", "family_health", "family_email"):
            st.session_state.pop(key, None)
        st.session_state["reset_family_form"] = False

    render_section_header("👨‍👩‍👧‍👦", T("manage_family"), T("family_subtitle"))

    user = st.session_state.user

    with st.expander(f"➕ {T('add_family_member')}", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            member_name = st.text_input(T("member_name"), key="family_member_name")
            relationship_labels = [T(f"relationship_{rel}") for rel in FAMILY_RELATIONSHIPS]
            selected_label = st.selectbox(
                T("relationship"),
                relationship_labels,
                key="family_relationship"
            )
            relationship = FAMILY_RELATIONSHIPS[relationship_labels.index(selected_label)]

        with col2:
            age = st.number_input(T("age"), min_value=1, max_value=120, value=30, key="family_age")
            email = st.text_input(T("email"), key="family_email")
            st.caption(T("family_email_instructions"))
            health_conditions = st.text_area(T("health_conditions"), key="family_health")

        if st.button(T("save_member"), key="family_save_btn"):
            if member_name.strip():
                email_value = (email or "").strip()
                if email_value and not re.match(r"[^@]+@[^@]+\.[^@]+", email_value):
                    st.error(T("invalid_email"))
                    return
                conn.execute(
                    """
                    INSERT INTO family_members(user_id, member_name, relationship, age, health_conditions, email)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user,
                        member_name.strip(),
                        relationship,
                        int(age),
                        health_conditions.strip() or None,
                        email_value or None
                    )
                )
                conn.commit()
                st.success(T("member_saved"))
                st.session_state["reset_family_form"] = True
                st.rerun()
            else:
                st.error(T("member_name_required"))

    st.markdown("### " + T("saved_family_members"))

    df = pd.read_sql_query(
        """
        SELECT id, member_name, relationship, age, health_conditions, email, created_at
        FROM family_members
        WHERE user_id=?
        ORDER BY id DESC
        """,
        conn,
        params=(user,)
    )

    if df.empty:
        st.info(T("no_family_members"))
        return

    for _, row in df.iterrows():
        rel_display = relationship_label(row["relationship"])
        health_info = row["health_conditions"] or T("health_none")
        email_info = row["email"] or T("family_email_missing")

        st.markdown(
            f"""
            <div class='blue-box'>
                <b>{row['member_name']}</b> · {rel_display}<br>
                {T('age')}: {row['age'] or '-'}<br>
                {T('health_conditions')}: {health_info}<br>
                {T('email')}: {email_info}
            </div>
            """,
            unsafe_allow_html=True
        )

        delete_key = f"family_delete_{row['id']}"
        if st.button(T("delete_member"), key=delete_key):
            conn.execute("DELETE FROM family_members WHERE id=?", (row["id"],))
            conn.commit()
            st.success(T("family_deleted"))
            st.rerun()


# ============================================================
# SLEEP INSIGHTS PAGE
# ============================================================
def sleep_insights_page(conn):
    render_section_header("🌙", T("sleep_insights"), T("sleep_subtitle"))

    user = st.session_state.user
    c = conn.cursor()

    with st.expander(T("sleep_log_header"), expanded=True):
        today = datetime.now().date()
        col1, col2 = st.columns(2)

        log_date = col1.date_input(
            T("sleep_log_date"),
            value=today,
            key="sleep_log_date_input"
        )
        hours = col1.number_input(
            T("sleep_hours"),
            min_value=0.0,
            max_value=24.0,
            value=7.0,
            step=0.25,
            key="sleep_hours_input"
        )

        quality = col2.slider(
            T("sleep_quality_label"),
            min_value=1,
            max_value=5,
            value=3,
            key="sleep_quality_slider"
        )
        mood = col2.slider(
            T("sleep_mood_label"),
            min_value=1,
            max_value=5,
            value=3,
            key="sleep_mood_slider"
        )
        notes = st.text_area(T("notes_label"), key="sleep_notes_input")

        if st.button(T("sleep_save_entry"), key="sleep_save_btn"):
            c.execute(
                """
                INSERT INTO sleep_logs(user_id, log_date, hours, quality, mood, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user,
                    log_date.strftime("%Y-%m-%d"),
                    float(hours),
                    int(quality),
                    int(mood),
                    notes.strip() or None,
                ),
            )
            conn.commit()
            st.success(T("sleep_saved"))
            st.rerun()

    df = pd.read_sql_query(
        """
        SELECT log_date, hours, quality, mood, notes
        FROM sleep_logs
        WHERE user_id=?
        ORDER BY log_date
        """,
        conn,
        params=(user,),
    )

    if df.empty:
        st.info(T("sleep_empty"))
        return

    df["log_date"] = pd.to_datetime(df["log_date"])
    df = df.sort_values("log_date")
    df["notes"] = df["notes"].fillna("")

    last14 = df.tail(14).copy()
    last7 = df.tail(7).copy()
    prev7 = df.iloc[:-len(last7)].tail(7) if len(df) > len(last7) else pd.DataFrame()

    avg_hours = float(last7["hours"].mean())
    avg_quality = float(last7["quality"].mean())
    delta_hours = None if prev7.empty else avg_hours - float(prev7["hours"].mean())
    delta_quality = None if prev7.empty else avg_quality - float(prev7["quality"].mean())
    variability = last7["hours"].std() if len(last7) > 1 else None

    today = datetime.now().date()
    week_start = today - timedelta(days=6)
    logged_last_week = df[df["log_date"].dt.date >= week_start]["log_date"].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric(
        T("sleep_avg_hours"),
        f"{avg_hours:.1f}h",
        delta=None if delta_hours is None else f"{delta_hours:+.1f}h vs prev",
    )
    col2.metric(
        T("sleep_quality_trend"),
        f"{avg_quality:.1f}/5",
        delta=None if delta_quality is None else f"{delta_quality:+.1f} vs prev",
    )
    variability_text = (
        None if variability is None else f"{T('sleep_variability')}: +/-{variability:.1f}h"
    )
    col3.metric(T("sleep_streak"), f"{logged_last_week}/7", delta=variability_text)

    st.markdown("### " + T("sleep_chart_title"))
    chart_df = last14.set_index("log_date")[["hours"]]
    chart_df.index = chart_df.index.strftime("%b %d")
    st.line_chart(chart_df, height=260)

    recent_df = df.sort_values("log_date", ascending=False).head(10).copy()
    recent_df["log_date"] = recent_df["log_date"].dt.strftime("%b %d, %Y")
    recent_df = recent_df.rename(
        columns={
            "log_date": T("sleep_log_date"),
            "hours": T("sleep_hours"),
            "quality": T("sleep_quality_label"),
            "mood": T("sleep_mood_label"),
            "notes": T("notes_label"),
        }
    )

    st.markdown("### " + T("sleep_recent_entries"))
    st.dataframe(recent_df, use_container_width=True)

    if avg_hours >= 7:
        st.success(T("sleep_tip_positive"))
    else:
        st.warning(T("sleep_tip_negative"))


# ============================================================
# TOOLS PAGE
# ============================================================
# ============================================================
# CLEAN FIXED TOOLS PAGE  (FULL BLUE VERSION)
# ============================================================
def tools_page(conn):
    render_section_header("🧰", T("tools"), T("tools_subtitle"))

    
    tools = [
        ("inventory", f"💊 {T('inventory_tool')}", inventory_page),
        ("photos", f"🗂️ {T('prescription_photos')}", prescription_upload_page),
        ("interactions", f"⚠️ {T('interaction_checker')}", interaction_checker_page),
        ("sleep", f"🌙 {T('sleep_insights')}", sleep_insights_page),
        ("appointments", f"📅 {T('doctor_appointments')}", appointment_page),
        ("family", f"👪 {T('manage_family')}", family_members_page),
    ]

    
    tool_labels = [label for _, label, _ in tools]

    tool_tabs = st.tabs(tool_labels)

    
    for i, tab in enumerate(tool_tabs):
        with tab:
            st.markdown("<br>", unsafe_allow_html=True) 
            tools[i][2](conn)
        # ============================================================
# PART 4 — AI ASSISTANT (Gemini Flash + Blue UI + Voice Output)
# ============================================================

import requests
import re

# ------------------------------
# Detect Language (Bangla vs English)
# ------------------------------
def detect_lang(text):
    return "bn" if re.search(r"[\u0980-\u09FF]", text) else "en"


# ------------------------------
# Gemini API Setup
# ============================================================
# GEMINI 2.0 FLASH — AI ENGINE (WORKING)
# ============================================================
GEMINI_API_KEY = "AIzaSyDusUSm3HodwbyrepjAZQSC0nRV4OVKxqw"

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
)

# Gemini Function
def get_ai_reply(prompt):

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    try:
        res = requests.post(GEMINI_URL, headers=headers, json=payload)
        data = res.json()

        # SAFEST POSSIBLE CHECKS
        if "candidates" not in data:
            return ("AI Error: Gemini returned no candidates.", "en")

        cand = data["candidates"]
        if not cand or "content" not in cand[0]:
            return ("AI Error: Empty content response.", "en")

        parts = cand[0]["content"]["parts"]
        if not parts or "text" not in parts[0]:
            return ("AI Error: No text in response parts.", "en")

        reply = parts[0]["text"]
        return reply, detect_lang(reply)

    except Exception as e:
        return (f"AI Error: {str(e)}", "en")




# ============================================================
# AI CHAT PAGE (Blue Theme)
# ============================================================
def ai_chat_page():
    render_section_header("🤖", T("ai"), T("ai_subtitle"))

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [("ai", T("ai_greeting"))]
    else:
        default_greetings = {TEXT["en"]["ai_greeting"], TEXT["bn"]["ai_greeting"]}
        if (
            st.session_state.chat_history
            and st.session_state.chat_history[0][0] == "ai"
            and st.session_state.chat_history[0][1] in default_greetings
        ):
            st.session_state.chat_history[0] = ("ai", T("ai_greeting"))

    def process_prompt(prompt: str):
        st.session_state.chat_history.append(("user", prompt))
        with st.spinner(T("ai_thinking")):
            reply, lang = get_ai_reply(prompt)
        st.session_state.chat_history.append(("ai", reply))
        st.session_state.ai_last_reply = reply
        st.session_state.ai_last_lang = lang
        st.rerun()

    chat_col, side_col = st.columns([1.7, 1])
    user_label = T("ai_you_label")
    bot_label = T("ai_bot_label")

    with chat_col:
        st.markdown("<div class='ai-shell'><div class='chat-timeline'>", unsafe_allow_html=True)
        for sender, msg in st.session_state.chat_history:
            icon = "🧑" if sender == "user" else "🤖"
            bubble_class = "user-bubble" if sender == "user" else "ai-bubble"
            label = user_label if sender == "user" else bot_label
            st.markdown(
                f"""
                <div class='chat-bubble {bubble_class}'>
                    <div class='bubble-label'>{icon} {label}</div>
                    <p>{msg}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div></div>", unsafe_allow_html=True)

        user_input = st.chat_input(T("ask"))
        if user_input:
            process_prompt(user_input)

    with side_col:
        st.markdown("<div class='quick-card'>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Quick prompts")
        st.markdown("<p class='prompt-note'>Tap to auto-fill a helpful AI request.</p>", unsafe_allow_html=True)
        prompts = [
            "Summarize today's reminders",
            "Suggest a gentle motivation message",
            "Draft a friendly message for my family",
        ]
        for idx, prompt in enumerate(prompts):
            if st.button(prompt, key=f"ai_prompt_{idx}", use_container_width=True):
                process_prompt(prompt)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='quick-card voice-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔊 " + T("ai_listen_header"))
        if st.session_state.get("ai_last_reply"):
            lang = st.session_state.get("ai_last_lang", "en")
            st.caption("Last response language: " + ("Bangla" if lang == "bn" else "English"))
            
            voice_cols = st.columns(2)
            
            # --- BUTTON 1: LISTEN IN ENGLISH ---
            with voice_cols[0]:
                if st.button(T("ai_play_en"), key="ai_eng_voice", use_container_width=True):
                    # Direct playback (English engine)
                    speak(st.session_state.ai_last_reply, "en")

            # --- BUTTON 2: TRANSLATE & LISTEN IN BANGLA ---
            with voice_cols[1]:
                if st.button(T("ai_play_bn"), key="ai_bn_voice", use_container_width=True):
                    text_to_speak = st.session_state.ai_last_reply
                    
                    # Logic: If the text is English, translate it first!
                    if lang == "en":
                        with st.spinner("Translating to Bangla..."):
                            # We use your existing Gemini function to do the translation
                            trans_prompt = f"Translate the following text to Bengali. Return ONLY the translated text:\n\n{text_to_speak}"
                            translated_text, _ = get_ai_reply(trans_prompt)
                            text_to_speak = translated_text
                            
                    # Now speak the (translated) Bangla text
                    speak(text_to_speak, "bn")
        else:
            st.caption("Ask something to enable playback controls.")
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# REPORTS PAGE — FIXED + CONNECTED
# ============================================================
def reports_page(conn):
    render_section_header("📑", T("reports"), T("reports_subtitle"))

    report_options = [
        ("weekly", f"📆 {T('report_weekly')}"),
        ("analytics", f"📊 {T('report_analytics')}"),
        ("monthly", f"📅 {T('report_monthly')}")
    ]
    choice = st.radio(
        T("report_choose"),
        [label for _, label in report_options],
        horizontal=True,
        key="reports_selector"
    )
    selected_report = next((key for key, label in report_options if label == choice), "weekly")

    if selected_report == "weekly":
        weekly_summary(conn)
    elif selected_report == "analytics":
        analytics_page(conn)
    elif selected_report == "monthly":
        monthly_report_page(conn)



# ============================================================
# MAIN APP CONTROLLER
# ============================================================
def main_app():
    sidebar_controls()
    # Ensure worker runs every time
    if st.session_state.user:
        ensure_notification_worker(st.session_state.user)
    conn = sqlite3.connect("medicine.db")

    tabs = st.tabs([
        "🏠 " + T("dashboard"),
        "💊 " + T("reminders"),
        "📑 " + T("reports"),
        "🧰 " + T("tools"),
        "🤖 " + T("ai")
    ])

    with tabs[0]: dashboard_page(conn)
    with tabs[1]: reminders_page(conn)
    with tabs[2]: reports_page(conn)
    with tabs[3]: tools_page(conn)
    with tabs[4]: ai_chat_page()

    conn.close()


# ============================================================
# ENTRY POINT
# ============================================================
if st.session_state.logged:
    main_app()
else:
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "signup":
        signup_page()
    elif st.session_state.page == "recovery":
        password_recovery_page()
    elif st.session_state.page == "reset":
        reset_password_page()
    else:

        login_page()
