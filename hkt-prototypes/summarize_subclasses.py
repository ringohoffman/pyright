from pathlib import Path

content_file = Path("/Users/ringo/Library/Application Support/Code/User/workspaceStorage/edc72902a191183b3c13fe882fde4645/GitHub.copilot-chat/chat-session-resources/152073ee-cab9-4ee6-97fd-c7d8113aa9ef/call_MHwzY2U2Q2tpNk9GelNzanJicjc__vscode-1790578408954/content.txt")
lines = content_file.read_text().splitlines()

for line in lines:
    if line.startswith("Subclasses of "):
        print("\n" + line)
    elif line.startswith("  "):
        parts = line.strip().split(" -> ")
        loc = parts[0]
        cname = parts[1].split(" (")[0]
        has_fromkeys = "'fromkeys'" in line
        has_or = "'__or__'" in line
        notes = []
        if has_fromkeys:
            notes.append("overrides fromkeys")
        if has_or:
            notes.append("overrides __or__")
        note_str = f" [{', '.join(notes)}]" if notes else ""
        print(f"  {cname:28s} | {loc:35s}{note_str}")
