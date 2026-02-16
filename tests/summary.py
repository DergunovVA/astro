import json

with open("test_results_20260216_205636.json", "r", encoding="utf-8") as f:
    results = json.load(f)

for r in results:
    name = r["profile"]["name"]
    sun = r["chart"]["sun"]
    moon = r["chart"]["moon"]
    asc = r["chart"]["ascendant"]

    print(f"{name}: {sun} Sun, {moon} Moon, {asc} ASC")

    # Top 3 aspects
    if r["key_aspects"]:
        print("  Key aspects:")
        for asp in r["key_aspects"][:3]:
            planets = asp["planets"]
            asptype = asp["type"]
            orb = asp["orb"]
            print(f"    {planets} {asptype} (orb {orb})")

    # Demons count and types
    demons = r.get("demons", [])
    demon_count = len(demons)
    print(f"  Demons: {demon_count}")

    if demon_count > 0:
        for d in demons[:3]:
            planet = d.get("planet", "?")
            desc = d.get("description", "")
            # Показываем только первые 60 символов
            if len(desc) > 60:
                desc = desc[:60] + "..."
            print(f"    {planet}: {desc}")

    # Proofs
    proofs = r.get("proofs", [])
    proof_count = len(proofs)
    if proof_count > 0:
        print(f"  Proofs: {proof_count}")
        for proof in proofs[:2]:
            planet = proof.get("planet", "?")
            sign = proof.get("sign", "?")
            print(f"    {planet} in {sign}")

    print()
