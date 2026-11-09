"""Disclaimer generators and auto-attachments."""

DISCLAIMERS = {
    "faq": "This is general information. Your policy terms and conditions apply.",
    "approx_cost": "Approximate cost is indicative and is not a claim approval.",
    "doc_extraction": "Details were read automatically from your document. Final assessment is done by our claims team.",
    "final": "Claim intimation is not a claim approval.",
}


def get_disclaimer(kind: str) -> str | None:
    # get disclaimer string
    return DISCLAIMERS.get(kind)
