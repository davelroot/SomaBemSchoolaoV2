"""
Sistema de Gestão Escolar - Banco de Dados Relacional Completo
Autor: Sistema SomaBemSchool
Versão: 2.0.0
Data: 2026
Descrição: Modelo relacional completo para gestão de colégio público-privado em Angola
"""

from datetime import datetime, date, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, 
    Date, DateTime, Time, Text, Enum as SQLEnum, DECIMAL,
    ForeignKey, Table, MetaData, Index, UniqueConstraint,
    CheckConstraint, BigInteger, Numeric, JSON, LargeBinary,
    event, DDL, func, text, Sequence
)
from sqlalchemy.orm import (
    declarative_base, relationship, sessionmaker, 
    backref, validates, Session
)
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.mutable import MutableDict, MutableList
import hashlib
import uuid


# ============================================================================
# CURSOS TÉCNICOS ESPECÍFICOS
# ============================================================================

class CursoTecnico(Base):
    """Cursos técnicos oferecidos"""
    __tablename__ = 'cursos_tecnicos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identificação
    codigo_med = Column(String(50), unique=True, comment='Código do MED')
    nome = Column(String(200), nullable=False)
    nome_curto = Column(String(50))
    
    # Características
    nivel = Column(SQLEnum(NivelCursoTecnico), nullable=False)
    duracao_meses = Column(Integer, nullable=False)
    carga_horaria_total = Column(Integer, nullable=False)  # horas
    
    # Requisitos
    escolaridade_minima = Column(String(50), nullable=False)  # '9_classe', '12_classe'
    idade_minima = Column(Integer, default=16)
    vagas_ano = Column(Integer, default=30)
    
    # Área
    area_tecnologica = Column(String(100), nullable=False)  # 'informatica', 'construcao_civil', etc.
    setor_economico = Column(String(100))
    
    # Certificação
    certificacao = Column(String(200))
    reconhecimento_med = Column(Boolean, default=True, nullable=False)
    reconhecimento_minintt = Column(Boolean, default=True, nullable=False)
    
    # Descrição
    objetivo = Column(Text)
    perfil_egresso = Column(Text)
    mercado_trabalho = Column(Text)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    modulos = relationship("ModuloTecnico", back_populates="curso", cascade="all, delete-orphan")
    turmas_tecnicas = relationship("TurmaTecnica", back_populates="curso", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_curso_tecnico_nivel', 'nivel'),
        Index('idx_curso_tecnico_area', 'area_tecnologica'),
        Index('idx_curso_tecnico_ativo', 'ativo'),
    )

class ModuloTecnico(Base):
    """Módulos dos cursos técnicos"""
    __tablename__ = 'modulos_tecnicos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    curso_id = Column(Integer, ForeignKey('cursos_tecnicos.id', ondelete='CASCADE'), nullable=False)
    
    # Identificação
    codigo = Column(String(20), nullable=False)
    nome = Column(String(200), nullable=False)
    ordem = Column(Integer, nullable=False)
    
    # Características
    carga_horaria = Column(Integer, nullable=False)  # horas
    tipo = Column(String(50), default='teorico')  # teorico, pratico, estagio
    prerequisitos = Column(JSON, default=list)  # Lista de códigos de módulos pré-requisitos
    
    # Conteúdo
    ementa = Column(Text)
    competencias = Column(Text)
    recursos_necessarios = Column(Text)
    
    # Avaliação
    peso_avaliacao = Column(Numeric(5, 2), default=1.0)
    nota_minima_aprovacao = Column(Numeric(5, 2), default=10.0)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    curso = relationship("CursoTecnico", back_populates="modulos")
    
    __table_args__ = (
        UniqueConstraint('curso_id', 'codigo', name='uq_modulo_codigo'),
        UniqueConstraint('curso_id', 'ordem', name='uq_modulo_ordem'),
        Index('idx_modulo_curso', 'curso_id'),
    )

class TurmaTecnica(Base):
    """Turmas específicas de cursos técnicos"""
    __tablename__ = 'turmas_tecnicas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    curso_id = Column(Integer, ForeignKey('cursos_tecnicos.id', ondelete='CASCADE'), nullable=False)
    turma_base_id = Column(Integer, ForeignKey('turmas.id', ondelete='CASCADE'), nullable=False)
    
    # Identificação
    codigo = Column(String(20), nullable=False)
    nome = Column(String(100), nullable=False)
    
    # Período
    data_inicio = Column(Date, nullable=False)
    data_termino_previsto = Column(Date, nullable=False)
    data_termino_real = Column(Date)
    
    # Horário
    turno = Column(SQLEnum(Turno), nullable=False)
    horario_especifico = Column(String(200))
    
    # Laboratório/Workshop
    laboratorio_id = Column(Integer, ForeignKey('salas.id'))
    
    # Coordenação
    coordenador_id = Column(Integer, ForeignKey('professores.id'))
    tutor_id = Column(Integer, ForeignKey('professores.id'))
    
    # Status
    status = Column(String(20), default='em_andamento', nullable=False)  # planejada, em_andamento, concluida, suspensa
    vagas_total = Column(Integer, nullable=False)
    vagas_preenchidas = Column(Integer, default=0)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    curso = relationship("CursoTecnico", back_populates="turmas_tecnicas")
    turma_base = relationship("Turma")
    laboratorio = relationship("Sala")
    coordenador = relationship("Professor", foreign_keys=[coordenador_id])
    tutor = relationship("Professor", foreign_keys=[tutor_id])
    
    __table_args__ = (
        UniqueConstraint('curso_id', 'codigo', name='uq_turma_tecnica_codigo'),
        Index('idx_turma_tecnica_curso', 'curso_id'),
        Index('idx_turma_tecnica_status', 'status'),
        CheckConstraint('data_termino_previsto > data_inicio', name='ck_turma_tecnica_datas'),
    )

# ============================================================================
# HISTÓRICO E DOCUMENTOS
# ============================================================================

class HistoricoAcademico(Base):
    """Histórico acadêmico completo do aluno"""
    __tablename__ = 'historico_academico'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id', ondelete='CASCADE'), nullable=False)
    
    # Ano letivo
    ano_letivo_id = Column(Integer, ForeignKey('anos_letivos.id', ondelete='CASCADE'), nullable=False)
    
    # Turma e classe
    turma_id = Column(Integer, ForeignKey('turmas.id'), nullable=False)
    classe_nome = Column(String(100), nullable=False)
    
    # Resultado
    resultado = Column(SQLEnum(ResultadoAvaliacao), nullable=False)
    media_final = Column(Numeric(5, 2))
    faltas_totais = Column(Integer, default=0)
    faltas_justificadas = Column(Integer, default=0)
    frequencia_percentual = Column(Numeric(5, 2))
    
    # Disciplinas
    disciplinas_aprovadas = Column(Integer, default=0)
    disciplinas_reprovadas = Column(Integer, default=0)
    disciplinas_em_recuperacao = Column(Integer, default=0)
    
    # Posição
    posicao_turma = Column(Integer)
    total_alunos_turma = Column(Integer)
    
    # Menções
    mencoes_honrosas = Column(JSON, default=list)
    observacoes = Column(Text)
    
    # Documentação
    boletim_path = Column(String(500))
    historico_path = Column(String(500))
    
    # Datas
    data_conclusao = Column(Date)
    data_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    aluno = relationship("Aluno", back_populates="historico_academico")
    ano_letivo = relationship("AnoLetivo")
    turma = relationship("Turma")
    
    __table_args__ = (
        UniqueConstraint('aluno_id', 'ano_letivo_id', name='uq_historico_ano'),
        Index('idx_historico_aluno', 'aluno_id'),
        Index('idx_historico_resultado', 'resultado'),
        CheckConstraint('media_final IS NULL OR media_final BETWEEN 0 AND 20', name='ck_historico_media'),
    )

class DocumentoAluno(Base):
    """Documentos dos alunos"""
    __tablename__ = 'documentos_aluno'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id', ondelete='CASCADE'), nullable=False)
    
    # Identificação
    tipo = Column(String(50), nullable=False)  # 'certificado', 'historico', 'declaracao', 'atestado'
    descricao = Column(String(200), nullable=False)
    
    # Documento
    numero_documento = Column(String(50))
    data_emissao = Column(Date, nullable=False)
    data_validade = Column(Date)
    
    # Arquivo
    arquivo_path = Column(String(500), nullable=False)
    arquivo_hash = Column(String(64), nullable=False)  # SHA256 para integridade
    
    # Emissão
    emitido_por_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    autorizado_por_id = Column(Integer, ForeignKey('funcionarios.id'))
    
    # Status
    valido = Column(Boolean, default=True, nullable=False)
    motivo_invalidacao = Column(String(500))
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    aluno = relationship("Aluno")
    emitido_por = relationship("Funcionario", foreign_keys=[emitido_por_id])
    autorizado_por = relationship("Funcionario", foreign_keys=[autorizado_por_id])
    
    __table_args__ = (
        Index('idx_doc_aluno_tipo', 'tipo'),
        Index('idx_doc_aluno_valido', 'valido'),
        Index('idx_doc_aluno_emissao', 'data_emissao'),
        UniqueConstraint('numero_documento', 'tipo', name='uq_documento_numero'),
    )

class CalendarioEscolar(Base):
    """Calendário escolar da instituição"""
    __tablename__ = 'calendario_escolar'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano_letivo_id = Column(Integer, ForeignKey('anos_letivos.id', ondelete='CASCADE'), nullable=False)
    
    # Evento
    tipo = Column(String(50), nullable=False)  # 'aula', 'feriado', 'recesso', 'avaliacao', 'evento'
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text)
    
    # Período
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date)
    dia_inteiro = Column(Boolean, default=True, nullable=False)
    hora_inicio = Column(Time)
    hora_fim = Column(Time)
    
    # Aplicação
    aplicavel_todas_turmas = Column(Boolean, default=True, nullable=False)
    turma_id = Column(Integer, ForeignKey('turmas.id'))
    classe_id = Column(Integer, ForeignKey('classes.id'))
    
    # Repetição
    recorrente = Column(Boolean, default=False)
    recorrencia_tipo = Column(String(20))  # 'diaria', 'semanal', 'mensal', 'anual'
    recorrencia_fim = Column(Date)
    
    # Status
    confirmado = Column(Boolean, default=True, nullable=False)
    cancelado = Column(Boolean, default=False)
    motivo_cancelamento = Column(String(500))
    
    # Organização
    cor_evento = Column(String(7), default='#1E88E5')
    local = Column(String(200))
    
    # Responsável
    responsavel_id = Column(Integer, ForeignKey('funcionarios.id'))
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    ano_letivo = relationship("AnoLetivo", back_populates="calendarios")
    turma = relationship("Turma")
    classe = relationship("Classe")
    responsavel = relationship("Funcionario")
    
    __table_args__ = (
        Index('idx_calendario_ano', 'ano_letivo_id'),
        Index('idx_calendario_tipo', 'tipo'),
        Index('idx_calendario_data', 'data_inicio'),
        CheckConstraint('data_fim IS NULL OR data_fim >= data_inicio', name='ck_calendario_datas'),
    )

# ============================================================================
# SISTEMA - USUÁRIOS, ACESSOS, LOGS
# ============================================================================

class Usuario(Base):
    """Usuários do sistema"""
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id', ondelete='CASCADE'), nullable=False)
    
    # Credenciais
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)
    
    # Nível de acesso
    nivel_acesso = Column(SQLEnum(NivelAcesso), nullable=False)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    data_ativacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_desativacao = Column(DateTime)
    motivo_desativacao = Column(String(500))
    
    # Segurança
    data_ultimo_login = Column(DateTime)
    data_ultima_troca_senha = Column(DateTime, default=datetime.utcnow, nullable=False)
    trocar_senha_proximo_login = Column(Boolean, default=True, nullable=False)
    
    # Tentativas de login
    tentativas_login_falhas = Column(Integer, default=0)
    data_bloqueio = Column(DateTime)
    
    # Token recuperação
    token_recuperacao = Column(String(100))
    token_recuperacao_expira = Column(DateTime)
    
    # Preferências
    tema = Column(String(50), default='claro')
    idioma = Column(String(10), default='pt')
    notificacoes_email = Column(Boolean, default=True)
    notificacoes_push = Column(Boolean, default=True)
    
    # Relacionamentos
    pessoa = relationship("Pessoa")
    logs = relationship("LogSistema", back_populates="usuario", cascade="all, delete-orphan")
    permissoes = relationship("PermissaoUsuario", back_populates="usuario", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_usuario_username', 'username'),
        Index('idx_usuario_email', 'email'),
        Index('idx_usuario_ativo', 'ativo'),
        Index('idx_usuario_nivel', 'nivel_acesso'),
    )
    
    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha está correta"""
        import hashlib
        senha_hash = hashlib.sha256((senha + self.salt).encode()).hexdigest()
        return senha_hash == self.senha_hash
    
    def atualizar_senha(self, nova_senha: str):
        """Atualiza a senha do usuário"""
        import hashlib
        import secrets
        self.salt = secrets.token_hex(16)
        self.senha_hash = hashlib.sha256((nova_senha + self.salt).encode()).hexdigest()
        self.data_ultima_troca_senha = datetime.utcnow()
        self.tentativas_login_falhas = 0
        self.data_bloqueio = None

class PermissaoUsuario(Base):
    """Permissões específicas por usuário"""
    __tablename__ = 'permissoes_usuario'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    
    # Módulo
    modulo = Column(String(50), nullable=False)  # 'financeiro', 'academico', 'rh', etc.
    
    # Permissões CRUD
    criar = Column(Boolean, default=False, nullable=False)
    ler = Column(Boolean, default=True, nullable=False)
    atualizar = Column(Boolean, default=False, nullable=False)
    deletar = Column(Boolean, default=False, nullable=False)
    
    # Permissões específicas
    exportar = Column(Boolean, default=False)
    aprovar = Column(Boolean, default=False)
    relatorios = Column(Boolean, default=False)
    
    # Restrições
    restricao_turmas = Column(JSON, default=list)  # IDs de turmas permitidas
    restricao_disciplinas = Column(JSON, default=list)  # IDs de disciplinas permitidas
    
    # Validade
    data_inicio = Column(Date, default=date.today, nullable=False)
    data_fim = Column(Date)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="permissoes")
    
    __table_args__ = (
        UniqueConstraint('usuario_id', 'modulo', name='uq_permissao_modulo'),
        Index('idx_permissao_usuario', 'usuario_id'),
        Index('idx_permissao_modulo', 'modulo'),
        CheckConstraint('data_fim IS NULL OR data_fim >= data_inicio', name='ck_permissao_datas'),
    )

class LogSistema(Base):
    """Logs do sistema para auditoria"""
    __tablename__ = 'logs_sistema'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    
    # Ação
    acao = Column(String(50), nullable=False)  # 'login', 'logout', 'create', 'update', 'delete'
    modulo = Column(String(50), nullable=False)
    descricao = Column(Text, nullable=False)
    
    # Dados
    dados_anteriores = Column(JSON)
    dados_novos = Column(JSON)
    registro_id = Column(Integer)  # ID do registro afetado
    tabela = Column(String(50))    # Nome da tabela afetada
    
    # Localização
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Data
    data_log = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="logs")
    
    __table_args__ = (
        Index('idx_log_usuario', 'usuario_id'),
        Index('idx_log_acao', 'acao'),
        Index('idx_log_modulo', 'modulo'),
        Index('idx_log_data', 'data_log'),
    )

# ============================================================================
# VIEWS E FUNÇÕES AUXILIARES
# ============================================================================

# Views Materializadas (exemplos)
class ViewAlunosAtivos(Base):
    """View de alunos ativos com informações completas"""
    __tablename__ = 'view_alunos_ativos'
    
    aluno_id = Column(Integer, primary_key=True)
    codigo_aluno = Column(String(50))
    nome_completo = Column(String(200))
    data_nascimento = Column(Date)
    idade = Column(Integer)
    genero = Column(String(20))
    turma_atual = Column(String(100))
    classe_atual = Column(String(100))
    turno = Column(String(20))
    encarregado_principal = Column(String(200))
    telefone_encarregado = Column(String(20))
    status_pagamento = Column(String(50))
    meses_atraso = Column(Integer)
    valor_devido = Column(Numeric(10, 2))
    
    __table_args__ = (
        {'info': {'is_view': True}},
    )

class ViewFinanceiroMensal(Base):
    """View de resumo financeiro mensal"""
    __tablename__ = 'view_financeiro_mensal'
    
    id = Column(Integer, primary_key=True)
    ano = Column(Integer)
    mes = Column(Integer)
    mes_nome = Column(String(20))
    total_previsto = Column(Numeric(12, 2))
    total_recebido = Column(Numeric(12, 2))
    total_pendente = Column(Numeric(12, 2))
    inadimplencia_percentual = Column(Numeric(5, 2))
    total_descontos = Column(Numeric(12, 2))
    total_juros = Column(Numeric(12, 2))
    alunos_ativos = Column(Integer)
    alunos_inadimplentes = Column(Integer)
    
    __table_args__ = (
        {'info': {'is_view': True}},
    )
    