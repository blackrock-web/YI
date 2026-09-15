"""
MY AI - Intent Definition & Deterministic Intent Matcher
Defines standard intents, keyword matchers, regex patterns, and extensible registry.
"""
from enum import Enum
import re
from typing import List, Dict, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from app.brain.parser import TextParser

class Intent(str, Enum):
    # Conversational & System
    GREETING = "GREETING"
    GOODBYE = "GOODBYE"
    ASK_NAME = "ASK_NAME"
    ASK_TIME = "ASK_TIME"
    ASK_DATE = "ASK_DATE"
    ASK_CAPABILITIES = "ASK_CAPABILITIES"
    
    # Task Management
    CREATE_TASK = "CREATE_TASK"
    DELETE_TASK = "DELETE_TASK"
    COMPLETE_TASK = "COMPLETE_TASK"
    SHOW_TASKS = "SHOW_TASKS"
    
    # Reminder Management
    CREATE_REMINDER = "CREATE_REMINDER"
    SHOW_REMINDERS = "SHOW_REMINDERS"
    DELETE_REMINDER = "DELETE_REMINDER"
    
    # Calendar & Planning
    CREATE_EVENT = "CREATE_EVENT"
    SHOW_SCHEDULE = "SHOW_SCHEDULE"
    
    # Memory
    REMEMBER = "REMEMBER"
    FORGET = "FORGET"
    SEARCH_MEMORY = "SEARCH_MEMORY"
    
    # Conversational & Advice
    ASK_FOR_ADVICE = "ASK_FOR_ADVICE"
    
    # User Emotional States
    USER_HAPPY = "USER_HAPPY"
    USER_SAD = "USER_SAD"
    USER_ANGRY = "USER_ANGRY"
    USER_STRESSED = "USER_STRESSED"
    USER_TIRED = "USER_TIRED"
    USER_EXCITED = "USER_EXCITED"
    
    # System Actions
    OPEN_APPLICATION = "OPEN_APPLICATION"
    CLOSE_APPLICATION = "CLOSE_APPLICATION"
    
    UNKNOWN = "UNKNOWN"

@dataclass
class IntentMatchResult:
    intent: Intent
    confidence: float
    matched_pattern: Optional[str] = None
    extracted_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntentRule:
    intent: Intent
    patterns: List[str]
    keywords: List[str]
    priority: int = 10
    param_extractor: Optional[Callable[[str, re.Match], Dict[str, Any]]] = None

class IntentRegistry:
    def __init__(self):
        self.rules: List[IntentRule] = []
        self._register_default_rules()

    def register(self, rule: IntentRule) -> None:
        """Register a new custom or extended intent rule."""
        self.rules.append(rule)
        # Sort rules by priority descending
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def _register_default_rules(self) -> None:
        # 1. GREETING
        self.register(IntentRule(
            intent=Intent.GREETING,
            patterns=[
                r"^(hello|hi|hey|greetings|good morning|good afternoon|good evening|howdy)( there| assistant| my ai)?([!?. ]*)$",
                r"^what is up\??$",
                r"^how are you( doing)?\??$",
            ],
            keywords=["hello", "hi", "hey", "greetings", "howdy"],
            priority=20
        ))

        # 2. GOODBYE
        self.register(IntentRule(
            intent=Intent.GOODBYE,
            patterns=[
                r"^(bye|goodbye|see you|see ya|farewell|talk to you later|have a good day|good night)([!. ]*)$",
                r"^catch you later\??$",
            ],
            keywords=["bye", "goodbye", "farewell", "cya"],
            priority=20
        ))

        # 3. ASK_NAME
        self.register(IntentRule(
            intent=Intent.ASK_NAME,
            patterns=[
                r"what is your name\??",
                r"who are you\??",
                r"what should i call you\??",
                r"do you have a name\??",
            ],
            keywords=["your name", "who are you"],
            priority=25
        ))

        # 4. ASK_TIME
        self.register(IntentRule(
            intent=Intent.ASK_TIME,
            patterns=[
                r"what time is it\??",
                r"what is the time\??",
                r"tell me the time\??",
                r"current time\??",
            ],
            keywords=["what time", "current time"],
            priority=25
        ))

        # 5. ASK_DATE
        self.register(IntentRule(
            intent=Intent.ASK_DATE,
            patterns=[
                r"what is (today's|the) date\??",
                r"what day is (it|today)\??",
                r"tell me today's date\??",
                r"what is the day today\??",
            ],
            keywords=["what date", "today's date", "what day is today"],
            priority=25
        ))

        # 6. ASK_CAPABILITIES
        self.register(IntentRule(
            intent=Intent.ASK_CAPABILITIES,
            patterns=[
                r"what can you do\??",
                r"what are your capabilities\??",
                r"how can you help( me)?\??",
                r"list your features\??",
                r"what do you do\??",
            ],
            keywords=["what can you do", "capabilities", "features", "how can you help"],
            priority=25
        ))

        # 7. REMEMBER (Priority high for preferences & facts)
        def extract_memory_params(text: str, match: re.Match) -> Dict[str, Any]:
            groups = match.groupdict()
            return {
                "key": groups.get("key", "").strip(),
                "value": groups.get("value", "").strip(),
                "raw_statement": text
            }

        self.register(IntentRule(
            intent=Intent.REMEMBER,
            patterns=[
                r"my (?P<key>[a-zA-Z0-9_\s]+?) is (?P<value>[a-zA-Z0-9_\s,.'\"-]+)$",
                r"remember that (?P<key>[a-zA-Z0-9_\s]+?) is (?P<value>[a-zA-Z0-9_\s,.'\"-]+)$",
                r"remember:? (?P<key>[a-zA-Z0-9_\s]+?) is (?P<value>[a-zA-Z0-9_\s,.'\"-]+)$",
                r"remember:? (?P<value>[a-zA-Z0-9_\s,.'\"-]+)$",
                r"i like (?P<value>[a-zA-Z0-9_\s,.'\"-]+)$",
                r"i love (?P<value>[a-zA-Z0-9_\s,.'\"-]+)$",
                r"i prefer (?P<value>[a-zA-Z0-9_\s,.'\"-]+)$",
            ],
            keywords=["remember", "my favorite", "my preferred"],
            priority=30,
            param_extractor=extract_memory_params
        ))

        # 8. SEARCH_MEMORY
        def extract_search_memory_params(text: str, match: re.Match) -> Dict[str, Any]:
            groups = match.groupdict()
            return {"query": groups.get("query", "").strip(), "raw_statement": text}

        self.register(IntentRule(
            intent=Intent.SEARCH_MEMORY,
            patterns=[
                r"what is my (?P<query>[a-zA-Z0-9_\s]+)\??$",
                r"what are my (?P<query>[a-zA-Z0-9_\s]+)\??$",
                r"do you remember my (?P<query>[a-zA-Z0-9_\s]+)\??$",
                r"what do you remember about (?P<query>[a-zA-Z0-9_\s]+)\??$",
                r"recall (?P<query>[a-zA-Z0-9_\s]+)\??$",
                r"what did i say about (?P<query>[a-zA-Z0-9_\s]+)\??$",
            ],
            keywords=["what is my", "do you remember", "what did i say"],
            priority=30,
            param_extractor=extract_search_memory_params
        ))

        # 9. FORGET
        self.register(IntentRule(
            intent=Intent.FORGET,
            patterns=[
                r"forget (?P<query>[a-zA-Z0-9_\s]+)$",
                r"delete memory (about|of) (?P<query>[a-zA-Z0-9_\s]+)$",
                r"remove memory (?P<query>[a-zA-Z0-9_\s]+)$",
            ],
            keywords=["forget", "delete memory"],
            priority=30
        ))

        # 10. CREATE_TASK
        def extract_task_params(text: str, match: re.Match) -> Dict[str, Any]:
            groups = match.groupdict()
            title = groups.get("task", "").strip() or groups.get("title", "").strip()
            # clean leading "to " if present
            if title.lower().startswith("to "):
                title = title[3:].strip()
            return {"title": title, "raw": text}

        self.register(IntentRule(
            intent=Intent.CREATE_TASK,
            patterns=[
                r"(create|add|new) task:? (?P<task>.+)$",
                r"add a task (to )?:? ?(?P<task>.+)$",
                r"i need to (?P<task>.+)$",
                r"todo:? (?P<task>.+)$",
            ],
            keywords=["create task", "add task", "new task", "add a task", "todo"],
            priority=25,
            param_extractor=extract_task_params
        ))

        # 11. SHOW_TASKS
        self.register(IntentRule(
            intent=Intent.SHOW_TASKS,
            patterns=[
                r"(show|list|get|view|what are) (my )?tasks\??$",
                r"what do i have to do\??$",
                r"show todo list\??$",
            ],
            keywords=["show tasks", "list tasks", "my tasks", "todo list"],
            priority=25
        ))

        # 12. COMPLETE_TASK
        self.register(IntentRule(
            intent=Intent.COMPLETE_TASK,
            patterns=[
                r"(complete|finish|done|check off) task (?P<task_id_or_title>.+)$",
                r"mark task (?P<task_id_or_title>.+) as (done|complete)$",
            ],
            keywords=["complete task", "finish task", "task done"],
            priority=26
        ))

        # 13. DELETE_TASK
        self.register(IntentRule(
            intent=Intent.DELETE_TASK,
            patterns=[
                r"(delete|remove) task (?P<task_id_or_title>.+)$",
            ],
            keywords=["delete task", "remove task"],
            priority=26
        ))

        # 14. CREATE_REMINDER
        def extract_reminder_params(text: str, match: re.Match) -> Dict[str, Any]:
            groups = match.groupdict()
            msg = groups.get("reminder", "").strip()
            if msg.lower().startswith("to "):
                msg = msg[3:].strip()
            return {"message": msg, "time": groups.get("time", "").strip()}

        self.register(IntentRule(
            intent=Intent.CREATE_REMINDER,
            patterns=[
                r"remind me to (?P<reminder>.+?) (at|in|on|tomorrow) (?P<time>.+)$",
                r"remind me to (?P<reminder>.+)$",
                r"(create|set|add) (a )?reminder:? (?P<reminder>.+)$",
            ],
            keywords=["remind me", "set reminder", "create reminder"],
            priority=27,
            param_extractor=extract_reminder_params
        ))

        # 15. SHOW_REMINDERS
        self.register(IntentRule(
            intent=Intent.SHOW_REMINDERS,
            patterns=[
                r"(show|list|get|what are) (my )?reminders\??$",
            ],
            keywords=["show reminders", "my reminders", "list reminders"],
            priority=25
        ))

        # 16. DELETE_REMINDER
        self.register(IntentRule(
            intent=Intent.DELETE_REMINDER,
            patterns=[
                r"(delete|remove|cancel) reminder (?P<id_or_title>.+)$",
            ],
            keywords=["delete reminder", "cancel reminder"],
            priority=26
        ))

        # 17. CREATE_EVENT / SHOW_SCHEDULE
        self.register(IntentRule(
            intent=Intent.SHOW_SCHEDULE,
            patterns=[
                r"(plan|schedule|show|what is) (my )?(day|schedule|calendar)\??$",
                r"what is on my schedule today\??$",
                r"plan my day\??$",
            ],
            keywords=["plan my day", "my schedule", "show schedule", "daily plan"],
            priority=25
        ))

        self.register(IntentRule(
            intent=Intent.CREATE_EVENT,
            patterns=[
                r"(add|schedule|create) event:? (?P<title>.+?) (at|on) (?P<time>.+)$",
                r"meeting (?P<title>.+?) at (?P<time>.+)$",
            ],
            keywords=["add event", "schedule event", "create event"],
            priority=25
        ))

        # 18. ASK_FOR_ADVICE
        self.register(IntentRule(
            intent=Intent.ASK_FOR_ADVICE,
            patterns=[
                r"what should i do( about .+)?\??$",
                r"can you give me (some )?advice\??$",
                r"i need advice( on .+)?\??$",
                r"how should i handle .+\??$",
            ],
            keywords=["advice", "what should i do", "how should i handle"],
            priority=20
        ))

        # 19. EMOTIONS
        self.register(IntentRule(
            intent=Intent.USER_HAPPY,
            patterns=[
                r"i (am|feel) (feeling )?(so |very )?(happy|glad|delighted|joyful)( today)?([!.]*)$",
                r"today is a great day([!.]*)$",
                r"i got good news([!.]*)$",
            ],
            keywords=["happy", "glad", "joyful", "great day", "feel happy", "so happy"],
            priority=22
        ))

        self.register(IntentRule(
            intent=Intent.USER_SAD,
            patterns=[
                r"i (am|feel) (feeling )?(so |very )?(sad|down|depressed|heartbroken|unhappy)([!. ]*)$",
                r"i feel down([!. ]*)$",
                r"today was terrible([!. ]*)$",
            ],
            keywords=["sad", "depressed", "unhappy", "feel down", "feel sad"],
            priority=22
        ))

        self.register(IntentRule(
            intent=Intent.USER_ANGRY,
            patterns=[
                r"i am (feeling )?(so )?(angry|furious|mad|pissed off)([!. ]*)$",
                r"this makes me angry([!. ]*)$",
            ],
            keywords=["angry", "furious", "mad"],
            priority=18
        ))

        self.register(IntentRule(
            intent=Intent.USER_STRESSED,
            patterns=[
                r"i am (so )?(stressed|overwhelmed|anxious|under pressure)([!. ]*)$",
                r"i have too much work([!. ]*)$",
            ],
            keywords=["stressed", "overwhelmed", "anxious"],
            priority=18
        ))

        self.register(IntentRule(
            intent=Intent.USER_TIRED,
            patterns=[
                r"i am (so )?(tired|exhausted|sleepy|drained)([!. ]*)$",
                r"i need some rest([!. ]*)$",
            ],
            keywords=["tired", "exhausted", "sleepy", "drained"],
            priority=18
        ))

        self.register(IntentRule(
            intent=Intent.USER_EXCITED,
            patterns=[
                r"i am (so )?(excited|thrilled|hyped|pumped)([!. ]*)$",
                r"i can't wait([!. ]*)$",
                r"i cannot wait([!. ]*)$",
            ],
            keywords=["excited", "thrilled", "hyped"],
            priority=18
        ))

        # 20. COMPUTER ACTIONS (OPEN_APPLICATION, CLOSE_APPLICATION)
        self.register(IntentRule(
            intent=Intent.OPEN_APPLICATION,
            patterns=[
                r"open (application|app)? ?(?P<app_name>[a-zA-Z0-9_\- ]+)$",
                r"launch (?P<app_name>[a-zA-Z0-9_\- ]+)$",
                r"start (?P<app_name>[a-zA-Z0-9_\- ]+)$",
            ],
            keywords=["open application", "launch", "open app"],
            priority=25,
            param_extractor=lambda t, m: {"app_name": m.groupdict().get("app_name", "").strip()}
        ))

        self.register(IntentRule(
            intent=Intent.CLOSE_APPLICATION,
            patterns=[
                r"close (application|app)? ?(?P<app_name>[a-zA-Z0-9_\- ]+)$",
                r"quit (?P<app_name>[a-zA-Z0-9_\- ]+)$",
                r"kill (?P<app_name>[a-zA-Z0-9_\- ]+)$",
            ],
            keywords=["close application", "quit", "close app"],
            priority=25,
            param_extractor=lambda t, m: {"app_name": m.groupdict().get("app_name", "").strip()}
        ))

    def match(self, raw_text: str) -> IntentMatchResult:
        normalized = TextParser.normalize(raw_text)
        
        # 1. Regex Pattern Matching on both raw text and normalized text
        for rule in self.rules:
            for pattern_str in rule.patterns:
                regex = re.compile(pattern_str, re.IGNORECASE)
                # First try raw_text to preserve original capitalization of extracted items
                match = regex.search(raw_text)
                target_text = raw_text
                if not match:
                    # Fallback to normalized text
                    match = regex.search(normalized)
                    target_text = normalized
                    
                if match:
                    params = {}
                    if rule.param_extractor:
                        try:
                            params = rule.param_extractor(target_text, match)
                        except Exception:
                            params = match.groupdict()
                    else:
                        params = match.groupdict()
                    return IntentMatchResult(
                        intent=rule.intent,
                        confidence=0.95,
                        matched_pattern=pattern_str,
                        extracted_params=params
                    )

        # 2. Keyword Fallback Matching
        best_match: Optional[IntentRule] = None
        highest_score = 0
        tokens = set(normalized.split())
        STOP_WORDS = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "my", "your", "is", "it", "i", "me"}
        
        for rule in self.rules:
            score = 0
            for kw in rule.keywords:
                kw_norm = TextParser.normalize(kw)
                if kw_norm in normalized:
                    score += len(kw_norm.split()) * 2
                else:
                    meaningful_kw_tokens = [t for t in kw_norm.split() if t not in STOP_WORDS]
                    if meaningful_kw_tokens and any(tok in tokens for tok in meaningful_kw_tokens):
                        score += 1
            if score > highest_score:
                highest_score = score
                best_match = rule

        if best_match and highest_score >= 2:
            return IntentMatchResult(
                intent=best_match.intent,
                confidence=min(0.85, 0.5 + (highest_score * 0.1)),
                matched_pattern="keyword_match"
            )

        return IntentMatchResult(intent=Intent.UNKNOWN, confidence=0.2)
