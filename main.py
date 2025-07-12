import json

HUMAN_DICT = {
    "고형석": {
        "go": "EE",
        "have": [0, 0, 0, 0],
    }
}

def main():
    with open("data/app.tsv", "rt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            [nm, e1, w1, e2, w2, go1, go2] = line.split("\t")
            e1, w1, e2, w2 = int(e1), int(w2), int(e2), int(w2)
            assert go1 in ("E", "W") and go2 in ("E", "W")

            igo1 = "W" if e1 == 0 else "E"
            igo2 = "W" if e2 == 0 else "E"

            if igo1 != go1:
                print(f"E: {nm} applied for {igo1} but wants {go1} in saturday")
            if igo2 != go2:
                print(f"E: {nm} applied for {igo2} but wants {go2} in sunday")

            HUMAN_DICT[nm] = {
                "go": go1+go2,
                "have": [0, 0, 0, 0],
            }

    with open("data/app2.tsv", "rt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            [nm1, nm2, e1, w1, e2, w2] = line.split("\t")
            e1, w1, e2, w2 = int(e1), int(w1), int(e2), int(w2)

            assert e1 == 0 or w1 == 0
            assert not (e1 == 0 and w1 == 0)
            assert e2 == 0 or w2 == 0
            assert not (e2 == 0 and w2 == 0)

            go1, go2 = HUMAN_DICT[nm2]["go"]
            igo1 = "W" if e1 == 0 else "E"
            igo2 = "W" if e2 == 0 else "E"
            if igo1 != go1:
                print(f"E: {nm} received {igo1} but wants {go1} in saturday")
            if igo2 != go2:
                print(f"E: {nm} received {igo2} but wants {go2} in sunday")

    with open("data/result.tsv", "rt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            [nm1, nm2, e1, w1, e2, w2] = line.split("\t")
            e1, w1, e2, w2 = int(e1), int(w1), int(e2), int(w2)

            name = nm2 if len(nm2) > 0 else nm1
            HUMAN_DICT[name]["have"][0] += e1
            HUMAN_DICT[name]["have"][1] += w1
            HUMAN_DICT[name]["have"][2] += e2
            HUMAN_DICT[name]["have"][3] += w2

    with open("plan.json", "wt") as f:
        json.dump(HUMAN_DICT, f, indent=2, ensure_ascii=False)

    pools = [[], [], [], []]
    # Yield tickets to pools
    for name in HUMAN_DICT:
        human_obj = HUMAN_DICT[name]
        go1, go2 = human_obj["go"]

        idx_sat = 0 if go1 == "E" else 1
        idx_nsat = 1 if go1 == "E" else 0
        if human_obj["have"][idx_sat] > 1:
            left_tickets = human_obj["have"][idx_sat] - 1
            pools[idx_sat].extend([name for _ in range(left_tickets)])
        assert human_obj["have"][idx_nsat] == 0, human_obj

        idx_sun = 2 if go2 == "E" else 3
        idx_nsun = 3 if go2 == "E" else 2
        if human_obj["have"][idx_sun] > 1:
            left_tickets = human_obj["have"][idx_sun] - 1
            pools[idx_sun].extend([name for _ in range(left_tickets)])
        assert human_obj["have"][idx_nsun] == 0

    yield_plans = [{}, {}, {}, {}]
    failures = [[], [], [], []]
    for name in HUMAN_DICT:
        human_obj = HUMAN_DICT[name]
        go1, go2 = human_obj["go"]

        idx_sat = 0 if go1 == "E" else 1
        if human_obj["have"][idx_sat] < 1:
            if len(pools[idx_sat]):
                got_from = pools[idx_sat].pop()
                if got_from not in yield_plans[idx_sat]:
                    yield_plans[idx_sat][got_from] = []
                yield_plans[idx_sat][got_from].append(name)
            else:
                failures[idx_sat].append(name)

        idx_sun = 2 if go2 == "E" else 3
        if human_obj["have"][idx_sun] < 1:
            if len(pools[idx_sun]):
                got_from = pools[idx_sun].pop()
                if got_from not in yield_plans[idx_sun]:
                    yield_plans[idx_sun][got_from] = []
                yield_plans[idx_sun][got_from].append(name)
            else:
                failures[idx_sun].append(name)

    print("\n----- 티켓 양도 플랜 -----")
    for i in range(4):
        yield_plan = yield_plans[i]
        pool = pools[i]
        failure = failures[i]
        print("1일차 " if i // 2 == 0 else "2일차 ", end="")
        print("동: " if i % 2 == 0 else "서남: ", end="")
        print(f"잔여 티켓 {pool}")
        for yield_from, yield_to_list in yield_plan.items():
            print(f"\t{yield_from} -> {", ".join(yield_to_list)}")
        for failed_name in failure:
            print(f"\tError: {failed_name} 수요 충족 불가")
    print("----- 티켓 양도 플랜 끝 -----")

    print("\n----- 일반 통계 -----")
    goto = [[], [], [], []]
    for name in HUMAN_DICT:
        go1, go2 = HUMAN_DICT[name]["go"]
        goto[0 if go1 == "E" else 1].append(name)
        goto[2 if go2 == "E" else 3].append(name)

    for i in range(4):
        print("1일차 " if i // 2 == 0 else "2일차 ", end="")
        print("동  : " if i % 2 == 0 else "서남: ", end="")
        print(f"{len(goto[i])}명")
        print("\t" + ", ".join(goto[i]))


    print("----- 일반 통계 끝 -----")

if __name__ == "__main__":
    main()