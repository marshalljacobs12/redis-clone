# persistence/aof_replayer.py

async def replay_aof(filepath: str, command_handler):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return

    i = 0
    while i < len(lines):
        if not lines[i].startswith("*"):
            i += 1
            continue
        argc = int(lines[i][1:])
        i += 1
        tokens = []
        for _ in range(argc):
            i += 1  # skip $<len>
            tokens.append(lines[i].strip())
            i += 1
        await command_handler.handle(tokens)
