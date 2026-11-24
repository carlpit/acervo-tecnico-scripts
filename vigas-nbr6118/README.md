# vigas-nbr6118

[![CI](https://github.com/carlpit/acervo-tecnico-scripts/actions/workflows/vigas-nbr6118.yml/badge.svg)](https://github.com/carlpit/acervo-tecnico-scripts/actions/workflows/vigas-nbr6118.yml)

CLI em Python que dimensiona **vigas retangulares de concreto armado à flexão simples** pela
NBR 6118 e gera um **memorial de cálculo em Markdown**, com as premissas explícitas e o cálculo
passo a passo.

> ⚠️ **Ferramenta de estudo.** Não substitui projeto estrutural elaborado e verificado por
> engenheiro habilitado, com ART recolhida no CREA.

## O que calcula

- Md, linha neutra x, relação x/d e domínio de deformação (2, 3 ou 4)
- Armadura simples ou **dupla** (quando x/d > 0,45), com σs' pela compatibilidade de deformações
- As,mín (tabela 17.3, com interpolação) e verificação de As + As' ≤ 4 % Ac
- Sugestão de barras (uma bitola)
- Memorial `.md` e saída em JSON, para integrar com outras ferramentas

## Instalação

```bash
git clone https://github.com/carlpit/acervo-tecnico-scripts.git
cd acervo-tecnico-scripts/vigas-nbr6118
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

```bash
vigas dimensionar --b 20 --h 50 --d 45 --fck 25 --mk 100 --memorial v1.md --titulo V1
```

```
Md      = 140.00 kN·m
x       = 14.74 cm   (x/d = 0.328, domínio 3)
As,calc = 8.23 cm²   As,mín = 1.50 cm²
As      = 8.23 cm²
Barras  : 7φ12.5, 5φ16, 3φ20, 2φ25
Memorial salvo em v1.md
```

| Opção | Unidade | Padrão |
|---|---|---|
| `--b`, `--h` | cm | obrigatório |
| `--d` | cm | h − 5 (avisado na saída) |
| `--d-linha` | cm | 4 |
| `--fck` | MPa (20 a 50) | obrigatório |
| `--mk` | kN·m | obrigatório |
| `--aco` | CA-25 / CA-50 / CA-60 | CA-50 |
| `--gamma-f` / `--gamma-c` / `--gamma-s` | – | 1,4 / 1,4 / 1,15 |
| `--memorial ARQ.md` | – | não gera |
| `--json` | – | desligado |

Códigos de saída: `0` ok · `1` entrada inválida · `2` seção insuficiente (As + As' > 4 % Ac).

Exemplos de memorial em [`exemplos/`](exemplos/).

## Normas e premissas

| Item | Referência |
|---|---|
| Diagrama retangular, λ = 0,8 e αc = 0,85 | NBR 6118, 17.2.2 / 8.2.10.1 |
| εcu = 3,5 ‰; εsu = 10 ‰; Es = 210 GPa | NBR 6118, 8.2.10.1 / 8.3.5 |
| γc = 1,4; γs = 1,15 | NBR 6118, tabela 12.1 |
| Ductilidade x/d ≤ 0,45 (fck ≤ 50 MPa) | NBR 6118, 14.6.4.3 |
| ρmín (seção retangular) | NBR 6118, tabela 17.3 |
| As + As' ≤ 4 % Ac | NBR 6118, 17.3.5.2.4 |
| fyk dos aços | NBR 7480 |

**Escopo da v0.1:** fck de 20 a 50 MPa (grupo I). Para fck > 40 MPa a ferramenta emite um aviso
para conferir na edição vigente da NBR 6118 se há fator redutor adicional da resistência do
concreto não contemplado aqui.

**Não verifica:** cisalhamento, torção, fissuração (ELS-W), flecha (ELS-DEF), ancoragem,
espaçamento entre barras e cobrimento (NBR 6118, tabela 7.2). Tudo isso precisa ser verificado
à parte.

## Validação

Os testes (`pytest`) cobrem:

1. **Caso de referência conferido à mão**: 20×50, d = 45 cm, C25, CA-50, Mk = 100 kN·m →
   x = 14,74 cm, As = 8,23 cm², domínio 3.
2. **Equilíbrio**: para qualquer resultado, Rcc = Rst e Rcc·z = Md (armadura simples), e o
   equilíbrio de forças e momentos com As' (armadura dupla). Isso testa a física, não a fórmula.
3. Fronteira x/d = 0,45, armadura mínima governando, As,máx estourando, validação de entradas e a CLI.

| Caso | Fonte | x (cm) | As (cm²) | Diferença |
|---|---|---|---|---|
| 20×50, C25, Mk = 100 kN·m | cálculo manual | 14,74 | 8,23 | 0 % |
| _(adicione exemplos resolvidos de livro aqui)_ | | | | |

## Roadmap

- [ ] Verificação de espaçamento horizontal e número de camadas
- [ ] Cisalhamento (modelos I e II)
- [ ] Seção T (mesa colaborante)
- [ ] ELS: abertura de fissuras e flecha
- [ ] fck de 55 a 90 MPa (grupo II)

## Licença

MIT
