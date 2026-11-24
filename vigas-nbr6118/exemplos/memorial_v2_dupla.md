# Memorial de cálculo — V2 (armadura dupla): flexão simples

Gerado por `vigas-nbr6118` v0.1.0 em 23/11/2026.

> **Ferramenta de estudo.** Não substitui projeto estrutural elaborado e verificado por
> engenheiro habilitado, com ART recolhida no CREA.

## 1. Dados de entrada

| Grandeza | Valor |
|---|---|
| Seção b × h | 20,0 × 50,0 cm |
| Altura útil d | 45,0 cm |
| d' (armadura comprimida) | 4,0 cm |
| Concreto | C25 (fck = 25 MPa) |
| Aço | CA-50 (fyk = 500 MPa) |
| Momento característico Mk | 250,00 kN·m |
| γf / γc / γs | 1,40 / 1,40 / 1,15 |

## 2. Premissas

- NBR 6118 — Projeto de estruturas de concreto (verificar edição vigente).
- Diagrama retangular simplificado: λ = 0,8, αc = 0,85 (fck ≤ 50 MPa).
- εcu = 3,5 ‰; εsu = 10,0 ‰; Es = 210.000 MPa.
- Ductilidade: x/d ≤ 0,45 (item 14.6.4.3).
- Armadura mínima pela tabela 17.3 (seção retangular); máxima As + As' ≤ 4 % Ac.
- Não verifica: cisalhamento, fissuração, flecha, ancoragem, espaçamento entre barras.

## 3. Cálculo

### 3.1 Resistências e esforço de cálculo

- fcd = fck/γc = 25/1,40 = 17,86 MPa = 1,7857 kN/cm²
- fyd = fyk/γs = 500/1,15 = 434,78 MPa = 43,478 kN/cm²
- εyd = fyd/Es = 2,070 ‰
- Md = γf·Mk = 1,40 × 250,00 = 350,00 kN·m = 35.000 kN·cm

### 3.2 Limites de domínio

- x₂₃ = εcu/(εcu + εsu)·d = 11,67 cm
- x₃₄ = εcu/(εcu + εyd)·d = 28,27 cm
- x_lim (ductilidade) = 0,45·d = 20,25 cm
- Md,lim = 0,68·fcd·b·x_lim·(d − 0,4·x_lim) = 181,47 kN·m

### 3.3 Linha neutra e armadura

Md = 350,00 kN·m > Md,lim = 181,47 kN·m → **armadura dupla**.

- x = x_lim = 20,25 cm; z = 36,90 cm
- ΔM = Md − Md,lim = 168,53 kN·m
- σs' = min(Es·εcu·(x − d')/x; fyd) = 43,478 kN/cm²
- As' = ΔM/[σs'·(d − d')] = **9,45 cm²**
- As,calc = Md,lim/(fyd·z) + ΔM/[fyd·(d − d')] = **20,77 cm²**
- Domínio de deformação: **3**

### 3.4 Armaduras mínima e máxima

- ρmín = 0,150 % → As,mín = 1,50 cm²
- As,máx = 4 % Ac = 40,00 cm² → As + As' = 30,22 cm² ✔

## 4. Resultado

- **As (tracionada) = 20,77 cm²**
- **As' (comprimida) = 9,45 cm²**

Sugestões de barras (uma bitola; conferir espaçamento e cobrimento no detalhamento):

| φ (mm) | nº barras | As,ef (cm²) |
|---|---|---|
| 20,0 | 7 | 21,99 |
| 25,0 | 5 | 24,54 |
| 32,0 | 3 | 24,13 |

## 5. Avisos

- ⚠ x/d > 0,45 com armadura simples: adotada armadura dupla. Avalie aumentar h — costuma sair mais barato e mais rígido.
