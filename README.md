# crt_monitor.py

Ferramenta CLI em Python que consulta os logs públicos de Certificate Transparency (crt.sh), levanta domínios e subdomínios que contêm o nome de uma marca e verifica em paralelo quais têm DNS ativo, ajudando a identificar possíveis domínios de phishing.

- 100% biblioteca padrão, sem dependências externas
- Resolução DNS concorrente com `ThreadPoolExecutor`
- Exportação opcional em JSON

## Requisitos

Python 3.10+

## Uso

```bash
# Busca domínios com o termo e verifica DNS (padrão: até 50 domínios, 10 threads)
python3 crt_monitor.py -t exemplo

# Somente domínios com DNS ativo, salvando relatório em JSON
python3 crt_monitor.py -t exemplo --only-active -o resultado.json

# Ajustando limite e número de threads
python3 crt_monitor.py -t exemplo -l 100 -w 20
```

| Opção | Descrição |
|-------|-----------|
| `-t`, `--target` | Termo ou domínio alvo (obrigatório) |
| `-l`, `--limit` | Limite de domínios verificados (padrão: 50) |
| `-w`, `--workers` | Threads para resolução DNS (padrão: 10) |
| `--only-active` | Exibe apenas domínios com DNS ativo |
| `-o`, `--output` | Salva os resultados em arquivo JSON |

## Observações

- O script encontra domínios que contêm o termo exato; ele não gera variações de typosquatting.
- Cada execução é uma consulta pontual. Para monitoramento contínuo, agende a execução (por exemplo, com `cron`).
- A resolução DNS verifica apenas IPv4.

## Uso ético

Destinado a estudo, defesa e testes em ambientes próprios ou com autorização expressa.

---

Desenvolvido por Carlpit
