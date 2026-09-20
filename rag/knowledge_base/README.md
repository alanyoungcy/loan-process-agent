# HK Compliance Knowledge Base — RAG Sources

Authoritative Hong Kong regulatory documents for grounding GenAI in the loan-collection (催收) demo. Each file is provided in both **PDF** (authoritative, verified copy) and **.txt** (extracted text layer, ready for semantic chunking).

## Files

| File | Source | What it covers | RAG role |
|------|--------|----------------|----------|
| `Money_Lenders_Ordinance_Cap163_2022.pdf` / `.txt` | e-Legislation verified copy (last updated 30.12.2022), mirrored via mpl.hk | Money Lenders Ordinance (Cap. 163): licensing, loan agreements, excessive interest rates (24/25), offences, penalties | **Statutory backbone** — offences, interest caps, licensing |
| `PDPO_Cap486_Consolidated_2022.pdf` / `.txt` | Consolidated whole-chapter copy (01-10-2022) | Personal Data (Privacy) Ordinance (Cap. 486): Data Protection Principles (DPP1–6), data access/correction, direct-marketing rules, offences | **Data-privacy grounding** — lawful collection, retention, disclosure limits |
| `LMLA_Code_of_Money_Lending_Practice_2018.pdf` / `.txt` | Licensed Money Lenders Association (LMLA), Sept 2018 | Code of Money Lending Practice — includes **Chapter 3 "Recovery of Loans and Advances"** (§19 Debt Collection Activities, §20 Management of Debt Collection Agencies) and appendices 1(a)–1(f) with the **Guidelines on Additional Licensing Conditions of Money Lenders Licence** | **Primary conduct source** — this is where the debt-collection red lines live (no third-party contact unless legally liable, no harassment, collector identification, reasonable hours/frequency) |

## Recommended ingestion pipeline

1. **Chunk** the `.txt` files (semantic chunking, ~500–800 tokens with overlap; keep section numbers as metadata).
2. **Embed** with `text-embedding-3-large` (or local BAAI/bge) into the `compliance_policies` vector collection.
3. **Retrieve** hybrid (vector + keyword) with a cross-encoder re-ranker.
4. **Cite** — force the LLM to quote the section/clause number it relies on (e.g., "Cap. 163 s. 29", "Code of Money Lending Practice §19").

## Notes

- The Code of Money Lending Practice is **non-statutory** (voluntary) but is the de-facto industry conduct standard; the LMLA Code explicitly states it is "supplementary to … the Money Lenders Ordinance (Cap. 163)".
- The Money Lenders Ordinance itself does **not** contain detailed debt-collection conduct rules — those live in the Code of Practice. Keep both in the knowledge base.
- Optional additional sources (not yet downloaded): Code of Banking Practice (HKMA/HKAB, for bank collection), CLIC "Debt Collection" plain-language summary (for human-readable paraphrases of "harassment").

## Suggested Drools red-line mapping (see IMPLEMENTATION_PLAN.md §10.2)

| Drools rule | Grounded in |
|-------------|-------------|
| `no_collector_identification` | Code of Money Lending Practice §19 (identify self + purpose) |
| `third_party_disclosure` | Code of Money Lending Practice §8 (Personal Referees) + §19 |
| `harassment` / `threatening_language` | Cap. 163 s. 29 (offences) + Code of Practice §19 |
| `misrepresentation` | Code of Money Lending Practice §19 (no false claim of legal authority) |
| `outside_contact_hours` / `excessive_frequency` | Code of Money Lending Practice §19 (reasonable hours/frequency — tunable parameter) |
| data-privacy breaches | PDPO (Cap. 486) DPP1–DPP3 |
