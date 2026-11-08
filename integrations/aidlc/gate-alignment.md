# AI-DLC ↔ QA Gate Alignment

In companion mode (MVP) this table is used for **readiness prerequisites** only. From v2
(`gateAlignment: true`) the QA gate pack is offered right after the matching AI-DLC
approval, so the same team reviews both in one sitting. In embedded mode (v3) they become
joint gates.

| AI-DLC approval point | QA stages it unlocks (prerequisite) | QA gate aligned |
|---|---|---|
| Reverse engineering approved | 0.2 domain discovery (docs-led for AI-DLC scope) | G0 |
| Requirements analysis approved | 1.1–1.3 | G1 |
| User stories / units generation approved | 1.4–1.6 | G2 |
| Functional + NFR design approved (per unit) | 2.1–2.4 for that unit | G3 |
| Code generation complete (per unit) | 3.1, 3.2 (v2) | – |
| Build & test complete | 3.3–3.4 (v2) | G4 |
| Operations (when available) | 4.x (v4) | G5 |

**Highest-value moment:** run QA 1.2 testability review on AI-DLC requirements *before*
AI-DLC moves to design. In v2, findings can be written back as AI-DLC questions.
