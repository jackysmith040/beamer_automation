"""
tests.test_agent_helper
Comprehensive test suite verifying all atomic utilities and pipeline orchestration.
"""

import os
from pathlib import Path
import unittest

from agent_helper.normalizer import normalize_text, extract_frontmatter
from agent_helper.escaper import escape_latex
from agent_helper.parser import parse_slides, Slide
from agent_helper.template_engine import extract_preamble, detect_archetypes, inject_content
from agent_helper.slide_builder import build_frame, build_presentation
from agent_helper.reviewer import review_presentation
from agent_helper.compiler import parse_latex_errors, self_heal_tex
from agent_helper.runner import run_pipeline


class TestNormalizer(unittest.TestCase):
    def test_normalize_text(self):
        raw = "\ufeffLine 1 \r\nLine 2   \r\n\r\n"
        norm = normalize_text(raw)
        self.assertEqual(norm, "Line 1\nLine 2")

    def test_extract_frontmatter(self):
        content = "---\ntitle: My Deck\nauthor: Alice\n---\n# Main Title\nBody"
        meta, body = extract_frontmatter(content)
        self.assertEqual(meta.get("title"), "My Deck")
        self.assertEqual(meta.get("author"), "Alice")
        self.assertIn("# Main Title", body)


class TestEscaper(unittest.TestCase):
    def test_escape_special_characters(self):
        raw = "Cost is 50% for R&D on user_id #1"
        escaped = escape_latex(raw)
        self.assertIn(r"50\%", escaped)
        self.assertIn(r"R\&D", escaped)
        self.assertIn(r"user\_id", escaped)
        self.assertIn(r"\#1", escaped)

    def test_preserve_math_and_commands(self):
        raw = r"We use \textbf{bold} and inline math $x_1 + x_2 = 100\%$ formula."
        escaped = escape_latex(raw)
        self.assertIn(r"\textbf{bold}", escaped)
        self.assertIn(r"$x_1 + x_2 = 100\%$", escaped)


class TestParser(unittest.TestCase):
    def test_parse_multi_layout_slides(self):
        content = """---
title: Test Presentation
---

# Test Presentation

## Slide 1: Overview
- Bullet 1
- Bullet 2

## Slide 2: Two Columns
::: columns
::: column
- Left item
::: column
- Right item
:::

## Slide 3: Code Demo
```python
def hello():
    return "world"
```

## Slide 4: Alert Callout
> [!ALERT] Warning Notice
> Do not touch the red wire.
"""
        meta, slides = parse_slides(content)
        self.assertEqual(meta.get("title"), "Test Presentation")
        self.assertEqual(len(slides), 4)
        self.assertEqual(slides[0].layout, "standard")
        self.assertEqual(slides[1].layout, "columns")
        self.assertEqual(len(slides[1].columns), 2)
        self.assertEqual(slides[2].layout, "code")
        self.assertTrue(slides[2].is_fragile)
        self.assertEqual(slides[3].layout, "block")
        self.assertEqual(slides[3].block_type, "alertblock")


class TestTemplateEngine(unittest.TestCase):
    def test_extract_preamble_and_inject(self):
        template = r"""\documentclass{beamer}
\usetheme{metropolis}
\title{Old Title}
\begin{document}
% {{SLIDES}}
\end{document}
"""
        preamble = extract_preamble(template)
        self.assertIn(r"\documentclass{beamer}", preamble)
        self.assertIn(r"\usetheme{metropolis}", preamble)

        archetypes = detect_archetypes(template)
        self.assertEqual(archetypes["theme"], "metropolis")
        self.assertTrue(archetypes["has_placeholder"])

        injected = inject_content(template, r"\begin{frame}\frametitle{New}\end{frame}")
        self.assertIn(r"\frametitle{New}", injected)


class TestSlideBuilderAndReviewer(unittest.TestCase):
    def test_build_and_review(self):
        s1 = Slide(title="Test Slide", bullets=["Point A", "Point B"])
        s2 = Slide(title="Code Slide", layout="code", code_content="print(1)", is_fragile=True)
        tex = build_presentation({"title": "Deck"}, [s1, s2])
        self.assertIn(r"\frametitle{Test Slide}", tex)
        self.assertIn(r"[fragile]", tex)

        report = review_presentation(tex, [s1, s2])
        self.assertTrue(report.valid)
        self.assertEqual(len(report.errors), 0)

    def test_reviewer_catches_missing_fragile(self):
        bad_tex = r"""
\begin{frame}
  \begin{semiverbatim}
  some_code()
  \end{semiverbatim}
\end{frame}
"""
        report = review_presentation(bad_tex)
        self.assertFalse(report.valid)
        self.assertTrue(any("fragile" in e for e in report.errors))


class TestCompilerSelfHealing(unittest.TestCase):
    def test_self_healing_missing_fragile(self):
        broken = r"\begin{frame}\n\begin{semiverbatim}code\end{semiverbatim}\n\end{frame}"
        errors = [{"message": "semiverbatim in non-fragile frame"}]
        fixed = self_heal_tex(broken, errors)
        self.assertIn(r"\begin{frame}[fragile]", fixed)


class TestEndToEndPipeline(unittest.TestCase):
    def test_e2e_run(self):
        root = Path(__file__).resolve().parent.parent
        output_d = root / "digestion" / "test_out"
        digestion_d = root / "digestion" / "test_dig"
        output_d.mkdir(parents=True, exist_ok=True)
        digestion_d.mkdir(parents=True, exist_ok=True)

        input_f = digestion_d / "test_sample.md"
        input_f.write_text(
            "---\ntitle: Sample Test Deck\nauthor: Antigravity\n---\n# Slide One\n- Point A\n- Point B\n",
            encoding="utf-8",
        )
        template_f = digestion_d / "test_template.tex"
        template_f.write_text(
            r"\documentclass{beamer}\begin{document}\title{Title}\maketitle % CONTENT_PLACEHOLDER \end{document}",
            encoding="utf-8",
        )

        res = run_pipeline(
            input_file=str(input_f),
            template_file=str(template_f),
            output_dir=str(output_d),
            digestion_dir=str(digestion_d),
        )

        self.assertIn(res["status"], ["success", "tex_generated"])
        self.assertTrue((digestion_d / "test_sample_digested.json").exists())
        self.assertTrue((digestion_d / "test_sample_review.json").exists())
        self.assertTrue((output_d / "test_sample.tex").exists())

        # Cleanup test files
        import shutil
        shutil.rmtree(output_d, ignore_errors=True)
        shutil.rmtree(digestion_d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
