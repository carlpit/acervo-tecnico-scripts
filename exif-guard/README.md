# exif-guard

[![CI](https://github.com/carlpit/acervo-tecnico-scripts/actions/workflows/exif-guard.yml/badge.svg)](https://github.com/carlpit/acervo-tecnico-scripts/actions/workflows/exif-guard.yml)

CLI em Python que audita metadados EXIF de **fotos suas** antes de você publicá-las:
extrai GPS (latitude/longitude decimal + link de mapa), fabricante, modelo, número de
série, data/hora e software; calcula um score de risco por arquivo; gera relatório em
Markdown e JSON; e, com `--strip`, cria **cópias** sem metadados.

Os originais nunca são alterados. Não há chamadas de rede: o link de mapa é apenas uma URL.

> ⚠️ **Aviso legal.** Use esta ferramenta apenas em arquivos que são seus ou para os quais
> você tem autorização expressa. Auditar, extrair ou publicar metadados de fotos de
> terceiros sem permissão pode violar a privacidade e a lei. O exif-guard é uma ferramenta
> de higiene digital e de estudo de OSINT **defensivo** — não é um kit para investigar
> outras pessoas.

## Por que isso importa

Toda foto tirada com um celular pode carregar, escondido no arquivo, muito mais do que a
imagem. No EXIF costumam viajar:

- a **localização exata** (GPS) de onde a foto foi feita;
- o **modelo do aparelho** e, em alguns casos, o **número de série**;
- a **data e a hora** da captura e o software usado.

Isso não é teórico. Nos testes desta ferramenta, um JPEG sintético com EXIF fictício em
`10,500000, 20,260000` (10°30' N, 20°15'36" E — coordenada de laboratório, não um lugar
real) entrega o ponto no [OpenStreetMap](https://www.openstreetmap.org/?mlat=10.500000&mlon=20.260000#map=16/10.500000/20.260000),
o aparelho `FakePhone Pixel Test` e o serial `SN-TEST-0001`. Se fosse uma foto sua, de
casa ou do trabalho, qualquer pessoa com o arquivo original poderia abrir o mesmo mapa.

OSINT começa pelo que você mesmo deixa vazar.

## Instalação

```bash
git clone https://github.com/carlpit/acervo-tecnico-scripts.git
cd acervo-tecnico-scripts/exif-guard
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Requer Python 3.11+. Dependências: Pillow e piexif.

## Uso

```bash
# Audita a pasta e grava relatorio-exif.md + relatorio-exif.json no diretório atual
exif-guard pasta_das_fotos

# Percorre subpastas e escolhe os caminhos dos relatórios
exif-guard pasta_das_fotos -r --md relatorio.md --json relatorio.json

# Só imprime no terminal, sem gravar relatório
exif-guard pasta_das_fotos --no-report

# Gera cópias sem metadados em outra pasta (os originais não são tocados)
exif-guard pasta_das_fotos --strip --out pasta_limpa
```

Exemplo de saída:

```
arquivo : pasta_das_fotos/com_gps.jpg
  risco : Alto
  make  : FakePhone
  model : Pixel Test
  serial: SN-TEST-0001
  data  : 2026:11:25 12:00:00
  soft  : TestCam 1.0
  GPS   : 10.500000, 20.260000
  mapa  : https://www.openstreetmap.org/?mlat=10.500000&mlon=20.260000#map=16/10.500000/20.260000
  motivos: GPS presente (localização exata); aparelho: FakePhone Pixel Test; número de série do dispositivo

resumo: 6 arquivo(s) — alto: 2, médio: 2, baixo: 2
relatório Markdown: relatorio-exif.md
relatório JSON    : relatorio-exif.json
```

| Opção | Descrição |
|-------|-----------|
| `pasta` | Pasta com as fotos (obrigatório) |
| `-r`, `--recursive` | Percorre subpastas |
| `--md ARQ.md` | Relatório Markdown (padrão: `relatorio-exif.md`) |
| `--json ARQ.json` | Relatório JSON (padrão: `relatorio-exif.json`) |
| `--no-report` | Não grava relatórios em arquivo |
| `--strip` | Gera cópias sem metadados |
| `--out PASTA` | Destino das cópias (obrigatório com `--strip`) |

Formatos lidos: JPEG, TIFF e WebP. O `--out` não pode ser a mesma pasta dos originais;
se o arquivo de destino já existir, a cópia é recusada e o original permanece intacto.

Códigos de saída: `0` ok · `1` pasta inválida ou uso incorreto · `2` alguma cópia `--strip` falhou.

## Score de risco

| Nível | Quando |
|-------|--------|
| **Alto** | A foto tem GPS (localização exata). Fabricante, modelo e serial, se existirem, entram como motivos adicionais. |
| **Médio** | Fabricante, modelo ou número de série, sem GPS. |
| **Baixo** | Apenas data/hora, software, ou nenhum metadado sensível. |

## Checklist de privacidade antes de postar

- [ ] Rodei o `exif-guard` na pasta das fotos que pretendo publicar.
- [ ] Li o relatório e tratei todo risco **alto** (GPS) que eu não quero expor.
- [ ] Gerei cópias com `--strip --out` e vou enviar **só as cópias**, nunca o original.
- [ ] Não publiquei o relatório junto (ele contém as coordenadas e o serial).
- [ ] Revisei o enquadramento da imagem: placa, endereço, crachá ou rosto de terceiros não são metadados, mas também vazam.

## Testes

```bash
pip install -e ".[dev]"
pytest
```

Os JPEGs de teste são gerados em memória pelo `tests/conftest.py`, com GPS e serial
**fictícios**. Nada de fotos reais entra no repositório.

## Licença

MIT. Copyright (c) 2026 Carlos Vinicius.

---

## English

exif-guard is a local Python CLI that audits EXIF metadata on **your own** photos (or
files you have explicit authorization to review). It converts GPS to decimal coordinates
plus an OpenStreetMap link, scores privacy risk (GPS = high, device/serial = medium,
otherwise low), writes Markdown and JSON reports, and can emit metadata-free **copies**
with `--strip` (originals are never overwritten). No network calls are made.

Legal notice: do not use this tool on other people's files without permission. It is a
defensive privacy / hygiene tool, not a kit for investigating third parties.
