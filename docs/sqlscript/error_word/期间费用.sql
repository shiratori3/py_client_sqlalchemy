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
        (SELECT S_WORD, L_WORD = LEN(S_WORD) FROM (SELECT S_WORD = '期间费用') C) B
    WHERE --XGSJ > '2020-11-20' AND
        RWID IS NOT NULL
        AND A.MXKMYSMC <> S_WORD
        AND A.MXKMYSMC NOT LIKE '% %'
        AND LEN(A.MXKMYSMC) < L_WORD + 2
        AND LEN(A.MXKMYSMC) > L_WORD - 2
    UNION ALL 
    SELECT DISTINCT [TPYE] = 'ZBSZ', S_WORD, L_WORD, A.RWID, [DATA] = A.ZBSZ
    FROM usrCWFZZYC A WITH(NOLOCK),
        (SELECT S_WORD, L_WORD = LEN(S_WORD) FROM (SELECT S_WORD = '期间费用') C) B
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
        --AND A.DATA NOT LIKE '%%'
            LEFT(A.DATA,1) NOT LIKE '[]'
        AND RIGHT(A.DATA,1) NOT LIKE '[]'
        AND 
            (
                (LEN(A.DATA) = L_WORD
                --AND A.DATA <> ''
                --AND A.DATA NOT LIKE ''
                --AND A.DATA NOT IN ('')
                AND (
                        A.DATA LIKE '期_费_'
                    OR  A.DATA LIKE '期__用'
                    OR  A.DATA LIKE '_间费_'
                    OR  A.DATA LIKE '_间_用'
                )
            )
            OR (
                LEN(A.DATA) = L_WORD + 1
                --AND A.DATA NOT IN ('')
                AND (
                    A.DATA LIKE '_[期间][费用]_' 
                )
            )
            OR (
                LEN(A.DATA) = L_WORD - 1
                --AND A.DATA NOT IN ('')
                AND (
                    A.DATA LIKE '[期间][费用]' 
                )
            )
        )
    )
ORDER BY [存疑数据], [数据类型]