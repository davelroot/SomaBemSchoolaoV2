






# ============================================================================
# ESTRUTURA FÍSICA
# ============================================================================

class Bloco(Base):
    """Blocos ou edifícios do campus"""
    __tablename__ = 'blocos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campus_id = Column(Integer, ForeignKey('campi.id', ondelete='CASCADE'), nullable=False)
    codigo = Column(String(20), nullable=False)
    nome = Column(String(150), nullable=False)
    
    # Características
    andares = Column(Integer, default=1, nullable=False)
    ano_construcao = Column(Integer)
    situacao = Column(String(50), default='regular')  # regular, reforma, interditado
    
    # Recursos
    possui_elevador = Column(Boolean, default=False)
    possui_rampa_acessibilidade = Column(Boolean, default=False)
    possui_gerador = Column(Boolean, default=False)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    campus = relationship("Campus", back_populates="blocos")
    salas = relationship("Sala", back_populates="bloco", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('campus_id', 'codigo', name='uq_bloco_codigo'),
        Index('idx_bloco_campus', 'campus_id'),
    )

class Sala(Base):
    """Salas de aula, laboratórios, etc."""
    __tablename__ = 'salas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campus_id = Column(Integer, ForeignKey('campi.id', ondelete='CASCADE'), nullable=False)
    bloco_id = Column(Integer, ForeignKey('blocos.id', ondelete='CASCADE'))
    codigo = Column(String(20), nullable=False)
    nome = Column(String(150))
    
    # Características
    tipo = Column(String(50), nullable=False)  # aula, laboratorio, informatica, biblioteca, administracao
    capacidade = Column(Integer, nullable=False)
    area = Column(Float)  # m²
    
    # Recursos
    possui_projetor = Column(Boolean, default=False)
    possui_ar_condicionado = Column(Boolean, default=False)
    possui_internet = Column(Boolean, default=False)
    possui_computadores = Column(Boolean, default=False)
    numero_computadores = Column(Integer, default=0)
    
    # Estado
    disponivel = Column(Boolean, default=True, nullable=False)
    manutencao_ate = Column(Date)
    observacoes = Column(Text)
    
    # Localização
    andar = Column(Integer, default=0)
    referencia = Column(String(100))
    
    # Relacionamentos
    campus = relationship("Campus", back_populates="salas")
    bloco = relationship("Bloco", back_populates="salas")
    turmas = relationship("Turma", back_populates="sala")
    
    __table_args__ = (
        UniqueConstraint('campus_id', 'codigo', name='uq_sala_codigo'),
        Index('idx_sala_tipo', 'tipo'),
        Index('idx_sala_disponivel', 'disponivel'),
    )
    
    @property
    def localizacao_completa(self) -> str:
        """Retorna localização completa"""
        local = []
        if self.bloco:
            local.append(f"Bloco {self.bloco.codigo}")
        if self.andar > 0:
            local.append(f"{self.andar}º andar")
        local.append(f"Sala {self.codigo}")
        if self.nome:
            local.append(f"({self.nome})")
        return " - ".join(local)

# ============================================================================
# ESTRUTURA ACADÊMICA
# ============================================================================

class AnoLetivo(Base):
    """Anos letivos da instituição"""
    __tablename__ = 'anos_letivos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    instituicao_id = Column(Integer, ForeignKey('instituicoes.id', ondelete='CASCADE'), nullable=False)
    ano = Column(Integer, nullable=False)  # Ex: 2024
    codigo = Column(String(20), nullable=False)  # Ex: 2024-2025
    
    # Períodos
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    
    # Status
    aberto_inscricoes = Column(Boolean, default=False, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    concluido = Column(Boolean, default=False, nullable=False)
    
    # Configurações
    max_alunos_turma = Column(Integer, default=35)
    max_turmas_serie = Column(Integer, default=5)
    
    # Datas importantes
    data_inicio_inscricoes = Column(Date)
    data_fim_inscricoes = Column(Date)
    data_inicio_matriculas = Column(Date)
    data_fim_matriculas = Column(Date)
    
    # Observações
    observacoes = Column(Text)
    
    # Relacionamentos
    instituicao = relationship("Instituicao")
    classes = relationship("Classe", back_populates="ano_letivo", cascade="all, delete-orphan")
    turmas = relationship("Turma", back_populates="ano_letivo", cascade="all, delete-orphan")
    calendarios = relationship("CalendarioEscolar", back_populates="ano_letivo", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('instituicao_id', 'ano', name='uq_ano_letivo_instituicao'),
        UniqueConstraint('instituicao_id', 'codigo', name='uq_codigo_ano_letivo'),
        Index('idx_ano_letivo_ano', 'ano'),
        Index('idx_ano_letivo_ativo', 'ativo'),
        CheckConstraint('data_fim > data_inicio', name='ck_datas_ano_letivo'),
    )
    
    @property
    def descricao(self) -> str:
        """Descrição completa do ano letivo"""
        return f"Ano Letivo {self.ano} ({self.data_inicio.strftime('%d/%m/%Y')} - {self.data_fim.strftime('%d/%m/%Y')})"

class Classe(Base):
    """Classes/Series do sistema educativo"""
    __tablename__ = 'classes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano_letivo_id = Column(Integer, ForeignKey('anos_letivos.id', ondelete='CASCADE'), nullable=False)
    nivel = Column(String(50), nullable=False)  # 'primario', 'i_ciclo', 'ii_ciclo', 'tecnico'
    codigo = Column(String(20), nullable=False)  # '1A', '7B', '10TEC', etc
    nome = Column(String(100), nullable=False)  # '1ª Classe', '7ª Classe', '10ª Classe Técnico'
    ordem = Column(Integer, nullable=False)  # Para ordenação
    
    # Características
    faixa_etaria_min = Column(Integer, comment='Idade mínima em anos')
    faixa_etaria_max = Column(Integer, comment='Idade máxima em anos')
    carga_horaria_semanal = Column(Integer, comment='Carga horária semanal em horas')
    
    # Currículo
    tem_exame_nacional = Column(Boolean, default=False)
    ciclo = Column(String(50))  # 'primario', 'i_ciclo_secundario', 'ii_ciclo_secundario'
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    ano_letivo = relationship("AnoLetivo", back_populates="classes")
    turmas = relationship("Turma", back_populates="classe", cascade="all, delete-orphan")
    disciplinas = relationship("DisciplinaClasse", back_populates="classe", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('ano_letivo_id', 'codigo', name='uq_classe_codigo'),
        Index('idx_classe_nivel', 'nivel'),
        Index('idx_classe_ordem', 'ordem'),
    )

class Disciplina(Base):
    """Disciplinas curriculares"""
    __tablename__ = 'disciplinas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_med = Column(String(50), comment='Código do MED se aplicável')
    nome = Column(String(150), nullable=False)
    nome_curto = Column(String(50))
    area = Column(String(100))  # 'linguagens', 'ciencias', 'humanas', 'tecnicas'
    
    # Características
    obrigatoria = Column(Boolean, default=True, nullable=False)
    tem_pratica = Column(Boolean, default=False)
    tem_laboratorio = Column(Boolean, default=False)
    
    # Carga horária base
    horas_semanais_base = Column(Integer, default=3)
    
    # Descrição
    ementa = Column(Text)
    competencias = Column(Text)
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    classes = relationship("DisciplinaClasse", back_populates="disciplina", cascade="all, delete-orphan")
    professores = relationship("ProfessorDisciplina", back_populates="disciplina", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_disciplina_area', 'area'),
        Index('idx_disciplina_ativa', 'ativa'),
    )

class DisciplinaClasse(Base):
    """Associação entre disciplinas e classes (com carga horária específica)"""
    __tablename__ = 'disciplina_classe'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    disciplina_id = Column(Integer, ForeignKey('disciplinas.id', ondelete='CASCADE'), nullable=False)
    classe_id = Column(Integer, ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    
    # Carga horária específica para esta classe
    horas_semanais = Column(Integer, nullable=False)
    aulas_semanais = Column(Integer, default=1, nullable=False)
    
    # Avaliação
    peso_avaliacao = Column(Numeric(5, 2), default=1.0, nullable=False)
    incluir_media_final = Column(Boolean, default=True, nullable=False)
    
    # Ordem
    ordem_grade = Column(Integer, nullable=False)
    
    # Relacionamentos
    disciplina = relationship("Disciplina", back_populates="classes")
    classe = relationship("Classe", back_populates="disciplinas")
    
    __table_args__ = (
        UniqueConstraint('disciplina_id', 'classe_id', name='uq_disciplina_classe'),
        Index('idx_disc_classe_classe', 'classe_id'),
    )

class Turma(Base):
    """Turmas (divisão de classes em grupos)"""
    __tablename__ = 'turmas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano_letivo_id = Column(Integer, ForeignKey('anos_letivos.id', ondelete='CASCADE'), nullable=False)
    classe_id = Column(Integer, ForeignKey('classes.id', ondelete='CASCADE'), nullable=False)
    sala_id = Column(Integer, ForeignKey('salas.id'))
    
    codigo = Column(String(20), nullable=False)  # Ex: '7A', '10TEC-A'
    nome = Column(String(100), nullable=False)   # Ex: '7ª Classe A', '10ª Técnico A'
    
    # Turno
    turno = Column(SQLEnum(Turno), nullable=False, default=Turno.MANHA)
    
    # Horário
    hora_inicio = Column(Time, default=time(7, 0), nullable=False)
    hora_fim = Column(Time, default=time(12, 30), nullable=False)
    
    # Capacidade
    capacidade_maxima = Column(Integer, default=35, nullable=False)
    vagas_disponiveis = Column(Integer, nullable=False)
    
    # Status
    ativa = Column(Boolean, default=True, nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Responsável
    professor_coordenador_id = Column(Integer, ForeignKey('professores.id'))
    
    # Relacionamentos
    ano_letivo = relationship("AnoLetivo", back_populates="turmas")
    classe = relationship("Classe", back_populates="turmas")
    sala = relationship("Sala", back_populates="turmas")
    professor_coordenador = relationship("Professor", foreign_keys=[professor_coordenador_id])
    alunos = relationship("Matricula", back_populates="turma", cascade="all, delete-orphan")
    horarios = relationship("HorarioAula", back_populates="turma", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('ano_letivo_id', 'classe_id', 'codigo', name='uq_turma_codigo'),
        Index('idx_turma_ano_letivo', 'ano_letivo_id'),
        Index('idx_turma_classe', 'classe_id'),
        Index('idx_turma_turno', 'turno'),
    )
    
    @hybrid_property
    def total_alunos(self):
        """Total de alunos matriculados na turma"""
        if hasattr(self, '_alunos_count'):
            return self._alunos_count
        from sqlalchemy import func, select
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session is None:
            return 0
        return session.query(func.count(Matricula.id)).filter(
            Matricula.turma_id == self.id,
            Matricula.ativa == True
        ).scalar()
    
    @hybrid_property
    def ocupacao_percentual(self):
        """Percentual de ocupação da turma"""
        if self.capacidade_maxima == 0:
            return 0
        return (self.total_alunos / self.capacidade_maxima) * 100

class HorarioAula(Base):
    """Horário de aulas por turma"""
    __tablename__ = 'horarios_aula'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    turma_id = Column(Integer, ForeignKey('turmas.id', ondelete='CASCADE'), nullable=False)
    disciplina_id = Column(Integer, ForeignKey('disciplinas.id', ondelete='CASCADE'), nullable=False)
    professor_id = Column(Integer, ForeignKey('professores.id'), nullable=False)
    sala_id = Column(Integer, ForeignKey('salas.id'))
    
    # Dia e horário
    dia_semana = Column(Integer, nullable=False)  # 1=Segunda, 2=Terça, ..., 7=Domingo
    hora_inicio = Column(Time, nullable=False)
    hora_fim = Column(Time, nullable=False)
    
    # Frequência
    recorrencia = Column(String(20), default='semanal', nullable=False)  # semanal, quinzenal, mensal
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Datas específicas (para aulas avulsas)
    data_especifica = Column(Date)
    
    # Observações
    observacoes = Column(String(500))
    
    # Relacionamentos
    turma = relationship("Turma", back_populates="horarios")
    disciplina = relationship("Disciplina")
    professor = relationship("Professor", foreign_keys=[professor_id])
    sala = relationship("Sala")
    presencas = relationship("PresencaAula", back_populates="horario", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_horario_turma', 'turma_id'),
        Index('idx_horario_professor', 'professor_id'),
        Index('idx_horario_dia', 'dia_semana'),
        CheckConstraint('hora_fim > hora_inicio', name='ck_horario_aula'),
    )
    
    @property
    def duracao_minutos(self) -> int:
        """Duração da aula em minutos"""
        inicio = datetime.combine(date.today(), self.hora_inicio)
        fim = datetime.combine(date.today(), self.hora_fim)
        diferenca = fim - inicio
        return int(diferenca.total_seconds() / 60)
