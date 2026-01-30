




# ============================================================================
# PESSOAS - ALUNOS, ENCARREGADOS, FUNCIONÁRIOS
# ============================================================================


class Aluno(Base):
    """Informações específicas de alunos"""
    __tablename__ = 'alunos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id', ondelete='CASCADE'), nullable=False)
    codigo_aluno = Column(String(50), unique=True, nullable=False)  # Código interno
    
    # Escola anterior
    escola_anterior_nome = Column(String(200))
    escola_anterior_provincia = Column(String(100))
    escola_anterior_ano_conclusao = Column(Integer)
    
    # Transporte
    utiliza_transporte_escolar = Column(Boolean, default=False)
    rota_transporte = Column(String(100))
    
    # Alimentação
    precisa_almoco_escola = Column(Boolean, default=False)
    restricoes_alimentares = Column(Text)
    
    # Uniforme
    tamanho_camisola = Column(String(10))  # P, M, G, GG
    tamanho_calca = Column(String(10))
    
    # Status acadêmico
    status = Column(SQLEnum(StatusAluno), default=StatusAluno.ATIVO, nullable=False)
    data_entrada = Column(Date, nullable=False)
    data_saida = Column(Date)
    motivo_saida = Column(String(500))
    
    # Dados MED
    codigo_med_aluno = Column(String(50), unique=True, comment='Código atribuído pelo MED')
    numero_processo = Column(String(50), unique=True)
    
    # Observações
    observacoes_medicas = Column(Text)
    observacoes_comportamentais = Column(Text)
    observacoes_pedagogicas = Column(Text)
    
    # Relacionamentos
    pessoa = relationship("Pessoa", foreign_keys=[pessoa_id])
    matriculas = relationship("Matricula", back_populates="aluno", cascade="all, delete-orphan")
    encarregados = relationship("EncarregadoEducacao", back_populates="aluno", cascade="all, delete-orphan")
    pagamentos = relationship("Pagamento", back_populates="aluno", cascade="all, delete-orphan")
    historico_academico = relationship("HistoricoAcademico", back_populates="aluno", cascade="all, delete-orphan")
    presencas = relationship("PresencaAula", back_populates="aluno", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_aluno_codigo', 'codigo_aluno'),
        Index('idx_aluno_status', 'status'),
        Index('idx_aluno_codigo_med', 'codigo_med_aluno'),
    )
    
    @property
    def encarregado_principal(self):
        """Retorna o encarregado de educação principal"""
        for enc in self.encarregados:
            if enc.principal:
                return enc
        return None

class Matricula(Base):
    """Matrícula do aluno em um ano letivo e turma"""
    __tablename__ = 'matriculas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id', ondelete='CASCADE'), nullable=False)
    ano_letivo_id = Column(Integer, ForeignKey('anos_letivos.id', ondelete='CASCADE'), nullable=False)
    turma_id = Column(Integer, ForeignKey('turmas.id'), nullable=False)
    
    # Dados da matrícula
    numero_matricula = Column(String(50), unique=True, nullable=False)
    data_matricula = Column(Date, nullable=False)
    data_confirmacao = Column(Date)
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False)
    transferencia = Column(Boolean, default=False)
    repetente = Column(Boolean, default=False)
    
    # Processo
    processo_matricula = Column(String(50))
    tipo_ingresso = Column(String(50), default='normal')  # normal, transferencia, recurso
    
    # Custo
    valor_matricula = Column(Numeric(10, 2), default=0)
    valor_matricula_pago = Column(Numeric(10, 2), default=0)
    desconto_matricula_percentual = Column(Numeric(5, 2), default=0)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    aluno = relationship("Aluno", back_populates="matriculas")
    ano_letivo = relationship("AnoLetivo")
    turma = relationship("Turma", back_populates="alunos")
    parcelas = relationship("ParcelaPropina", back_populates="matricula", cascade="all, delete-orphan")
    notas = relationship("Nota", back_populates="matricula", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('aluno_id', 'ano_letivo_id', name='uq_matricula_ano'),
        Index('idx_matricula_ativa', 'ativa'),
        Index('idx_matricula_numero', 'numero_matricula'),
    )
    
    @property
    def status_pagamento_matricula(self) -> str:
        """Status do pagamento da taxa de matrícula"""
        if self.valor_matricula == 0:
            return "Isento"
        elif self.valor_matricula_pago >= self.valor_matricula:
            return "Pago"
        elif self.valor_matricula_pago > 0:
            return "Parcial"
        else:
            return "Pendente"

class EncarregadoEducacao(Base):
    """Encarregados de educação dos alunos"""
    __tablename__ = 'encarregados_educacao'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id', ondelete='CASCADE'), nullable=False)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id', ondelete='CASCADE'), nullable=False)
    
    # Relacionamento
    parentesco = Column(SQLEnum(TipoParentesco), nullable=False)
    principal = Column(Boolean, default=False, nullable=False)
    responsavel_financeiro = Column(Boolean, default=False, nullable=False)
    autorizado_buscar_aluno = Column(Boolean, default=False, nullable=False)
    
    # Responsabilidades
    acompanha_estudos = Column(Boolean, default=True)
    recebe_comunicacoes = Column(Boolean, default=True)
    autorizado_emergencia = Column(Boolean, default=True)
    
    # Dados profissionais
    profissao = Column(String(150))
    local_trabalho = Column(String(200))
    cargo = Column(String(150))
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    aluno = relationship("Aluno", back_populates="encarregados")
    pessoa = relationship("Pessoa", foreign_keys=[pessoa_id])
    autorizacoes_pagamento = relationship("AutorizacaoPagamento", back_populates="encarregado", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('aluno_id', 'pessoa_id', name='uq_encarregado_aluno'),
        Index('idx_encarregado_principal', 'principal'),
    )
