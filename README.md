# Projeto de Controle de Irrigação Baseado em NDVI

## Sobre o Projeto

Sistema de controle automatizado para irrigação de pomar de citros baseado no monitoramento contínuo do NDVI (Índice de Vegetação por Diferença Normalizada). O projeto implementa e compara diferentes estratégias de controle (P, PI, PD e PID) para manter as plantas em condições hídricas ideais.

## Objetivos

- Modelar o sistema solo-planta como processo de controle
- Projetar controladores P, PI, PD e PID
- Analisar desempenho e estabilidade
- Comparar estratégias de controle
- Identificar melhor solução para aplicação agronômica

## Estrutura do Projeto

```
├── config.py              # Constantes e parâmetros do sistema
├── system_models.py       # Modelos de planta e controladores
├── questao2.py           # Questão 2 - Controle Proporcional (P)
├── questao3.py           # Questão 3 - Controle PI
├── questao4.py           # Questão 4 - Controle PD
├── questao5.py           # Questão 5 - Controle PID
├── resolver_questoes.py  # Script para resolver todas as questões
└── output/               # Pasta com gráficos e resultados gerados
```

## Como Usar

### Instalação de Dependências

```bash
pip install numpy scipy matplotlib pandas control
```

### Resolver Todas as Questões do PDF

**Modo Interativo (Menu):**
```bash
python3 resolver_questoes.py
```

**Modo Automático (Executa todas as questões):**
```bash
python3 resolver_questoes.py --all
```

### Executar Questões Individuais

```bash
python3 questao1.py  # Diagrama de blocos
python3 questao2.py  # Controle P
python3 questao3.py  # Controle PI
python3 questao4.py  # Controle PD
python3 questao5.py  # Controle PID
```

**Nota:** Todos os gráficos serão salvos na pasta `output/`

## Parâmetros do Sistema

```
G(s) = (Ks·Kp) / ((τs·s + 1)(τp·s + 1))

τs = 2 dias    (constante de tempo do solo)
τp = 25 dias   (constante de tempo da planta)
```

**Especificações Agronômicas:**
- NDVI de referência: 0,75
- Faixa segura: 0,65 ≤ NDVI ≤ 0,85

## Aplicação Agronômica

### Recomendação Final
**Controlador PI** oferece o melhor compromisso:
- Erro nulo (NDVI ótimo mantido)
- Estabilidade e baixa variabilidade
- Simplicidade operacional
- Economia de água e energia



---

