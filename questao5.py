import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import control as ctrl
from config import TAU_S, TAU_P, SETPOINT
import os
os.makedirs('output', exist_ok=True)


def questao5_controle_PID(Ks=1.0, Kp=1.0):
    print("\n" + "="*80)
    print("QUESTÃO 5: CONTROLE PROPORCIONAL-INTEGRAL-DERIVATIVO (PID)")
    print("="*80)
    K = Ks * Kp
    num = [K]
    den = np.convolve([TAU_S, 1], [TAU_P, 1])
    G = signal.TransferFunction(num, den)
    G_ctrl = ctrl.TransferFunction(num, den)
    print(f"\nParâmetros: Ks={Ks}, Kp={Kp}, K={K}")
    
    # 5b) Projeto do PID
    print("\n" + "-"*80)
    print("5b) Projeto dos Parâmetros do Controlador PID")
    print("-"*80)
    print("""
    Especificações:
      • Erro em regime permanente: nulo
      • Faixa de operação: 0,70 ≤ NDVI ≤ 0,85
      • Sobressinal máximo: ≤ 5% (NDVI_max ≤ 0,7875)
      • Tempo de acomodação: < 25 dias
    """)
    
    # Busca otimizada de parâmetros
    best_params = None
    best_score = np.inf
    results = []
    Kc_range = np.linspace(2.0, 8.0, 15)
    Ti_range = np.linspace(10.0, 30.0, 15)
    Td_range = np.linspace(0.1, 5.0, 12)
    print("\nBuscando parâmetros ótimos...")
    for Kc in Kc_range:
        for Ti in Ti_range:
            for Td in Td_range:
                C = signal.TransferFunction([Kc*Ti*Td, Kc*Ti, Kc], [Ti, 0])
                num_cl = np.polymul(C.num, G.num)
                den_cl = np.polyadd(np.polymul(C.den, G.den), num_cl)
                T = signal.TransferFunction(num_cl, den_cl)
                t = np.linspace(0, 200, 2000)
                try:
                    _, y = signal.step(T, T=t)
                    y = y * SETPOINT
                    y_ss = y[-1]
                    y_max = np.max(y)
                    y_min = np.min(y)
                    erro_ss = abs(SETPOINT - y_ss)
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
                    # Verificar critérios
                    if (erro_ss < 0.001 and 
                        y_max <= 0.7875 and 
                        y_min >= 0.70 and 
                        ts < 25 and
                        overshoot <= 5):
                        # Função objetivo: minimizar Ts e overshoot
                        score = ts + 2*overshoot
                        results.append({
                            'Kc': Kc,
                            'Ti': Ti,
                            'Td': Td,
                            'ts': ts,
                            'overshoot': overshoot,
                            'y_max': y_max,
                            'y_ss': y_ss,
                            'score': score
                        })
                        if score < best_score:
                            best_score = score
                            best_params = (Kc, Ti, Td)
                except:
                    continue
    if best_params:
        Kc_best, Ti_best, Td_best = best_params
        best_result = min(results, key=lambda x: x['score'])
    else:
        # Valores padrão ajustados
        Kc_best, Ti_best, Td_best = 4.22, 20.0, 1.5
        print("Usando valores padrão")
    
    print(f"\nParâmetros projetados:")
    print(f"Kc = {Kc_best:.3f}")
    print(f"Ti = {Ti_best:.3f} dias")
    print(f"Td = {Td_best:.3f} dias")
    if best_params and results:
        print(f"\n  Desempenho:")
        print(f"    NDVI regime: {best_result['y_ss']:.4f}")
        print(f"    NDVI máximo: {best_result['y_max']:.4f}")
        print(f"    Sobressinal: {best_result['overshoot']:.2f}%")
        print(f"    Ts (2%): {best_result['ts']:.2f} dias")
    
    # 5c) Resposta ao degrau
    print("\n" + "-"*80)
    print("5c) Resposta ao Degrau")
    print("-"*80)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    t_plot = np.linspace(0, 150, 1500)
    # Malha aberta
    _, y_open = signal.step(G, T=t_plot)
    y_open = y_open * SETPOINT
    # PID
    C_PID = signal.TransferFunction([Kc_best*Ti_best*Td_best, Kc_best*Ti_best, Kc_best], [Ti_best, 0])
    num_pid = np.polymul(C_PID.num, G.num)
    den_pid = np.polyadd(np.polymul(C_PID.den, G.den), num_pid)
    T_PID = signal.TransferFunction(num_pid, den_pid)
    _, y_pid = signal.step(T_PID, T=t_plot)
    y_pid = y_pid * SETPOINT
    # Gráfico 1: Resposta temporal
    axes[0, 0].plot(t_plot, y_open, 'k--', linewidth=2, label='Sem Controle', alpha=0.7)
    axes[0, 0].plot(t_plot, y_pid, 'r-', linewidth=2.5, 
                    label=f'PID (Kc={Kc_best:.2f}, Ti={Ti_best:.1f}, Td={Td_best:.2f})')
    axes[0, 0].axhline(SETPOINT, color='g', linestyle=':', linewidth=2, label='Referência (0,75)')
    axes[0, 0].axhline(0.70, color='orange', linestyle='-.', linewidth=1.5, alpha=0.6)
    axes[0, 0].axhline(0.85, color='orange', linestyle='-.', linewidth=1.5, alpha=0.6)
    axes[0, 0].fill_between(t_plot, 0.70, 0.85, color='green', alpha=0.1, label='Faixa Segura')
    axes[0, 0].set_xlabel('Tempo (dias)', fontsize=11)
    axes[0, 0].set_ylabel('NDVI', fontsize=11)
    axes[0, 0].set_title('Resposta ao Degrau - PID', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend(fontsize=9)
    axes[0, 0].set_xlim([0, 150])
    axes[0, 0].set_ylim([0, 1])
    # Gráfico 2: Zoom no transitório
    axes[0, 1].plot(t_plot, y_pid, 'r-', linewidth=2.5)
    axes[0, 1].axhline(SETPOINT, color='g', linestyle=':', linewidth=2)
    axes[0, 1].axhline(SETPOINT * 1.05, color='orange', linestyle='--', linewidth=1, alpha=0.6, label='±5%')
    axes[0, 1].axhline(SETPOINT * 0.95, color='orange', linestyle='--', linewidth=1, alpha=0.6)
    axes[0, 1].fill_between(t_plot, SETPOINT*0.95, SETPOINT*1.05, color='yellow', alpha=0.2)
    axes[0, 1].set_xlabel('Tempo (dias)', fontsize=11)
    axes[0, 1].set_ylabel('NDVI', fontsize=11)
    axes[0, 1].set_title('Zoom - Sobressinal', fontsize=12)
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend(fontsize=9)
    axes[0, 1].set_xlim([0, 80])
    axes[0, 1].set_ylim([0.65, 0.85])
    # Gráfico 3: Comparação P, PI, PD, PID
    # P
    C_P = signal.TransferFunction([6.5], [1])
    num_p = np.polymul(C_P.num, G.num)
    den_p = np.polyadd(np.polymul(C_P.den, G.den), num_p)
    T_P = signal.TransferFunction(num_p, den_p)
    _, y_p = signal.step(T_P, T=t_plot)
    y_p = y_p * SETPOINT
    # PI
    C_PI = signal.TransferFunction([3.11*7.33, 3.11], [7.33, 0])
    num_pi = np.polymul(C_PI.num, G.num)
    den_pi = np.polyadd(np.polymul(C_PI.den, G.den), num_pi)
    T_PI = signal.TransferFunction(num_pi, den_pi)
    _, y_pi = signal.step(T_PI, T=t_plot)
    y_pi = y_pi * SETPOINT
    # PD
    C_PD = signal.TransferFunction([6.5*2.0, 6.5], [1])
    num_pd = np.polymul(C_PD.num, G.num)
    den_pd = np.polyadd(np.polymul(C_PD.den, G.den), num_pd)
    T_PD = signal.TransferFunction(num_pd, den_pd)
    _, y_pd = signal.step(T_PD, T=t_plot)
    y_pd = y_pd * SETPOINT
    axes[1, 0].plot(t_plot, y_p, 'b-', linewidth=2, label='P', alpha=0.8)
    axes[1, 0].plot(t_plot, y_pi, 'g-', linewidth=2, label='PI', alpha=0.8)
    axes[1, 0].plot(t_plot, y_pd, 'orange', linewidth=2, label='PD', alpha=0.8)
    axes[1, 0].plot(t_plot, y_pid, 'r-', linewidth=2.5, label='PID')
    axes[1, 0].axhline(SETPOINT, color='k', linestyle=':', linewidth=2, alpha=0.5)
    axes[1, 0].fill_between(t_plot, 0.70, 0.85, color='green', alpha=0.1)
    axes[1, 0].set_xlabel('Tempo (dias)', fontsize=11)
    axes[1, 0].set_ylabel('NDVI', fontsize=11)
    axes[1, 0].set_title('Comparação: P vs PI vs PD vs PID', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend(fontsize=10)
    axes[1, 0].set_xlim([0, 150])
    axes[1, 0].set_ylim([0, 1])
    # Gráfico 4: Métricas de desempenho
    if results:
        scatter_data = sorted(results, key=lambda x: x['score'])[:30]
        ts_data = [r['ts'] for r in scatter_data]
        os_data = [r['overshoot'] for r in scatter_data]
        colors = [r['score'] for r in scatter_data]
        
        scatter = axes[1, 1].scatter(ts_data, os_data, c=colors, cmap='RdYlGn_r', s=100, alpha=0.7)
        axes[1, 1].plot(best_result['ts'], best_result['overshoot'], 'r*', 
                       markersize=20, label='Ótimo')
        axes[1, 1].axvline(25, color='r', linestyle='--', linewidth=1, alpha=0.5, label='Ts máx')
        axes[1, 1].axhline(5, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='OS máx')
        axes[1, 1].set_xlabel('Tempo de Acomodação (dias)', fontsize=11)
        axes[1, 1].set_ylabel('Sobressinal (%)', fontsize=11)
        axes[1, 1].set_title('Espaço de Parâmetros PID', fontsize=12)
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend(fontsize=9)
        cbar = plt.colorbar(scatter, ax=axes[1, 1])
        cbar.set_label('Score', fontsize=9)
    plt.tight_layout()
    plt.savefig('output/questao5c_resposta_PID.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5d) Impacto do termo integral - Bode
    print("\n" + "-"*80)
    print("5d) Impacto do Termo Integral - Diagrama de Bode")
    print("-"*80)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    w = np.logspace(-3, 1, 500)
    # Controladores
    C_P_ctrl = ctrl.TransferFunction([6.5], [1])
    C_PI_ctrl = ctrl.TransferFunction([3.11*7.33, 3.11], [7.33, 0])
    C_PD_ctrl = ctrl.TransferFunction([6.5*2.0, 6.5], [1])
    C_PID_ctrl = ctrl.TransferFunction([Kc_best*Ti_best*Td_best, Kc_best*Ti_best, Kc_best], [Ti_best, 0])
    # Malha aberta
    L_P = ctrl.series(C_P_ctrl, G_ctrl)
    L_PI = ctrl.series(C_PI_ctrl, G_ctrl)
    L_PD = ctrl.series(C_PD_ctrl, G_ctrl)
    L_PID = ctrl.series(C_PID_ctrl, G_ctrl)
    # Bode magnitude
    mag_p, _, _ = ctrl.bode(L_P, w, plot=False)
    mag_pi, _, _ = ctrl.bode(L_PI, w, plot=False)
    mag_pd, _, _ = ctrl.bode(L_PD, w, plot=False)
    mag_pid, _, _ = ctrl.bode(L_PID, w, plot=False)
    axes[0, 0].semilogx(w, 20*np.log10(mag_p), 'b-', linewidth=2, label='P')
    axes[0, 0].semilogx(w, 20*np.log10(mag_pi), 'g-', linewidth=2, label='PI')
    axes[0, 0].semilogx(w, 20*np.log10(mag_pd), 'orange', linewidth=2, label='PD')
    axes[0, 0].semilogx(w, 20*np.log10(mag_pid), 'r-', linewidth=2.5, label='PID')
    axes[0, 0].axhline(0, color='k', linestyle='--', linewidth=1, alpha=0.5)
    axes[0, 0].set_ylabel('Magnitude (dB)', fontsize=11)
    axes[0, 0].set_title('Bode - Magnitude', fontsize=12)
    axes[0, 0].legend(fontsize=10)
    axes[0, 0].grid(True, which='both', alpha=0.3)
    # Bode fase
    _, phase_p, _ = ctrl.bode(L_P, w, plot=False)
    _, phase_pi, _ = ctrl.bode(L_PI, w, plot=False)
    _, phase_pd, _ = ctrl.bode(L_PD, w, plot=False)
    _, phase_pid, _ = ctrl.bode(L_PID, w, plot=False)
    axes[0, 1].semilogx(w, phase_p * 180/np.pi, 'b-', linewidth=2, label='P')
    axes[0, 1].semilogx(w, phase_pi * 180/np.pi, 'g-', linewidth=2, label='PI')
    axes[0, 1].semilogx(w, phase_pd * 180/np.pi, 'orange', linewidth=2, label='PD')
    axes[0, 1].semilogx(w, phase_pid * 180/np.pi, 'r-', linewidth=2.5, label='PID')
    axes[0, 1].axhline(-180, color='k', linestyle='--', linewidth=1, alpha=0.5)
    axes[0, 1].set_ylabel('Fase (graus)', fontsize=11)
    axes[0, 1].set_xlabel('Frequência (rad/dia)', fontsize=11)
    axes[0, 1].set_title('Bode - Fase', fontsize=12)
    axes[0, 1].legend(fontsize=10)
    axes[0, 1].grid(True, which='both', alpha=0.3)
    # Margens de estabilidade
    controllers = ['P', 'PI', 'PD', 'PID']
    loops = [L_P, L_PI, L_PD, L_PID]
    gms, pms = [], []
    for L in loops:
        gm, pm, _, _ = ctrl.margin(L)
        gms.append(20*np.log10(gm) if gm > 0 else 0)
        pms.append(pm)
    x_pos = np.arange(len(controllers))
    axes[1, 0].bar(x_pos, gms, color=['blue', 'green', 'orange', 'red'], alpha=0.7)
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(controllers)
    axes[1, 0].set_ylabel('Margem de Ganho (dB)', fontsize=11)
    axes[1, 0].set_title('Margens de Estabilidade - Ganho', fontsize=12)
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    axes[1, 1].bar(x_pos, pms, color=['blue', 'green', 'orange', 'red'], alpha=0.7)
    axes[1, 1].axhline(45, color='r', linestyle='--', linewidth=1.5, label='Mínimo (45°)')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(controllers)
    axes[1, 1].set_ylabel('Margem de Fase (graus)', fontsize=11)
    axes[1, 1].set_title('Margens de Estabilidade - Fase', fontsize=12)
    axes[1, 1].legend(fontsize=9)
    axes[1, 1].grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig('output/questao5d_bode_integral.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Gráfico final comparativo
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(t_plot, y_p, 'b-', linewidth=2, label='P', alpha=0.8)
    ax.plot(t_plot, y_pi, 'g-', linewidth=2.5, label='PI (RECOMENDADO)', alpha=0.9)
    ax.plot(t_plot, y_pd, 'orange', linewidth=2, label='PD', alpha=0.8)
    ax.plot(t_plot, y_pid, 'r-', linewidth=2.5, label='PID', alpha=0.9)
    ax.axhline(SETPOINT, color='k', linestyle=':', linewidth=2, label='Referência Ótima')
    ax.fill_between(t_plot, 0.70, 0.85, color='green', alpha=0.1, label='Faixa Fisiológica Segura')
    ax.set_xlabel('Tempo (dias)', fontsize=13)
    ax.set_ylabel('NDVI', fontsize=13)
    ax.set_title('Comparação Final: Escolha do Controlador para Irrigação de Citros', 
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best')
    ax.set_xlim([0, 150])
    ax.set_ylim([0, 1])
    plt.tight_layout()
    plt.savefig('output/questao5e_comparacao_final.png', dpi=300, bbox_inches='tight')
    plt.close()
    return Kc_best, Ti_best, Td_best


if __name__ == "__main__":
    Kc, Ti, Td = questao5_controle_PID(Ks=1.0, Kp=1.0)
    print(f"\n{'='*80}")
    print(f"Parâmetros PID ótimos: Kc = {Kc:.3f}, Ti = {Ti:.3f}, Td = {Td:.3f} dias")
    print(f"{'='*80}")
