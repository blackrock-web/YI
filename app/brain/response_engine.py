"""
MY AI - Deterministic Response Engine
Template-based responses with personality weighting, slot filling, and fallback handling.
"""
from datetime import datetime
import random
from typing import Dict, Any, List, Optional
from app.brain.intents import Intent

TEMPLATES: Dict[Intent, List[str]] = {
    Intent.GREETING: [
        "Hello! How can I assist you today?",
        "Hi there! Good to see you. How can I help?",
        "Greetings! I'm ready to help with your schedule, tasks, or anything on your mind.",
        "Hey! What's on your plan for today?",
    ],
    Intent.GOODBYE: [
        "Goodbye! Take care, and feel free to return whenever you need me.",
        "Have a great day ahead! Your data remains safely stored locally.",
        "Catch you later! I'll be right here when you need anything.",
    ],
    Intent.ASK_NAME: [
        "I am MY AI, your private, personal AI assistant and companion.",
        "My name is MY AI. I run 100% locally on your machine with custom in-house models.",
    ],
    Intent.ASK_TIME: [
        "The current time is {current_time}.",
        "Right now it's {current_time}.",
    ],
    Intent.ASK_DATE: [
        "Today is {current_date}.",
        "It's {current_date}.",
    ],
    Intent.ASK_CAPABILITIES: [
        "I can help you manage tasks, set reminders, plan your daily schedule, remember personal preferences, track people and notes, monitor mood, and safely execute computer actions—all 100% private and local.",
        "Here is what I do: Task & reminder tracking, calendar daily planning, local memory storage, emotional awareness, computer tool actions (with permission safeguards), and private conversational companionship.",
    ],
    Intent.ASK_FOR_ADVICE: [
        "I recommend breaking the problem down into small, concrete steps. Focus on the most urgent priority first, take a short breather, and tackle each piece systematically.",
        "A good approach is to list your options, evaluate the immediate trade-offs, and start with the simplest action that produces real progress.",
    ],
    Intent.USER_HAPPY: [
        "That is wonderful to hear! I'm glad things are going well for you.",
        "Great news! Celebrating positive moments is important. What made your day so good?",
    ],
    Intent.USER_SAD: [
        "I'm sorry you're feeling down today. Remember to take it easy on yourself. I'm here if you'd like to talk or organize your thoughts.",
        "That sounds tough. Take a deep breath and give yourself some space. I'm here to support you in whatever small way I can.",
    ],
    Intent.USER_ANGRY: [
        "I hear you. Frustration can be overwhelming. Taking a brief walk or stepping away for a few minutes can sometimes help clear your head.",
        "That sounds really irritating. It's completely valid to feel angry—take your time before responding or making big decisions.",
    ],
    Intent.USER_STRESSED: [
        "You seem under a lot of pressure right now. Let's look at your tasks and prioritize only what is essential today. Everything else can wait.",
        "Deep breath. When overwhelmed, focus on just one single task for the next 25 minutes. Would you like me to help schedule a break?",
    ],
    Intent.USER_TIRED: [
        "You sound exhausted. Make sure you drink some water and rest when you can. Productivity is nothing without recovery.",
        "Rest is essential. If possible, consider wrapping up for the day or taking a power nap.",
    ],
    Intent.USER_EXCITED: [
        "That's so exciting! Channeling that energy into your projects can lead to great things.",
        "I love the enthusiasm! Let's make the most of this momentum.",
    ],
    Intent.UNKNOWN: [
        "I'm listening, but I didn't quite catch that. You can ask me about tasks, reminders, schedules, memories, or tell me how you're feeling.",
        "I'm not sure how to respond to that yet. Could you rephrase, or ask me to check your tasks, schedule, or memory?",
    ]
}

class ResponseEngine:
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)

    def render(self, intent: Intent, slots: Optional[Dict[str, Any]] = None) -> str:
        templates = TEMPLATES.get(intent, TEMPLATES[Intent.UNKNOWN])
        chosen = self.rng.choice(templates)
        
        # Standard system slots
        now = datetime.now()
        data = {
            "current_time": now.strftime("%I:%M %p"),
            "current_date": now.strftime("%A, %B %d, %Y"),
        }
        if slots:
            data.update(slots)
            
        try:
            return chosen.format(**data)
        except KeyError:
            return chosen
