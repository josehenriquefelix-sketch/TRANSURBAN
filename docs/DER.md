# DER — TRANSURBAN

## Diagrama Entidade-Relacionamento

```mermaid
erDiagram

    CIDADE {
        INTEGER id_cidade PK
        VARCHAR nome
    }

    LINHA_ONIBUS {
        INTEGER id_linha PK
        VARCHAR codigo
        VARCHAR nome
    }

    TRECHO {
        INTEGER id_trecho PK
        INTEGER id_cidade_origem FK
        INTEGER id_cidade_destino FK
        VARCHAR nome
        NUMERIC distancia_km
    }

    LINHA_TRECHO {
        INTEGER id_linha PK, FK
        INTEGER id_trecho PK, FK
        INTEGER ordem
    }

    FAIXA_EXCLUSIVA {
        INTEGER id_faixa PK
        INTEGER id_trecho FK
        VARCHAR tipo
        VARCHAR status
    }

    REGISTRO_ATRASO {
        INTEGER id_atraso PK
        INTEGER id_linha FK
        INTEGER id_trecho FK
        DATE data_registro
        INTEGER minutos_atraso
        VARCHAR observacao
    }

    CIDADE ||--o{ TRECHO : "origem"
    CIDADE ||--o{ TRECHO : "destino"

    LINHA_ONIBUS ||--o{ LINHA_TRECHO : utiliza
    TRECHO ||--o{ LINHA_TRECHO : possui

    TRECHO ||--o{ FAIXA_EXCLUSIVA : possui

    LINHA_ONIBUS ||--o{ REGISTRO_ATRASO : apresenta
    TRECHO ||--o{ REGISTRO_ATRASO : registra
