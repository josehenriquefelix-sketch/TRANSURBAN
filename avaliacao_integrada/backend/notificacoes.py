"""Entrega da fila por SMTP com TLS; sem senha não afirma que enviou e-mail."""
import logging
import os
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from threading import Event, Thread
from backend.database import get_supabase

logger = logging.getLogger(__name__)


def smtp_configurado():
    return all(os.getenv(k, '').strip() for k in ('SMTP_HOST','SMTP_USER','SMTP_PASSWORD','SMTP_FROM'))


def mensagem_acesso(registro):
    papel = 'motorista' if registro['papel']=='motorista' else 'gestão'
    evento = registro['evento']
    status = {'recebido':'Pedido recebido','aprovado':'Acesso aprovado','recusado':'Pedido não aprovado','revisar':'Novo pedido para análise'}[evento]
    base = (os.getenv('APP_URL') or 'http://127.0.0.1:8000').rstrip('/')
    caminho = '/gestao/' if evento=='revisar' or registro['papel']=='gestor' else '/motorista/'
    texto = f'TRANSURBAN — {status}\n\nPerfil: {papel}.\nProtocolo: {registro["pedido_id"]}.\n'
    if evento=='recebido': texto += 'O pedido foi registrado. Aguarde a análise; este e-mail não concede acesso.\n'
    if evento=='aprovado': texto += 'A autorização foi registrada. Entre com a mesma conta confirmada.\n'
    if evento=='recusado': texto += 'Consulte a decisão no sistema ou procure a administração da equipe.\n'
    texto += f'\nAcesso local: {base+caminho}\nO endereço local funciona no computador que está executando o projeto.\nNunca envie sua senha por e-mail.'
    return f'TRANSURBAN | {status}', texto


def enviar(registro):
    if not smtp_configurado(): raise RuntimeError('SMTP não configurado')
    assunto, texto = mensagem_acesso(registro)
    mensagem = EmailMessage()
    mensagem['Subject']=assunto
    mensagem['From']=os.environ['SMTP_FROM']
    mensagem['To']=registro['destinatario']
    mensagem['Message-ID']=f'<{registro["id"]}@transurban.local>'
    mensagem.set_content(texto)
    host=os.environ['SMTP_HOST'];porta=int(os.getenv('SMTP_PORT','587'))
    contexto=ssl.create_default_context()
    if porta==465:
        conexao=smtplib.SMTP_SSL(host,porta,timeout=20,context=contexto)
    elif porta==587:
        conexao=smtplib.SMTP(host,porta,timeout=20)
    else:
        raise ValueError('Use SMTP com TLS na porta 587 ou 465.')
    with conexao as smtp:
        if porta==587: smtp.starttls(context=contexto)
        smtp.login(os.environ['SMTP_USER'],os.environ['SMTP_PASSWORD'])
        recusados=smtp.send_message(mensagem)
        if recusados: raise RuntimeError('O servidor recusou o destinatário')


def processar_um():
    if not smtp_configurado(): return False
    db=get_supabase();registro=db.rpc('tu_reservar_email',{}).execute().data
    if not registro: return False
    agora=datetime.now(timezone.utc)
    try:
        enviar(registro)
        atualizacao={'estado':'enviado','enviado_em':agora.isoformat(),'erro':None,'reserva':None,'reservado_ate':None}
    except (OSError,ValueError,RuntimeError,smtplib.SMTPException) as erro:
        # Não grava credenciais, corpo de e-mail ou resposta SMTP com dados privados.
        atualizacao={'estado':'falha' if registro['tentativas']>=5 else 'pendente',
                     'proxima_tentativa':(agora+timedelta(minutes=min(60,2**min(registro['tentativas'],6)))).isoformat(),
                     'erro':type(erro).__name__,'reserva':None,'reservado_ate':None}
    db.rpc('tu_concluir_email', {'p_pedido':registro['pedido_id'], 'p_id':registro['id'],
           'p_reserva':registro['reserva'], 'p_dados':atualizacao}).execute()
    return True


def iniciar_entrega():
    parar=Event()
    def trabalhar():
        while not parar.is_set():
            try:
                houve_envio=processar_um()
            except Exception as erro:
                logger.warning('Fila de e-mail indisponível (%s). Nova tentativa automática.',type(erro).__name__)
                houve_envio=False
            parar.wait(1 if houve_envio else 20)
    thread=Thread(target=trabalhar,name='transurban-email',daemon=True)
    thread.start()
    return parar,thread
