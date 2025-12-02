import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import control as ctrl
from config import TAU_S, TAU_P, SETPOINT
import os

os.makedirs('output', exist_ok=True)


def questao2_controle_proporcional(Ks=1.0, Kp=1.0):
    print("\n" + "="*80)
    print("QUESTÃO 2: CONTROLE PROPORCIONAL")
    K = Ks * Kp
    num = [K]
    den = np.convolve([TAU_S, 1], [TAU_P, 1])
    G = signal.TransferFunction(num, den)
    G_ctrl = ctrl.TransferFunction(num, den)
    print(f"\nParâmetros: Ks={Ks}, Kp={Kp}, K={K}")
    print(f"τs = {TAU_S} dias, τp = {TAU_P} dias")
    
    # 2b) Lugar das Raízes e estabilidade
    print("\n" + "-"*80)
    print("2b) Lugar das Raízes - Intervalo de Estabilidade")
    print("-"*80)
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    ctrl.root_locus(G_ctrl, grid=True)
    plt.title('Lugar das Raízes - Controle P')
    plt.xlabel('Parte Real')
    plt.ylabel('Parte Imaginária')
    plt.grid(True, alpha=0.3)
    # Análise de estabilidade
    a2 = TAU_S * TAU_P
    a1 = TAU_S + TAU_P
    a0_base = 1
    
    print(f"\nPolinômio característico: {a2:.1f}s² + {a1:.1f}s + (1 + Kc·{K})")
    print(f"\nCritério de Routh-Hurwitz:")
    print(f"  a2 = {a2:.1f} > 0 ")
    print(f"  a1 = {a1:.1f} > 0 ")
    print(f"  a0 = 1 + Kc·{K} > 0  ->  Kc > {-1/K:.3f}")
    print(f"\nPara sistema de 2ª ordem com todos coeficientes positivos:")
    print(f"  Sistema é SEMPRE ESTÁVEL para Kc > {-1/K:.3f}")
    print(f"  Intervalo prático:  Kc >0")
    
    # 2c) Projeto do ganho proporcional
    print("\n" + "-"*80)
    print("2c) Projeto do Ganho Proporcional")
    print("-"*80)
    print("""
    Especificações agronômicas:
      - NDVI de referência: 0,75
      - NDVI mínimo em regime permanente: ≥ 0,65
      - NDVI máximo no transitório: ≤ 0,85
      - Tempo de acomodação: < 30 dias
    """)
    
    # Análise de diferentes ganhos
    Kc_values = np.linspace(0.5, 15, 50)
    results = []
    for Kc in Kc_values:
        C = signal.TransferFunction([Kc], [1])
        num_cl = np.polymul(C.num, G.num)
        den_cl = np.polyadd(np.polymul(C.den, G.den), num_cl)
        T = signal.TransferFunction(num_cl, den_cl)
        t = np.linspace(0, 150, 1000)
        _, y = signal.step(T, T=t)
        y = y * SETPOINT
        y_ss = y[-1]
        y_max = np.max(y)
        # Tempo de acomodação (2%)
        tolerance = 0.02 * y_ss
        settling_idx = np.where(np.abs(y - y_ss) <= tolerance)[0]
        if len(settling_idx) > 0:
            for idx in settling_idx:
                if np.all(np.abs(y[idx:] - y_ss) <= tolerance):
                    ts = t[idx]
                    break
            else:
                ts = np.inf
        else:
            ts = np.inf
        # Verifica critérios
        criterio_min = y_ss >= 0.65
        criterio_max = y_max <= 0.85
        criterio_ts = ts < 30
        results.append({
            'Kc': Kc,
            'y_ss': y_ss,
            'y_max': y_max,
            'ts': ts,
            'atende': criterio_min and criterio_max and criterio_ts
        })
    # Encontra melhores valores
    valid_results = [r for r in results if r['atende']]
    if valid_results:
        best = min(valid_results, key=lambda x: x['ts'])
        Kc_best = best['Kc']
        print(f"\nGanho proporcional projetado: Kc = {Kc_best:.3f}")
        print(f" NDVI regime permanente: {best['y_ss']:.4f}")
        print(f" NDVI máximo (transitório): {best['y_max']:.4f}")
        print(f" Tempo de acomodação: {best['ts']:.2f} dias")
    else:
        Kc_best = 6.5
        print(f"\n⚠ Usando valor típico: Kc = {Kc_best}")
    # Gráfico de análise
    plt.subplot(1, 2, 2)
    Kc_plot = [r['Kc'] for r in results]
    ts_plot = [r['ts'] if r['ts'] < 100 else 100 for r in results]
    yss_plot = [r['y_ss'] for r in results]
    plt.plot(Kc_plot, ts_plot, 'b-', label='Ts (dias)', linewidth=2)
    plt.axhline(30, color='r', linestyle='--', label='Ts máximo (30 dias)')
    plt.xlabel('Ganho Kc')
    plt.ylabel('Tempo de Acomodação (dias)')
    plt.title('Análise do Ganho Proporcional')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xlim([0, 15])
    plt.tight_layout()
    plt.savefig('output/questao2b_lugar_raizes_P.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2d) Resposta ao degrau
    print("\n" + "-"*80)
    print("2d) Resposta ao Degrau")
    print("-"*80)
    plt.figure(figsize=(12, 6))
    t = np.linspace(0, 150, 1000)
    # Sem controle (malha aberta)
    _, y_open = signal.step(G, T=t)
    y_open = y_open * SETPOINT
    plt.plot(t, y_open, 'k--', linewidth=2, label='Sem Controle (Malha Aberta)', alpha=0.7)
    # Com controle P
    C = signal.TransferFunction([Kc_best], [1])
    num_cl = np.polymul(C.num, G.num)
    den_cl = np.polyadd(np.polymul(C.den, G.den), num_cl)
    T = signal.TransferFunction(num_cl, den_cl)
    _, y_cl = signal.step(T, T=t)
    y_cl = y_cl * SETPOINT
    plt.plot(t, y_cl, 'b-', linewidth=2.5, label=f'Controle P (Kc={Kc_best:.2f})')
    # Limites agronômicos
    plt.axhline(SETPOINT, color='g', linestyle=':', linewidth=2, label='Referência (0,75)', alpha=0.8)
    plt.axhline(0.65, color='r', linestyle='-.', linewidth=1.5, label='Limite Mínimo (0,65)', alpha=0.6)
    plt.axhline(0.85, color='r', linestyle='-.', linewidth=1.5, label='Limite Máximo (0,85)', alpha=0.6)
    plt.fill_between(t, 0.65, 0.85, color='green', alpha=0.1, label='Faixa Segura')
    plt.xlabel('Tempo (dias)', fontsize=12)
    plt.ylabel('NDVI', fontsize=12)
    plt.title('Resposta ao Degrau - Controle Proporcional', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10, loc='best')
    plt.xlim([0, 150])
    plt.ylim([0, 1])
    plt.tight_layout()
    plt.savefig('output/questao2d_resposta_P.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Resposta ao degrau salva em: output/questao2d_resposta_P.png")
    return Kc_best


if __name__ == "__main__":
    Kc = questao2_controle_proporcional(Ks=1.0, Kp=1.0)
    print(f"\n{'='*80}")
    print(f"Ganho proporcional ótimo: Kc = {Kc:.3f}")
    print(f"{'='*80}")
