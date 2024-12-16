import asyncio
import aiofiles
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Tuple, Dict, Set
from rich.console import Console
from rich.table import Table
from rich.progress import track
from config import Config


class LangAnalyzer:

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.config.dump_dir.mkdir(parents=True, exist_ok=True)
        self.config.log_dir.mkdir(parents=True, exist_ok=True)

    async def read_file(self, file_path: Path) -> Set[str]:

        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return {line.strip() for line in await f.readlines()}
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
            return set()
        except Exception as e:
            print(f"Error reading file: {file_path}: {e}")
            return set()

    def _process_lines(self, lines: Set[str]) -> Dict:

        prefix_counts = defaultdict(int)
        empty_value_count = 0
        unique_prefixes = set()
        item_values: List[str] = []
        total_length = sum(len(line) for line in lines)

        for line in lines:
            parts = line.split('.', 1)
            if len(parts) > 1:
                prefix, value = parts
                prefix_counts[prefix] += 1
                unique_prefixes.add(prefix)
                value_parts = value.split('=', 1)
                if len(value_parts) > 1 and not value_parts[1].strip():
                    empty_value_count += 1
                if line.startswith("item."):
                    try:
                        item_values.append(value_parts[1].strip())
                    except IndexError:
                        pass

        prefix_counts = dict(sorted(prefix_counts.items(), key=lambda item: item[1], reverse=True))
        max_prefix_len = max(len(prefix) for prefix in prefix_counts) if prefix_counts else 0

        return {
            "prefix_counts": prefix_counts,
            "empty_value_count": empty_value_count,
            "total_length": total_length,
            "unique_prefixes": len(unique_prefixes),
            "item_values": item_values,
            "max_prefix_len": max_prefix_len,
            "new_lines_count": len(lines),
        }

    async def analyze_file(self, new_file_path: Path):
        old_file_path = await find_latest_file(self.config.dump_dir, "ru_lang_*.txt")
        old_lines = await self.read_file(old_file_path) if old_file_path else set()
        new_lines = await self.read_file(new_file_path)

        analysis_results = self._process_lines(new_lines - old_lines)
        await self._write_logs(analysis_results, new_lines, new_file_path, old_file_path)

    async def _write_logs(self, analysis_results: Dict, new_lines: Set[str], new_file_path: Path, old_file_path: Path):
        console = Console()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = self.config.log_dir / f"log_{timestamp}.txt"
        dump_file_path = self.config.dump_dir / f"ru_lang_{timestamp}.txt"

        log_data = self._format_log_data(analysis_results, new_lines, new_file_path, old_file_path)
        total_lines = len(log_data) + len(new_lines)

        with console.status("[bold green]Writing to files...") as status:
            async with aiofiles.open(log_file_path, 'w', encoding='utf-8') as log, \
                    aiofiles.open(dump_file_path, 'w', encoding='utf-8') as dump:
                
                async def write_file(file, lines):
                    for line in lines:
                        await file.write(line + '\n')

                await asyncio.gather(write_file(log, log_data), write_file(dump, new_lines))
            console.log("Files written successfully!")


    def _format_log_data(self, analysis_results: Dict, new_lines: Set[str], new_file_path: Path, old_file_path: Path) -> List[str]:
        log_data = [
            f"Analysis time: {datetime.now().isoformat()}",
            f"New file: {new_file_path}",
            f"Comparison file: {old_file_path or 'Not found'}",
            f"Total number of new lines: {analysis_results['new_lines_count']}",
            f"Number of lines with empty values: {analysis_results['empty_value_count']}",
            f"Total length of new lines: {analysis_results['total_length']}",
            f"Number of unique prefixes: {analysis_results['unique_prefixes']}",
            "\nPrefix statistics:",
        ]
        log_data.extend([f"{prefix: <{analysis_results['max_prefix_len']}}: {count}" for prefix, count in analysis_results['prefix_counts'].items()])
        log_data.extend(["\nNew lines:", ""])
        log_data.extend(new_lines)
        return log_data

    def _display_summary(self, analysis_results: Dict, log_file_path: Path, dump_file_path: Path, console: Console, new_file_path:Path, old_file_path:Path):
        """Displays a summary of the analysis using rich."""
        table = Table(title="Analysis Summary")
        table.add_column("Metric", style="bold cyan")
        table.add_column("Value")

        table.add_row("Analysis Time", datetime.now().isoformat())
        table.add_row("New File", str(new_file_path))
        table.add_row("Comparison File", str(old_file_path) or "Not found")
        table.add_row("New Lines", str(analysis_results["new_lines_count"]))
        table.add_row("Empty Values", str(analysis_results["empty_value_count"]))
        table.add_row("Total Length", str(analysis_results["total_length"]))
        table.add_row("Unique Prefixes", str(analysis_results["unique_prefixes"]))

        console.print(table)

        prefix_table = Table(title="Prefix Statistics")
        prefix_table.add_column("Prefix", style="bold magenta")
        prefix_table.add_column("Count")
        for prefix, count in analysis_results["prefix_counts"].items():
            prefix_table.add_row(prefix, str(count))
        console.print(prefix_table)

        console.print(f"\nLog written to: [link file://{log_file_path}]{log_file_path}[/link]")
        console.print(f"Dump file created: [link file://{dump_file_path}]{dump_file_path}[/link]")


async def find_latest_file(directory: Path, pattern: str) -> Path:
    """Finds the latest file matching the pattern in the given directory."""
    files = list(directory.glob(pattern))
    if files:
        return max(files, key=lambda p: p.stat().st_mtime)
    return None


async def main():   
    ru_lang_path = 'C:\\sc\\EXBO\\runtime\\stalcraft\\modassets\\assets\\stalker\\lang\\ru.lang' #change if need
    if ru_lang_path:
        analyzer = LangAnalyzer()
        await analyzer.analyze_file(ru_lang_path)
    else:
        print("Error: ru.lang file not found.")


if __name__ == "__main__":
    asyncio.run(main())
