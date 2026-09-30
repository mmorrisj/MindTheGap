# Kaggle: open challenges suited to one developer working with AI (as of 2026-09-30)

> **How this was gathered:** Kaggle is blocked from the sandbox this was written in, so everything below comes from web search results. **Confirm deadlines and rules on each competition page before committing time.**

## Assessment

| Competition | Deadline (UTC) | Prize | Solo + AI fit | Why |
|---|---|---|---|---|
| [Enveda CASMI 2026: molecule ID from mass spectra](https://www.kaggle.com/competitions?tagIds=7100-Biology) | ~Dec 14, 2026 (unverified) | not found | ★★★ | A real scientific gap: most mass spectra in metabolomics are never identified. Large open training set (~2.5M spectra, 275k molecules, including Enveda-180). Hidden test set of ~400 unpublished molecules. It stays open as a benchmark after the contest. Reasonable baselines (spectral library search, fingerprint prediction plus candidate re-ranking) fit on one GPU. |
| [Filament Segmentation Challenge 2026](https://www.kaggle.com/competitions/filament-segmentation-2026) (IEEE BigData Cup) | not found; likely Nov, ahead of the conference | $3,000 + a talk at IEEE BigData | ★★★ | Small, clean dataset (MAGFiLO: 1,593 GONG images, 10k polygons). Few competitors. A U-Net or SAM fine-tune runs on a single GPU in hours. Best odds of placing, and it counts as a real research credential. |
| [Gemma 4 Developer Agent](https://www.kaggle.com/competitions/gemma-4-developer-agent/overview) plus the [Paper Track](https://www.kaggle.com/competitions/gemma-4-developer-agent-paper) | Paper Nov 12; entry Nov 25; final Dec 2 | $65k main, $35k paper | ★★☆ main / ★★★ paper | The main track means post-training Gemma 4 on SWE-bench-style tasks, which needs a lot of compute and favours teams. The **paper track's "new resource" and "new application" prizes** are reachable alone, and fit MindTheGap well (see below). |
| [ARC Prize 2026: ARC-AGI-2 / ARC-AGI-3](https://arcprize.org/competitions/2026/arc-agi-3) | Entry Oct 26; final Nov 2 | $700k+ grand prizes | ★☆☆ | Prestigious and open-ended, but about 5 weeks remain. Top teams have spent months on it, and evaluation runs offline under tight compute limits. Worth doing to learn, not to win. |
| Kaggriculture (agent simulation) | Sep 30, 2026 (closed) | | n/a | Closes today. |

## Recommendation

1. **Fastest win: Filament Segmentation.** It's a bounded vision task with low competition. AI tools speed up the routine parts (data loaders, augmentation, metric code), which leaves your time for the modelling decisions.
2. **Most meaningful: CASMI 2026.** It's the closest match to the "under-served gap" theme. Structure elucidation from mass spectra is a bottleneck in drug and natural-product discovery, and the benchmark will outlast the contest.
3. **Link to MindTheGap: the Gemma 4 paper track.** A "new resource" entry could be a dataset of open issues in *critical-but-fragile* PyPI packages (ranked by this repo's scorer), framed as a benchmark for agents that reduce maintainer workload. That turns the existing scanner into a paper contribution and doesn't require winning the compute-heavy main track. **The paper deadline is Nov 12.**

## Solo + AI workflow notes
- Code competitions run offline at inference (no API calls), so the AI assistant helps with *building* the solution, not inside the submission.
- Pin a local validation split that tracks the leaderboard before you tune anything. That keeps you from chasing public-leaderboard noise.
- Keep each experiment small and logged (config, CV score, LB score), which matches the incremental style used in this repo.

## Sources
- [Kaggle: Gemma 4 Developer Agent announcement](https://x.com/kaggle/status/2102793965854662859)
- [AAS Solar News: Filament Segmentation Challenge 2026](https://solarnews.aas.org/2026/solar-filament-segmentation-challenge-2026/) · [IEEE BigData 2026 Cup](https://bigdataieee.org/BigData2026/cup/solar-filament-segmentation/)
- [Enveda CASMI 2026 coverage](https://www.webull.com/news/15582421858583552)
- [ARC Prize 2026: ARC-AGI-2](https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-2) · [ARC-AGI-3 rules](https://arcprize.org/competitions/2026/arc-agi-3)
- [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture/)
