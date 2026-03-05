import pytest


from app.prompt.loader import prompts


def test_prompts_yaml_loads():
    data = prompts.load()
    assert "assist" in data


@pytest.mark.parametrize(
    "key",
    [
        "assist.explain",
        "assist.review_diff",
        "assist.docstrings",
        "assist.tests",
    ],
)
def test_prompt_bundle_has_system(key):
    bundle = prompts.bundle(key)
    assert bundle.system.strip() != ""


def test_review_diff_has_contract():
    bundle = prompts.bundle("assist.review_diff")
    assert "Suggested Diff" in bundle.output_contract
