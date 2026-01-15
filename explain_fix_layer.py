# Explain/Fix Layer (optional)
def explain_signals(signals):
    return [{"signal": s.id, "reason": "Demo reason for " + s.id} for s in signals]

def fix_signals(signals):
    return [{"signal": s.id, "advice": "Demo advice for " + s.id} for s in signals]
