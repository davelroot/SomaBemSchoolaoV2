# ============================================================================
# FINANCEIRO - SISTEMA COMPLETO DE PAGAMENTOS
# ============================================================================

class PlanoPagamento(Base):
    """Planos de pagamento (mensalidade, anual, etc.)"""
    __tablename__ = 'planos_pagamento'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano_letivo_id = Column(Integer, ForeignKey('anos_letivos.id', ondelete='CASCADE'), nullable=False)
    classe_id = Column(Integer, ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    
    nome = Column(String(150), nullable=False)
    descricao = Column(Text)
    
    # Tipo de plano
    tipo = Column(String(50), nullable=False)  # 'regular', 'tecnico', 'integral', 'parcial'
    
    # Valor base
    valor_total = Column(Numeric(10, 2), nullable=False)
    valor_matricula = Column(Numeric(10, 2), default=0)
    
    # Parcelamento
    numero_parcelas = Column(Integer, default=10, nullable=False)  # Geralmente 10 meses (fev-nov)
    tipo_cobranca = Column(String(50), default='mensal', nullable=False)  # mensal, trimestral, semestral, anual
    
    # Descontos automáticos
    desconto_pagamento_avista_percentual = Column(Numeric(5, 2), default=0)
    desconto_irmaos_percentual = Column(Numeric(5, 2), default=0)
    desconto_funcionarios_percentual = Column(Numeric(5, 2), default=0)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    ano_letivo = relationship("AnoLetivo")
    classe = relationship("Classe")
    parcelas_template = relationship("ParcelaTemplate", back_populates="plano_pagamento", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('ano_letivo_id', 'classe_id', 'nome', name='uq_plano_pagamento'),
        Index('idx_plano_ativo', 'ativo'),
        CheckConstraint('numero_parcelas > 0', name='ck_parcelas_positivo'),
    )

class ParcelaTemplate(Base):
    """Template para geração automática de parcelas"""
    __tablename__ = 'parcelas_template'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plano_pagamento_id = Column(Integer, ForeignKey('planos_pagamento.id', ondelete='CASCADE'), nullable=False)
    
    # Identificação
    numero_parcela = Column(Integer, nullable=False)
    nome = Column(String(100), nullable=False)  # Ex: "Fevereiro", "1ª Parcela"
    
    # Valores
    valor_parcela = Column(Numeric(10, 2), nullable=False)
    percentual_valor_total = Column(Numeric(5, 2), nullable=False)
    
    # Vencimento
    dia_vencimento = Column(Integer, nullable=False)  # Dia do mês
    mes_referencia = Column(Integer, nullable=False)  # Mês (1-12)
    
    # Serviços inclusos
    inclui_propina = Column(Boolean, default=True, nullable=False)
    inclui_alimentacao = Column(Boolean, default=False)
    inclui_transporte = Column(Boolean, default=False)
    inclui_material = Column(Boolean, default=False)
    inclui_uniforme = Column(Boolean, default=False)
    inclui_atividades = Column(Boolean, default=False)
    
    # Observações
    observacoes = Column(String(500))
    
    # Relacionamentos
    plano_pagamento = relationship("PlanoPagamento", back_populates="parcelas_template")
    
    __table_args__ = (
        UniqueConstraint('plano_pagamento_id', 'numero_parcela', name='uq_parcela_template'),
        UniqueConstraint('plano_pagamento_id', 'mes_referencia', name='uq_mes_referencia'),
        CheckConstraint('numero_parcela > 0', name='ck_num_parcela_positivo'),
        CheckConstraint('mes_referencia BETWEEN 1 AND 12', name='ck_mes_valido'),
    )

class ParcelaPropina(Base):
    """Parcelas de propina geradas para cada aluno"""
    __tablename__ = 'parcelas_propina'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    matricula_id = Column(Integer, ForeignKey('matriculas.id', ondelete='CASCADE'), nullable=False)
    parcela_template_id = Column(Integer, ForeignKey('parcelas_template.id'))
    
    # Identificação
    numero_parcela = Column(Integer, nullable=False)
    nome_parcela = Column(String(100), nullable=False)
    mes_referencia = Column(Integer, nullable=False)
    ano_referencia = Column(Integer, nullable=False)
    
    # Valores
    valor_original = Column(Numeric(10, 2), nullable=False)
    valor_com_desconto = Column(Numeric(10, 2), nullable=False)
    valor_pago = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Descontos aplicados
    desconto_percentual = Column(Numeric(5, 2), default=0)
    desconto_valor = Column(Numeric(10, 2), default=0)
    motivo_desconto = Column(String(200))
    
    # Vencimento
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date)
    
    # Juros e multas
    juros_mora = Column(Numeric(10, 2), default=0)
    multa_atraso = Column(Numeric(10, 2), default=0)
    dias_atraso = Column(Integer, default=0)
    
    # Status
    status = Column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE, nullable=False)
    pago_parcialmente = Column(Boolean, default=False)
    
    # Histórico
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    matricula = relationship("Matricula", back_populates="parcelas")
    pagamentos = relationship("Pagamento", back_populates="parcela", cascade="all, delete-orphan")
    template = relationship("ParcelaTemplate")
    
    __table_args__ = (
        Index('idx_parcela_matricula', 'matricula_id'),
        Index('idx_parcela_status', 'status'),
        Index('idx_parcela_vencimento', 'data_vencimento'),
        Index('idx_parcela_mes_ano', 'mes_referencia', 'ano_referencia'),
        CheckConstraint('valor_pago <= valor_com_desconto + juros_mora + multa_atraso', name='ck_valor_pago'),
    )
    
    @hybrid_property
    def valor_devido(self) -> Decimal:
        """Valor total devido (com juros e multas)"""
        total = self.valor_com_desconto + self.juros_mora + self.multa_atraso
        return Decimal(total)
    
    @hybrid_property
    def valor_restante(self) -> Decimal:
        """Valor ainda a pagar"""
        return self.valor_devido - Decimal(self.valor_pago)
    
    @hybrid_property
    def em_atraso(self) -> bool:
        """Verifica se a parcela está em atraso"""
        hoje = date.today()
        return self.status == StatusPagamento.PENDENTE and hoje > self.data_vencimento
    
    @hybrid_property
    def dias_para_vencer(self) -> int:
        """Dias restantes para o vencimento (negativo se vencido)"""
        hoje = date.today()
        return (self.data_vencimento - hoje).days

class Pagamento(Base):
    """Registro de pagamentos realizados"""
    __tablename__ = 'pagamentos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id', ondelete='CASCADE'), nullable=False)
    parcela_id = Column(Integer, ForeignKey('parcelas_propina.id', ondelete='CASCADE'))
    encarregado_id = Column(Integer, ForeignKey('encarregados_educacao.id'))
    
    # Identificação
    numero_recibo = Column(String(50), unique=True, nullable=False)
    referencia = Column(String(100), unique=True, nullable=False)  # Para transferências
    
    # Valor
    valor_pago = Column(Numeric(10, 2), nullable=False)
    valor_troco = Column(Numeric(10, 2), default=0)
    
    # Forma de pagamento
    forma_pagamento = Column(SQLEnum(TipoPagamento), nullable=False)
    detalhes_pagamento = Column(JSON)  # Número cheque, comprovante, etc.
    
    # Descontos aplicados no momento do pagamento
    desconto_aplicado = Column(Numeric(10, 2), default=0)
    motivo_desconto = Column(String(200))
    
    # Data e hora
    data_pagamento = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_contabilizacao = Column(Date, nullable=False)
    
    # Responsável
    funcionario_recebedor_id = Column(Integer, ForeignKey('funcionarios.id'))
    caixa_id = Column(Integer, ForeignKey('caixas.id'))
    
    # Status
    confirmado = Column(Boolean, default=True, nullable=False)
    estornado = Column(Boolean, default=False, nullable=False)
    data_estorno = Column(DateTime)
    motivo_estorno = Column(String(500))
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    aluno = relationship("Aluno", back_populates="pagamentos")
    parcela = relationship("ParcelaPropina", back_populates="pagamentos")
    encarregado = relationship("EncarregadoEducacao", back_populates="autorizacoes_pagamento")
    funcionario_recebedor = relationship("Funcionario")
    caixa = relationship("Caixa")
    
    __table_args__ = (
        Index('idx_pagamento_recibo', 'numero_recibo'),
        Index('idx_pagamento_aluno', 'aluno_id'),
        Index('idx_pagamento_data', 'data_pagamento'),
        Index('idx_pagamento_forma', 'forma_pagamento'),
        Index('idx_pagamento_confirmado', 'confirmado'),
    )

class Caixa(Base):
    """Controle de caixa (diário, mensal)"""
    __tablename__ = 'caixas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    funcionario_responsavel_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    
    # Identificação
    codigo_caixa = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(200))
    
    # Período
    data_abertura = Column(DateTime, nullable=False)
    data_fechamento = Column(DateTime)
    periodo = Column(String(20), default='diario', nullable=False)  # diario, semanal, mensal
    
    # Valores iniciais
    saldo_inicial = Column(Numeric(10, 2), nullable=False)
    saldo_final = Column(Numeric(10, 2))
    
    # Totais
    total_entradas = Column(Numeric(10, 2), default=0)
    total_saidas = Column(Numeric(10, 2), default=0)
    
    # Status
    aberto = Column(Boolean, default=True, nullable=False)
    fechado_por = Column(String(150))
    
    # Conferência
    conferido = Column(Boolean, default=False)
    data_conferencia = Column(DateTime)
    conferido_por_id = Column(Integer, ForeignKey('funcionarios.id'))
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    responsavel = relationship("Funcionario", foreign_keys=[funcionario_responsavel_id])
    conferente = relationship("Funcionario", foreign_keys=[conferido_por_id])
    movimentos = relationship("MovimentoCaixa", back_populates="caixa", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_caixa_aberto', 'aberto'),
        Index('idx_caixa_periodo', 'periodo'),
        Index('idx_caixa_data_abertura', 'data_abertura'),
    )
    
    @hybrid_property
    def saldo_atual(self) -> Decimal:
        """Saldo atual do caixa"""
        if self.saldo_final is not None:
            return Decimal(self.saldo_final)
        return Decimal(self.saldo_inicial) + Decimal(self.total_entradas) - Decimal(self.total_saidas)

class MovimentoCaixa(Base):
    """Movimentações do caixa"""
    __tablename__ = 'movimentos_caixa'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    caixa_id = Column(Integer, ForeignKey('caixas.id', ondelete='CASCADE'), nullable=False)
    
    # Tipo
    tipo = Column(String(20), nullable=False)  # entrada, saida
    categoria = Column(String(100), nullable=False)  # propina, matricula, material, despesa
    
    # Valor
    valor = Column(Numeric(10, 2), nullable=False)
    descricao = Column(String(500), nullable=False)
    
    # Origem/Destino
    pagamento_id = Column(Integer, ForeignKey('pagamentos.id'))
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'))
    
    # Data
    data_movimento = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Responsável
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    
    # Comprovante
    numero_comprovante = Column(String(50))
    arquivo_comprovante_path = Column(String(500))
    
    # Status
    confirmado = Column(Boolean, default=True, nullable=False)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    caixa = relationship("Caixa", back_populates="movimentos")
    pagamento = relationship("Pagamento")
    fornecedor = relationship("Fornecedor")
    funcionario = relationship("Funcionario")
    
    __table_args__ = (
        Index('idx_movimento_caixa', 'caixa_id'),
        Index('idx_movimento_tipo', 'tipo'),
        Index('idx_movimento_data', 'data_movimento'),
    )

class Fornecedor(Base):
    """Fornecedores da instituição"""
    __tablename__ = 'fornecedores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Identificação
    nome = Column(String(200), nullable=False)
    nome_fantasia = Column(String(200))
    nif = Column(String(20), unique=True, nullable=False)
    
    # Contatos
    email = Column(String(150))
    website = Column(String(200))
    
    # Endereço
    provincia = Column(String(100))
    municipio = Column(String(100))
    bairro = Column(String(150))
    rua = Column(String(200))
    numero = Column(String(20))
    
    # Categorias
    categorias = Column(JSON, default=list)  # ['material didatico', 'uniforme', 'alimentacao']
    
    # Contato principal
    contato_nome = Column(String(200))
    contato_telefone = Column(String(20))
    contato_email = Column(String(150))
    
    # Dados bancários (para pagamentos)
    banco_nome = Column(String(100))
    banco_agencia = Column(String(20))
    banco_conta = Column(String(50))
    iban = Column(String(50))
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    telefones = relationship("TelefoneFornecedor", back_populates="fornecedor", cascade="all, delete-orphan")
    contratos = relationship("ContratoFornecedor", back_populates="fornecedor", cascade="all, delete-orphan")
    produtos = relationship("Produto", back_populates="fornecedor", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_fornecedor_nome', 'nome'),
        Index('idx_fornecedor_nif', 'nif'),
        Index('idx_fornecedor_ativo', 'ativo'),
    )

class TelefoneFornecedor(Base):
    """Telefones dos fornecedores"""
    __tablename__ = 'telefones_fornecedores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id', ondelete='CASCADE'), nullable=False)
    tipo = Column(SQLEnum(TipoTelefone), nullable=False, default=TipoTelefone.COMERCIAL)
    numero = Column(String(20), nullable=False)
    whatsapp = Column(Boolean, default=False)
    observacoes = Column(String(200))
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="telefones")
    
    __table_args__ = (
        UniqueConstraint('fornecedor_id', 'numero', name='uq_telefone_fornecedor'),
        Index('idx_tel_forn_fornecedor', 'fornecedor_id'),
    )

class ContratoFornecedor(Base):
    """Contratos com fornecedores"""
    __tablename__ = 'contratos_fornecedores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id', ondelete='CASCADE'), nullable=False)
    
    # Identificação
    numero_contrato = Column(String(50), unique=True, nullable=False)
    objeto = Column(String(500), nullable=False)
    
    # Valores
    valor_total = Column(Numeric(12, 2), nullable=False)
    valor_mensal = Column(Numeric(10, 2))
    
    # Vigência
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    renovacao_automatica = Column(Boolean, default=False)
    
    # Pagamento
    dia_vencimento = Column(Integer, default=10)
    forma_pagamento = Column(String(50), default='transferencia')
    
    # Status
    status = Column(String(20), default='ativo', nullable=False)  # ativo, suspenso, encerrado
    data_encerramento = Column(Date)
    motivo_encerramento = Column(String(500))
    
    # Documentos
    arquivo_contrato_path = Column(String(500))
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="contratos")
    pagamentos = relationship("PagamentoFornecedor", back_populates="contrato", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_contrato_fornecedor', 'fornecedor_id'),
        Index('idx_contrato_status', 'status'),
        Index('idx_contrato_data_fim', 'data_fim'),
        CheckConstraint('data_fim > data_inicio', name='ck_contrato_datas'),
    )

class PagamentoFornecedor(Base):
    """Pagamentos a fornecedores"""
    __tablename__ = 'pagamentos_fornecedores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contrato_id = Column(Integer, ForeignKey('contratos_fornecedores.id', ondelete='CASCADE'))
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id', ondelete='CASCADE'), nullable=False)
    
    # Identificação
    referencia = Column(String(50), unique=True, nullable=False)
    descricao = Column(String(500), nullable=False)
    
    # Valor
    valor = Column(Numeric(10, 2), nullable=False)
    valor_pago = Column(Numeric(10, 2), default=0)
    
    # Vencimento
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date)
    
    # Status
    status = Column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE, nullable=False)
    
    # Forma de pagamento
    forma_pagamento = Column(SQLEnum(TipoPagamento))
    comprovante_path = Column(String(500))
    
    # Responsável
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    contrato = relationship("ContratoFornecedor", back_populates="pagamentos")
    fornecedor = relationship("Fornecedor")
    funcionario = relationship("Funcionario")
    
    __table_args__ = (
        Index('idx_pag_forn_fornecedor', 'fornecedor_id'),
        Index('idx_pag_forn_status', 'status'),
        Index('idx_pag_forn_vencimento', 'data_vencimento'),
    )

class Produto(Base):
    """Produtos para venda (uniforme, material, etc.)"""
    __tablename__ = 'produtos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'))
    
    # Identificação
    codigo = Column(String(50), unique=True, nullable=False)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)
    categoria = Column(String(100), nullable=False)  # uniforme, material, livro, etc.
    
    # Unidade
    unidade_medida = Column(String(20), default='unidade', nullable=False)
    
    # Preços
    preco_custo = Column(Numeric(10, 2), nullable=False)
    preco_venda = Column(Numeric(10, 2), nullable=False)
    margem_lucro_percentual = Column(Numeric(5, 2))
    
    # Estoque
    quantidade_estoque = Column(Integer, default=0, nullable=False)
    estoque_minimo = Column(Integer, default=10, nullable=False)
    estoque_maximo = Column(Integer, default=1000)
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    controlar_estoque = Column(Boolean, default=True, nullable=False)
    
    # Imagem
    imagem_path = Column(String(500))
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="produtos")
    itens_venda = relationship("ItemVenda", back_populates="produto", cascade="all, delete-orphan")
    movimentacoes = relationship("MovimentacaoEstoque", back_populates="produto", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_produto_codigo', 'codigo'),
        Index('idx_produto_categoria', 'categoria'),
        Index('idx_produto_ativo', 'ativo'),
        CheckConstraint('preco_venda >= preco_custo', name='ck_preco_venda'),
        CheckConstraint('quantidade_estoque >= 0', name='ck_estoque_positivo'),
    )
    
    @property
    def necessita_reposicao(self) -> bool:
        """Verifica se precisa repor estoque"""
        return self.quantidade_estoque <= self.estoque_minimo

class MovimentacaoEstoque(Base):
    """Movimentações de estoque"""
    __tablename__ = 'movimentacoes_estoque'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    produto_id = Column(Integer, ForeignKey('produtos.id', ondelete='CASCADE'), nullable=False)
    
    # Tipo
    tipo = Column(String(20), nullable=False)  # entrada, saida, ajuste, perda
    motivo = Column(String(200), nullable=False)
    
    # Quantidade
    quantidade = Column(Integer, nullable=False)
    quantidade_anterior = Column(Integer, nullable=False)
    quantidade_atual = Column(Integer, nullable=False)
    
    # Valores
    valor_unitario = Column(Numeric(10, 2))
    valor_total = Column(Numeric(12, 2))
    
    # Origem/Destino
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'))
    venda_id = Column(Integer, ForeignKey('vendas.id'))
    
    # Responsável
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    
    # Data
    data_movimentacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    produto = relationship("Produto", back_populates="movimentacoes")
    fornecedor = relationship("Fornecedor")
    venda = relationship("Venda")
    funcionario = relationship("Funcionario")
    
    __table_args__ = (
        Index('idx_mov_estoque_produto', 'produto_id'),
        Index('idx_mov_estoque_tipo', 'tipo'),
        Index('idx_mov_estoque_data', 'data_movimentacao'),
        CheckConstraint('quantidade != 0', name='ck_quantidade_nao_zero'),
    )

class Venda(Base):
    """Vendas de produtos (uniforme, material, etc.)"""
    __tablename__ = 'vendas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id'))
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    
    # Identificação
    numero_venda = Column(String(50), unique=True, nullable=False)
    
    # Valores
    valor_total = Column(Numeric(10, 2), nullable=False)
    desconto = Column(Numeric(10, 2), default=0)
    valor_final = Column(Numeric(10, 2), nullable=False)
    valor_pago = Column(Numeric(10, 2), default=0)
    
    # Forma de pagamento
    forma_pagamento = Column(SQLEnum(TipoPagamento))
    
    # Status
    status = Column(String(20), default='pendente', nullable=False)  # pendente, paga, cancelada
    pago_parcialmente = Column(Boolean, default=False)
    
    # Data
    data_venda = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_pagamento = Column(DateTime)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    aluno = relationship("Aluno")
    funcionario = relationship("Funcionario")
    itens = relationship("ItemVenda", back_populates="venda", cascade="all, delete-orphan")
    pagamentos_venda = relationship("PagamentoVenda", back_populates="venda", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_venda_numero', 'numero_venda'),
        Index('idx_venda_aluno', 'aluno_id'),
        Index('idx_venda_data', 'data_venda'),
        Index('idx_venda_status', 'status'),
    )

class ItemVenda(Base):
    """Itens de uma venda"""
    __tablename__ = 'itens_venda'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    venda_id = Column(Integer, ForeignKey('vendas.id', ondelete='CASCADE'), nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.id', ondelete='CASCADE'), nullable=False)
    
    # Quantidade e valores
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Numeric(10, 2), nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    
    # Desconto
    desconto_percentual = Column(Numeric(5, 2), default=0)
    desconto_valor = Column(Numeric(10, 2), default=0)
    
    # Observações
    observacoes = Column(String(200))
    
    # Relacionamentos
    venda = relationship("Venda", back_populates="itens")
    produto = relationship("Produto", back_populates="itens_venda")
    
    __table_args__ = (
        UniqueConstraint('venda_id', 'produto_id', name='uq_item_venda'),
        CheckConstraint('quantidade > 0', name='ck_quantidade_positiva'),
        CheckConstraint('valor_total = quantidade * valor_unitario - desconto_valor', name='ck_valor_total'),
    )

class PagamentoVenda(Base):
    """Pagamentos de vendas (parcelado)"""
    __tablename__ = 'pagamentos_venda'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    venda_id = Column(Integer, ForeignKey('vendas.id', ondelete='CASCADE'), nullable=False)
    
    # Identificação
    numero_parcela = Column(Integer, nullable=False)
    
    # Valores
    valor_parcela = Column(Numeric(10, 2), nullable=False)
    valor_pago = Column(Numeric(10, 2), default=0)
    
    # Vencimento
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date)
    
    # Status
    status = Column(SQLEnum(StatusPagamento), default=StatusPagamento.PENDENTE, nullable=False)
    
    # Forma de pagamento
    forma_pagamento = Column(SQLEnum(TipoPagamento))
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    venda = relationship("Venda", back_populates="pagamentos_venda")
    
    __table_args__ = (
        Index('idx_pag_venda_venda', 'venda_id'),
        Index('idx_pag_venda_status', 'status'),
        CheckConstraint('valor_pago <= valor_parcela', name='ck_valor_pago_venda'),
    )
