# Acervo técnico de scripts

Scripts curtos de segurança, OSINT e redes, cada um em um único arquivo na raiz do repositório, e ferramentas maiores em pastas próprias.

| Script | O que faz |
|--------|-----------|
| [`crt_monitor.py`](#crt_monitorpy) | Busca em logs de Certificate Transparency domínios com o nome de uma marca e verifica DNS ativo |
| [`conn_spike_watchdog.sh`](#conn_spike_watchdogsh) | Monitora picos de sockets TCP, perda de pacotes e latência em Linux, com alerta e log |
| [`vigas-nbr6118/`](vigas-nbr6118/) | CLI que dimensiona vigas de concreto armado à flexão simples (NBR 6118) e gera memorial em Markdown |
| [`exif-guard/`](exif-guard/) | Audita EXIF de fotos próprias, calcula risco de privacidade e gera cópias sem metadados |

## crt_monitor.py

Ferramenta CLI em Python que consulta os logs públicos de Certificate Transparency (crt.sh), levanta domínios e subdomínios que contêm o nome de uma marca e verifica em paralelo quais têm DNS ativo, ajudando a identificar possíveis domínios de phishing.

- 100% biblioteca padrão, sem dependências externas
- Resolução DNS concorrente com `ThreadPoolExecutor`
- Exportação opcional em JSON

### Requisitos

Python 3.10+

### Uso

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

### Observações

- O script encontra domínios que contêm o termo exato; ele não gera variações de typosquatting.
- Cada execução é uma consulta pontual. Para monitoramento contínuo, agende a execução (por exemplo, com `cron`).
- A resolução DNS verifica apenas IPv4.

## conn_spike_watchdog.sh

Watchdog em Bash que acompanha tempestades de reconexão em servidores Linux e homelabs usando só ferramentas nativas (`ss`, `ping` e `awk`). A cada 5 segundos ele:

- conta sockets TCP nos estados `ESTAB`, `SYN-RECV` e `TIME-WAIT`;
- mede perda de pacotes e latência média contra um gateway ou host crítico;
- grava tudo em `watchdog_rede.log` e marca `[ALERTA]` quando `SYN-RECV` atinge o limite, há qualquer perda de pacote ou a latência passa do limite.

Inspirado no caso da paralisação de voos nos EUA em 13/11/2026, quando um roteador novo passou a gerar mais de 1.000 tentativas de conexão a cada 4 a 5 segundos e desestabilizou a rede legada ([nota da FAA](https://www.faa.gov/newsroom/nationwide-ground-stop-questions-and-answers)). O script monitora a própria máquina onde roda; não é uma ferramenta de monitoramento de rede inteira.

### Uso

```bash
chmod +x conn_spike_watchdog.sh

# alvo, limite de SYN-RECV, limite de latência em ms
./conn_spike_watchdog.sh 192.168.1.1 30 50
```

| Argumento | Padrão | Descrição |
|-----------|--------|-----------|
| 1º | `1.1.1.1` | IP do gateway ou host crítico |
| 2º | `50` | Alerta quando `SYN-RECV` for maior ou igual a este valor |
| 3º | `80` | Alerta quando a latência média (ms) for maior ou igual a este valor |

Interrompa com `Ctrl+C`. O log é criado na pasta onde o script é executado.

## vigas-nbr6118/

Pacote Python com CLI que dimensiona vigas retangulares de concreto armado à flexão simples pela NBR 6118: linha neutra, domínio de deformação, armadura simples ou dupla, As,mín/As,máx, sugestão de barras e memorial de cálculo em Markdown. Tem testes (pytest) e CI próprio.

```bash
cd vigas-nbr6118 && pip install -e ".[dev]"
vigas dimensionar --b 20 --h 50 --d 45 --fck 25 --mk 100 --memorial v1.md
```

Documentação completa, normas e premissas no [README da pasta](vigas-nbr6118/README.md). Ferramenta de estudo: não substitui projeto estrutural com ART.

## exif-guard/

Pacote Python com CLI que lê metadados EXIF de fotos suas (GPS em decimal + link de mapa, aparelho, serial, data/hora e software), calcula um score de risco e gera relatório em Markdown/JSON. O modo `--strip` cria cópias sem metadados e nunca altera os originais. Tem testes (pytest) e CI próprio.

```bash
cd exif-guard && pip install -e ".[dev]"
exif-guard pasta_das_fotos
exif-guard pasta_das_fotos --strip --out pasta_limpa
```

Documentação completa, aviso legal e checklist de privacidade no [README da pasta](exif-guard/README.md). Use apenas em arquivos próprios ou com autorização expressa.

## Uso ético

Destinado a estudo, defesa e testes em ambientes próprios ou com autorização expressa.

---

Desenvolvido por Carlpit
