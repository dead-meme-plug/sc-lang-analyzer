from pathlib import Path

class Config:
    def __init__(self, dump_dir="dumps", log_dir="logs"):
        self.dump_dir = Path(dump_dir)
        self.log_dir = Path(log_dir)
