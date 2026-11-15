# LLM Hiring Audit

An independent validity and bias audit of an LLM-based resume screening pipeline,
in the style of a TEVV (Test, Evaluation, Verification & Validation) review.

**The question:** if an employer used an LLM to score resumes against job
descriptions, would its scores agree with real hiring decisions, and could
the scores carry demographic proxies?

## System under test

A two-stage LLM screener:

1. **JD → rubric:** an LLM extracts a structured rubric (mandatory and optional
   qualifications, technical skills, seniority) from a job description.
2. **Resume + rubric → score:** a second call scores the resume 0–100 with a
   confidence value, risk flags, and written reasoning.

I evaluated it against synthetic resumes labelled with recruiter Hire/Reject
decisions and an earlier "original AI" screening score.

## Method

- **Criterion validity:** do pipeline scores separate Hire from Reject? Compared
  with the original AI score and a naive "predict all Hire" baseline.
- **Manual review:** I hand-scored disagreement cases on an 8-dimension rubric
  (minimum qualifications, core skills, experience, impact, problem solving,
  communication, culture fit, risk flags) and compared my scores with the model's.
- **Flag analysis:** how often the model raises flags that could act as
  demographic proxies.

## Findings (pilot, n = 25)

| Score source | Hire mean | Reject mean | Gap | Best cutoff accuracy |
|---|---|---|---|---|
| LLM pipeline | 34.2 | 30.4 | 3.8 | 20/25 |
| Original AI | 93.2 | 55.0 | 38.2 | **25/25** |

Naive baseline (predict all Hire): **20/25**

1. **The pipeline barely separates hires from rejects.** A 3.8-point gap, and no
   cutoff beats the naive baseline. As a screening signal it adds nothing over the
   base rate on this sample.
2. **The ground truth may itself be contaminated.** Recruiter decisions track the
   *original AI* score perfectly: a cutoff of 70 reproduces all 25 decisions. If recruiters saw that score, the labels
   partly measure agreement with the old AI, not candidate quality. Validating a
   new model against those labels would just reward copying the old one.
3. **JD and label mismatch.** In a reviewed case (recruiter: Hire, original AI: 100,
   pipeline: 22), the "Cybersecurity Analyst" label was paired with a GRC / technical
   risk JD. The candidate's offensive-security skills fit the label but not the JD.
   My manual scoring agreed with the pipeline, not the recruiter.
4. **Low confidence on sparse resumes.** Mean confidence was 0.48, and 23/25 resumes
   were flagged `underqualified`. The model correctly reports uncertainty, but a
   downstream user reading only the score would miss it.
5. **Proxy-risk flags.** `non_us_degree` (3/25) and `non_traditional_path` (12/25)
   are plausible proxies for national origin, age, or socioeconomic background.
   They need disparate-impact testing before any production use.

## Recommendations

- Validate against outcomes the model being replaced never influenced, such as
  interview or performance results, not prior screening decisions.
- Audit JD-to-label pairings before scoring.
- Add an explicit "insufficient evidence" state so missing data isn't scored as
  weak performance.
- Treat `non_us_degree`-style flags as protected-attribute proxies. Run
  counterfactual tests that swap names and demographics and measure score shifts.
- Drop or tightly define "culture fit". It has no evidence base in a resume and is
  a known bias vector.

## Next steps

- Scale from n = 25 to the full dataset for stable estimates.
- Counterfactual bias audit: score demographically swapped resume pairs and test
  for significant score differences.

## Reproduce the summary

```bash
python audit.py path/to/results.csv
```

`audit.py` is standard-library Python. Results files aren't included.
