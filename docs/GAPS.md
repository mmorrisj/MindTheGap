# Underinvested challenges: shortlist

These are gaps where the problem is well documented but the investment and coordination behind it lag well behind how much it matters. Each one is judged on whether one developer could make real progress with a small amount of data collection or coordination.

| # | Gap | Evidence | Why it stays under-served | Manageable first step | Solo-dev fit |
|---|-----|----------|---------------------------|-----------------------|--------------|
| 1 | **Critical-but-fragile open-source dependencies** | 60% of surveyed maintainers have quit or considered quitting, and 61% of unpaid maintainers work alone. Sonatype reports an 18% drop in actively maintained projects. xz-utils (2024) showed the failure mode. | The benefit is spread across everyone who uses the code, so no single company owns the problem. Existing tools (OpenSSF Scorecard, Criticality Score) *measure* risk, but nobody tracks *who is stepping in*. | Score a dependency list, publish the risky, unclaimed ones, and let people claim watch, triage, co-maintain or fund roles. | ★★★ (all data comes from public APIs) |
| 2 | **"Data available on request" is mostly fiction** | Gabelica et al. 2022 found that of 1,792 papers promising data on request, 93% of authors did not respond or declined. Only 6.8% shared. | Nothing enforces it after publication, and no public record exists of which requests went unanswered. | A crowd log of requests sent and their outcomes, keyed by DOI, with rates per journal and per funder. | ★★☆ (needs a community to adopt it) |
| 3 | **Unknown-material water service lines (lead)** | EPA's 2025 inventory data leaves more than 24M lines of *unknown* material. Its estimate of lead lines fell from 9.2M to about 4M, largely by *modeling* those unknowns. | About 9,000+ utilities publish in inconsistent formats. The unknowns are a data problem before they are a construction problem. | Scrape or normalize utility inventory files and track the unknown share per utility over time. | ★★☆ (messy ingestion, high civic value) |
| 4 | **Legacy and orphaned medical-device software** | About 14% of connected medical devices run an unsupported OS, and about a third of those are imaging systems. | Devices outlive vendor support. Hospitals can't patch them, and vendors charge extra for updates. | A shared registry of end-of-support dates and known vulnerabilities per device model (hospitals share this informally now). | ★☆☆ (data is gated, and there is liability risk) |
| 5 | **Research software maintenance** | Scientific code is funded for papers, not for upkeep. Many widely used scientific Python packages depend on one or two people. | Grants reward novelty. Citation credit rarely reaches maintainers. | A special case of #1: run the scanner over the scientific Python stack. | ★★★ (reuses #1) |

## Pick: #1, with #5 as the first target domain

Why #1:
- **The data is free and machine-readable.** PyPI, GitHub and deps.dev cover it, so there are no partnerships to negotiate and no scraping of PDFs.
- **The missing piece is coordination, not measurement.** Scorecard and Criticality Score already exist. The gap is turning "this is risky" into "person X has committed to help." That is a small data model (the `claims` table).
- **It is useful to you on day one.** Scan your own `requirements.txt`.
- **It grows naturally** into #5 (the scientific stack), into npm and crates.io, and into semantic search over package descriptions using pgvector.

Honest caveats:
- The risk score is a heuristic. Release and commit staleness can mean "finished and stable" rather than "abandoned" (for example `six`). Calibrate it against known incidents before publishing rankings.
- Commit concentration understates the bus factor for projects that squash-merge or use bots.
- Claims only work if maintainers welcome them. The product must not become a pressure tool. Contacting maintainers should stay a human step.

## Sources
- [The Register: State of Open Source maintainers (2025)](https://www.theregister.com/2025/02/16/open_source_maintainers_state_of_open/)
- [Linux Foundation: Lessons from maintainers of critical software](https://www.linuxfoundation.org/blog/lessons-from-maintainers-of-the-worlds-most-critical-software)
- [Gabelica et al. 2022 (PDF)](https://www.Gwern.net/doc/statistics/bias/2022-gabelica.pdf) · [Nature coverage](https://media.nature.com/original/magazine-assets/d41586-022-01692-1/d41586-022-01692-1.pdf)
- [EPA 7th DWINSA fact sheet (2025)](https://www.epa.gov/system/files/documents/2025-11/fact-sheet-2025-7th-dwinsa-update.pdf) · [NRDC commentary](https://www.nrdc.org/media/epa-now-says-there-arent-9-million-lead-pipes-there-are-4-million-be-skeptical) · [Policy Innovation](https://www.policyinnovation.org/insights/what-best-available-data-tells-us-about-lead-service-lines)
- [MedTech Dive: legacy medical devices](https://www.medtechdive.com/news/legacy-medical-devices-growing-hacker-threats-create-medtech-cyber-risks/602157/) · [TechTarget: 63% of KEVs on healthcare networks](https://www.techtarget.com/healthtechsecurity/news/366593999/63-of-known-exploited-vulnerabilities-found-on-healthcare-networks)
