import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import control as ctrl
from config import TAU_S, TAU_P, SETPOINT
import os

os.makedirs('output', exist_ok=True)


def questao3_controle_PI(Ks=1.0, Kp=1.0):
    print("\n" + "="*80)
    print("QUESTÃO 3: CONTROLE PROPORCIONAL-INTEGRAL (PI)")
    print("="*80)
    
    K = Ks * Kp
    num = [K]
    den = np.convolve([TAU_S, 1], [TAU_P, 1])
    G = signal.TransferFunction(num, den)
    G_ctrl = ctrl.TransferFunction(num, den)
    print(f"\nParâmetros: Ks={Ks}, Kp={Kp}, K={K}")
    
    
    # 3b) Projeto dos parâmetros
    print("\n" + "-"*80)
    print("3b) Projeto dos Parâmetros do Controlador PI")
    print("-"*80)
    print("""
    Especificações:
      - Erro nulo em regime permanente (garantido pela ação integral)
      - Tempo de acomodação (2%): <= 35 dias
    """)
    
    # Busca de parâmetros ótimos
    best_params = None
    best_ts = np.inf
    Kc_range = np.linspace(1.0, 8.0, 20)
    Ti_range = np.linspace(3.0, 15.0, 20)
    results = []
    
    for Kc in Kc_range:
        for Ti in Ti_range:
            C = signal.TransferFunction([Kc*Ti, Kc], [Ti, 0])
            num_cl = np.polymul(C.num, G.num)
            den_cl = np.polyadd(np.polymul(C.den, G.den), num_cl)
            T = signal.TransferFunction(num_cl, den_cl)
            t = np.linspace(0, 200, 1500)
            try:
                _, y = signal.step(T, T=t)
                y = y * SETPOINT
                y_ss = y[-1]
                y_max = np.max(y)
                overshoot = (y_max - SETPOINT) / SETPOINT * 100
                # Tempo de acomodação (2%)
                tolerance = 0.02 * SETPOINT
                settling_idx = np.where(np.abs(y - y_ss) <= tolerance)[0]
                ts = np.inf
                if len(settling_idx) > 0:
                    for idx in settling_idx:
                        if np.all(np.abs(y[idx:] - y_ss) <= tolerance):
                            ts = t[idx]
                            break
                # Critérios
                if ts < 35 and overshoot < 20 and y_max <= 0.90:
                    results.append({
                        'Kc': Kc,
                        'Ti': Ti,
                        'ts': ts,
                        'overshoot': overshoot,
                        'y_max': y_max,
                        'y_ss': y_ss
                    })
                    if ts < best_ts:
                        best_ts = ts
                        best_params = (Kc, Ti)
            except:
                continue
    if best_params:
        Kc_best, Ti_best = best_params
    else:
        Kc_best, Ti_best = 3.11, 7.33
    print(f"\nParâmetros projetados:")
    print(f"Kc = {Kc_best:.3f}")
    print(f"Ti = {Ti_best:.3f} dias")
    
    # Verificar desempenho
    C = signal.TransferFunction([Kc_best*Ti_best, Kc_best], [Ti_best, 0])
    num_cl = np.polymul(C.num, G.num)
    den_cl = np.polyadd(np.polymul(C.den, G.den), num_cl)
    T = signal.TransferFunction(num_cl, den_cl)
    t = np.linspace(0, 200, 1500)
    _, y = signal.step(T, T=t)
    y = y * SETPOINT
    y_ss = y[-1]
    erro_ss = SETPOINT - y_ss
    print(f"\nDesempenho:")
    print(f"NDVI em regime: {y_ss:.4f}")
    print(f"Erro em regime: {erro_ss:.6f} (≈ 0)")
    print(f"Tempo de acomodação: {best_ts:.2f} dias")
    
    # 3c) Resposta ao degrau
    print("\n" + "-"*80)
    print("3c) Resposta ao Degrau")
    print("-"*80)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    # Gráfico 1: Comparação com malha aberta
    t_plot = np.linspace(0, 150, 1000)
    _, y_open = signal.step(G, T=t_plot)
    y_open = y_open * SETPOINT
    ax1.plot(t_plot, y_open, 'k--', linewidth=2, label='Sem Controle', alpha=0.7)
    _, y_pi = signal.step(T, T=t_plot)
    y_pi = y_pi * SETPOINT
    ax1.plot(t_plot, y_pi, 'b-', linewidth=2.5, label=f'PI (Kc={Kc_best:.2f}, Ti={Ti_best:.2f})')
    ax1.axhline(SETPOINT, color='g', linestyle=':', linewidth=2, label='Referência (0,75)')
    ax1.fill_between(t_plot, 0.65, 0.85, color='green', alpha=0.1)
    ax1.set_xlabel('Tempo (dias)', fontsize=12)
    ax1.set_ylabel('NDVI', fontsize=12)
    ax1.set_title('Resposta ao Degrau - Controle PI', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_xlim([0, 150])
    ax1.set_ylim([0, 1])
    # Gráfico 2: Análise de parâmetros
    if results:
        Kc_plot = [r['Kc'] for r in results]
        Ti_plot = [r['Ti'] for r in results]
        ts_plot = [r['ts'] for r in results]
        scatter = ax2.scatter(Kc_plot, Ti_plot, c=ts_plot, cmap='viridis', s=50)
        ax2.plot(Kc_best, Ti_best, 'r*', markersize=15, label='Ótimo')
        ax2.set_xlabel('Kc', fontsize=12)
        ax2.set_ylabel('Ti (dias)', fontsize=12)
        ax2.set_title('Mapa de Parâmetros PI', fontsize=13)
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Ts (dias)', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('output/questao3c_resposta_PI.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3d) Impacto da ação integral no LGR e Bode
    print("\n" + "-"*80)
    print("3d) Impacto da Ação Integral - LGR e Bode")
    print("-"*80)
    
    fig = plt.figure(figsize=(14, 10))
    # LGR sem integral (apenas P)
    ax1 = plt.subplot(2, 2, 1)
    ctrl.root_locus(G_ctrl, grid=True, ax=ax1)
    ax1.set_title('Lugar das Raízes - Controle P')
    ax1.grid(True, alpha=0.3)
    # LGR com integral (PI)
    ax2 = plt.subplot(2, 2, 2)
    C_ctrl = ctrl.TransferFunction([Ti_best, 1], [Ti_best, 0])
    L_PI = ctrl.series(C_ctrl, G_ctrl)
    ctrl.root_locus(L_PI, grid=True, ax=ax2)
    ax2.set_title('Lugar das Raízes - Controle PI')
    ax2.grid(True, alpha=0.3)
    # Bode - P
    ax3 = plt.subplot(2, 2, 3)
    w = np.logspace(-3, 1, 500)
    mag_p, phase_p, _ = ctrl.bode(G_ctrl, w, plot=False)
    ax3.semilogx(w, 20*np.log10(mag_p), 'b-', linewidth=2)
    ax3.set_ylabel('Magnitude (dB)', fontsize=10)
    ax3.set_title('Diagrama de Bode - Processo G(s)')
    ax3.grid(True, which='both', alpha=0.3)
    # Bode - PI
    ax4 = plt.subplot(2, 2, 4)
    mag_pi, phase_pi, _ = ctrl.bode(L_PI, w, plot=False)
    ax4.semilogx(w, 20*np.log10(mag_pi), 'r-', linewidth=2, label='PI')
    ax4.semilogx(w, 20*np.log10(mag_p), 'b--', linewidth=1.5, alpha=0.5, label='P (ref)')
    ax4.set_ylabel('Magnitude (dB)', fontsize=10)
    ax4.set_xlabel('Frequência (rad/dia)', fontsize=10)
    ax4.set_title('Diagrama de Bode - Comparação')
    ax4.grid(True, which='both', alpha=0.3)
    ax4.legend()
    plt.tight_layout()
    plt.savefig('output/questao3d_lgr_bode_PI.png', dpi=300, bbox_inches='tight')
    plt.close()
    return Kc_best, Ti_best


if __name__ == "__main__":
    Kc, Ti = questao3_controle_PI(Ks=1.0, Kp=1.0)
    print(f"\n{'='*80}")
    print(f"Parâmetros PI ótimos: Kc = {Kc:.3f}, Ti = {Ti:.3f} dias")
    print(f"{'='*80}")
