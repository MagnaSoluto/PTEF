# Getting Started

Este guia irá ajudá-lo a começar a usar o PTEF rapidamente.

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

## Primeiro Exemplo

### Python

```python
import ptef

# Estimação básica para N=1000
result = ptef.estimate(N=1000, policy="R1", B=16, return_ci=True)

print(f"Tempo esperado: {result['mean']:.3f} segundos")
print(f"Variância: {result['var']:.6f} segundos²")

if 'ci95' in result:
    ci = result['ci95']
    print(f"IC 95%: [{ci['lower']:.3f}, {ci['upper']:.3f}] segundos")
```

### R

```r
library(ptef)

# Estimação básica para N=1000
result <- estimate(N = 1000, policy = "R1", B = 16, return_ci = TRUE)

cat("Tempo esperado:", round(result$mean, 3), "segundos\n")
cat("Variância:", round(result$var, 6), "segundos²\n")

if (!is.null(result$ci95)) {
  cat("IC 95%: [", round(result$ci95$lower, 3), ", ", 
      round(result$ci95$upper, 3), "] segundos\n")
}
```

## Conceitos Básicos

### Políticas Gramaticais

O PTEF atualmente suporta a política R1, que implementa as regras padrão do português brasileiro para geração de números por extenso.

### Parâmetros Principais

- **N**: Número máximo para estimação (1 a N)
- **policy**: Política gramatical (atualmente apenas "R1")
- **B**: Tamanho do bloco para pausas estruturais (padrão: 16)
- **return_ci**: Se deve retornar intervalos de confiança

### Componentes da Estimação

O tempo total é composto por:

1. **Duração das sílabas**: Baseada em modelo lognormal
2. **Duração das pausas**: Pausas prosódicas e estruturais

## Exemplos Práticos

### Análise de Crescimento

```python
import ptef
import matplotlib.pyplot as plt
import numpy as np

# Valores de N para análise
N_values = [100, 500, 1000, 2000, 5000]

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

# Usar parâmetros personalizados
result = ptef.estimate(
    N=1000, 
    policy="R1", 
    B=16, 
    params=create_params(duration_params=duration_params),
    return_ci=True
)
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

## Próximos Passos

1. **Explore os exemplos**: Veja os notebooks Jupyter para exemplos mais detalhados
2. **Personalize parâmetros**: Ajuste os parâmetros para seus dados específicos
3. **Valide resultados**: Use a função de validação para verificar a precisão
4. **Contribua**: Participe do desenvolvimento do projeto

## Recursos Adicionais

- [Notebooks Jupyter](https://github.com/MagnaSoluto/PTEF/tree/main/python/notebooks)
- [Vignette R](https://github.com/MagnaSoluto/PTEF/tree/main/r/vignettes)
- [API Reference](api-reference.md)
- [Methodology](methodology.md)
