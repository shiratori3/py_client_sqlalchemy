SELECT DISTINCT 
    [校验类型] = '录入错误："{correct_word}"错录入为"{error_word}"',
    RWID,
    HBM,
    MXKMYSMC = (CASE 
        WHEN MXKMYSMC LIKE '%{error_word}%' THEN MXKMYSMC
    END),
    XMMC = (CASE 
        WHEN ZBSZ LIKE '%{error_word}%' THEN XMMC
    END),
    ZBSZ = (CASE 
        WHEN ZBSZ LIKE '%{error_word}%' THEN ZBSZ
    END)
FROM usrCWFZZYC WITH(NOLOCK)
WHERE
    RWID IS NOT NULL
    AND (
            (
                ZBSZ LIKE '%{error_word}%'
        )
        OR (
            MXKMYSMC LIKE '%{error_word}%'
        )
    )
