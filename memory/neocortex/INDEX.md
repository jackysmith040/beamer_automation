---
neuron_id: neocortex/INDEX.md
title: Neocortex — Memory Palace Lobby
synaptic_weight: 100
---

# Neocortex — Memory Palace Lobby

*The spatial hub of all structured knowledge. Navigate by Room.*

---

## 🧠 Left Hemisphere — Analytical Chamber
> Formal logic, mathematics, structured reasoning, deterministic systems.

*Empty. Awaiting ingestion.*

---

## 🎨 Right Hemisphere — Intuition Chamber  
> Spatial reasoning, metaphor, pattern recognition, creative synthesis.

*Empty. Awaiting ingestion.*

---

## How to populate a Room
1. Create a `.md` file in `neocortex/left_hemisphere/` or `neocortex/right_hemisphere/`
2. Add the required frontmatter (see template below)
3. Axon will run the scanner automatically — the graph updates itself

### Neuron Template
```yaml
---
neuron_id: unique-concept-id
title: Human-Readable Title
synaptic_weight: 40          # 1–100, increases on reinforcement
corpus_callosum: other-id    # link to opposite hemisphere counterpart
blindspot: false             # set true if Director has made errors here before
summary: One-sentence description for the graph tooltip
---
```
