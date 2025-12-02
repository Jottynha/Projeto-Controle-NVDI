import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import control as ctrl
from config import TAU_S, TAU_P, SETPOINT
import os

os.makedirs('output', exist_ok=True)


def questao4_controle_PD(Ks=1.0, Kp=1.0, Kc_P_base=None):
    print("\n" + "="*80)
    print("QUESTÃO 4: CONTROLE PROPORCIONAL-DERIVATIVO (PD)")
    print("="*80)
    
    K = Ks * Kp
    num = [K]
    den = np.convolve([TAU_S, 1], [TAU_P, 1])
    G = signal.TransferFunction(num, den)
    G_ctrl = ctrl.TransferFunction(num, den)
    # Se não foi fornecido Kc base, calcular
    if Kc_P_base is None:
        print("\nCalculando Kc base do controle P...")
        Kc_P_base = 6.5
    
    print(f"\nParâmetros: Ks={Ks}, Kp={Kp}, K={K}")
    print(f"Kc base (do controle P): {Kc_P_base:.3f}")
    
    
    
    # 4b) Projeto do PD
    print("\n" + "-"*80)
    print("4b) Projeto do Controlador PD")
    print("-"*80)
    print("""
    Especificações:
      • Reduzir Ts em pelo menos 20% em relação ao controle P
      • Sobressinal máximo: y_max < 0,85
    """)
    
    # Resposta com controle P base
    C_P = signal.TransferFunction([Kc_P_base], [1])
    num_P = np.polymul(C_P.num, G.num)
    den_P = np.polyadd(np.polymul(C_P.den, G.den), num_P)
    T_P = signal.TransferFunction(num_P, den_P)
    t = np.linspace(0, 150, 1500)
    _, y_P = signal.step(T_P, T=t)
    y_P = y_P * SETPOINT
    # Calcular Ts do P
    y_ss_P = y_P[-1]
    tolerance = 0.02 * y_ss_P
    settling_idx = np.where(np.abs(y_P - y_ss_P) <= tolerance)[0]
    ts_P = np.inf
    if len(settling_idx) > 0:
        for idx in settling_idx:
            if np.all(np.abs(y_P[idx:] - y_ss_P) <= tolerance):
                ts_P = t[idx]
                break
    
    print(f"\nDesempenho do controle P (base):")
    print(f"Ts = {ts_P:.2f} dias")
    print(f"Meta Ts (PD): < {0.8 * ts_P:.2f} dias (redução de 20%)")
    # Busca de Td ótimo
    Td_range = np.linspace(0.5, 10, 30)
    results = []
    for Td in Td_range:
        for Kc in np.linspace(Kc_P_base * 0.8, Kc_P_base * 1.5, 15):
            C_PD = signal.TransferFunction([Kc*Td, Kc], [1])
            num_PD = np.polymul(C_PD.num, G.num)
            den_PD = np.polyadd(np.polymul(C_PD.den, G.den), num_PD)
            T_PD = signal.TransferFunction(num_PD, den_PD)
            try:
                _, y_PD = signal.step(T_PD, T=t)
                y_PD = y_PD * SETPOINT
                y_ss = y_PD[-1]
                y_max = np.max(y_PD)
                # Ts
                tol = 0.02 * y_ss
                idx_settle = np.where(np.abs(y_PD - y_ss) <= tol)[0]
                ts = np.inf
                if len(idx_settle) > 0:
                    for idx in idx_settle:
                        if np.all(np.abs(y_PD[idx:] - y_ss) <= tol):
                            ts = t[idx]
                            break
                # Critérios
                if ts < 0.8 * ts_P and y_max <= 0.85:
                    results.append({
                        'Kc': Kc,
                        'Td': Td,
                        'ts': ts,
                        'y_max': y_max,
                        'reducao': (1 - ts/ts_P) * 100
                    })
            except:
                continue
    if results:
        best = min(results, key=lambda x: x['ts'])
        Kc_best = best['Kc']
        Td_best = best['Td']
    else:
        Kc_best = Kc_P_base
        Td_best = 2.0
    print(f"\nParâmetros projetados:")
    print(f"Kc = {Kc_best:.3f}")
    print(f"Td = {Td_best:.3f} dias")
    if results:
        print(f"\nDesempenho:")
        print(f"Ts = {best['ts']:.2f} dias")
        print(f"y_max = {best['y_max']:.4f}")
        print(f"Redução de Ts: {best['reducao']:.1f}%")

    # 4c) Ruído e filtro derivativo
    print("\n" + "-"*80)
    print("4c) Termo Derivativo - Ruído e Filtragem")
    print("-"*80)
    # Demonstração do efeito do ruído
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    # Simular NDVI com ruído
    np.random.seed(42)
    t_sim = np.linspace(0, 100, 2000)
    # Sinal limpo
    C_PD = signal.TransferFunction([Kc_best*Td_best, Kc_best], [1])
    num_cl = np.polymul(C_PD.num, G.num)
    den_cl = np.polyadd(np.polymul(C_PD.den, G.den), num_cl)
    T_PD = signal.TransferFunction(num_cl, den_cl)
    _, y_clean = signal.step(T_PD, T=t_sim)
    y_clean = y_clean * SETPOINT
    # Adicionar ruído
    noise_level = 0.02
    y_noisy = y_clean + np.random.normal(0, noise_level, len(y_clean))
    axes[0, 0].plot(t_sim, y_clean, 'b-', linewidth=2, label='Sem ruído')
    axes[0, 0].plot(t_sim, y_noisy, 'r-', alpha=0.5, linewidth=0.5, label='Com ruído')
    axes[0, 0].set_xlabel('Tempo (dias)')
    axes[0, 0].set_ylabel('NDVI')
    axes[0, 0].set_title('Medição de NDVI com Ruído')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Resposta de Bode - PD vs PD filtrado
    w = np.logspace(-3, 2, 500)
    # PD ideal
    C_PD_ctrl = ctrl.TransferFunction([Td_best, 1], [1])
    mag_pd, phase_pd, _ = ctrl.bode(C_PD_ctrl, w, plot=False)
    # PD filtrado (N=10)
    N = 10
    tau_f = Td_best / N
    C_PD_filt = ctrl.TransferFunction([Td_best + tau_f, 1], [tau_f, 1])
    mag_filt, phase_filt, _ = ctrl.bode(C_PD_filt, w, plot=False)
    axes[0, 1].semilogx(w, 20*np.log10(mag_pd), 'b-', linewidth=2, label='PD ideal')
    axes[0, 1].semilogx(w, 20*np.log10(mag_filt), 'r-', linewidth=2, label=f'PD filtrado (N={N})')
    axes[0, 1].set_xlabel('Frequência (rad/dia)')
    axes[0, 1].set_ylabel('Magnitude (dB)')
    axes[0, 1].set_title('Bode - PD Ideal vs Filtrado')
    axes[0, 1].legend()
    axes[0, 1].grid(True, which='both', alpha=0.3)
    
    # 4d) LGR mostrando efeito do zero
    print("\n" + "-"*80)
    print("4d) Lugar das Raízes - Efeito do Zero Derivativo")
    print("-"*80)
    
    # LGR sem derivativo (P)
    ctrl.root_locus(G_ctrl, grid=True, ax=axes[1, 0])
    axes[1, 0].set_title('LGR - Controle P (sem zero)')
    axes[1, 0].grid(True, alpha=0.3)
    # LGR com derivativo (PD)
    C_ctrl = ctrl.TransferFunction([Td_best, 1], [1])
    L_PD = ctrl.series(C_ctrl, G_ctrl)
    ctrl.root_locus(L_PD, grid=True, ax=axes[1, 1])
    axes[1, 1].set_title(f'LGR - Controle PD (zero em s=-{1/Td_best:.3f})')
    axes[1, 1].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/questao4_analise_PD.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4e) Margem de fase com Td elevado
    print("\n" + "-"*80)
    print("4e) Margem de Fase vs Td")
    print("-"*80)
    
    Td_test = [0.5, 2.0, 5.0, 10.0, 20.0]
    margins = []
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    for Td in Td_test:
        C_test = ctrl.TransferFunction([Td, 1], [1])
        L_test = ctrl.series(C_test, G_ctrl)
        gm, pm, wg, wp = ctrl.margin(L_test)
        margins.append({'Td': Td, 'PM': pm, 'GM': gm})
        mag, phase, w = ctrl.bode(L_test, plot=False)
        ax1.semilogx(w, 20*np.log10(mag), label=f'Td={Td}')
    ax1.axhline(0, color='k', linestyle='--', linewidth=1)
    ax1.set_xlabel('Frequência (rad/dia)')
    ax1.set_ylabel('Magnitude (dB)')
    ax1.set_title('Bode - Variação de Td')
    ax1.legend()
    ax1.grid(True, which='both', alpha=0.3)
    Td_plot = [m['Td'] for m in margins]
    PM_plot = [m['PM'] for m in margins]
    ax2.plot(Td_plot, PM_plot, 'bo-', linewidth=2, markersize=8)
    ax2.set_xlabel('Td (dias)')
    ax2.set_ylabel('Margem de Fase (graus)')
    ax2.set_title('Margem de Fase vs Td')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(45, color='r', linestyle='--', label='PM mínima (45°)')
    ax2.legend()
    plt.tight_layout()
    plt.savefig('output/questao4e_margem_fase.png', dpi=300, bbox_inches='tight')
    plt.close()

    
    # Comparação final P vs PD
    fig, ax = plt.subplots(figsize=(12, 6))    
    t_final = np.linspace(0, 150, 1000)
    # Sem controle
    _, y_open = signal.step(G, T=t_final)
    y_open = y_open * SETPOINT
    ax.plot(t_final, y_open, 'k--', linewidth=2, label='Sem Controle', alpha=0.7)
    # P
    _, y_P_final = signal.step(T_P, T=t_final)
    y_P_final = y_P_final * SETPOINT
    ax.plot(t_final, y_P_final, 'b-', linewidth=2, label=f'P (Kc={Kc_P_base:.2f})')
    # PD
    C_PD_final = signal.TransferFunction([Kc_best*Td_best, Kc_best], [1])
    num_pd = np.polymul(C_PD_final.num, G.num)
    den_pd = np.polyadd(np.polymul(C_PD_final.den, G.den), num_pd)
    T_PD_final = signal.TransferFunction(num_pd, den_pd)
    _, y_PD_final = signal.step(T_PD_final, T=t_final)
    y_PD_final = y_PD_final * SETPOINT
    ax.plot(t_final, y_PD_final, 'g-', linewidth=2.5, label=f'PD (Kc={Kc_best:.2f}, Td={Td_best:.2f})')
    ax.axhline(SETPOINT, color='r', linestyle=':', linewidth=2, label='Referência (0,75)')
    ax.fill_between(t_final, 0.65, 0.85, color='green', alpha=0.1)
    ax.set_xlabel('Tempo (dias)', fontsize=12)
    ax.set_ylabel('NDVI', fontsize=12)
    ax.set_title('Comparação: P vs PD', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    ax.set_xlim([0, 150])
    ax.set_ylim([0, 1])
    plt.tight_layout()
    plt.savefig('output/questao4_comparacao_P_PD.png', dpi=300, bbox_inches='tight')
    plt.close()
    return Kc_best, Td_best


if __name__ == "__main__":
    Kc, Td = questao4_controle_PD(Ks=1.0, Kp=1.0, Kc_P_base=6.5)
    print(f"\n{'='*80}")
    print(f"Parâmetros PD ótimos: Kc = {Kc:.3f}, Td = {Td:.3f} dias")
    print(f"{'='*80}")
