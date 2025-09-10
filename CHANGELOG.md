# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2024-01-01

### Adicionado
- Implementação inicial do framework PTEF
- Módulos Python para gramática, léxico, combinatória, duração e pausas
- Módulos R equivalentes com funcionalidade completa
- Interface de linha de comando (CLI) para Python
- Algoritmos O(log N) para contagem de tokens
- Modelos de duração lognormal para sílabas
- Estimação de pausas prosódicas
- Intervalos de confiança para estimações
- Testes abrangentes para Python e R
- Notebooks Jupyter de demonstração
- Vignette R com exemplos de uso
- Documentação completa em português
- Configuração de CI/CD com GitHub Actions
- Suporte a parâmetros personalizados
- Validação cruzada de algoritmos
- Estrutura de projeto modular e extensível

### Características Técnicas
- **Python**: Suporte a Python 3.10+
- **R**: Suporte a R ≥4.3
- **Dependências**: numpy, scipy, pydantic, click, pandas (Python)
- **Dependências**: tibble, dplyr, readr (R)
- **Licença**: MIT
- **Testes**: pytest (Python), testthat (R)
- **Linting**: ruff, black, mypy (Python), lintr (R)

### Funcionalidades Principais
- Geração de texto por extenso para números em português brasileiro
- Contagem eficiente de sílabas baseada em léxico fixo
- Algoritmos combinatórios para contagem de tokens e conectivos
- Modelos probabilísticos para duração de sílabas
- Estimação de pausas prosódicas e estruturais
- Interface unificada para estimação de tempos de pronúncia
- Validação e testes de consistência

### Exemplos de Uso
```python
# Python
import ptef
result = ptef.estimate(N=1000, policy="R1", B=16, return_ci=True)
print(f"Tempo esperado: {result['mean']:.3f} segundos")
```

```r
# R
library(ptef)
result <- estimate(N = 1000, policy = "R1", B = 16, return_ci = TRUE)
cat("Tempo esperado:", round(result$mean, 3), "segundos\n")
```

### Comandos CLI
```bash
# Estimação básica
ptef estimate --N 1000 --policy R1 --B 16

# Saída em JSON
ptef estimate --N 1000 --json

# Validação
ptef validate --N 100 --json
```

### Próximas Versões
- [ ] Integração com engines TTS reais
- [ ] Suporte a outras políticas gramaticais
- [ ] Otimizações de performance
- [ ] Interface web para demonstração
- [ ] Suporte a outros idiomas
- [ ] Validação com dados reais de fala
- [ ] Modelos de duração mais sofisticados
- [ ] Análise de variabilidade entre falantes
