# ============================================================================
# TABELAS PRINCIPAIS - INSTITUIÇÃO
# ============================================================================

class Instituicao(Base):
    """Tabela principal da instituição"""
    __tablename__ = 'instituicoes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_med = Column(String(50), unique=True, nullable=False, comment='Código atribuído pelo MED')
    nome_oficial = Column(String(200), nullable=False)
    nome_comercial = Column(String(200))
    tipo = Column(SQLEnum(TipoInstituicao), nullable=False, default=TipoInstituicao.PUBLICO_PRIVADA)
    nif = Column(String(20), unique=True, nullable=False)
    alvara_numero = Column(String(50), unique=True)
    data_autorizacao = Column(Date, nullable=False)
    data_fundacao = Column(Date)
    
    # Contatos
    email_principal = Column(String(150), nullable=False)
    email_secundario = Column(String(150))
    website = Column(String(200))
    
    # Endereço
    provincia = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    bairro = Column(String(150), nullable=False)
    rua = Column(String(200))
    numero = Column(String(20))
    complemento = Column(String(100))
    
    # Configurações
    moeda = Column(String(10), default='Kz', nullable=False)
    idioma_principal = Column(String(20), default='pt', nullable=False)
    idiomas_secundarios = Column(JSON, default=list)
    fuso_horario = Column(String(50), default='Africa/Luanda')
    
    # Logos e assinaturas
    logo_path = Column(String(500))
    carimbo_path = Column(String(500))
    assinatura_diretor_path = Column(String(500))
    
    # Configurações acadêmicas
    inicio_ano_letivo = Column(Date, nullable=False)
    fim_ano_letivo = Column(Date, nullable=False)
    dias_letivos_ano = Column(Integer, default=180, nullable=False)
    carga_horaria_diaria = Column(Integer, default=5, nullable=False)  # horas
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    campi = relationship("Campus", back_populates="instituicao", cascade="all, delete-orphan")
    telefones = relationship("TelefoneInstituicao", back_populates="instituicao", cascade="all, delete-orphan")
    licencas = relationship("LicencaSoftware", back_populates="instituicao", cascade="all, delete-orphan")
    configuracoes = relationship("ConfiguracaoSistema", back_populates="instituicao", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_instituicao_provincia', 'provincia'),
        Index('idx_instituicao_tipo', 'tipo'),
        Index('idx_instituicao_ativa', 'ativa'),
        UniqueConstraint('codigo_med', name='uq_codigo_med'),
        UniqueConstraint('nif', name='uq_nif_instituicao'),
    )
    
    @property
    def endereco_completo(self) -> str:
        """Retorna o endereço completo formatado"""
        partes = []
        if self.rua:
            partes.append(f"{self.rua}")
        if self.numero:
            partes.append(f"Nº {self.numero}")
        if self.bairro:
            partes.append(f"{self.bairro}")
        if self.municipio:
            partes.append(f"{self.municipio}")
        if self.provincia:
            partes.append(f"{self.provincia}")
        if self.complemento:
            partes.append(f"({self.complemento})")
        return ", ".join(partes)

class Campus(Base):
    """Campi ou polos da instituição"""
    __tablename__ = 'campi'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instituicao_id = Column(Integer, ForeignKey('instituicoes.id', ondelete='CASCADE'), nullable=False)
    codigo = Column(String(20), nullable=False)
    nome = Column(String(150), nullable=False)
    
    # Endereço específico do campus
    provincia = Column(String(100))
    municipio = Column(String(100))
    bairro = Column(String(150))
    rua = Column(String(200))
    numero = Column(String(20))
    
    # Contatos
    telefone_principal = Column(String(20))
    email = Column(String(150))
    
    # Características
    area_total = Column(Float, comment='Área total em m²')
    capacidade_alunos = Column(Integer, default=1000)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Responsável
    diretor_campus = Column(String(150))
    
    # Datas
    data_inauguracao = Column(Date)
    data_cadastro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    instituicao = relationship("Instituicao", back_populates="campi")
    blocos = relationship("Bloco", back_populates="campus", cascade="all, delete-orphan")
    salas = relationship("Sala", back_populates="campus", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('instituicao_id', 'codigo', name='uq_campus_codigo'),
        Index('idx_campus_instituicao', 'instituicao_id'),
    )

class TelefoneInstituicao(Base):
    """Telefones da instituição"""
    __tablename__ = 'telefones_instituicao'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instituicao_id = Column(Integer, ForeignKey('instituicoes.id', ondelete='CASCADE'), nullable=False)
    tipo = Column(SQLEnum(TipoTelefone), nullable=False, default=TipoTelefone.COMERCIAL)
    numero = Column(String(20), nullable=False)
    whatsapp = Column(Boolean, default=False)
    observacoes = Column(String(200))
    
    # Relacionamentos
    instituicao = relationship("Instituicao", back_populates="telefones")
    
    __table_args__ = (
        UniqueConstraint('instituicao_id', 'numero', name='uq_telefone_instituicao'),
        Index('idx_telefone_tipo', 'tipo'),
    )

# ============================================================================
# LICENÇAS E CONFIGURAÇÕES
# ============================================================================

class LicencaSoftware(Base):
    """Licenças de software da instituição"""
    __tablename__ = 'licencas_software'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instituicao_id = Column(Integer, ForeignKey('instituicoes.id', ondelete='CASCADE'), nullable=False)
    codigo_licenca = Column(String(100), unique=True, nullable=False)
    produto = Column(String(150), nullable=False)
    versao = Column(String(50), nullable=False)
    
    # Validade
    data_ativacao = Column(Date, nullable=False)
    data_expiracao = Column(Date, nullable=False)
    
    # Limites
    max_usuarios = Column(Integer, default=100)
    max_alunos = Column(Integer, default=5000)
    max_funcionarios = Column(Integer, default=200)
    
    # Módulos ativos (JSON com lista de módulos)
    modulos_ativos = Column(JSON, default=list, nullable=False)
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False)
    motivo_inativacao = Column(String(500))
    
    # Controle
    chave_ativacao = Column(String(500), nullable=False)
    data_renovacao = Column(Date)
    renovacao_automatica = Column(Boolean, default=True)
    
    # Relacionamentos
    instituicao = relationship("Instituicao", back_populates="licencas")
    
    __table_args__ = (
        Index('idx_licenca_expiracao', 'data_expiracao'),
        Index('idx_licenca_ativa', 'ativa'),
        CheckConstraint('data_expiracao > data_ativacao', name='ck_data_licenca'),
    )
    
    @property
    def dias_restantes(self) -> int:
        """Retorna dias restantes para expiração"""
        if not self.ativa:
            return 0
        hoje = date.today()
        if hoje > self.data_expiracao:
            return 0
        return (self.data_expiracao - hoje).days
    
    @property
    def status_detalhado(self) -> str:
        """Status detalhado da licença"""
        if not self.ativa:
            return "Inativa"
        dias = self.dias_restantes
        if dias <= 0:
            return "Expirada"
        elif dias <= 7:
            return f"Expira em {dias} dias"
        elif dias <= 30:
            return f"Expira em {dias} dias"
        else:
            return "Ativa"

class ConfiguracaoSistema(Base):
    """Configurações do sistema por instituição"""
    __tablename__ = 'configuracoes_sistema'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instituicao_id = Column(Integer, ForeignKey('instituicoes.id', ondelete='CASCADE'), nullable=False)
    
    # Configurações acadêmicas
    nota_minima_aprovacao = Column(Numeric(4, 2), default=10.0, nullable=False)
    nota_maxima = Column(Numeric(4, 2), default=20.0, nullable=False)
    percentual_frequencia_minima = Column(Numeric(5, 2), default=75.0, nullable=False)
    max_faltas_injustificadas = Column(Integer, default=10)
    
    # Trimestres
    trimestre1_inicio = Column(Date)
    trimestre1_fim = Column(Date)
    trimestre2_inicio = Column(Date)
    trimestre2_fim = Column(Date)
    trimestre3_inicio = Column(Date)
    trimestre3_fim = Column(Date)
    
    # Pagamentos
    dia_vencimento_propina = Column(Integer, default=10, nullable=False)
    tolerancia_pagamento_dias = Column(Integer, default=5, nullable=False)
    juros_mora_diarios = Column(Numeric(5, 2), default=0.1, nullable=False)
    multa_atraso_percentual = Column(Numeric(5, 2), default=2.0, nullable=False)
    
    # Descontos
    desconto_irmaos_percentual = Column(Numeric(5, 2), default=10.0)
    desconto_pontualidade_percentual = Column(Numeric(5, 2), default=5.0)
    desconto_funcionarios_percentual = Column(Numeric(5, 2), default=20.0)
    
    # Notificações
    notificar_atraso_dias_antes = Column(Integer, default=3)
    notificar_faltas_minimas = Column(Integer, default=3)
    
    # Segurança
    tempo_sessao_minutos = Column(Integer, default=60)
    tentativas_login_max = Column(Integer, default=5)
    bloqueio_login_minutos = Column(Integer, default=30)
    
    # Backup
    intervalo_backup_horas = Column(Integer, default=24)
    manter_backups_dias = Column(Integer, default=30)
    
    # Personalização
    tema_cor_principal = Column(String(7), default='#1E88E5')
    logo_login_path = Column(String(500))
    mensagem_boas_vindas = Column(String(500))
    
    # Datas
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    instituicao = relationship("Instituicao", back_populates="configuracoes")
    
    __table_args__ = (
        UniqueConstraint('instituicao_id', name='uq_config_instituicao'),
        CheckConstraint('nota_minima_aprovacao <= nota_maxima', name='ck_nota_min_max'),
        CheckConstraint('percentual_frequencia_minima BETWEEN 0 AND 100', name='ck_frequencia_min'),
    )
