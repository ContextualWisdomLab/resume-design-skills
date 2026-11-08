# Resume Design Skills

Preserve the package boundary: `skills/resume-design/` is the installable unit.
Keep scripts and required references within it; repository documentation and
evaluation records must not become hidden runtime dependencies.

Use original synthetic fixtures only. Never publish real applicant records,
mail contents, private metrics, contact details or author metadata. Preserve
user facts and employer forms in actual resume work.

Separate official guidance, product-specific behavior, local design defaults,
structural checks, visual review and actual ATS tests. Do not claim hiring
outcomes, universal parser compatibility or accessibility conformance from
local checks.

Run `python3 -m unittest discover -s tests -v` after changing the DOCX audit.
Generate and render the examples after layout changes, inspect all pages and
record the renderer, page counts and untested limits in the validation report.
Use standard-library code for the preflight. `python-docx` is optional and only
needed to rebuild examples. Do not add a web service, external document upload,
model API calls or an LLM-based CI gate to this package.

Make normal commits, inspect the current remote head before publishing and
preserve concurrent work. Never force-push or bypass repository protections.
