import pytest

from app.prompt.context import PromptContext, ContextKeyError


def test_set_and_get_flat_key():
    ctx = PromptContext()
    ctx.set("diff", "abc")
    assert ctx.get("diff") == "abc"


def test_set_and_get_dot_path_creates_nested_dicts():
    ctx = PromptContext()
    ctx.set("git.diff", "patch")
    assert ctx.get("git.diff") == "patch"
    assert ctx.to_dict() == {"git": {"diff": "patch"}}


def test_get_missing_key_raises_clean_error():
    ctx = PromptContext()
    with pytest.raises(ContextKeyError) as e:
        ctx.get("missing.key")
    assert "missing.key" in str(e.value)


def test_get_missing_key_returns_default_if_provided():
    ctx = PromptContext()
    assert ctx.get("missing.key", default=None) is None


def test_update_sets_multiple_keys():
    ctx = PromptContext()
    ctx.update({"diff": "d1", "repo.name": "myrepo"})
    assert ctx.get("diff") == "d1"
    assert ctx.get("repo.name") == "myrepo"


def test_set_raises_if_mid_path_is_not_dict():
    ctx = PromptContext()
    ctx.set("repo", "not-a-dict")
    with pytest.raises(TypeError):
        ctx.set("repo.name", "x")
