SELECT DISTINCT --(SELECT MAX(ID) FROM usrCWFZZYC WHERE RWID=A.RWID) ID,
    [校验类型] = CONCAT('【', S_WORD, '】错别字'),
    [数据类型] = A.TPYE,
    -- [RWID] = A.RWID,
    -- [最小行编码] = (
    --     SELECT MIN(CONVERT(INT,HBM)) FROM usrCWFZZYC WITH(NOLOCK) WHERE RWID=A.RWID AND 
    --         (MXKMYSMC = A.DATA OR ZBSZ = A.DATA)
    --     ),
    -- [最大行编码] = (
    --     SELECT MAX(CONVERT(INT,HBM)) FROM usrCWFZZYC WITH(NOLOCK) WHERE RWID=A.RWID AND 
    --         (MXKMYSMC = A.DATA OR ZBSZ = A.DATA)
    --     ),
    [存疑数据] = A.DATA
FROM (
    SELECT DISTINCT [TPYE] = 'MXKMYSMC', S_WORD, L_WORD, A.RWID, [DATA] = A.MXKMYSMC
    FROM usrCWFZZYC A WITH(NOLOCK),
        (SELECT S_WORD, L_WORD = LEN(S_WORD) FROM (SELECT S_WORD = '二、将重分类进损益的其他综合收益：权益法下可转损益的其他综合收益') C) B
    WHERE --XGSJ > '2020-11-20' AND
        RWID IS NOT NULL
        AND A.MXKMYSMC <> S_WORD
        AND A.MXKMYSMC NOT LIKE '% %'
        AND LEN(A.MXKMYSMC) < L_WORD + 2
        AND LEN(A.MXKMYSMC) > L_WORD - 2
    UNION ALL 
    SELECT DISTINCT [TPYE] = 'ZBSZ', S_WORD, L_WORD, A.RWID, [DATA] = A.ZBSZ
    FROM usrCWFZZYC A WITH(NOLOCK),
        (SELECT S_WORD, L_WORD = LEN(S_WORD) FROM (SELECT S_WORD = '二、将重分类进损益的其他综合收益：权益法下可转损益的其他综合收益') C) B
    WHERE --XGSJ > '2020-11-20' AND
        RWID IS NOT NULL
        AND A.ZBSZ <> S_WORD
        AND A.ZBSZ NOT LIKE '% %'
        AND LEN(A.ZBSZ) < L_WORD + 2
        AND LEN(A.ZBSZ) > L_WORD - 2
) A
WHERE
    A.DATA IS NOT NULL
    AND (
            LEFT(A.DATA,1) NOT LIKE '[]'
        AND RIGHT(A.DATA,1) NOT LIKE '[]'
        AND 
            (
                (LEN(A.DATA) = L_WORD --AND A.RWID IS NULL
                --AND A.DATA <> ''
                --AND A.DATA NOT LIKE ''
                --AND A.DATA NOT IN ('')
                AND (
                        (SUBSTRING(A.DATA, 3, 1) = '将' OR SUBSTRING(A.DATA, 4, 1) = '重')
                    AND (SUBSTRING(A.DATA, 22, 1) = '可' OR SUBSTRING(A.DATA, 23, 1) = '转')
                    AND (SUBSTRING(A.DATA, 30, 1) = '合' OR SUBSTRING(A.DATA, 31, 1) = '收')
                    --AND (SUBSTRING(A.DATA, , 1) = '' OR SUBSTRING(A.DATA, , 1) = '')
                    --AND (SUBSTRING(A.DATA, , 1) = '' OR SUBSTRING(A.DATA, , 1) = '')
                    --AND (SUBSTRING(A.DATA, , 1) = '' OR SUBSTRING(A.DATA, , 1) = '')
                )
                -- AND (
                -- 	SUBSTRING(A.DATA, 2, 1) NOT LIKE '[]' 
                -- 	AND SUBSTRING(A.DATA, 3, 1) NOT LIKE '[]' 
                -- )
            )
            OR (
                LEN(A.DATA) = L_WORD + 1 --AND A.RWID IS NULL
                --AND A.DATA NOT IN ('')
                AND (
                        (
                            SUBSTRING(A.DATA, 3+1, 1) LIKE '[将重]' 
                        AND SUBSTRING(A.DATA, 22+1, 1) LIKE '[可转]'
                        AND (SUBSTRING(A.DATA, 30+1, 1) LIKE '[合收]')
                        --AND (SUBSTRING(A.DATA, +1, 1) LIKE '[]')
                        --AND (SUBSTRING(A.DATA, +1, 1) LIKE '[]')
                        --AND (SUBSTRING(A.DATA, +1, 1) LIKE '[]')
                    )
                    --OR  (SUBSTRING(A.DATA, 4, 1) LIKE '[]' AND SUBSTRING(A.DATA, L_WORD+1-2, 1) = '[]')
                )
            )
            OR (
                LEN(A.DATA) = L_WORD - 1 --AND A.RWID IS NULL
                --AND A.DATA NOT IN ('')
                AND (
                        (
                            SUBSTRING(A.DATA, 3-1, 1) LIKE '[将重]' 
                        AND SUBSTRING(A.DATA, 22-1, 1) LIKE '[可转]'
                        AND (SUBSTRING(A.DATA, 30-1, 1) LIKE '[合收]')
                        --AND (SUBSTRING(A.DATA, -1, 1) LIKE '[]')
                        --AND (SUBSTRING(A.DATA, -1, 1) LIKE '[]')
                        --AND (SUBSTRING(A.DATA, -1, 1) LIKE '[]')
                    )
                    --OR  (SUBSTRING(A.DATA, 3, 1) LIKE '[]' AND SUBSTRING(A.DATA, L_WORD-3, 1) = '[]')
                )
            )
        )
    )
ORDER BY [存疑数据], [数据类型]