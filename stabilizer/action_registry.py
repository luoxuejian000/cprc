ACTION_KINDS = [
    "NO_OP",
    "DAMP_LOCAL",
    "REFRESH_ANCHOR",
    "REQUEST_CLARIFICATION",
    "CHECKPOINT_SNAPSHOT",
]

class ActionRegistry:
    def __init__(self):
        self.actions = {}

    def register(self, name: str, handler):
        self.actions[name] = handler

    def get(self, name: str):
        return self.actions.get(name)