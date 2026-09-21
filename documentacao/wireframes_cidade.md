# Wireframes — tabela cidade

Os wireframes abaixo nascem diretamente dos campos existentes no DER e no Dicionário de Dados.

## Cadastro de cidade ↔ POST

```text
┌──────────────────────────────────────────────┐
│ TRANSURBAN — Cadastro de cidade              │
├──────────────────────────────────────────────┤
│ ID da cidade                                 │
│ [ 99                                      ]  │
│                                              │
│ Nome                                         │
│ [ Cidade Teste Módulo 6                   ]  │
│                                              │
│              [ CADASTRAR ]                   │
└──────────────────────────────────────────────┘
```

Campos enviados:

- `id_cidade`
- `nome`

Ação planejada: `POST /cidades/`.

## Consulta de cidades ↔ GET

```text
┌──────────────────────────────────────────────┐
│ TRANSURBAN — Cidades cadastradas             │
├──────────────┬───────────────────────────────┤
│ ID           │ Nome                          │
├──────────────┼───────────────────────────────┤
│ 1            │ Maringá                       │
│ 2            │ Sarandi                       │
│ 99           │ Cidade Teste Módulo 6         │
└──────────────┴───────────────────────────────┘
│                 [ ATUALIZAR ]                │
└──────────────────────────────────────────────┘
```

Ação planejada: `GET /cidades/`.

## Relação com o modelo

Nenhum campo foi inventado para o cadastro. A interface utiliza apenas os atributos previstos para `cidade` no modelo atual.
