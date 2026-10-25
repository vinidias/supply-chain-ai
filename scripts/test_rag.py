import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from rag.llm import answer_question

questions = [
    "Qual o supplier com maior GMV?",
    "Quantos pedidos foram atrasados?",
    "Qual o ticket medio dos pedidos?",
]

for q in questions:
    print("\n" + "="*60)
    print(f"PERGUNTA: {q}")
    print("="*60)
    try:
        answer, sources, model = answer_question(q)
        print(f"Provider: {model}")
        print(f"\nSQL gerado:")
        for s in sources:
            print(f"  {s}")
        print(f"\nResposta:")
        print(f"  {answer}")
    except Exception as e:
        import traceback
        traceback.print_exc()
