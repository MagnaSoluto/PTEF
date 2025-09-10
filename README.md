# PTEF - Pronunciation-Time Estimation Framework

[![CI Python](https://github.com/MagnaSoluto/PTEF/workflows/CI%20Python/badge.svg)](https://github.com/MagnaSoluto/PTEF/actions/workflows/ci-python.yml)
[![CI R](https://github.com/MagnaSoluto/PTEF/workflows/CI%20R/badge.svg)](https://github.com/MagnaSoluto/PTEF/actions/workflows/ci-r.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://github.com/MagnaSoluto/PTEF)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17090324.svg)](https://doi.org/10.5281/zenodo.17090324)

Um framework probabilístico para estimar o tempo de pronúncia de sequências numéricas no português brasileiro.

## Descrição

O PTEF implementa algoritmos eficientes O(log N) para estimar o tempo de pronúncia de números em português brasileiro, baseado em:

- **Geração de texto por extenso**: Converte números em palavras portuguesas usando a política R1
- **Contagem de sílabas**: Baseada em léxico fixo do português brasileiro
- **Contagem combinatória**: Algoritmos O(log N) para contagem de tokens e conectivos
- **Modelos de duração**: Microduração lognormal por sílaba + pausas prosódicas
- **Estimação de confiança**: Intervalos de confiança para tempos estimados

### Fórmulas Principais

**Esperança do tempo total:**
```
E[T(N)] = E[T_syllables(N)] + E[T_pauses(N)]
```

**Variância do tempo total:**
```
Var[T(N)] = Var[T_syllables(N)] + Var[T_pauses(N)]
```

**Duração esperada por sílaba (lognormal):**
```
E[T_syllable] = exp(μ + σ²/2) × speaker_effect
```

**Variância da duração por sílaba:**
```
Var[T_syllable] = exp(2μ + σ²) × (exp(σ²) - 1) × speaker_effect²
```

## Instalação

### Python

```bash
# Instalar via pip
pip install ptef

# Ou instalar do repositório
pip install git+https://github.com/MagnaSoluto/PTEF.git#subdirectory=python
```

### R

```r
# Instalar via devtools
devtools::install_github("MagnaSoluto/PTEF", subdir = "r")

# Ou instalar localmente
devtools::install_local("r/")
```

## Uso Rápido

### Python

```python
import ptef

# Estimação básica para N=1000
result = ptef.estimate(N=1000, policy="R1", B=16, return_ci=True)

print(f"Tempo esperado: {result['mean']:.3f} segundos")
print(f"IC 95%: [{result['ci95']['lower']:.3f}, {result['ci95']['upper']:.3f}] segundos")

# Análise de componentes
details = result['details']
print(f"Total de sílabas: {details['total_syllables']}")
print(f"Duração das sílabas: {details['syllable_duration']:.3f}s")
print(f"Duração das pausas: {details['pause_duration']:.3f}s")
```

### R

```r
library(ptef)

# Estimação básica para N=1000
result <- estimate(N = 1000, policy = "R1", B = 16, return_ci = TRUE)

cat("Tempo esperado:", round(result$mean, 3), "segundos\n")
cat("IC 95%: [", round(result$ci95$lower, 3), ", ", 
    round(result$ci95$upper, 3), "] segundos\n")

# Análise de componentes
details <- result$details
cat("Total de sílabas:", details$total_syllables, "\n")
cat("Duração das sílabas:", round(details$syllable_duration, 3), "s\n")
cat("Duração das pausas:", round(details$pause_duration, 3), "s\n")
```

## Interface de Linha de Comando

```bash
# Estimação básica
ptef estimate --N 1000 --policy R1 --B 16

# Saída em JSON
ptef estimate --N 1000 --json

# Parâmetros personalizados
ptef estimate --N 1000 --mu 0.2 --sigma 0.4 --speaker-effect 1.2

# Validação
ptef validate --N 100 --json
```

## Estrutura do Projeto

```
ptef-bp/
├── README.md
├── LICENSE
├── CITATION.cff
├── CHANGELOG.md
├── .gitignore
├── .gitattributes
├── .editorconfig
├── .pre-commit-config.yaml
├── docs/
│   ├── index.md
│   ├── getting-started.md
│   └── methodology.md
├── data/
│   └── lexicon/
│       └── bp_number_tokens_syllables.csv
├── python/
│   ├── pyproject.toml
│   ├── src/ptef/
│   │   ├── __init__.py
│   │   ├── grammar.py
│   │   ├── lexicon.py
│   │   ├── combinatorics.py
│   │   ├── duration.py
│   │   ├── pauses.py
│   │   ├── ptef.py
│   │   └── cli.py
│   ├── tests/
│   └── notebooks/
├── r/
│   ├── DESCRIPTION
│   ├── NAMESPACE
│   ├── R/
│   ├── inst/extdata/
│   ├── tests/testthat/
│   └── vignettes/
└── .github/
    └── workflows/
        ├── ci-python.yml
        └── ci-r.yml
```

## Exemplos

### Análise de Crescimento

```python
import ptef
import matplotlib.pyplot as plt
import numpy as np

# Valores de N para análise
N_values = [100, 500, 1000, 2000, 5000, 10000]

# Estimação para múltiplos valores
results = []
for N in N_values:
    result = ptef.estimate(N=N, policy="R1", B=16, return_ci=True)
    results.append({
        'N': N,
        'mean': result['mean'],
        'std': np.sqrt(result['var']),
        'syllables': result['details']['total_syllables']
    })

# Visualização
plt.figure(figsize=(10, 6))
plt.errorbar([r['N'] for r in results], 
             [r['mean'] for r in results], 
             yerr=[r['std'] for r in results],
             fmt='o-', capsize=5)
plt.xlabel('N (número máximo)')
plt.ylabel('Tempo (segundos)')
plt.title('Tempo de Pronúncia vs N')
plt.grid(True, alpha=0.3)
plt.show()
```

### Parâmetros Personalizados

```python
from ptef import create_params, DurationParams, PauseParams

# Parâmetros personalizados
duration_params = DurationParams(
    mu=0.2,           # Média do log da duração
    sigma=0.4,        # Desvio padrão do log da duração
    speaker_effect=1.2, # Efeito do falante
    fatigue_coeff=0.01 # Coeficiente de fadiga
)

pause_params = PauseParams(
    weak_pause_duration=0.15,    # Duração de pausas fracas
    strong_pause_duration=0.4,   # Duração de pausas fortes
    weak_pause_prob=0.4,         # Probabilidade de pausas fracas
    strong_pause_prob=0.15       # Probabilidade de pausas fortes
)

# Usar parâmetros personalizados
result = ptef.estimate(
    N=1000, 
    policy="R1", 
    B=16, 
    params=create_params(
        duration_params=duration_params,
        pause_params=pause_params
    ),
    return_ci=True
)
```

## Testes

### Python

```bash
# Executar todos os testes
pytest python/tests/

# Executar com cobertura
pytest python/tests/ --cov=python/src/ptef

# Executar testes específicos
pytest python/tests/test_grammar.py -v
```

### R

```r
# Executar todos os testes
testthat::test_dir("r/tests/testthat/")

# Executar testes específicos
testthat::test_file("r/tests/testthat/test-grammar.R")
```

## Linting e Formatação

### Python

```bash
# Instalar pre-commit
pre-commit install

# Executar manualmente
ruff python/src/ptef/
black python/src/ptef/
mypy python/src/ptef/
```

### R

```r
# Linting
lintr::lint_package("r/")
```

## Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Convenções

- Use [Conventional Commits](https://www.conventionalcommits.org/)
- Mantenha cobertura de testes alta (>90%)
- Siga as convenções de código do projeto
- Documente novas funcionalidades

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Citação

Se você usar o PTEF em sua pesquisa, por favor cite:

```bibtex
@article{ptef2024,
  title={PTEF: Um Framework Probabilístico para Estimar o Tempo de Pronúncia de Sequências Numéricas no Português Brasileiro},
  author={PTEF Team},
  journal={arXiv preprint},
  year={2024},
  url={https://github.com/MagnaSoluto/PTEF}
}
```

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para histórico de mudanças.

## Suporte

- **Issues**: [GitHub Issues](https://github.com/MagnaSoluto/PTEF/issues)
- **Discussões**: [GitHub Discussions](https://github.com/MagnaSoluto/PTEF/discussions)
- **Email**: ptef@example.com

## Roadmap

- [ ] Integração com engines TTS reais
- [ ] Suporte a outras políticas gramaticais
- [ ] Otimizações de performance
- [ ] Interface web para demonstração
- [ ] Suporte a outros idiomas

---

**PTEF** - Desenvolvido com ❤️ para a comunidade de síntese de fala em português brasileiro.
