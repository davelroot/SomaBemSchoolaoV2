# SomaBemSchoolaoV2
somabemschool/
├── app.py                    # Aplicação principal
├── database_model.py         # Modelo do banco de dados
├── requirements.txt          # Dependências
├── README.md                 # Documentação
├── icons/                    # Ícones do sistema
│   ├── logo.png
│   ├── logo_small.png
│   └── theme/
├── styles/                   # Estilos CSS/QSS
│   ├── angola.qss
│   ├── light.qss
│   └── dark.qss
├── reports/                  # Templates de relatórios
│   ├── financeiro/
│   ├── academico/
│   └── administrativo/
├── backups/                  # Backups automáticos
├── logs/                    # Logs do sistema
└── config/                  # Configurações
    ├── settings.json
    └── themes.json

# SomaBemSchoolaoV2


# Instalar dependências
pip install PySide6 matplotlib pandas qrcode[pil] sqlalchemy psycopg2-binary

# Executar aplicação
python sistema_completo.py

# Para desenvolvimento
python -m pdb sistema_completo.py


# 1. Clone o repositório
git clone https://github.com/seu-usuario/somabemschool.git
cd somabemschool

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure o banco de dados
# Edite database_model.py com suas credenciais

# 5. Execute a aplicação
python app.py
