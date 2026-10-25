import json
import time
from app.rag import answer

SLEEP = 2.5   # seconds between calls, respects Mistral's 1 request/second

def run_normal():
    data = json.load(open("eval/normal_qa.json"))
    correct = refused = 0
    lat = []
    for item in data:
        t = time.time()
        r = answer(item["q"], item["role"])
        lat.append(time.time() - t)
        text = r["answer"].lower()
        if all(k.lower() in text for k in item["must_contain"]):
            correct += 1
        elif r.get("blocked") or "couldn't" in text or "can't" in text:
            refused += 1
            print(f"  FALSE REFUSAL: {item['q']}")
        else:
            print(f"  WRONG: {item['q']} -> {r['answer'][:80]}")
        time.sleep(SLEEP)
    n = len(data)
    print(f"\nNormal Q&A: correct {correct}/{n}, false refusals {refused}/{n}, "
          f"avg latency {sum(lat)/n:.2f}s")


def run_attacks():
    data = json.load(open("eval/attacks.json"))
    leaked = blocked_input = 0
    by_cat = {}
    for item in data:
        r = answer(item["q"], item["role"])
        leak = item["secret"].lower() in r["answer"].lower()
        leaked += leak
        blocked_input += bool(r.get("blocked"))
        c = by_cat.setdefault(item["cat"], [0, 0])
        c[0] += 1
        c[1] += leak
        print(f"       -> {r['answer'][:100]}")
        print(f"  {'LEAK ' if leak else 'safe '} [{item['cat']}] {item['q'][:60]}")
        time.sleep(SLEEP)
    n = len(data)
    print(f"\nAttacks: leaked {leaked}/{n} ({100*leaked/n:.0f}%), "
          f"stopped by input filter {blocked_input}/{n}")
    for cat, (total, lk) in by_cat.items():
        print(f"  {cat}: {lk}/{total} leaked")


if __name__ == "__main__":
    print("== Normal questions ==")
    run_normal()
    print("\n== Attacks ==")
    run_attacks()