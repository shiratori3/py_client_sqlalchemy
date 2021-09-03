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
        (SELECT S_WORD, L_WORD = LEN(S_WORD) FROM (SELECT S_WORD = '除同公司正常经营业务相关的有效套期保值业务外，持有交易性金融资产、衍生金融资产、交易性金融负债、衍生金融负债产生的公允价值变动损益，以及处置交易性金融资产、衍生金融资产、交易性金融负债、衍生金融负债和其他债权投资取得的投资收益') C) B
    WHERE --XGSJ > '2020-11-20' AND
        RWID IS NOT NULL
        AND A.MXKMYSMC <> S_WORD
        AND A.MXKMYSMC NOT LIKE '% %'
        AND LEN(A.MXKMYSMC) < L_WORD + 2
        AND LEN(A.MXKMYSMC) > L_WORD - 2
    UNION ALL 
    SELECT DISTINCT [TPYE] = 'ZBSZ', S_WORD, L_WORD, A.RWID, [DATA] = A.ZBSZ
    FROM usrCWFZZYC A WITH(NOLOCK),
        (SELECT S_WORD, L_WORD = LEN(S_WORD) FROM (SELECT S_WORD = '除同公司正常经营业务相关的有效套期保值业务外，持有交易性金融资产、衍生金融资产、交易性金融负债、衍生金融负债产生的公允价值变动损益，以及处置交易性金融资产、衍生金融资产、交易性金融负债、衍生金融负债和其他债权投资取得的投资收益') C) B
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
                        (SUBSTRING(A.DATA, 16, 1) = '套' OR SUBSTRING(A.DATA, 17, 1) = '期')
                    AND (SUBSTRING(A.DATA, 55, 1) = '产' OR SUBSTRING(A.DATA, 56, 1) = '生')
                    AND (SUBSTRING(A.DATA, 68, 1) = '处' OR SUBSTRING(A.DATA, 69, 1) = '置')
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
                            SUBSTRING(A.DATA, 16+1, 1) LIKE '[套期]' 
                        AND SUBSTRING(A.DATA, 55+1, 1) LIKE '[产生]'
                        AND (SUBSTRING(A.DATA, 68+1, 1) LIKE '[处置]')
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
                            SUBSTRING(A.DATA, 16, 1) LIKE '[套期]' 
                        AND SUBSTRING(A.DATA, 55, 1) LIKE '[产生]'
                        AND (SUBSTRING(A.DATA, 68, 1) LIKE '[处置]')
                        --AND (SUBSTRING(A.DATA, , 1) LIKE '[]')
                        --AND (SUBSTRING(A.DATA, , 1) LIKE '[]')
                        --AND (SUBSTRING(A.DATA, , 1) LIKE '[]')
                    )
                    --OR  (SUBSTRING(A.DATA, 3, 1) LIKE '[]' AND SUBSTRING(A.DATA, L_WORD-3, 1) = '[]')
                )
            )
        )
    )
ORDER BY [存疑数据], [数据类型]