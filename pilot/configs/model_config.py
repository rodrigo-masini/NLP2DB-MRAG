#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import nltk

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PILOT_PATH = os.path.join(ROOT_PATH, "pilot")
LOGDIR = os.path.join(ROOT_PATH, "logs")
DATASETS_DIR = os.path.join(PILOT_PATH, "datasets")
KNOWLEDGE_UPLOAD_ROOT_PATH = os.path.join(PILOT_PATH, "data")
PLUGINS_DIR = os.path.join(ROOT_PATH, "plugins")

os.makedirs(LOGDIR, exist_ok=True)
os.makedirs(KNOWLEDGE_UPLOAD_ROOT_PATH, exist_ok=True)

nltk.data.path = [os.path.join(PILOT_PATH, "nltk_data")] + nltk.data.path

# This is no longer needed for local models, but kept for compatibility with any code that might reference it.
LLM_MODEL_CONFIG = {
    "proxyllm": "proxyllm",
}

VECTOR_SEARCH_TOP_K = 10
