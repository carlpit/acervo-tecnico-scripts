# exif-guard

CLI em Python que lê metadados EXIF de **fotos suas**, converte GPS para latitude/longitude
decimal e gera um link de mapa. Em construção: score de risco, relatórios e modo `--strip`.

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
exif-guard pasta_das_fotos -r
```

## Licença

MIT
