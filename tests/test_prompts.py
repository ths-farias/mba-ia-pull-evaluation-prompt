"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_data():
    return load_prompts(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")["bug_to_user_story_v2"]

class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert prompt_data.get("system_prompt", "").strip()

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        text = prompt_data["system_prompt"].lower()
        assert "product manager" in text or "persona" in text

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        text = prompt_data["system_prompt"].lower()
        assert "markdown" in text and "user story" in text

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text = prompt_data["system_prompt"].lower()
        assert text.count("entrada:") >= 2
        assert text.count("saída:") >= 2

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        assert "[todo]" not in " ".join(str(value) for value in prompt_data.values()).lower()

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        assert len(prompt_data.get("techniques_applied", [])) >= 2
        assert validate_prompt_structure(prompt_data)[0]

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
