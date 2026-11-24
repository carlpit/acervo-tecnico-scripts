# Memorial de cálculo — V1 (exemplo): flexão simples

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
| Momento característico Mk | 100,00 kN·m |
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
- Md = γf·Mk = 1,40 × 100,00 = 140,00 kN·m = 14.000 kN·cm

### 3.2 Limites de domínio

- x₂₃ = εcu/(εcu + εsu)·d = 11,67 cm
- x₃₄ = εcu/(εcu + εyd)·d = 28,27 cm
- x_lim (ductilidade) = 0,45·d = 20,25 cm
- Md,lim = 0,68·fcd·b·x_lim·(d − 0,4·x_lim) = 181,47 kN·m

### 3.3 Linha neutra e armadura

Md = 140,00 kN·m ≤ Md,lim = 181,47 kN·m → **armadura simples**.

- KMD = Md/(b·d²·fcd) = 0,1936
- x = 1,25·d·[1 − √(1 − KMD/0,425)] = **14,74 cm**
- x/d = 0,328 ≤ 0,45 ✔
- z = d − 0,4·x = 39,10 cm
- As,calc = Md/(fyd·z) = **8,23 cm²**
- Domínio de deformação: **3**

### 3.4 Armaduras mínima e máxima

- ρmín = 0,150 % → As,mín = 1,50 cm²
- As,máx = 4 % Ac = 40,00 cm² → As + As' = 8,23 cm² ✔

## 4. Resultado

- **As (tracionada) = 8,23 cm²**

Sugestões de barras (uma bitola; conferir espaçamento e cobrimento no detalhamento):

| φ (mm) | nº barras | As,ef (cm²) |
|---|---|---|
| 12,5 | 7 | 8,59 |
| 16,0 | 5 | 10,05 |
| 20,0 | 3 | 9,42 |
| 25,0 | 2 | 9,82 |
| 32,0 | 2 | 16,08 |
