import argparse
import os
from typing import Iterable, List

from scripts.KeytermsExtraction import KeytermExtractor
from scripts.ReadPdf import read_single_pdf
from scripts.utils.Utils import TextCleaner


def read_text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        return read_single_pdf(path)
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def normalize_keyterms(keyterms: Iterable) -> List[str]:
    normalized = []
    for item in keyterms:
        if isinstance(item, tuple) and len(item) >= 1:
            normalized.append(str(item[0]))
        else:
            normalized.append(str(item))
    return normalized


def extract_keywords(text: str, top_n: int) -> List[str]:
    cleaned_text = TextCleaner.clean_text(text)
    extractor = KeytermExtractor(cleaned_text, top_n_values=top_n)
    keyterms = extractor.get_keyterms_based_on_textrank()
    normalized = normalize_keyterms(keyterms)
    seen = set()
    unique_terms = []
    for term in normalized:
        lower_term = term.lower()
        if lower_term not in seen:
            seen.add(lower_term)
            unique_terms.append(term)
    return unique_terms


def build_tailored_resume(
    resume_text: str,
    matched_keywords: List[str],
    missing_keywords: List[str],
    max_keywords: int,
) -> str:
    matched_section = ", ".join(matched_keywords[:max_keywords]) or "None detected"
    missing_section = ", ".join(missing_keywords[:max_keywords]) or "None detected"
    return (
        f"{resume_text.strip()}\n\n"
        "ATS KEYWORD ALIGNMENT\n"
        f"Matched keywords: {matched_section}\n"
        f"Keywords to emphasize: {missing_section}\n"
    )


def build_cover_letter(
    name: str,
    role: str,
    company: str,
    matched_keywords: List[str],
    missing_keywords: List[str],
) -> str:
    highlighted = ", ".join(matched_keywords[:6]) or "relevant skills"
    growth = ", ".join(missing_keywords[:6]) or "role-specific expertise"
    return (
        f"Dear Hiring Manager,\n\n"
        f"I am excited to apply for the {role} role at {company}. "
        "My background aligns closely with the requirements in the job description, "
        f"including experience with {highlighted}. "
        "I have a track record of delivering measurable outcomes by collaborating across "
        "teams, improving processes, and maintaining high quality standards.\n\n"
        f"I am particularly interested in this opportunity because it will allow me to deepen my "
        f"experience in {growth} while contributing to the goals of {company}. "
        "I would welcome the opportunity to discuss how I can support your team.\n\n"
        "Sincerely,\n"
        f"{name}\n"
    )


def write_output(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tailor a resume and cover letter based on ATS keyword matching."
    )
    parser.add_argument("--resume", required=True, help="Path to resume (txt or pdf).")
    parser.add_argument("--job-desc", required=True, help="Path to job description (txt or pdf).")
    parser.add_argument("--output-dir", default="Data/Output", help="Output directory.")
    parser.add_argument("--name", default="Your Name", help="Name for the cover letter.")
    parser.add_argument("--role", default="the role", help="Role title for the cover letter.")
    parser.add_argument("--company", default="the company", help="Company name.")
    parser.add_argument("--top-n", type=int, default=30, help="Number of keywords to extract.")
    parser.add_argument(
        "--max-keywords",
        type=int,
        default=20,
        help="Max keywords to include in outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    resume_text = read_text(args.resume)
    job_text = read_text(args.job_desc)

    resume_keywords = extract_keywords(resume_text, args.top_n)
    job_keywords = extract_keywords(job_text, args.top_n)

    resume_lookup = {term.lower() for term in resume_keywords}
    matched = [term for term in job_keywords if term.lower() in resume_lookup]
    missing = [term for term in job_keywords if term.lower() not in resume_lookup]

    tailored_resume = build_tailored_resume(
        resume_text,
        matched,
        missing,
        args.max_keywords,
    )
    cover_letter = build_cover_letter(
        args.name,
        args.role,
        args.company,
        matched,
        missing,
    )

    resume_output = os.path.join(args.output_dir, "tailored_resume.txt")
    cover_output = os.path.join(args.output_dir, "cover_letter.txt")
    write_output(resume_output, tailored_resume)
    write_output(cover_output, cover_letter)

    print("Tailored resume written to:", resume_output)
    print("Cover letter written to:", cover_output)
    print(
        "Note: This script does not submit applications automatically. "
        "Use the generated files when applying on job boards."
    )


if __name__ == "__main__":
    main()
