from typing import List, Optional, Dict, Tuple
from Controller.models import (Process,
                               Segment,
                               Hole,
                               AllocatedBlock)


class MemoryManager:
    def __init__(self, total_size: int):
        self.total_size = total_size
        self.holes: List[Hole] = []
        self.allocated: List[AllocatedBlock] = []
        self.processes: Dict[str, Process] = {}
        self.history: List[str] = []
        self.allocation_method = "first_fit"

    def add_hole(self, start: int, size: int):
        if start < 0 or start + size > self.total_size:
            raise ValueError("Hole out of memory bounds")
        self.holes.append(Hole(start, size))
        self._sort_holes()

    def set_allocation_method(self, method: str):
        method = method.lower().replace("-", "_").replace(" ", "_")
        if method in ("first_fit", "best_fit"):
            self.allocation_method = method
        else:
            raise ValueError("Method must be first_fit or best_fit")

    def _sort_holes(self):
        self.holes.sort(key=lambda h: h.start)

    def _find_hole(self, holes: List[Hole], size: int) -> Optional[int]:
        if self.allocation_method == "first_fit":
            for i, hole in enumerate(holes):
                if hole.size >= size:
                    return i
            return None
        else:  # best_fit
            best_idx = None
            best_size = float('inf')
            for i, hole in enumerate(holes):
                if hole.size >= size and hole.size < best_size:
                    best_size = hole.size
                    best_idx = i
            return best_idx

    def allocate_process(self, process: Process) -> bool:
        if process.name in self.processes and self.processes[process.name].is_allocated:
            self.history.append(f"Process {process.name} is already allocated.")
            return False

        # Simulation: check if all segments can fit before committing
        temp_holes = [Hole(h.start, h.size) for h in self.holes]
        planned: List[Tuple[int, int, Segment]] = []  # (start, size, segment)

        for seg in process.segments:
            idx = self._find_hole(temp_holes, seg.size)
            if idx is None:
                self.history.append(
                    f"Process {process.name} does not fit "
                    f"(segment '{seg.name}' of size {seg.size}K cannot be allocated)."
                )
                return False

            hole = temp_holes[idx]
            planned.append((hole.start, seg.size, seg))

            # Update temp hole
            if hole.size == seg.size:
                temp_holes.pop(idx)
            else:
                hole.start += seg.size
                hole.size -= seg.size
                # Keep sorted by start address for correct first-fit behavior
                temp_holes.sort(key=lambda h: h.start)

        # Commit allocations
        for start, size, seg in planned:
            seg.base = start
            self.allocated.append(
                AllocatedBlock(start, size, process.name, seg.name)
            )
            self._consume_hole(start, size)

        process.is_allocated = True
        self.processes[process.name] = process
        self.history.append(
            f"Allocated process {process.name}: " + ", ".join(
                f"{s.name}={s.size}K@{s.base}" for s in process.segments
            )
        )
        return True

    def _consume_hole(self, start: int, size: int):
        for i, hole in enumerate(self.holes):
            if hole.start == start and hole.size >= size:
                if hole.size == size:
                    self.holes.pop(i)
                else:
                    hole.start += size
                    hole.size -= size
                self._sort_holes()
                return
        # Defensive fallback: find any hole containing this start
        for i, hole in enumerate(self.holes):
            if hole.start <= start < hole.end and hole.end >= start + size:
                before_size = start - hole.start
                after_size = hole.end - (start + size)
                self.holes.pop(i)
                if before_size > 0:
                    self.holes.append(Hole(hole.start, before_size))
                if after_size > 0:
                    self.holes.append(Hole(start + size, after_size))
                self._sort_holes()
                return

    def deallocate_process(self, process_name: str) -> bool:
        if process_name not in self.processes:
            self.history.append(f"Process {process_name} does not exist.")
            return False

        process = self.processes[process_name]
        if not process.is_allocated:
            self.history.append(f"Process {process_name} is not allocated.")
            return False

        to_remove = [a for a in self.allocated if a.process_name == process_name]
        for alloc in to_remove:
            self.allocated.remove(alloc)
            self.holes.append(Hole(alloc.start, alloc.size))
            # Reset segment base
            for seg in process.segments:
                if seg.name == alloc.segment_name:
                    seg.base = -1

        self._merge_holes()
        process.is_allocated = False
        self.history.append(f"Deallocated process {process_name}.")
        return True

    def _merge_holes(self):
        if not self.holes:
            return
        self._sort_holes()
        merged = [self.holes[0]]
        for hole in self.holes[1:]:
            last = merged[-1]
            if last.end == hole.start:
                last.size += hole.size
            else:
                merged.append(hole)
        self.holes = merged

    def get_memory_layout(self) -> List[dict]:
        blocks = []
        for hole in self.holes:
            blocks.append({
                'start': hole.start,
                'size': hole.size,
                'type': 'hole',
                'label': f'Hole\n{hole.start} – {hole.end - 1}',
                'process': '',
                'segment': ''
            })
        for alloc in self.allocated:
            blocks.append({
                'start': alloc.start,
                'size': alloc.size,
                'type': 'allocated',
                'label': f'{alloc.process_name}:{alloc.segment_name}\n{alloc.start} – {alloc.end - 1}',
                'process': alloc.process_name,
                'segment': alloc.segment_name
            })
        blocks.sort(key=lambda b: b['start'])
        return blocks

    def get_segment_table(self, process_name: str) -> Optional[List[dict]]:
        if process_name not in self.processes:
            return None
        process = self.processes[process_name]
        if not process.is_allocated:
            return None
        return [
            {
                'segment': seg.name,
                'limit': seg.size,
                'base': seg.base
            }
            for seg in process.segments
        ]

    def get_processes_summary(self) -> List[dict]:
        result = []
        for name, proc in self.processes.items():
            result.append({
                'name': name,
                'allocated': proc.is_allocated,
                'segments': len(proc.segments)
            })
        return result
