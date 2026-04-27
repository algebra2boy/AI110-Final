"""
Safety guardrails: detect crisis language and block misuse.
"""

from utils.logger import log_guardrail_trigger

CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "end my life",
    "want to die",
    "self-harm",
    "self harm",
    "cutting myself",
    "overdose",
    "hurt myself",
    "not worth living",
]

CRISIS_RESPONSE = """
I noticed some of what you wrote might be expressing really serious pain.
MoodArc is a music tool, not a mental health service.

If you're in crisis, please reach out:
• **988 Suicide & Crisis Lifeline**: call or text **988** (US)
• **Crisis Text Line**: text HOME to **741741**
• **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/

You deserve real support from real people. 💙
""".strip()

ABUSE_PATTERNS = [
    "ignore previous",
    "ignore all instructions",
    "you are now",
    "act as",
    "jailbreak",
    "forget your instructions",
]


class GuardrailResult:
    def __init__(self, blocked: bool, reason: str, message: str = ""):
        self.blocked = blocked
        self.reason = reason
        self.message = message


def check_input(user_input: str) -> GuardrailResult:
    """
    Check user input against crisis and prompt-injection patterns.
    Returns GuardrailResult with blocked=True if input should be halted.
    """
    lowered = user_input.lower()

    for keyword in CRISIS_KEYWORDS:
        if keyword in lowered:
            log_guardrail_trigger(keyword, user_input)
            return GuardrailResult(
                blocked=True,
                reason="crisis_language",
                message=CRISIS_RESPONSE,
            )

    for pattern in ABUSE_PATTERNS:
        if pattern in lowered:
            log_guardrail_trigger(pattern, user_input)
            return GuardrailResult(
                blocked=True,
                reason="prompt_injection",
                message="That input pattern isn't supported. Please describe your emotional state or mood.",
            )

    if len(user_input.strip()) < 3:
        return GuardrailResult(
            blocked=True,
            reason="too_short",
            message="Please describe how you're feeling in a few words so MoodArc can help.",
        )

    if len(user_input) > 2000:
        return GuardrailResult(
            blocked=True,
            reason="too_long",
            message="Please keep your description under 2000 characters.",
        )

    return GuardrailResult(blocked=False, reason="ok")
