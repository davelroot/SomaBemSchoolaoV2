


class ProfessorDisciplina(Base):
    """Disciplinas que cada professor pode lecionar"""
    __tablename__ = 'professor_disciplina'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    professor_id = Column(Integer, ForeignKey('professores.id', ondelete='CASCADE'), nullable=False)
    disciplina_id = Column(Integer, ForeignKey('disciplinas.id', ondelete='CASCADE'), nullable=False)
    
    # Nível de habilitação
    nivel_habilitacao = Column(String(50), default='licenciatura')  # licenciatura, mestrado, doutoramento
    anos_experiencia = Column(Integer, default=0)
    preferencia = Column(Boolean, default=False, nullable=False)  # Disciplina preferida
    
    # Status
    ativo = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    professor = relationship("Professor", back_populates="disciplinas")
    disciplina = relationship("Disciplina", back_populates="professores")
    
    __table_args__ = (
        UniqueConstraint('professor_id', 'disciplina_id', name='uq_professor_disciplina'),
        Index('idx_prof_disc_ativa', 'ativo'),
    )

