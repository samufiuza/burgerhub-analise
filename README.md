# 🍔 BurgerHub — Análise de Dados de Franquia

Esse é um projeto de análise de dados fictícios de uma rede de fast food com 5 unidades, cobrindo vendas, marketing e metas ao longo de 12 meses (2024).

---

## Sobre o projeto

Simula o trabalho de um analista de dados contratado pela franquia **BurgerHub** para transformar dados brutos em decisões de negócio. O banco de dados é gerado automaticamente com dados fictícios e realistas.

**Stack utilizada:** Python · Pandas · NumPy · SQLite · OpenPyXL

---

## Estrutura do projeto

```
burgerhub/
├── burgerhub.py          # Script principal (geração de dados + análise)
├── burgerhub_queries.sql # Todas as queries SQL separadas por missão de análise
├── output/
│   └── BurgerHub_Relatorio_2024.xlsx  # Aqui é Gerado automaticamente
└── README.md
```

---

## Missões de análise

| # | Missão | Técnicas |
|---|--------|----------|
| M1 | Diagnóstico geral de vendas | Agregação, variação %, ranking |
| M2 | Margem por produto + análise ABC | Lucro bruto, curva ABC, groupby |
| M3 | ROI de marketing por canal | JOIN SQL, cálculo de ROI |
| M4 | Metas vs. realizado | Atingimento %, detecção de sequências |
| M5 | Canal de venda (delivery vs. balcão) | Comparação de ticket médio, custo operacional |
| M6 | Relatório executivo automatizado | Exportação multi-aba Excel |

---

## Como executar

### Pré-requisitos

- Python 3.8+
- pip

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/burgerhub-analise.git
cd burgerhub-analise

# Instale as dependências
pip install pandas numpy openpyxl
```

### Execução

```bash
python burgerhub.py
```

O script irá:
1. Criar o banco SQLite (`burgerhub.db`) com ~33.000 registros fictícios
2. Executar todas as 6 missões que listamos acima, de análise no terminal
3. Gerar o relatório `output/BurgerHub_Relatorio_2024.xlsx` com 7 abas

---

## Listados os Resultados esperados

Ao rodar o script, você verá no terminal:

- Evolução mensal de receita com identificação de quedas
- Ranking das 5 unidades por receita
- Margem de lucro e classificação ABC de cada produto
- ROI por canal de marketing (Instagram, Google Ads, Flyer)
- Atingimento de metas mensais com alertas automáticos
- Comparativo de canais de venda (balcão, delivery, app)

---

## Aqui as Queries SQL

O arquivo `burgerhub_queries.sql` contém todas as queries organizadas por missão, compatíveis com **SQLite**. Você pode rodá-las em qualquer client SQL:

- [DB Browser for SQLite](https://sqlitebrowser.org/)
- DBeaver
- VS Code com extensão SQLite

```bash
# Rodar direto no terminal (após gerar o banco)
sqlite3 burgerhub.db < burgerhub_queries.sql
```

---

## Dependências

```
pandas>=2.0
numpy>=1.24
openpyxl>=3.1
```

---

## Autor

Desenvolvido por Samuel Fiuza, como projeto de estudo em análise de dados com Python e SQL.
