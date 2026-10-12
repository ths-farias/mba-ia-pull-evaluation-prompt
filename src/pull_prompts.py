"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    client = Client()
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    prompt = client.pull_prompt(
        prompt_name,
        dangerously_pull_public_prompt=True,
    )

    messages = {}
    for message in getattr(prompt, "messages", []):
        prompt_template = getattr(message, "prompt", None)
        if prompt_template is not None:
            role = "system_prompt" if message.__class__.__name__ == "SystemMessagePromptTemplate" else "user_prompt"
            messages[role] = prompt_template.template

    if not messages:
        raise ValueError("O prompt retornado não contém mensagens serializáveis")

    return {
        "bug_to_user_story_v1": {
            "description": "Prompt importado do LangSmith Prompt Hub",
            "system_prompt": messages.get("system_prompt", ""),
            "user_prompt": messages.get("user_prompt", ""),
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPT DO LANGSMITH HUB")
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        data = pull_prompts_from_langsmith()
        output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"
        if not save_yaml(data, str(output_path)):
            return 1
        print(f"[OK] Prompt salvo em {output_path}")
        return 0
    except Exception as exc:
        print(f"[ERRO] Falha ao fazer pull do prompt: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
