
import sys
import os
from datetime import datetime

os.makedirs('output', exist_ok=True)

# Importar módulos das questões
from questao2 import questao2_controle_proporcional
from questao3 import questao3_controle_PI
from questao4 import questao4_controle_PD
from questao5 import questao5_controle_PID


def criar_relatorio_header():
    """Cria cabeçalho do relatório"""
    print("\n" + "="*80)
    print(" "*20 + "PROJETO DE CONTROLE DE IRRIGAÇÃO")
    print(" "*25 + "BASEADO EM NDVI")
    print("="*80)
    print(f"\nData de execução: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("Disciplina: Teoria de Controle")
    print("Tema: Controle de Irrigação em Pomar de Citros")
    print("\n" + "="*80)


def executar_todas_questoes():
    criar_relatorio_header()
    # Parâmetros do sistema
    Ks = 1.0
    Kp = 1.0
    print("\n\nIniciando resolução das questões...")
    print("-"*80)
    try:
        # QUESTÃO 2: Controle Proporcional
        print("\n\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + " "*25 + "QUESTÃO 2" + " "*44 + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        Kc_P = questao2_controle_proporcional(Ks=Ks, Kp=Kp)
        input("\nPressione ENTER para continuar para a Questão 3...")
        
        # QUESTÃO 3: Controle PI
        print("\n\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + " "*25 + "QUESTÃO 3" + " "*44 + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        Kc_PI, Ti_PI = questao3_controle_PI(Ks=Ks, Kp=Kp)
        input("\nPressione ENTER para continuar para a Questão 4...")
        
        # QUESTÃO 4: Controle PD
        print("\n\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + " "*25 + "QUESTÃO 4" + " "*44 + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        Kc_PD, Td_PD = questao4_controle_PD(Ks=Ks, Kp=Kp, Kc_P_base=Kc_P)
        input("\nPressione ENTER para continuar para a Questão 5...")
        
        # QUESTÃO 5: Controle PID
        print("\n\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + " "*25 + "QUESTÃO 5" + " "*44 + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        Kc_PID, Ti_PID, Td_PID = questao5_controle_PID(Ks=Ks, Kp=Kp)
        
        # RESUMO FINAL
        print("\n\n" + "="*80)
        print(" "*25 + "RESUMO FINAL - PARÂMETROS")
        print("="*80)
        
        print("\n┌" + "─"*78 + "┐")
        print("│" + " "*25 + "CONTROLADORES PROJETADOS" + " "*29 + "│")
        print("├" + "─"*78 + "┤")
        print(f"│  Controle P:   Kc = {Kc_P:.3f}" + " "*(60-len(f"Kc = {Kc_P:.3f}")) + "│")
        print(f"│  Controle PI:  Kc = {Kc_PI:.3f},  Ti = {Ti_PI:.3f} dias" + " "*(40-len(f"Kc = {Kc_PI:.3f},  Ti = {Ti_PI:.3f} dias")) + "│")
        print(f"│  Controle PD:  Kc = {Kc_PD:.3f},  Td = {Td_PD:.3f} dias" + " "*(40-len(f"Kc = {Kc_PD:.3f},  Td = {Td_PD:.3f} dias")) + "│")
        print(f"│  Controle PID: Kc = {Kc_PID:.3f},  Ti = {Ti_PID:.3f},  Td = {Td_PID:.3f} dias" + " "*(29-len(f"Kc = {Kc_PID:.3f},  Ti = {Ti_PID:.3f},  Td = {Td_PID:.3f} dias")) + "│")
        print("└" + "─"*78 + "┘")
        
        print("\n" + "="*80)
        print(" "*20 + "TODOS OS ARQUIVOS FORAM GERADOS!")
        print("="*80)
        
        print("\nArquivos gerados:")
        arquivos = [
            "output/questao1_diagrama_blocos.png",
            "output/questao2b_lugar_raizes_P.png",
            "output/questao2d_resposta_P.png",
            "output/questao3c_resposta_PI.png",
            "output/questao3d_lgr_bode_PI.png",
            "output/questao4_analise_PD.png",
            "output/questao4e_margem_fase.png",
            "output/questao4_comparacao_P_PD.png",
            "output/questao5c_resposta_PID.png",
            "output/questao5d_bode_integral.png",
            "output/questao5e_comparacao_final.png"
        ]
        
        for i, arquivo in enumerate(arquivos, 1):
            if os.path.exists(arquivo):
                print(f"{i:2d}. {arquivo}")
            else:
                print(f"{i:2d}. {arquivo} (não encontrado)")
        
        print("\n" + "="*80)
        print("Projeto concluído com sucesso!")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n\nERRO durante a execução: {e}")
        import traceback
        traceback.print_exc()
        return False


def menu_interativo():
    """Menu para escolher quais questões executar"""
    while True:
        print("\n" + "="*80)
        print(" "*20 + "SISTEMA DE CONTROLE DE IRRIGAÇÃO - NDVI")
        print("="*80)
        print("\nEscolha uma opção:")
        print("  1 - Executar TODAS as questões em sequência")
        print("  2 - Executar Questão 2 (Controle P)")
        print("  3 - Executar Questão 3 (Controle PI)")
        print("  4 - Executar Questão 4 (Controle PD)")
        print("  5 - Executar Questão 5 (Controle PID)")
        print("  0 - Sair")
        print("="*80)
        
        escolha = input("\nOpção: ").strip()
        
        if escolha == "0":
            print("\nEncerrando...")
            break
        elif escolha == "1":
            executar_todas_questoes()
            break
        elif escolha == "2":
            criar_relatorio_header()
            questao2_controle_proporcional(Ks=1.0, Kp=1.0)
        elif escolha == "3":
            criar_relatorio_header()
            questao3_controle_PI(Ks=1.0, Kp=1.0)
        elif escolha == "4":
            criar_relatorio_header()
            questao4_controle_PD(Ks=1.0, Kp=1.0, Kc_P_base=6.5)
        elif escolha == "5":
            criar_relatorio_header()
            questao5_controle_PID(Ks=1.0, Kp=1.0)
        else:
            print("\nOpção inválida! Tente novamente.")
        if escolha in ["2", "3", "4", "5", "6"]:
            input("\nPressione ENTER para voltar ao menu...")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        # Modo não-interativo: executa tudo
        executar_todas_questoes()
    else:
        # Modo interativo: menu
        menu_interativo()
