"""
=============================================================
  BurgerHub — Solução Completa de Análise de Dados - Teste Samuel Fiuza
  Franquia fictícia de fast food | 5 unidades | 12 meses
=============================================================
  Missões cobertas:
    M1 — Diagnóstico geral de vendas
    M2 — Margem por produto + análise ABC
    M3 — ROI de marketing por canal
    M4 — Metas vs. realizado
    M5 — Canal de venda (delivery vs. balcão)
    M6 — Automação: relatório executivo mensal em Excel
=============================================================
"""

import sqlite3
import random
import pandas as pd
import numpy as np
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
np.random.seed(42)

DB_PATH   = "burgerhub.db"
OUT_DIR   = Path("output")
OUT_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────
#  1. GERAÇÃO DOS DADOS FICTÍCIOS
# ──────────────────────────────────────────────

def gerar_dados(conn: sqlite3.Connection):
    """Cria as 4 tabelas e popula com dados fictícios realistas."""
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS unidades;
        DROP TABLE IF EXISTS produtos;
        DROP TABLE IF EXISTS vendas;
        DROP TABLE IF EXISTS marketing;

        CREATE TABLE unidades (
            unidade_id   INTEGER PRIMARY KEY,
            nome         TEXT,
            cidade       TEXT,
            abertura     TEXT,
            meta_mensal  REAL
        );

        CREATE TABLE produtos (
            produto_id  INTEGER PRIMARY KEY,
            nome        TEXT,
            categoria   TEXT,
            preco       REAL,
            custo       REAL
        );

        CREATE TABLE vendas (
            venda_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            unidade_id  INTEGER,
            data        TEXT,
            produto_id  INTEGER,
            quantidade  INTEGER,
            valor_total REAL,
            canal       TEXT,
            FOREIGN KEY (unidade_id) REFERENCES unidades(unidade_id),
            FOREIGN KEY (produto_id) REFERENCES produtos(produto_id)
        );

        CREATE TABLE marketing (
            campanha_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            unidade_id   INTEGER,
            mes          INTEGER,
            ano          INTEGER,
            canal_mkt    TEXT,
            investimento REAL,
            impressoes   INTEGER,
            cliques      INTEGER,
            FOREIGN KEY (unidade_id) REFERENCES unidades(unidade_id)
        );
    """)

    # ── Unidades
    unidades = [
        (1, "BurgerHub Centro",    "São Paulo",    "2020-03-01", 90_000),
        (2, "BurgerHub Pinheiros", "São Paulo",    "2021-01-15", 80_000),
        (3, "BurgerHub Campinas",  "Campinas",     "2021-06-10", 70_000),
        (4, "BurgerHub Santos",    "Santos",       "2022-02-20", 60_000),
        (5, "BurgerHub Ribeirão",  "Ribeirão Preto","2022-11-05",55_000),
    ]
    cur.executemany("INSERT INTO unidades VALUES (?,?,?,?,?)", unidades)

    # ── Produtos
    produtos = [
        (1,  "Classic Burger",       "Lanche",   28.90, 9.50),
        (2,  "Smash Burger Duplo",   "Lanche",   39.90, 13.00),
        (3,  "Veggie Burger",        "Lanche",   34.90, 10.00),
        (4,  "Chicken Crispy",       "Lanche",   32.90, 10.50),
        (5,  "Batata Frita P",       "Acompan.", 14.90, 3.50),
        (6,  "Batata Frita G",       "Acompan.", 19.90, 5.00),
        (7,  "Onion Rings",          "Acompan.", 22.90, 6.00),
        (8,  "Refrigerante",         "Bebida",    8.90, 2.00),
        (9,  "Milkshake",            "Bebida",   22.90, 5.50),
        (10, "Combo Família (4 pax)","Combo",    99.90, 38.00),
        (11, "Brownie",              "Sobremesa",12.90, 3.80),
        (12, "Sorvete Casquinha",    "Sobremesa", 7.90, 1.50),
    ]
    cur.executemany("INSERT INTO produtos VALUES (?,?,?,?,?)", produtos)

    # ── Vendas (≈ 18 000 registros)
    canais    = ["Balcão", "Delivery", "App"]
    canal_p   = [0.45, 0.35, 0.20]
    inicio    = date(2024, 1, 1)
    fim       = date(2024, 12, 31)
    dias      = (fim - inicio).days + 1
    preco_map = {p[0]: (p[3], p[4]) for p in produtos}

    vendas_rows = []
    for unidade_id in range(1, 6):
        n_dias_venda = random.randint(340, 366)
        datas = sorted(random.choices(
            [inicio + timedelta(d) for d in range(dias)],
            k=n_dias_venda
        ))
        for data_v in datas:
            n_trans = random.randint(8, 30)
            for _ in range(n_trans):
                prod_id = random.randint(1, 12)
                qtd     = random.randint(1, 4)
                preco, _ = preco_map[prod_id]
                # Delivery tem ticket ligeiramente mais alto
                canal   = random.choices(canais, weights=canal_p)[0]
                mult    = 1.10 if canal == "Delivery" else 1.0
                total   = round(preco * qtd * mult * random.uniform(0.95, 1.05), 2)
                vendas_rows.append((unidade_id, str(data_v), prod_id, qtd, total, canal))

    cur.executemany(
        "INSERT INTO vendas (unidade_id,data,produto_id,quantidade,valor_total,canal) VALUES (?,?,?,?,?,?)",
        vendas_rows,
    )

    # ── Marketing (mensal, 3 canais, 5 unidades → 180 linhas)
    canais_mkt = ["Instagram", "Google Ads", "Flyer"]
    mkt_rows   = []
    for unidade_id in range(1, 6):
        for mes in range(1, 13):
            for canal_m in canais_mkt:
                inv = round(random.uniform(800, 5000), 2)
                ctr = random.uniform(0.02, 0.08)
                imp = random.randint(10_000, 80_000)
                clq = int(imp * ctr)
                mkt_rows.append((unidade_id, mes, 2024, canal_m, inv, imp, clq))

    cur.executemany(
        "INSERT INTO marketing (unidade_id,mes,ano,canal_mkt,investimento,impressoes,cliques) VALUES (?,?,?,?,?,?,?)",
        mkt_rows,
    )

    conn.commit()
    print(f"✅  Dados gerados: {len(vendas_rows):,} vendas | {len(mkt_rows)} campanhas")


# ──────────────────────────────────────────────
#  2. CONSULTAS SQL (QUERIES)
# ──────────────────────────────────────────────

SQL_M1_MENSAL = """
    SELECT
        strftime('%Y-%m', v.data)                 AS mes,
        SUM(v.valor_total)                        AS receita,
        COUNT(*)                                  AS qtd_transacoes,
        ROUND(AVG(v.valor_total), 2)              AS ticket_medio
    FROM vendas v
    GROUP BY mes
    ORDER BY mes;
"""

SQL_M1_RANKING = """
    SELECT
        u.nome                          AS unidade,
        u.cidade,
        ROUND(SUM(v.valor_total), 2)    AS receita_total,
        COUNT(*)                        AS transacoes,
        ROUND(AVG(v.valor_total), 2)    AS ticket_medio
    FROM vendas v
    JOIN unidades u ON u.unidade_id = v.unidade_id
    GROUP BY v.unidade_id
    ORDER BY receita_total DESC;
"""

SQL_M2_MARGEM = """
    SELECT
        p.nome                                              AS produto,
        p.categoria,
        ROUND(p.preco - p.custo, 2)                        AS lucro_bruto_unit,
        ROUND((p.preco - p.custo) / p.preco * 100, 1)      AS margem_pct,
        SUM(v.quantidade)                                   AS qtd_vendida,
        ROUND(SUM(v.quantidade) * (p.preco - p.custo), 2)  AS lucro_total
    FROM vendas v
    JOIN produtos p ON p.produto_id = v.produto_id
    GROUP BY v.produto_id
    ORDER BY lucro_total DESC;
"""

SQL_M3_ROI = """
    SELECT
        m.canal_mkt,
        u.nome                                                        AS unidade,
        ROUND(SUM(m.investimento), 2)                                 AS invest_total,
        ROUND(SUM(v_mes.receita), 2)                                  AS receita_periodo,
        ROUND((SUM(v_mes.receita) - SUM(m.investimento))
              / NULLIF(SUM(m.investimento), 0) * 100, 1)              AS roi_pct
    FROM marketing m
    JOIN unidades u ON u.unidade_id = m.unidade_id
    LEFT JOIN (
        SELECT
            unidade_id,
            CAST(strftime('%m', data) AS INTEGER) AS mes,
            SUM(valor_total) AS receita
        FROM vendas
        GROUP BY unidade_id, mes
    ) v_mes ON v_mes.unidade_id = m.unidade_id AND v_mes.mes = m.mes
    GROUP BY m.canal_mkt, m.unidade_id
    ORDER BY roi_pct DESC;
"""

SQL_M4_METAS = """
    SELECT
        u.nome                                        AS unidade,
        strftime('%Y-%m', v.data)                     AS mes,
        ROUND(SUM(v.valor_total), 2)                  AS receita,
        u.meta_mensal,
        ROUND(SUM(v.valor_total) / u.meta_mensal * 100, 1) AS atingimento_pct,
        CASE WHEN SUM(v.valor_total) >= u.meta_mensal
             THEN 'Atingiu' ELSE 'Abaixo' END         AS status
    FROM vendas v
    JOIN unidades u ON u.unidade_id = v.unidade_id
    GROUP BY v.unidade_id, mes
    ORDER BY unidade, mes;
"""

SQL_M5_CANAL = """
    SELECT
        canal,
        COUNT(*)                             AS transacoes,
        ROUND(SUM(valor_total), 2)           AS receita_total,
        ROUND(AVG(valor_total), 2)           AS ticket_medio,
        ROUND(SUM(valor_total)
            / (SELECT SUM(valor_total) FROM vendas) * 100, 1) AS share_pct
    FROM vendas
    GROUP BY canal
    ORDER BY receita_total DESC;
"""


# ──────────────────────────────────────────────
#  3. MISSÕES DE ANÁLISE (PYTHON + pandas)
# ──────────────────────────────────────────────

def m1_diagnostico(conn):
    print("\n" + "═"*60)
    print("  M1 — DIAGNÓSTICO GERAL DE VENDAS")
    print("═"*60)

    mensal = pd.read_sql(SQL_M1_MENSAL, conn)
    mensal["var_pct"] = mensal["receita"].pct_change() * 100

    print("\n📅  Evolução mensal:")
    print(mensal.to_string(index=False))

    quedas = mensal[mensal["var_pct"] < -5]
    if not quedas.empty:
        print(f"\n⚠️   Meses com queda > 5%: {quedas['mes'].tolist()}")

    ranking = pd.read_sql(SQL_M1_RANKING, conn)
    print("\n🏆  Ranking de unidades:")
    print(ranking.to_string(index=False))

    return mensal, ranking


def m2_margem_abc(conn):
    print("\n" + "═"*60)
    print("  M2 — MARGEM POR PRODUTO + ANÁLISE ABC")
    print("═"*60)

    df = pd.read_sql(SQL_M2_MARGEM, conn)

    # Análise ABC por lucro acumulado
    df = df.sort_values("lucro_total", ascending=False).reset_index(drop=True)
    df["lucro_acum_pct"] = df["lucro_total"].cumsum() / df["lucro_total"].sum() * 100
    df["abc"] = pd.cut(
        df["lucro_acum_pct"],
        bins=[-np.inf, 70, 90, np.inf],
        labels=["A", "B", "C"]
    )

    print("\n📊  Margem por produto (ordem decrescente de lucro):")
    print(df[["produto", "categoria", "margem_pct", "qtd_vendida", "lucro_total", "abc"]].to_string(index=False))

    por_cat = df.groupby("categoria").agg(
        margem_media=("margem_pct", "mean"),
        lucro_total=("lucro_total", "sum")
    ).sort_values("lucro_total", ascending=False)
    print("\n📂  Resumo por categoria:")
    print(por_cat.round(1).to_string())

    return df


def m3_roi_marketing(conn):
    print("\n" + "═"*60)
    print("  M3 — ROI DE MARKETING POR CANAL")
    print("═"*60)

    df = pd.read_sql(SQL_M3_ROI, conn)
    print("\n💰  ROI por canal e unidade:")
    print(df.to_string(index=False))

    resumo = (
        df.groupby("canal_mkt")
          .agg(invest=("invest_total","sum"), receita=("receita_periodo","sum"))
          .assign(roi_geral=lambda x: (x.receita - x.invest) / x.invest * 100)
          .sort_values("roi_geral", ascending=False)
    )
    print("\n🔝  ROI consolidado por canal:")
    print(resumo.round(1).to_string())
    best = resumo.index[0]
    print(f"\n✅  Melhor canal: {best} ({resumo.loc[best,'roi_geral']:.1f}% ROI)")

    return df


def m4_metas(conn):
    print("\n" + "═"*60)
    print("  M4 — METAS VS. REALIZADO")
    print("═"*60)

    df = pd.read_sql(SQL_M4_METAS, conn)
    print("\n📋  Atingimento mensal por unidade (primeiros 24 registros):")
    print(df.head(24).to_string(index=False))

    resumo = (
        df.groupby("unidade")
          .agg(
              meses_atingidos=("status", lambda x: (x == "Atingiu").sum()),
              atingimento_medio=("atingimento_pct", "mean"),
          )
    )
    print("\n📈  Resumo anual:")
    print(resumo.round(1).to_string())

    # Unidades com 3+ meses consecutivos abaixo da meta
    alertas = []
    for unidade, grupo in df.groupby("unidade"):
        grupo = grupo.sort_values("mes").reset_index(drop=True)
        consec = 0
        for _, row in grupo.iterrows():
            if row["status"] == "Abaixo":
                consec += 1
                if consec >= 3:
                    alertas.append(unidade)
                    break
            else:
                consec = 0

    if alertas:
        print(f"\n🚨  Alerta — 3+ meses seguidos abaixo da meta: {set(alertas)}")
    else:
        print("\n✅  Nenhuma unidade ficou 3+ meses seguidos abaixo da meta.")

    return df


def m5_canal_venda(conn):
    print("\n" + "═"*60)
    print("  M5 — CANAL DE VENDA (DELIVERY vs. BALCÃO vs. APP)")
    print("═"*60)

    df = pd.read_sql(SQL_M5_CANAL, conn)
    print("\n🛵  Breakdown por canal:")
    print(df.to_string(index=False))

    # Hipótese: delivery tem ~15% de custo operacional extra
    df["custo_operacional"] = df.apply(
        lambda r: r["receita_total"] * 0.15 if r["canal"] == "Delivery" else 0,
        axis=1,
    )
    df["receita_liq"] = df["receita_total"] - df["custo_operacional"]
    print("\n💡  Receita líquida pós-custo operacional:")
    print(df[["canal", "receita_total", "custo_operacional", "receita_liq"]].to_string(index=False))

    return df


# ──────────────────────────────────────────────
#  4. M6 — AUTOMAÇÃO: RELATÓRIO EXECUTIVO EXCEL
# ──────────────────────────────────────────────

def m6_relatorio_excel(conn, mensal, ranking, df_abc, df_roi, df_metas, df_canal):
    print("\n" + "═"*60)
    print("  M6 — GERANDO RELATÓRIO EXECUTIVO (.xlsx)")
    print("═"*60)

    path = OUT_DIR / "BurgerHub_Relatorio_2024.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:

        # ── Aba 1: Visão geral mensal
        mensal_out = mensal.copy()
        mensal_out["var_pct"] = mensal_out["var_pct"].round(1)
        mensal_out.to_excel(writer, sheet_name="Vendas Mensais", index=False)

        # ── Aba 2: Ranking unidades
        ranking.to_excel(writer, sheet_name="Ranking Unidades", index=False)

        # ── Aba 3: Margem + ABC
        df_abc[["produto","categoria","margem_pct","qtd_vendida","lucro_total","abc"]]\
            .to_excel(writer, sheet_name="Margem ABC", index=False)

        # ── Aba 4: ROI Marketing
        df_roi.to_excel(writer, sheet_name="ROI Marketing", index=False)

        # ── Aba 5: Metas vs Realizado
        df_metas.to_excel(writer, sheet_name="Metas", index=False)

        # ── Aba 6: Canal de venda
        df_canal.to_excel(writer, sheet_name="Canal Venda", index=False)

        # ── Aba 7: KPIs resumidos
        kpis = pd.DataFrame({
            "KPI": [
                "Receita Total 2024",
                "Ticket Médio Geral",
                "Melhor Unidade",
                "Pior Unidade",
                "Produto Mais Lucrativo",
                "Melhor Canal de Marketing",
                "Canal de Venda Dominante",
            ],
            "Valor": [
                f"R$ {mensal['receita'].sum():,.2f}",
                f"R$ {mensal['ticket_medio'].mean():,.2f}",
                ranking.iloc[0]["unidade"],
                ranking.iloc[-1]["unidade"],
                df_abc.iloc[0]["produto"],
                df_roi.groupby("canal_mkt")["roi_pct"].mean().idxmax(),
                df_canal.iloc[0]["canal"],
            ],
        })
        kpis.to_excel(writer, sheet_name="KPIs Executivos", index=False)

    print(f"\n✅  Relatório salvo em: {path}")
    return path


# ──────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────

def main():
    print("🍔  BurgerHub — Análise de Dados | Iniciando...\n")

    conn = sqlite3.connect(DB_PATH)

    # 1. Gera os dados
    gerar_dados(conn)

    # 2. Executa as missões
    mensal, ranking = m1_diagnostico(conn)
    df_abc           = m2_margem_abc(conn)
    df_roi           = m3_roi_marketing(conn)
    df_metas         = m4_metas(conn)
    df_canal         = m5_canal_venda(conn)

    # 3. Exporta relatório
    m6_relatorio_excel(conn, mensal, ranking, df_abc, df_roi, df_metas, df_canal)

    conn.close()
    print("\n🎉  Análise concluída! Arquivos na pasta /output")


if __name__ == "__main__":
    main()
