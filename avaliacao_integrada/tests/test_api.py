"""Testes locais com banco em memória; nenhuma escrita é enviada ao Supabase."""
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.controller import cidades, linhas
from backend.main import app


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, database, table_name):
        self.database = database
        self.table_name = table_name
        self.operation = None
        self.payload = None
        self.filters = {}

    def table(self, _name):
        return self

    def select(self, _columns):
        if self.operation is None:
            self.operation = "select"
        return self

    def insert(self, payload):
        self.operation, self.payload = "insert", payload
        return self

    def update(self, payload):
        self.operation, self.payload = "update", payload
        return self

    def delete(self):
        self.operation = "delete"
        return self

    def eq(self, column, value):
        self.filters[column] = value
        return self

    def order(self, _column):
        return self

    def limit(self, _count):
        return self

    def _represent(self, row):
        result = row.copy()
        if self.table_name == "linha_onibus":
            city = next((c for c in self.database["cidade"] if c["id_cidade"] == row["id_cidade"]), None)
            result["cidade"] = {"nome": city["nome"]} if city else None
        return result

    def execute(self):
        rows = self.database[self.table_name]
        matched = [r for r in rows if all(r.get(k) == v for k, v in self.filters.items())]
        if self.operation == "insert":
            pk = "id_cidade" if self.table_name == "cidade" else "id_linha"
            row = {pk: max((r[pk] for r in rows), default=0) + 1, **self.payload}
            rows.append(row)
            return FakeResponse([self._represent(row)])
        if self.operation == "update":
            for row in matched:
                row.update(self.payload)
            return FakeResponse([self._represent(r) for r in matched])
        if self.operation == "delete":
            result = [self._represent(r) for r in matched]
            for row in matched:
                rows.remove(row)
            return FakeResponse(result)
        return FakeResponse([self._represent(r) for r in matched])


class FakeSupabase:
    def __init__(self, database):
        self.database = database

    def table(self, name):
        return FakeQuery(self.database, name)


class EntregaTests(unittest.TestCase):
    def setUp(self):
        self.database = {"cidade": [], "linha_onibus": []}
        self.client = TestClient(app)
        fake = lambda: FakeSupabase(self.database)
        for module in (cidades, linhas):
            patcher = patch.object(module, "get_supabase", fake)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_crud_completo_de_cidade(self):
        self.assertEqual(self.client.get("/cidades").json(), [])
        criado = self.client.post("/cidades", json={"nome": "Cidade de Teste DS"})
        self.assertEqual(criado.status_code, 201)
        cidade = criado.json()
        self.assertEqual(cidade["id_cidade"], 1)
        self.assertEqual(self.client.get("/cidades/1").json()["nome"], "Cidade de Teste DS")
        atualizado = self.client.put("/cidades/1", json={"nome": "Cidade Atualizada"})
        self.assertEqual(atualizado.status_code, 200)
        self.assertEqual(atualizado.json()["nome"], "Cidade Atualizada")
        self.assertEqual(self.client.get("/cidades").json()[0]["nome"], "Cidade Atualizada")
        self.assertEqual(self.client.delete("/cidades/1").status_code, 204)
        self.assertEqual(self.client.get("/cidades/1").status_code, 404)

    def test_crud_integrado_de_linha_preserva_cidade(self):
        cidade = self.client.post("/cidades", json={"nome": "Maringá"}).json()
        payload = {"id_cidade": cidade["id_cidade"], "codigo": "001", "nome": "Terminal"}
        criada = self.client.post("/linhas", json=payload)
        self.assertEqual(criada.status_code, 201, criada.text)
        linha = criada.json()
        self.assertEqual(linha["cidade"], "Maringá")
        self.assertEqual(self.client.get("/linhas").json()[0]["codigo"], "001")
        self.assertEqual(self.client.get("/linhas/1").json()["id_cidade"], cidade["id_cidade"])
        payload["nome"] = "Terminal Atualizado"
        atualizada = self.client.put("/linhas/1", json=payload)
        self.assertEqual(atualizada.status_code, 200, atualizada.text)
        self.assertEqual(atualizada.json()["nome"], "Terminal Atualizado")
        self.assertEqual(self.client.delete("/linhas/1").status_code, 204)
        self.assertEqual(self.client.get("/linhas/1").status_code, 404)
        invalida = self.client.post("/linhas", json={**payload, "id_cidade": 999})
        self.assertEqual(invalida.status_code, 404)

    def test_modelo_rejeita_nome_vazio_e_id_no_cadastro(self):
        self.assertEqual(self.client.post("/cidades", json={"nome": "  "}).status_code, 422)
        self.assertEqual(self.client.post("/cidades", json={"id_cidade": 10, "nome": "Teste"}).status_code, 422)
        self.assertEqual(self.database["cidade"], [])

    def test_quatro_totalizacoes_retorna_json_completo(self):
        for rota in ("cidade", "periodo", "transito", "clima"):
            resposta = self.client.get(f"/ia/totalizacao/{rota}")
            self.assertEqual(resposta.status_code, 200, resposta.text)
            self.assertTrue(resposta.json())
            self.assertIn("observacoes", resposta.json()[0])
            self.assertIn("atraso_total_min", resposta.json()[0])
        resumo = self.client.get("/ia/resumo")
        self.assertEqual(resumo.status_code, 200, resumo.text)
        self.assertGreater(resumo.json()["observacoes_validas"], 0)

    def test_cors_permite_origem_local_configurada(self):
        resposta = self.client.options(
            "/ia/resumo",
            headers={"Origin": "http://127.0.0.1:5500", "Access-Control-Request-Method": "GET"},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.headers["access-control-allow-origin"], "http://127.0.0.1:5500")


if __name__ == "__main__":
    unittest.main()
