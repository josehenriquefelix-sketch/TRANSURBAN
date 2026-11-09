"""Ensaio explícito em SQLite. Nunca ativado automaticamente por falha no Supabase."""
import os
import sqlite3
from pathlib import Path
from types import SimpleNamespace
from postgrest.exceptions import APIError

class DemoDB:
    def __init__(self):
        self.path = Path(os.getenv('TRANSURBAN_DEMO_DB', str(Path(__file__).parents[1] / 'data' / 'ensaio.sqlite3')))
        with self.connect() as con:
            con.executescript('''
            CREATE TABLE IF NOT EXISTS cidade(id_cidade INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT NOT NULL UNIQUE);
            CREATE TABLE IF NOT EXISTS linha_onibus(id_linha INTEGER PRIMARY KEY AUTOINCREMENT,id_cidade INTEGER NOT NULL REFERENCES cidade(id_cidade) ON DELETE RESTRICT,codigo TEXT NOT NULL,nome TEXT NOT NULL,UNIQUE(id_cidade,codigo));
            ''')
    def connect(self):
        con=sqlite3.connect(self.path);con.row_factory=sqlite3.Row;con.execute('PRAGMA foreign_keys=ON');return con
    def table(self,name):
        if name not in ('cidade','linha_onibus'): raise ValueError('Tabela inválida')
        return Query(self,name)

class Query:
    def __init__(self,db,table):
        self.db=db;self.name=table;self.op='select';self.payload={};self.filters={};self.count=None
    def select(self,columns): return self
    def order(self,column): return self
    def limit(self,count): self.count=count;return self
    def eq(self,column,value):
        if column not in ('id_cidade','id_linha','codigo','nome'):raise ValueError('Coluna inválida')
        self.filters[column]=value;return self
    def insert(self,payload):self.op='insert';self.payload=payload;return self
    def update(self,payload):self.op='update';self.payload=payload;return self
    def delete(self):self.op='delete';return self
    def execute(self):
        pk='id_cidade' if self.name=='cidade' else 'id_linha'
        where=' AND '.join(f'{k}=?' for k in self.filters) or '1=1';values=list(self.filters.values())
        try:
            with self.db.connect() as con:
                if self.op in ('insert','update'):
                    allowed={'nome'} if self.name=='cidade' else {'nome','codigo','id_cidade'}
                    if not set(self.payload)<=allowed:raise ValueError('Campo inválido')
                if self.op=='insert':
                    cols=','.join(self.payload);marks=','.join('?' for _ in self.payload)
                    cur=con.execute(f'INSERT INTO {self.name} ({cols}) VALUES ({marks})',list(self.payload.values()))
                    rows=con.execute(f'SELECT * FROM {self.name} WHERE {pk}=?',(cur.lastrowid,)).fetchall()
                else:
                    if self.op=='update':
                        sets=','.join(f'{k}=?' for k in self.payload)
                        con.execute(f'UPDATE {self.name} SET {sets} WHERE {where}',list(self.payload.values())+values)
                    rows=con.execute(f'SELECT * FROM {self.name} WHERE {where} ORDER BY {pk}',values).fetchall()
                    if self.op=='delete':con.execute(f'DELETE FROM {self.name} WHERE {where}',values)
                data=[dict(r) for r in rows]
                if self.name=='linha_onibus':
                    for r in data:
                        city=con.execute('SELECT nome FROM cidade WHERE id_cidade=?',(r['id_cidade'],)).fetchone()
                        r['cidade']=dict(city) if city else None
                return SimpleNamespace(data=data[:self.count] if self.count else data)
        except sqlite3.IntegrityError as e:
            code='23503' if 'FOREIGN KEY' in str(e) else '23505'
            raise APIError({'code':code,'message':'Violação de integridade no banco de ensaio','details':None,'hint':None}) from e
