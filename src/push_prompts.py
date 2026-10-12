"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def prompt_identifier(prompt_name: str) -> str:
    """Usa handle público quando disponível; caso contrário, nome do workspace."""
    owner = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    return f"{owner}/{prompt_name}" if owner else prompt_name


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        client = Client()
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_data["system_prompt"]),
            ("human", prompt_data["user_prompt"]),
        ])
        client.push_prompt(
            prompt_name,
            object=prompt,
            description=(
                f"{prompt_data.get('description', '')}. "
                f"Técnicas: {', '.join(prompt_data.get('techniques_applied', []))}"
            ),
            tags=prompt_data.get("tags", []),
            is_public=True,
        )
        print(f"[OK] Prompt publicado: {prompt_name}")
        return True
    except Exception as exc:
        print(f"[ERRO] Falha ao publicar {prompt_name}: {exc}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    required = ("description", "system_prompt", "user_prompt", "version")
    errors.extend(f"Campo obrigatório faltando: {field}" for field in required if not prompt_data.get(field))
    if len(prompt_data.get("techniques_applied", [])) < 2:
        errors.append("O prompt deve listar pelo menos 2 técnicas")
    if "{bug_report}" not in prompt_data.get("user_prompt", ""):
        errors.append("user_prompt deve conter {bug_report}")
    return not errors, errors


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPT OTIMIZADO PARA O LANGSMITH HUB")
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    data = load_yaml(str(path))
    if not data or "bug_to_user_story_v2" not in data:
        print(f"[ERRO] Prompt não encontrado em {path}")
        return 1

    prompt_data = data["bug_to_user_story_v2"]
    valid, errors = validate_prompt(prompt_data)
    if not valid:
        print("[ERRO] Prompt inválido:")
        print("\n".join(f"  - {error}" for error in errors))
        return 1

    prompt_name = prompt_identifier(os.getenv("LANGSMITH_PROMPT_NAME", "bug_to_user_story_v2"))
    return 0 if push_prompt_to_langsmith(prompt_name, prompt_data) else 1


if __name__ == "__main__":
    sys.exit(main())
