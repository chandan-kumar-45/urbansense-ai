# teammate-road-damage/

This folder is a placeholder for the teammate's actual repository:
https://github.com/manvendrasrathore11/ai-urban-intelligence

We deliberately do **not** copy its files in here by hand — that would fork it
silently and your teammate's future commits would never reach the platform.
Instead, pull it in as a git submodule so `git pull` in this folder always
reflects the real upstream repo:

```bash
# from the urbansense-ai repo root
git submodule add https://github.com/manvendrasrathore11/ai-urban-intelligence teammate-road-damage
git submodule update --init --recursive
```

To pull your teammate's latest changes later:

```bash
cd teammate-road-damage
git pull origin main
cd ..
git add teammate-road-damage
git commit -m "Update teammate-road-damage submodule"
```

If your team prefers not to use submodules (some campus/college Git setups make
them awkward), a `git subtree` works too — see
`docs/AI_MODEL_INTEGRATION.md` for both options.

## What the platform actually imports from here

Nothing yet — `backend/app/ai/road_damage/inference.py` currently ships its own
`DemoRoadDamageDetector` (classical CV heuristic, not a trained model) because
this repo has no trained weights or inference code yet (confirmed by inspecting
it: `src/road_damage/{config,model,detector,main}.py` are placeholder files per
its own README).

Once your teammate adds real code here, wire it in by editing
`backend/app/ai/road_damage/inference.py`'s `TeammateRoadDamageModel` class to
actually import and call it — see `docs/AI_MODEL_INTEGRATION.md` step 5.
