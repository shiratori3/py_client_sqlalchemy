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
        (SELECT S_WORD, L_WORD = LEN(S_WORD) FROM (SELECT S_WORD = '{word_to_check}') C) B
    WHERE --XGSJ > '2020-11-20' AND
        RWID IS NOT NULL
        AND A.MXKMYSMC <> S_WORD
        AND A.MXKMYSMC NOT LIKE '% %'
        AND LEN(A.MXKMYSMC) < L_WORD + 2
        AND LEN(A.MXKMYSMC) > L_WORD - 2
    UNION ALL 
    SELECT DISTINCT [TPYE] = 'ZBSZ', S_WORD, L_WORD, A.RWID, [DATA] = A.ZBSZ
    FROM usrCWFZZYC A WITH(NOLOCK),
        (SELECT S_WORD, L_WORD = LEN(S_WORD) FROM (SELECT S_WORD = '{word_to_check}') C) B
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
                        (SUBSTRING(A.DATA, {pos_list[0]}, 1) = '{char_list[0]}' OR SUBSTRING(A.DATA, {pos_list[1]}, 1) = '{char_list[1]}')
                    AND (SUBSTRING(A.DATA, {pos_list[2]}, 1) = '{char_list[2]}' OR SUBSTRING(A.DATA, {pos_list[3]}, 1) = '{char_list[3]}')
                    --AND (SUBSTRING(A.DATA, {pos_list[4]}, 1) = '{char_list[4]}' OR SUBSTRING(A.DATA, {pos_list[5]}, 1) = '{char_list[5]}')
                    --AND (SUBSTRING(A.DATA, {pos_list[6]}, 1) = '{char_list[6]}' OR SUBSTRING(A.DATA, {pos_list[7]}, 1) = '{char_list[7]}')
                    --AND (SUBSTRING(A.DATA, {pos_list[8]}, 1) = '{char_list[8]}' OR SUBSTRING(A.DATA, {pos_list[9]}, 1) = '{char_list[9]}')
                    --AND (SUBSTRING(A.DATA, {pos_list[10]}, 1) = '{char_list[10]}' OR SUBSTRING(A.DATA, {pos_list[11]}, 1) = '{char_list[11]}')
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
                            SUBSTRING(A.DATA, {pos_list[0]}+1, 1) LIKE '[{char_list[0]}{char_list[1]}]' 
                        AND SUBSTRING(A.DATA, {pos_list[2]}+1, 1) LIKE '[{char_list[2]}{char_list[3]}]'
                        --AND (SUBSTRING(A.DATA, {pos_list[4]}+1, 1) LIKE '[{char_list[4]}{char_list[5]}]')
                        --AND (SUBSTRING(A.DATA, {pos_list[6]}+1, 1) LIKE '[{char_list[6]}{char_list[7]}]')
                        --AND (SUBSTRING(A.DATA, {pos_list[8]}+1, 1) LIKE '[{char_list[8]}{char_list[9]}]')
                        --AND (SUBSTRING(A.DATA, {pos_list[10]}+1, 1) LIKE '[{char_list[10]}{char_list[11]}]')
                    )
                    --OR  (SUBSTRING(A.DATA, 4, 1) LIKE '[]' AND SUBSTRING(A.DATA, L_WORD+1-2, 1) = '[]')
                )
            )
            OR (
                LEN(A.DATA) = L_WORD - 1 --AND A.RWID IS NULL
                --AND A.DATA NOT IN ('')
                AND (
                        (
                            SUBSTRING(A.DATA, {pos_list[0]}-1, 1) LIKE '[{char_list[0]}{char_list[1]}]' 
                        AND SUBSTRING(A.DATA, {pos_list[2]}-1, 1) LIKE '[{char_list[2]}{char_list[3]}]'
                        --AND (SUBSTRING(A.DATA, {pos_list[4]}-1, 1) LIKE '[{char_list[4]}{char_list[5]}]')
                        --AND (SUBSTRING(A.DATA, {pos_list[6]}-1, 1) LIKE '[{char_list[6]}{char_list[7]}]')
                        --AND (SUBSTRING(A.DATA, {pos_list[8]}-1, 1) LIKE '[{char_list[8]}{char_list[9]}]')
                        --AND (SUBSTRING(A.DATA, {pos_list[10]}-1, 1) LIKE '[{char_list[10]}{char_list[11]}]')
                    )
                    --OR  (SUBSTRING(A.DATA, 3, 1) LIKE '[]' AND SUBSTRING(A.DATA, L_WORD-3, 1) = '[]')
                )
            )
        )
    )
ORDER BY [存疑数据], [数据类型]