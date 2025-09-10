# PTEF - Documentação

Bem-vindo à documentação do PTEF (Pronunciation-Time Estimation Framework)!

## Visão Geral

O PTEF é um framework probabilístico para estimar o tempo de pronúncia de sequências numéricas no português brasileiro. Ele implementa algoritmos eficientes O(log N) para contagem de tokens, modelos de duração lognormal e estimação de pausas prosódicas.

## Características Principais

- **Geração de texto por extenso**: Converte números em palavras portuguesas usando a política R1
- **Contagem de sílabas**: Baseada em léxico fixo do português brasileiro
- **Algoritmos O(log N)**: Contagem combinatória por blocos para grandes N
- **Modelos de duração**: Microduração lognormal por sílaba + pausas prosódicas
- **Estimação de confiança**: Intervalos de confiança para tempos estimados

## Instalação

### Python

```bash
pip install ptef
```

### R

```r
devtools::install_github("MagnaSoluto/PTEF", subdir = "r")
```

## Uso Rápido

### Python

```python
import ptef

# Estimação básica
result = ptef.estimate(N=1000, policy="R1", B=16, return_ci=True)
print(f"Tempo esperado: {result['mean']:.3f} segundos")
```

### R

```r
library(ptef)

# Estimação básica
result <- estimate(N = 1000, policy = "R1", B = 16, return_ci = TRUE)
cat("Tempo esperado:", round(result$mean, 3), "segundos\n")
```

## Documentação Detalhada

- [Getting Started](getting-started.md) - Guia de início rápido
- [Methodology](methodology.md) - Metodologia e algoritmos
- [API Reference](api-reference.md) - Referência completa da API
- [Examples](examples.md) - Exemplos práticos
- [Contributing](contributing.md) - Como contribuir

## Recursos

- [GitHub Repository](https://github.com/MagnaSoluto/PTEF)
- [Issue Tracker](https://github.com/MagnaSoluto/PTEF/issues)
- [Discussions](https://github.com/MagnaSoluto/PTEF/discussions)
- [Changelog](https://github.com/MagnaSoluto/PTEF/blob/main/CHANGELOG.md)

## Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](https://github.com/MagnaSoluto/PTEF/blob/main/LICENSE) para detalhes.
