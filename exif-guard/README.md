# exif-guard

CLI em Python que lê metadados EXIF de **fotos suas**, converte GPS para latitude/longitude
decimal, calcula um score de risco de privacidade e gera relatório em Markdown e JSON.

> ⚠️ Use apenas em arquivos próprios ou com autorização expressa.

## Instalação

```bash
git clone https://github.com/carlpit/acervo-tecnico-scripts.git
cd acervo-tecnico-scripts/exif-guard
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

```bash
exif-guard pasta_das_fotos
exif-guard pasta_das_fotos -r --md relatorio.md --json relatorio.json
```

Por padrão grava `relatorio-exif.md` e `relatorio-exif.json` no diretório atual.

- **Alto**: a foto tem GPS (localização exata).
- **Médio**: fabricante, modelo ou número de série, sem GPS.
- **Baixo**: apenas data/hora, software, ou nenhum metadado sensível.

## Licença

MIT
