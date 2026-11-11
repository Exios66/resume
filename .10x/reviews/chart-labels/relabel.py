"""One-off relabel of the site's static chart SVGs and two chart titles (text only; data and marks untouched).

Run from the repository root: python3 .10x/reviews/chart-labels/relabel.py
Every replacement must match; the script fails loudly otherwise, so it cannot half-apply silently.
"""
import pathlib, re

MR = 'projects/mailroom-ml/figures/'
RV = 'projects/rvl-cdip-classifier/figures/'
EDITS = {
    MR + 'accuracy_by_windows.svg': [
        ('>Doc-type accuracy by document length · Arm B (Sep 27)<', '>Document-type accuracy by document length<'),
        ('>Documents bucketed by 8k-token window count<', '>Test documents grouped by number of 8,192-token windows · Arm B run, 27 September<'),
        ('>doc-type accuracy<', '>Document-type accuracy<'),
        ('>1 window (n=274)<', '>1 window (n = 274)<'), ('>2–3 (n=25)<', '>2–3 windows (n = 25)<'),
        ('>4–8 (n=9)<', '>4–8 windows (n = 9)<'), ('>9+ (n=15)<', '>9+ windows (n = 15)<')],
    MR + 'confusion.svg': [
        ('>Doc-type confusion matrix · Arm B (Sep 27)<', '>Document-type confusion matrix, test split<'),
        ('>Rows = true class, columns = predicted; shade = share of the row (blue diagonal, red errors)<',
         '>Rows: true type · Columns: predicted type · Shading: share of each row (blue correct, red errors) · Arm B run<'),
        ('>predicted<', '>Predicted type<'), ('>true class (rows)<', '>True type<')],
    MR + 'doc_type_recall.svg': [
        ('>Document-type recall by class<', '>Recall by document type across three training runs<'),
        ('>Share of each true class routed to it · Run 3 (Sep 21), Arm A (Sep 27), Arm B (Sep 27) · n = 323 documents<',
         '>Share of each true type classified correctly · 323 test documents<'),
        ('>Run 3 (Sep 21)<', '>Run 3 (21 Sep)<'), ('>Arm A (Sep 27)<', '>Arm A (27 Sep)<'), ('>Arm B (Sep 27)<', '>Arm B (27 Sep)<')],
    MR + 'head_ece.svg': [
        ('>Per-head calibration error · Arm B (Sep 27)<', '>Calibration error for each classifier head<'),
        ('>Expected calibration error per head; window-level ECE 0.0259<',
         '>Expected calibration error (ECE), lower is better · window-level ECE 0.026 · Arm B run, 27 September<'),
        ('>exclusion line 0.05<', '>Exclusion threshold (0.05)<'), ('>doc type<', '>Document type<')],
    MR + 'selective_risk.svg': [
        ('>Calibration and selective risk · Arm B (Sep 27)<', '>Raising the confidence threshold trades coverage for accuracy<'),
        ('>Pick 0.90: 87% of windows accepted at 99.4% accuracy<',
         '>At the chosen 0.90 threshold, 87% of windows are accepted at 99.4% accuracy · Arm B run, 27 September<'),
        ('>confidence threshold<', '>Confidence threshold<'), ('>pick<', '>chosen<'),
        ('>accuracy of accepted windows<', '>Accuracy of accepted windows<'),
        ('>coverage (share accepted)<', '>Coverage (share accepted)<'), ('>Wilson lower bound<', '>Accuracy, Wilson lower bound<')],
    MR + 'subclass_collapse.svg': [
        ('>Subclass accuracy and collapse signal · Arm B (Sep 27)<', '>Subclass accuracy, and how often each head repeats one answer<'),
        ('>Documents whose doc type was right. Orange far above grey = the head collapsed onto one answer<',
         '>Correctly typed documents · orange far above grey means the head collapses onto one subclass · Arm B run<'),
        ('>subclass accuracy<', '>Subclass accuracy<'),
        ('>share of predictions on one subclass<', '>Share of predictions on one subclass<'),
        ('>most common true subclass&#x27;s share<', '>Most common true subclass&#x27;s share<'),
        ('>P0 subclass gate 0.75<', '>Collapse gate (0.75)<')],
    RV + 'f1_accuracy_arc.svg': [
        ('>Accuracy on the 160-image tuning slice by prompt version (not held out)<', '>Tuning-slice accuracy rose from 80% to 99% across prompt versions<'),
        ('>Prompt version (qwen3.7-flash, 160-image slice)<', '>Prompt version (qwen3.7-flash, 160-image tuning slice)<')],
    RV + 'f2_generalization_falloff.svg': [
        ('>v11.8 transfer to larger, noisier slices<', '>Prompt v11.8 accuracy falls on larger, noisier slices<')],
    RV + 'f3_model_comparison.svg': [
        ('>Model comparison (best prompt version per model)<', '>Best tuning-slice accuracy for each model, with 95% intervals<'),
        ('>Exact-match accuracy (%) on the 160-image slice<', '>Exact-match accuracy (%)<'),
        ('>Model (best prompt version on the 160-image slice)<', '>Model and prompt version (160-image tuning slice)<'),
        ('>v1 baseline 80.1%<', '>v1 prompt baseline 80.1%<')],
    RV + 'f4_confusion_heatmap.svg': [
        ('>Confusion matrix — qwen3.7-flash v11.8, 160-image slice (98.7%)<', '>Confusion matrix: qwen3.7-flash with prompt v11.8, tuning slice (98.7% correct)<'),
        ('>Expected class<', '>True class<'), ('>Row % (expected)<', '>Share of true class (%)<')],
    RV + 'f5_per_class_accuracy.svg': [
        ('>Per-class accuracy — 1120-image run (overall 82.6%)<', '>Accuracy by document class, 1,120-image run (dashed line: overall 82.6%)<')],
    RV + 'f6_cost_projections.svg': [
        ('>Cost per image and scale-up projections (derived from OpenRouter metrics)<', '>Cost per image and projected cost at scale, from OpenRouter billing<'),
        ('>OpenRouter-reported per-image cost<', '>Billed cost per image<'),
        ('>Linear scale-up at 800 / 25k / 320k images<', '>Projected total for 800, 25,000 and 320,000 images<')],
    RV + 'f7_ensemble_vs_k.svg': [
        ('>Ensemble majority vote: monotone gains, diminishing returns<', '>Majority voting raises accuracy, with diminishing returns (simulated)<'),
        ('>Committee size K (majority vote)<', '>Votes per image (committee size K)<')]
        + [(f'>0.{v}<', f'>{v[:2]}.{v[2]}%<') for v in ('821', '836', '844', '850', '859', '863')],
    RV + 'f8_routing.svg': [
        ('>Confidence-gated escalation: peak 91.9% at 1.8× cost (simulated)<', '>Escalating the least confident images peaks at 91.9% accuracy for 1.8× cost (simulated)<'),
        ('>Cost factor (×)<', '>Cost relative to one pass (×)<'), ('>Cost (×)<', '>Relative cost<'),
        ('text-anchor: start" x="656.504308" y="235.262006" transform="rotate(-0 656.504308 235.262006)">baseline 82.1%<',
         'text-anchor: end" x="515" y="241" transform="rotate(-0 515 241)">Baseline, no escalation: 82.1%<')],
    RV + 'f9_hasty_stop.svg': [
        ('>Words associated with earlier stops and more errors (17.1% baseline error)<', '>Words linked to earlier stops and more errors (baseline error 17.1%)<'),
        ('>Hasty-score (early stop + elevated error, frequency-weighted)<', '>Hastiness score (early stop plus extra error, frequency-weighted)<')],
    'projects/mailroom-ml/report.qmd': [
        ('title="Per-head subclass macro-F1, Arm B to final run (test split)"', 'title="Subclass macro-F1 for each head: Arm B run against the final run (test split)"')],
    'projects/langtons-ant.qmd': [
        ('title="Steps per second: README laptop against three re-runs (millions)"', 'title="Engine speed in Node, million steps per second: README figure against three re-runs"')],
}
CLASSES = ['advertisement', 'budget', 'email', 'file_folder', 'form', 'handwritten', 'invoice', 'letter', 'memo', 'news_article',
           'presentation', 'questionnaire', 'resume', 'scientific_publication', 'scientific_report', 'specification']
for name in ('f4_confusion_heatmap.svg', 'f5_per_class_accuracy.svg'):
    EDITS[RV + name] += [(f'>{c}<', f'>{c.replace("_", " ").capitalize()}<') for c in CLASSES]

for path, pairs in EDITS.items():
    p = pathlib.Path(path); s = p.read_text()
    for old, new in pairs:
        if old not in s:
            raise SystemExit(f'{path}: not found: {old[:80]}')
        s = s.replace(old, new)
    p.write_text(s)

# f8: the x label is matplotlib mathtext (one glyph offset per letter); replace it with one plain, centred label.
p = pathlib.Path(RV + 'f8_routing.svg'); s = p.read_text()
s, n = re.subn(r'<g id="text_7">.*?</g>\s*</g>',
               '<g id="text_7"><text style="fill: #262626; font: 12.6px \'Arial\', \'DejaVu Sans\', sans-serif; text-anchor: middle" '
               'x="282.520078" y="321.745242">Share of images escalated, least confident first (α)</text></g>', s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('f8 x label not found')
p.write_text(s)
print('relabelled', len(EDITS), 'files')
