import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
AUDIO_FORMAT = "wav"

WHISPER_MODEL = "base"

GPT_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 500
TEMPERATURE = 0.7

MOOD_THRESHOLDS = {
    "very_low": 0, 
    "low": 3, 
    "moderate": 5, 
    "good": 7, 
    "excellent": 9
}

STRESS_KEYWORDS = [
    "stressed", "overwhelmed", "anxious", "worried", "pressure", 
    "deadline", "frustrated", "tired", "exhausted", "burned out",
    "difficult", "challenging", "struggling", "nervous", "tense"
]

POSITIVE_KEYWORDS = [
    "happy", "excited", "motivated", "energized", "confident",
    "accomplished", "satisfied", "peaceful", "calm", "focused",
    "productive", "successful", "grateful", "optimistic", "relaxed"
]

BREAK_SUGGESTIONS = {
    "high_stress": [
        "Take 5 deep breaths and do a quick meditation",
        "Step outside for a 10-minute walk",
        "Try progressive muscle relaxation",
        "Listen to calming music for 10 minutes"
    ],
    "low_energy": [
        "Do 10 jumping jacks or stretches",
        "Drink a glass of water and have a healthy snack",
        "Take a 5-minute power walk",
        "Do some desk exercises"
    ],
    "moderate": [
        "Take a 15-minute break from screens",
        "Practice gratitude - write down 3 things you are thankful for",
        "Chat with a colleague or friend",
        "Listen to an uplifting podcast"
    ]
}

FOCUS_TIPS = {
    "high_stress": "Try the 4-7-8 breathing technique before starting your next task",
    "distracted": "Use the Pomodoro technique - 25 minutes focused work, 5-minute break",
    "low_energy": "Tackle your easiest task first to build momentum",
    "overwhelmed": "Break your current task into 3 smaller, manageable steps"
}

JOURNALING_PROMPTS = {
    "stressed": "What is one small thing I can do right now to reduce my stress?",
    "tired": "What would help me feel more energized today?",
    "frustrated": "What can I learn from this challenging situation?",
    "anxious": "What are three things I can control in this situation?",
    "happy": "What contributed to my positive mood today?",
    "accomplished": "How can I celebrate this achievement?",
    "default": "What is one thing I am grateful for right now?"
}

APP_TITLE = "SereneDesk: AI Workspace Mood Optimizer"
APP_ICON = "??"
VERSION = "1.0.0"

MAX_HISTORY_ENTRIES = 1000
DATA_RETENTION_DAYS = 90
