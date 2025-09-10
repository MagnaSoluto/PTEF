# Metodologia

Este documento descreve a metodologia e algoritmos implementados no PTEF.

## Visão Geral

O PTEF implementa um framework probabilístico para estimar o tempo de pronúncia de sequências numéricas em português brasileiro. A abordagem combina:

1. **Geração de texto por extenso** usando regras gramaticais
2. **Contagem eficiente de tokens** com algoritmos O(log N)
3. **Modelos de duração** baseados em distribuições lognormais
4. **Estimação de pausas** prosódicas e estruturais

## Geração de Texto por Extenso

### Política R1

A política R1 implementa as regras padrão do português brasileiro para geração de números por extenso:

- **Unidades (1-19)**: Palavras específicas (um, dois, três, ..., dezenove)
- **Dezenas (20-99)**: Combinação de dezena + "e" + unidade (vinte e um, trinta e dois, ...)
- **Centenas (100-999)**: Combinação de centena + "e" + resto (cento e um, duzentos e trinta, ...)
- **Milhares (1000-999999)**: Combinação de milhar + "e" + resto (mil e um, dois mil, ...)
- **Milhões (1000000+)**: Combinação de milhão + "e" + resto (um milhão, dois milhões, ...)

### Regras de Conectivos

O conectivo "e" é inserido:
- Entre dezenas e unidades (vinte **e** um)
- Entre centenas e resto (cento **e** um)
- Entre milhares e resto (mil **e** um)
- Entre milhões e resto (um milhão **e** um)

## Contagem de Tokens

### Algoritmo O(log N)

Para grandes valores de N, o PTEF usa decomposição em blocos:

1. **Bloco base (1-999)**: Contagem direta de todos os tokens
2. **Blocos de milhares**: Replicação do bloco base + token "mil"
3. **Blocos de milhões**: Replicação do bloco base + token "milhão"/"milhões"

### Complexidade

- **Tempo**: O(log N) para contagem de tokens
- **Espaço**: O(1) para armazenamento de contadores
- **Precisão**: Exata para todos os valores de N

## Modelos de Duração

### Duração por Sílaba

A duração de cada sílaba é modelada como uma distribuição lognormal:

```
log(T_syllable) ~ Normal(μ, σ²)
```

**Parâmetros:**
- **μ**: Média do log da duração (padrão: 0.15)
- **σ**: Desvio padrão do log da duração (padrão: 0.3)
- **speaker_effect**: Efeito multiplicativo do falante (padrão: 1.0)
- **fatigue_coeff**: Coeficiente de fadiga linear (padrão: 0.0)

### Fórmulas

**Esperança:**
```
E[T_syllable] = exp(μ + σ²/2) × speaker_effect
```

**Variância:**
```
Var[T_syllable] = exp(2μ + σ²) × (exp(σ²) - 1) × speaker_effect²
```

**Duração total para n sílabas:**
```
E[T_total] = n × E[T_syllable] × (1 + fatigue_coeff × n)
Var[T_total] = n × Var[T_syllable]
```

## Estimação de Pausas

### Tipos de Pausas

1. **Pausas fracas**: Após conectivos "e" (probabilidade: 0.3, duração: 0.1s)
2. **Pausas fortes**: Após "mil", "milhão", "milhões" (probabilidade: 0.1, duração: 0.3s)
3. **Pausas estruturais**: Baseadas no tamanho do bloco B (probabilidade: 0.5, duração: 0.2s)

### Cálculo de Pausas

**Pausas fracas:**
```
count_weak = count("e") × weak_pause_prob
```

**Pausas fortes:**
```
count_strong = count("mil") × strong_pause_prob + 
               count("milhão") × strong_pause_prob + 
               count("milhões") × strong_pause_prob
```

**Pausas estruturais:**
```
count_structural = (total_tokens / B - 1) × structural_pause_prob
```

## Estimação Final

### Tempo Total

```
E[T_total] = E[T_syllables] + E[T_pauses]
Var[T_total] = Var[T_syllables] + Var[T_pauses]
```

### Intervalo de Confiança

```
CI_95% = E[T_total] ± 1.96 × √Var[T_total]
```

## Validação

### Validação Cruzada

Para N ≤ 1000, o algoritmo rápido é validado contra contagem direta:

1. Contagem direta: Iterar 1 a N, gerar tokens, contar
2. Contagem rápida: Usar algoritmo O(log N)
3. Comparar: Verificar que as contagens são idênticas

### Testes de Consistência

- **Consistência temporal**: Mesmo N sempre gera mesmo resultado
- **Consistência de tokens**: Todos os tokens gerados existem no léxico
- **Consistência de contagem**: Algoritmo rápido = contagem direta para N pequeno

## Limitações

### Limitações Atuais

1. **Políticas**: Apenas R1 implementada
2. **Idiomas**: Apenas português brasileiro
3. **Números**: Suporte até bilhões (10^12)
4. **Falantes**: Modelo genérico, não personalizado

### Limitações Teóricas

1. **Independência**: Sílabas assumidas independentes
2. **Lognormal**: Duração assumida lognormal
3. **Pausas**: Probabilidades fixas, não contextuais
4. **Fadiga**: Modelo linear simples

## Extensões Futuras

### Planejadas

1. **Múltiplas políticas**: R2, R3, etc.
2. **Personalização**: Modelos específicos por falante
3. **Contexto**: Pausas dependentes do contexto
4. **Validação**: Integração com TTS real

### Possíveis

1. **Outros idiomas**: Espanhol, francês, etc.
2. **Modelos avançados**: HMM, LSTM, etc.
3. **Análise prosódica**: Tom, acento, etc.
4. **Interface web**: Demonstração interativa
