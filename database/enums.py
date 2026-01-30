



# ============================================================================
# ENUMS E TIPOS PERSONALIZADOS
# ============================================================================

class TipoInstituicao(Enum):
    """Tipo de instituição educacional"""
    PUBLICA = "publica"
    PRIVADA = "privada"
    PUBLICO_PRIVADA = "publico_privada"
    CONVENIADA = "conveniada"

class TipoContrato(Enum):
    """Tipo de contrato de trabalho"""
    EFETIVO = "efetivo"
    CONTRATADO = "contratado"
    TEMPORARIO = "temporario"
    ESTAGIARIO = "estagiario"

class StatusPagamento(Enum):
    """Status de pagamento"""
    PENDENTE = "pendente"
    PAGO_PARCIAL = "pago_parcial"
    PAGO_TOTAL = "pago_total"
    ATRASADO = "atrasado"
    CANCELADO = "cancelado"
    ISENTO = "isento"

class TipoPagamento(Enum):
    """Formas de pagamento"""
    DINHEIRO = "dinheiro"
    TRANSFERENCIA = "transferencia"
    DEPOSITO = "deposito"
    MULTICAIXA = "multicaixa"
    CHEQUE = "cheque"
    CREDITO = "credito"
    DEBITO = "debito"

class Turno(Enum):
    """Turnos escolares"""
    MANHA = "manha"
    TARDE = "tarde"
    NOITE = "noite"
    INTEGRAL = "integral"

class Genero(Enum):
    """Gênero biológico"""
    MASCULINO = "masculino"
    FEMININO = "feminino"
    OUTRO = "outro"

class StatusAluno(Enum):
    """Status do aluno na instituição"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    TRANCADO = "trancado"
    TRANSFERIDO = "transferido"
    EXPULSO = "expulso"
    CONCLUIDO = "concluido"

class NivelAcesso(Enum):
    """Níveis de acesso ao sistema"""
    SUPER_ADMIN = "super_admin"
    DIRECAO_GERAL = "direcao_geral"
    DIRECAO_PEDAGOGICA = "direcao_pedagogica"
    COORDENACAO = "coordenacao"
    SECRETARIA = "secretaria"
    PROFESSOR = "professor"
    ALUNO = "aluno"
    ENCARREGADO = "encarregado"
    FUNCIONARIO = "funcionario"

class TipoTelefone(Enum):
    """Tipos de telefone"""
    CELULAR = "celular"
    RESIDENCIAL = "residencial"
    COMERCIAL = "comercial"
    WHATSAPP = "whatsapp"

class TipoParentesco(Enum):
    """Parentesco do encarregado de educação"""
    PAI = "pai"
    MAE = "mae"
    TIO = "tio"
    TIA = "tia"
    IRMAO = "irmao"
    IRMA = "irma"
    AVO = "avo"
    OUTRO = "outro"

class EstadoCivil(Enum):
    """Estado civil"""
    SOLTEIRO = "solteiro"
    CASADO = "casado"
    DIVORCIADO = "divorciado"
    VIUVO = "viuvo"
    UNIAO_ESTAVEL = "uniao_estavel"

class TipoDocumento(Enum):
    """Tipos de documentos"""
    BILHETE_IDENTIDADE = "bi"
    PASSAPORTE = "passaporte"
    CARTEIRA_MOTORISTA = "carta_conducao"
    OUTRO = "outro"

class StatusFuncionario(Enum):
    """Status do funcionário"""
    ATIVO = "ativo"
    FERIAS = "ferias"
    LICENCA = "licenca"
    DESLIGADO = "desligado"
    APOSENTADO = "aposentado"

class TipoAvaliacao(Enum):
    """Tipos de avaliação"""
    PROVA_ESCRITA = "prova_escrita"
    TRABALHO_PRATICO = "trabalho_pratico"
    PROJETO = "projeto"
    APRESENTACAO = "apresentacao"
    PARTICIPACAO = "participacao"
    TESTE = "teste"
    EXAME = "exame"

class ResultadoAvaliacao(Enum):
    """Resultados de avaliação"""
    APROVADO = "aprovado"
    REPROVADO = "reprovado"
    RECUPERACAO = "recuperacao"
    TRANSFERIDO = "transferido"
    EM_ANDAMENTO = "em_andamento"

class TipoCurso(Enum):
    """Tipos de cursos oferecidos"""
    REGULAR = "regular"
    TECNICO = "tecnico"
    PROFISSIONAL = "profissional"
    PRE_UNIVERSITARIO = "pre_universitario"
    CURTOS = "cursos_curtos"

class NivelCursoTecnico(Enum):
    """Níveis de cursos técnicos"""
    NIVEL_I = "nivel_i"      # 9ª classe + 1 ano
    NIVEL_II = "nivel_ii"    # 9ª classe + 2 anos
    NIVEL_III = "nivel_iii"  # 12ª classe + 2 anos
    NIVEL_IV = "nivel_iv"    # 12ª classe + 3 anos
