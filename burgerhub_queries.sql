;-- =============================================================
--  BurgerHub — Queries SQL Completas
--  Use com: sqlite3 burgerhub.db < burgerhub_queries.sql
--           ou execute cada bloco no DB Browser / DBeaver
-- =============================================================


-- ────────────────────────────────────────────
--  M1 — DIAGNÓSTICO GERAL DE VENDAS
-- ────────────────────────────────────────────

-- Receita e ticket médio por mês
SELECT
    strftime('%Y-%m', data)           AS mes,
    ROUND(SUM(valor_total), 2)        AS receita,
    COUNT(*)                          AS transacoes,
    ROUND(AVG(valor_total), 2)        AS ticket_medio
FROM vendas
GROUP BY mes
ORDER BY mes;

-- Ranking de unidades no ano
SELECT
    u.nome                            AS unidade,
    u.cidade,
    ROUND(SUM(v.valor_total), 2)      AS receita_total,
    COUNT(*)                          AS transacoes,
    ROUND(AVG(v.valor_total), 2)      AS ticket_medio
FROM vendas v
JOIN unidades u ON u.unidade_id = v.unidade_id
GROUP BY v.unidade_id
ORDER BY receita_total DESC;


-- Receita diária (útil para detectar sazonalidade semanal)
SELECT
    v.data,
    strftime('%w', v.data)            AS dia_semana,  -- 0=dom … 6=sáb
    ROUND(SUM(v.valor_total), 2)      AS receita
FROM vendas v
GROUP BY v.data
ORDER BY v.data;


-- ────────────────────────────────────────────
--  M2 — MARGEM POR PRODUTO + ANÁLISE ABC
-- ────────────────────────────────────────────

-- Lucro bruto e margem por produto
SELECT
    p.nome                                               AS produto,
    p.categoria,
    ROUND(p.preco - p.custo, 2)                         AS lucro_unit,
    ROUND((p.preco - p.custo) / p.preco * 100, 1)       AS margem_pct,
    SUM(v.quantidade)                                    AS qtd_vendida,
    ROUND(SUM(v.quantidade) * (p.preco - p.custo), 2)   AS lucro_total
FROM vendas v
JOIN produtos p ON p.produto_id = v.produto_id
GROUP BY v.produto_id
ORDER BY lucro_total DESC;


-- Margem média por categoria
SELECT
    p.categoria,
    ROUND(AVG((p.preco - p.custo) / p.preco * 100), 1)  AS margem_media_pct,
    ROUND(SUM(v.quantidade * (p.preco - p.custo)), 2)    AS lucro_total_cat
FROM vendas v
JOIN produtos p ON p.produto_id = v.produto_id
GROUP BY p.categoria
ORDER BY lucro_total_cat DESC;


-- ────────────────────────────────────────────
--  M3 — ROI DE MARKETING
-- ────────────────────────────────────────────

-- ROI por canal e unidade (join marketing com vendas do mesmo mês)
SELECT
    m.canal_mkt,
    u.nome                                                         AS unidade,
    ROUND(SUM(m.investimento), 2)                                  AS invest_total,
    ROUND(SUM(v_mes.receita), 2)                                   AS receita_periodo,
    ROUND(
        (SUM(v_mes.receita) - SUM(m.investimento))
        / NULLIF(SUM(m.investimento), 0) * 100
    , 1)                                                           AS roi_pct,
    ROUND(SUM(m.cliques) * 1.0 / NULLIF(SUM(m.impressoes),0) * 100, 2) AS ctr_pct
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


-- ROI consolidado por canal (visão geral)
SELECT
    m.canal_mkt,
    ROUND(SUM(m.investimento), 2)                                  AS invest_total,
    ROUND(SUM(v_mes.receita), 2)                                   AS receita_total,
    ROUND(
        (SUM(v_mes.receita) - SUM(m.investimento))
        / NULLIF(SUM(m.investimento), 0) * 100
    , 1)                                                           AS roi_pct
FROM marketing m
LEFT JOIN (
    SELECT
        unidade_id,
        CAST(strftime('%m', data) AS INTEGER) AS mes,
        SUM(valor_total) AS receita
    FROM vendas
    GROUP BY unidade_id, mes
) v_mes ON v_mes.unidade_id = m.unidade_id AND v_mes.mes = m.mes
GROUP BY m.canal_mkt
ORDER BY roi_pct DESC;


-- ────────────────────────────────────────────
--  M4 — METAS VS. REALIZADO
-- ────────────────────────────────────────────

-- Atingimento mensal por unidade
SELECT
    u.nome                                               AS unidade,
    strftime('%Y-%m', v.data)                            AS mes,
    ROUND(SUM(v.valor_total), 2)                         AS receita,
    u.meta_mensal                                        AS meta,
    ROUND(SUM(v.valor_total) / u.meta_mensal * 100, 1)  AS atingimento_pct,
    CASE WHEN SUM(v.valor_total) >= u.meta_mensal
         THEN '✅ Atingiu' ELSE '❌ Abaixo' END          AS status
FROM vendas v
JOIN unidades u ON u.unidade_id = v.unidade_id
GROUP BY v.unidade_id, mes
ORDER BY unidade, mes;


-- Percentual de meses com meta atingida por unidade (ranking de consistência)
SELECT
    u.nome,
    COUNT(*)                                                 AS total_meses,
    SUM(CASE WHEN sub.receita >= u.meta_mensal THEN 1 ELSE 0 END) AS meses_ok,
    ROUND(
        SUM(CASE WHEN sub.receita >= u.meta_mensal THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100
    , 1)                                                     AS pct_meses_ok
FROM (
    SELECT unidade_id, strftime('%Y-%m', data) AS mes, SUM(valor_total) AS receita
    FROM vendas
    GROUP BY unidade_id, mes
) sub
JOIN unidades u ON u.unidade_id = sub.unidade_id
GROUP BY sub.unidade_id
ORDER BY pct_meses_ok DESC;


-- ────────────────────────────────────────────
--  M5 — CANAL DE VENDA
-- ────────────────────────────────────────────

-- Breakdown de receita e ticket por canal
SELECT
    canal,
    COUNT(*)                             AS transacoes,
    ROUND(SUM(valor_total), 2)           AS receita_total,
    ROUND(AVG(valor_total), 2)           AS ticket_medio,
    ROUND(
        SUM(valor_total)
        / (SELECT SUM(valor_total) FROM vendas) * 100
    , 1)                                 AS share_pct
FROM vendas
GROUP BY canal
ORDER BY receita_total DESC;


-- Canal por unidade (para ver se o mix varia entre filiais)
SELECT
    u.nome                               AS unidade,
    v.canal,
    COUNT(*)                             AS transacoes,
    ROUND(SUM(v.valor_total), 2)         AS receita,
    ROUND(AVG(v.valor_total), 2)         AS ticket_medio
FROM vendas v
JOIN unidades u ON u.unidade_id = v.unidade_id
GROUP BY v.unidade_id, v.canal
ORDER BY unidade, receita DESC;


-- ────────────────────────────────────────────
--  BÔNUS — CROSS-ANALYSIS
-- ────────────────────────────────────────────

-- Top 3 produtos mais vendidos por unidade
SELECT *
FROM (
    SELECT
        u.nome                   AS unidade,
        p.nome                   AS produto,
        SUM(v.quantidade)        AS qtd,
        ROUND(SUM(v.valor_total), 2) AS receita,
        ROW_NUMBER() OVER (
            PARTITION BY v.unidade_id
            ORDER BY SUM(v.quantidade) DESC
        ) AS rank_prod
    FROM vendas v
    JOIN produtos p ON p.produto_id = v.produto_id
    JOIN unidades u ON u.unidade_id = v.unidade_id
    GROUP BY v.unidade_id, v.produto_id
) ranked
WHERE rank_prod <= 3
ORDER BY unidade, rank_prod;


-- Sazonalidade: receita média por dia da semana (0=dom, 6=sáb)
SELECT
    CASE strftime('%w', data)
        WHEN '0' THEN 'Domingo'
        WHEN '1' THEN 'Segunda'
        WHEN '2' THEN 'Terça'
        WHEN '3' THEN 'Quarta'
        WHEN '4' THEN 'Quinta'
        WHEN '5' THEN 'Sexta'
        WHEN '6' THEN 'Sábado'
    END                               AS dia_semana,
    ROUND(AVG(receita_dia), 2)        AS receita_media
FROM (
    SELECT data, SUM(valor_total) AS receita_dia
    FROM vendas
    GROUP BY data
) sub
GROUP BY strftime('%w', data)
ORDER BY strftime('%w', data);
