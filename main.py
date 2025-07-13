from typing import Literal, Tuple, List, Dict, cast, Optional, Type
from dataclasses import dataclass
from types import TracebackType
import json

DAY = Literal["SAT", "SUN"]
POS = Literal["E", "W"]
TicketTuple = Tuple[int, int, int, int]

DAY_POS: List[Tuple[DAY, POS]] = [
    ("SAT", "E"),
    ("SAT", "W"),
    ("SUN", "E"),
    ("SUN", "W"),
]
DAYS = ["SAT", "SUN"]
POSS = ["E", "W"]

class PrettyPrinter:
    def __init__(self, indent_lvl: int=0, indentation: str="  "):
        self.indent_lvl = indent_lvl
        self.indentation = indentation

    def print(self, *msg: str, end: str="\n"):
        indent = self.indentation * self.indent_lvl
        print(indent, end="")
        print(*msg, end=end)

    def __enter__(self) -> "PrettyPrinter":
        self.indent_lvl += 1
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> Optional[bool]:
        self.indent_lvl -= 1
        return None

@dataclass
class Ticket:
    applied_by: str
    applied_for: str
    day: DAY
    pos: POS

    def __str__(self) -> str:
        if self.applied_by == self.applied_for:
            return f"[{self.applied_by}]"
        else:
            return f"[{self.applied_by} -> {self.applied_for}]"

    def to_string(self) -> str:
        daypos = f"{"1일차" if self.day == "SAT" else "2일차"} {"동관" if self.pos == "E" else "서관"}"
        return f"{daypos} {str(self)}"

@dataclass
class Human:
    name: str
    need: Dict[DAY, POS]

    def get_pos_at(self, day: DAY) -> POS:
        return self.need[day]


def parse_num_tickets(num_tickets: List[str], allow_zero: bool) -> TicketTuple:
    assert len(num_tickets) == 4
    ticket_tuple = cast(TicketTuple, tuple(map(int, num_tickets)))

    e1, w1, e2, w2 = ticket_tuple
    assert e1 == 0 or w1 == 0
    assert e2 == 0 or w2 == 0

    if not allow_zero:
        assert not (e1 == 0 and w1 == 0)
        assert not (e2 == 0 and w2 == 0)

    return ticket_tuple


def parse_app() -> Dict[str, Human]:
    human_dict: Dict[str, Human] = {}
    with open("data/app.tsv", "rt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            [nm, *num_tickets, go1, go2] = line.split("\t")

            assert go1 in ("E", "W", "X") and go2 in ("E", "W", "X")
            e1, _, e2, _ = parse_num_tickets(num_tickets, False)

            needs: Dict[DAY, POS] = {}
            if go1 in ("E", "W"):
                igo1 = "W" if e1 == 0 else "E"
                if igo1 != go1:
                    print(f"E: {nm} applied for {igo1} but wants {go1} in saturday")
                needs["SAT"] = go1

            if go2 in ("E", "W"):
                igo2 = "W" if e2 == 0 else "E"
                if igo2 != go2:
                    print(f"E: {nm} applied for {igo2} but wants {go2} in sunday")
                needs["SUN"] = go2

            human_dict[nm] = Human(nm, needs)
    return human_dict


def parse_app2(human_dict: Dict[str, Human]):
    with open("data/app2.tsv", "rt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            [applied_by, applied_for, *num_tickets] = line.split("\t")

            e1, _, e2, _ = parse_num_tickets(num_tickets, False)
            igo1 = "W" if e1 == 0 else "E"
            igo2 = "W" if e2 == 0 else "E"

            go1 = human_dict[applied_for].need["SAT"]
            go2 = human_dict[applied_for].need["SUN"]

            if igo1 != go1:
                print(
                    f"E: {applied_for} received {igo1} by {applied_by} but wants {go1} in saturday"
                )
            if igo2 != go2:
                print(
                    f"E: {applied_for} received {igo2} by {applied_by} but wants {go2} in sunday"
                )


def parse_result(human_dict: Dict[str, Human]) -> List[Ticket]:
    tickets: List[Ticket] = []
    with open("data/result.tsv", "rt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue

            [applied_by, opt_applied_for, *num_tickets] = line.split("\t")
            ticket_tuple = parse_num_tickets(num_tickets, True)

            applied_for = opt_applied_for if len(opt_applied_for) > 0 else applied_by

            for i, (day, pos) in enumerate(DAY_POS):
                tickets.extend(
                    Ticket(applied_by, applied_for, day, pos)
                    for _ in range(ticket_tuple[i])
                )
    return tickets


class TicketPossession:
    def __init__(self, human_dict: Dict[str, Human], tickets: List[Ticket]):
        self.human_dict = human_dict.copy()
        self.tickets = tuple(tickets)

        self.tickets_left_ids: set[int] = set(range(len(tickets)))
        self.possession: Dict[str, List[int]] = {name: [] for name in human_dict}
        self.possessed_by: Dict[int, Optional[str]] = {
            i: None for i, _tkt in enumerate(tickets)
        }

    def take_ticket(self, name: str, tid: int):
        assert name in self.human_dict
        assert tid < len(self.tickets)

        assert tid not in self.possession[name], f"{tid} already in {name}"
        assert self.possessed_by[tid] is None

        assert tid in self.tickets_left_ids

        self.tickets_left_ids.remove(tid)
        self.possession[name].append(tid)
        self.possessed_by[tid] = name

    def find_ticket_one(
        self,
        cond_by: Optional[str] = None,
        cond_for: Optional[str] = None,
        cond_day: Optional[DAY] = None,
        cond_pos: Optional[POS] = None,
        include_possessed: bool = False,
    ) -> Optional[int]:
        search_scope = (
            range(len(self.tickets)) if include_possessed else self.tickets_left_ids
        )
        for tid in search_scope:
            ticket = self.tickets[tid]
            if all(
                (
                    (cond_by is None) or ticket.applied_by == cond_by,
                    (cond_for is None) or ticket.applied_for == cond_for,
                    (cond_day is None) or ticket.day == cond_day,
                    (cond_pos is None) or ticket.pos == cond_pos,
                )
            ):
                return tid
        return None

    def has_ticket(self, name: str, day: DAY, pos: POS) -> bool:
        for tid in self.possession[name]:
            ticket = self.tickets[tid]
            if ticket.day == day and ticket.pos == pos:
                return True
        return False

    def process_take_self(self):
        for name, human in self.human_dict.items():
            for day, pos in human.need.items():
                if self.has_ticket(name, day, pos):
                    continue
                else:
                    tid = self.find_ticket_one(name, name, day, pos)
                    if tid is None:
                        continue
                    print(f"{name} taken self {day} {pos}")
                    self.take_ticket(name, tid)
                    assert self.has_ticket(name, day, pos)

    def process_take_for_self(self):
        for name, human in self.human_dict.items():
            for day, pos in human.need.items():
                if self.has_ticket(name, day, pos):
                    continue
                else:
                    tid = self.find_ticket_one(None, name, day, pos)
                    if tid is None:
                        continue
                    self.take_ticket(name, tid)

    def pretty_print(self, label: str):
        pp = PrettyPrinter()
        print = pp.print
        print(f"----- {label} -----")
        for day, pos in DAY_POS:
            left_tickets: List[Ticket] = []
            for tid in self.tickets_left_ids:
                ticket = self.tickets[tid]
                if ticket.day == day and ticket.pos == pos:
                    left_tickets.append(ticket)

            need_tickets: List[str] = []
            for name, human in self.human_dict.items():
                for hday, hpos in human.need.items():
                    if day != hday or pos != hpos:
                        continue
                    if self.has_ticket(name, day, pos):
                        continue
                    need_tickets.append(name)

            acc = len(left_tickets) - len(need_tickets)
            print(f"{"1일차" if day == "SAT" else "2일차"} {"동관" if pos == "E" else "서관"}: {acc}")
            with pp:
                if len(left_tickets) > 0:
                    left_list = ", ".join(map(str, left_tickets))
                    print(f"잔여({len(left_tickets)}): {left_list}")

                if len(need_tickets) > 0:
                    need_list = ", ".join(need_tickets)
                    print(f"부족({len(need_tickets)}): {need_list}")

        print(f"----- {label} -----")

    def dump(self, path: str):
        pretty_data: Dict[str, List[str]] = {
            name: [
                self.tickets[tid].to_string()
                for tid in human
            ] for name, human in self.possession.items()
        }
        with open(path, "wt") as f:
            json.dump(pretty_data, f, ensure_ascii=False, indent=2)

def main():
    human_dict = parse_app()
    parse_app2(human_dict)
    tickets = parse_result(human_dict)

    possession = TicketPossession(human_dict, tickets)
    possession.process_take_self()
    possession.pretty_print("자기꺼 가져간 뒤 상태")
    possession.process_take_for_self()
    possession.pretty_print("자기명의 가져간 뒤 상태")

    possession.dump("dist.json")


if __name__ == "__main__":
    main()
