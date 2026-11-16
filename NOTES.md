# Notes

## Step 1.5: Hybrid search prototype (Nov 15, 2026)

Setup: 4 fictional PDFs in `sample_pdfs/` (6 pages, 14 chunks; chunk_size 500, overlap 50),
embeddings `all-MiniLM-L6-v2`, each retriever k = 3, hybrid = EnsembleRetriever 50/50.
Table shows each retriever's top result.

| Question | Right answer | BM25 (default) | BM25 (lowercased) | Dense | Hybrid |
| --- | --- | --- | --- | --- | --- |
| Does the building need a new roof? | inspection_report p1–2 | ❌ lease p2 | ❌ lease p2 | ✅ inspection p2 | ✅ inspection p2 |
| How much does rent go up each year? | lease p1 ("escalate by 3%") | ❌ hoa_rules p1 | ✅ lease p1 | ✅ lease p1 | ✅ lease p1 |
| Who pays for HVAC repairs? | lease p2 (also hoa_rules) | ✅ lease p2 | ✅ lease p2 | ✅ lease p2 | ✅ lease p2 |
| When does the lease end? | lease p1 | ❌ inspection p2 | ✅ lease p1 | ✅ lease p1 | ✅ lease p1 |
| Are pets allowed? | hoa_rules p1 (also lease p2, "animals") | ✅ hoa_rules p1 | ✅ hoa_rules p1 | ✅ hoa_rules p1 | ✅ hoa_rules p1 |
| What is the inspector's license number? | inspection_report p1 | — | ✅ inspection p1 | ✅ inspection p1 | ✅ inspection p1 |
| **Score (first 5)** | | **2/5** | **4/5** | **5/5** | **5/5** |

### Takeaways

- LangChain's `BM25Retriever` splits on spaces only by default: no lowercasing, punctuation kept
  (`lease` ≠ `LEASE`, `end?` ≠ `end`). Adding
  `preprocess_func=lambda t: re.findall(r"\w+", t.lower())` took BM25 from 2/5 to 4/5.
- BM25 still missed the roof question: "building" is rare and appears only in the lease, so it
  outweighed the inspection report's "roof" matches. Dense understood the meaning.
- Dense handled paraphrases ("go up" vs "escalate"). On this small set, dense alone matched hybrid.
- Why hybrid anyway: BM25 is the safety net for exact terms (license numbers, unit numbers,
  dollar amounts) that embeddings blur, especially in a larger corpus. Hybrid never did worse
  than the better of the two.
