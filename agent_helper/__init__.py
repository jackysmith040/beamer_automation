"""
agent_helper
Composable atomic utility toolkit for Beamer slide automation.
"""

from agent_helper.normalizer import normalize_text, extract_frontmatter
from agent_helper.escaper import escape_latex
from agent_helper.parser import parse_slides, Slide
from agent_helper.template_engine import extract_preamble, extract_postamble, detect_archetypes, inject_content
from agent_helper.slide_builder import build_frame, build_presentation
from agent_helper.reviewer import review_presentation, ReviewReport
from agent_helper.compiler import compile_tex, parse_latex_errors, self_heal_tex, find_latex_compiler
from agent_helper.runner import run_pipeline
from agent_helper.reset import reset_workspace

__all__ = [
    "normalize_text",
    "extract_frontmatter",
    "escape_latex",
    "parse_slides",
    "Slide",
    "extract_preamble",
    "extract_postamble",
    "detect_archetypes",
    "inject_content",
    "build_frame",
    "build_presentation",
    "review_presentation",
    "ReviewReport",
    "compile_tex",
    "parse_latex_errors",
    "self_heal_tex",
    "find_latex_compiler",
    "run_pipeline",
    "reset_workspace",
]
