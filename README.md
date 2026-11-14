# Acervo Técnico de Scripts

Repositório com scripts práticos em Python, HTML/JS e Bash inspirados em incidentes e problemas reais nas áreas de:

- `osint/`: coleta e monitoramento em fontes abertas
- `pentest/`: automação de reconhecimento e validação técnica
- `engenharia-civil/`: cálculos, verificações e utilitários de obra/projeto
- `engenharia-quimica/`: balanços, propriedades e automação de processos
- `rf-sdr/`: análise de sinais, frequências e utilitários de rádio

## Índice de scripts

| Área | Script | Descrição |
|------|--------|-----------|
| OSINT | [`osint/crt_monitor.py`](osint/crt_monitor.py) | Consulta os logs públicos de Certificate Transparency (crt.sh), levanta domínios e subdomínios que contêm o nome de uma marca e verifica em paralelo quais têm DNS ativo, ajudando a identificar possíveis domínios de phishing. |

## Exemplo de uso (`crt_monitor.py`)

Requer Python 3.10+ e nenhuma dependência externa.

```bash
# Busca domínios com o termo e verifica DNS (padrão: até 50 domínios, 10 threads)
python3 osint/crt_monitor.py -t exemplo

# Somente domínios com DNS ativo, salvando relatório em JSON
python3 osint/crt_monitor.py -t exemplo --only-active -o resultado.json

# Ajustando limite e número de threads
python3 osint/crt_monitor.py -t exemplo -l 100 -w 20
```

Observações:

- O script encontra domínios que contêm o termo exato; ele não gera variações de typosquatting (por exemplo, `exemplo` não encontra `exxemplo`).
- Cada execução é uma consulta pontual. Para monitoramento contínuo, agende a execução (por exemplo, com `cron`) e compare os relatórios JSON.
- A resolução DNS verifica apenas IPv4.

## Uso ético

Os scripts são destinados a estudo, defesa e testes em ambientes próprios ou com autorização expressa. O uso indevido é de responsabilidade de quem o executa.

---

Desenvolvido por Carlpit
