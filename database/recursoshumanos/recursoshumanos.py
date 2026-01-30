
class Funcionario(Base):
    """Funcionários administrativos e de apoio"""
    __tablename__ = 'funcionarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id', ondelete='CASCADE'), nullable=False)
    codigo_funcionario = Column(String(50), unique=True, nullable=False)
    
    # Dados profissionais
    cargo = Column(String(150), nullable=False)
    departamento = Column(String(100), nullable=False)
    setor = Column(String(100))
    
    # Contrato
    tipo_contrato = Column(SQLEnum(TipoContrato), nullable=False)
    data_admissao = Column(Date, nullable=False)
    data_demissao = Column(Date)
    motivo_demissao = Column(String(500))
    
    # Carga horária
    carga_horaria_semanal = Column(Integer, default=40, nullable=False)
    horario_entrada = Column(Time, default=time(8, 0))
    horario_saida = Column(Time, default=time(17, 0))
    
    # Remuneração
    salario_base = Column(Numeric(10, 2), nullable=False)
    beneficios = Column(JSON, default=dict)
    
    # Status
    status = Column(SQLEnum(StatusFuncionario), default=StatusFuncionario.ATIVO, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Acesso
    nivel_acesso = Column(SQLEnum(NivelAcesso), default=NivelAcesso.FUNCIONARIO, nullable=False)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    pessoa = relationship("Pessoa", foreign_keys=[pessoa_id])
    frequencias = relationship("FrequenciaFuncionario", back_populates="funcionario", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_funcionario_codigo', 'codigo_funcionario'),
        Index('idx_funcionario_cargo', 'cargo'),
        Index('idx_funcionario_status', 'status'),
    )




class Professor(Base):
    """Informações específicas de professores"""
    __tablename__ = 'professores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id', ondelete='CASCADE'), nullable=False)
    codigo_professor = Column(String(50), unique=True, nullable=False)
    
    # Dados profissionais
    formacao_academica = Column(String(200), nullable=False)
    area_formacao = Column(String(150))
    instituicao_formacao = Column(String(200))
    ano_conclusao_formacao = Column(Integer)
    
    # Registro
    numero_registro_profissional = Column(String(50), unique=True)
    orgao_registro = Column(String(100))
    data_registro = Column(Date)
    
    # Contrato
    tipo_contrato = Column(SQLEnum(TipoContrato), nullable=False)
    data_admissao = Column(Date, nullable=False)
    data_demissao = Column(Date)
    motivo_demissao = Column(String(500))
    
    # Carga horária
    carga_horaria_semanal = Column(Integer, default=40, nullable=False)  # horas
    carga_horaria_adicional = Column(Integer, default=0)
    
    # Remuneração
    salario_base = Column(Numeric(10, 2), nullable=False)
    salario_hora_aula = Column(Numeric(10, 2))
    beneficios = Column(JSON, default=dict)
    
    # Status
    status = Column(SQLEnum(StatusFuncionario), default=StatusFuncionario.ATIVO, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Áreas de atuação
    areas_especializacao = Column(JSON, default=list)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    pessoa = relationship("Pessoa", foreign_keys=[pessoa_id])
    disciplinas = relationship("ProfessorDisciplina", back_populates="professor", cascade="all, delete-orphan")
    turmas_coordenadas = relationship("Turma", foreign_keys="Turma.professor_coordenador_id", back_populates="professor_coordenador")
    horarios = relationship("HorarioAula", foreign_keys="HorarioAula.professor_id", back_populates="professor")
    avaliacoes = relationship("Avaliacao", back_populates="professor", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_professor_codigo', 'codigo_professor'),
        Index('idx_professor_status', 'status'),
        Index('idx_professor_contrato', 'tipo_contrato'),
    )


class TelefonePessoa(Base):
    """Telefones das pessoas"""
    __tablename__ = 'telefones_pessoas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pessoa_id = Column(Integer, ForeignKey('pessoas.id', ondelete='CASCADE'), nullable=False)
    tipo = Column(SQLEnum(TipoTelefone), nullable=False, default=TipoTelefone.CELULAR)
    numero = Column(String(20), nullable=False)
    whatsapp = Column(Boolean, default=False, nullable=False)
    principal = Column(Boolean, default=False, nullable=False)
    observacoes = Column(String(200))
    
    # Relacionamentos
    pessoa = relationship("Pessoa", back_populates="telefones")
    
    __table_args__ = (
        UniqueConstraint('pessoa_id', 'numero', name='uq_telefone_pessoa'),
        Index('idx_telefone_principal', 'principal'),
    )



class Pessoa(Base):
    """Tabela base para todas as pessoas"""
    __tablename__ = 'pessoas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String(20), nullable=False)  # 'aluno', 'professor', 'funcionario', 'encarregado'
    
    # Dados pessoais
    nome_completo = Column(String(200), nullable=False)
    nome_preferido = Column(String(100))
    data_nascimento = Column(Date, nullable=False)
    genero = Column(SQLEnum(Genero), nullable=False)
    estado_civil = Column(SQLEnum(EstadoCivil))
    nacionalidade = Column(String(100), default='angolana', nullable=False)
    
    # Documentos
    tipo_documento = Column(SQLEnum(TipoDocumento), nullable=False, default=TipoDocumento.BILHETE_IDENTIDADE)
    numero_documento = Column(String(50), unique=True, nullable=False)
    data_emissao_documento = Column(Date)
    data_validade_documento = Column(Date)
    orgao_emissor_documento = Column(String(100))
    
    # Contatos
    email_pessoal = Column(String(150))
    email_alternativo = Column(String(150))
    
    # Endereço
    provincia_residencia = Column(String(100))
    municipio_residencia = Column(String(100))
    bairro_residencia = Column(String(150))
    rua_residencia = Column(String(200))
    numero_residencia = Column(String(20))
    complemento_residencia = Column(String(100))
    
    # Saúde
    grupo_sanguineo = Column(String(5))
    alergias = Column(Text)
    medicamentos_uso = Column(Text)
    doencas_cronicas = Column(Text)
    
    # Emergência
    contato_emergencia_nome = Column(String(200))
    contato_emergencia_parentesco = Column(String(50))
    contato_emergencia_telefone = Column(String(20))
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos (herança)
    telefones = relationship("TelefonePessoa", back_populates="pessoa", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_pessoa_tipo', 'tipo'),
        Index('idx_pessoa_documento', 'numero_documento'),
        Index('idx_pessoa_nome', 'nome_completo'),
        Index('idx_pessoa_ativo', 'ativo'),
    )
    
    @property
    def idade(self) -> int:
        """Calcula idade em anos"""
        hoje = date.today()
        nascimento = self.data_nascimento
        idade = hoje.year - nascimento.year
        if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
            idade -= 1
        return idade
    
    @property
    def endereco_completo(self) -> str:
        """Retorna endereço completo formatado"""
        partes = []
        if self.rua_residencia:
            partes.append(f"{self.rua_residencia}")
        if self.numero_residencia:
            partes.append(f"Nº {self.numero_residencia}")
        if self.bairro_residencia:
            partes.append(f"{self.bairro_residencia}")
        if self.municipio_residencia:
            partes.append(f"{self.municipio_residencia}")
        if self.provincia_residencia:
            partes.append(f"{self.provincia_residencia}")
        if self.complemento_residencia:
            partes.append(f"({self.complemento_residencia})")
        return ", ".join(partes)


class Estagio(Base):
    """Estágios dos cursos técnicos"""
    __tablename__ = 'estagios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aluno_id = Column(Integer, ForeignKey('alunos.id', ondelete='CASCADE'), nullable=False)
    turma_tecnica_id = Column(Integer, ForeignKey('turmas_tecnicas.id', ondelete='CASCADE'), nullable=False)
    
    # Empresa
    empresa_nome = Column(String(200), nullable=False)
    empresa_nif = Column(String(20))
    empresa_endereco = Column(String(500))
    empresa_telefone = Column(String(20))
    empresa_email = Column(String(150))
    
    # Supervisor empresa
    supervisor_empresa_nome = Column(String(200), nullable=False)
    supervisor_empresa_cargo = Column(String(100))
    supervisor_empresa_telefone = Column(String(20))
    supervisor_empresa_email = Column(String(150))
    
    # Período
    data_inicio = Column(Date, nullable=False)
    data_termino = Column(Date, nullable=False)
    carga_horaria_semanal = Column(Integer, default=30, nullable=False)
    
    # Atividades
    atividades_desenvolvidas = Column(Text)
    setor_atuacao = Column(String(100))
    
    # Avaliação
    supervisor_escola_id = Column(Integer, ForeignKey('professores.id'))
    nota_empresa = Column(Numeric(5, 2))
    nota_supervisor = Column(Numeric(5, 2))
    nota_final = Column(Numeric(5, 2))
    
    # Documentação
    termo_compromisso_path = Column(String(500))
    relatorio_final_path = Column(String(500))
    certificado_estagio_path = Column(String(500))
    
    # Status
    status = Column(String(20), default='em_andamento', nullable=False)  # planejado, em_andamento, concluido, cancelado
    aprovado = Column(Boolean, default=False)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    aluno = relationship("Aluno")
    turma_tecnica = relationship("TurmaTecnica")
    supervisor_escola = relationship("Professor")
    
    __table_args__ = (
        UniqueConstraint('aluno_id', 'turma_tecnica_id', name='uq_estagio_aluno'),
        Index('idx_estagio_aluno', 'aluno_id'),
        Index('idx_estagio_status', 'status'),
        CheckConstraint('data_termino > data_inicio', name='ck_estagio_datas'),
    )




