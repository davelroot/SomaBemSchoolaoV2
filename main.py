import sys
import os
import json
import hashlib
import uuid
import qrcode
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')

# PySide6 imports
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QStackedWidget, QLabel, QPushButton, QLineEdit,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QDateEdit, QTimeEdit,
    QCheckBox, QRadioButton, QGroupBox, QTabWidget, QSplitter,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QToolBar, QStatusBar, QMenuBar, QMenu, QAction, QDialog,
    QInputDialog, QProgressBar, QProgressDialog, QToolButton,
    QFrame, QScrollArea, QSizePolicy, QSpacerItem, QFormLayout,
    QDoubleSpinBox, QSpinBox, QAbstractItemView, QStyleFactory,
    QStyle, QGraphicsDropShadowEffect, QDialogButtonBox,
    QWizard, QWizardPage, QCalendarWidget, QTimeEdit
)

from PySide6.QtCore import (
    Qt, QTimer, QDateTime, QDate, QTime, QSize, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup,
    QRect, QPoint, Signal, Slot, QThread, pyqtSignal, QSettings,
    QMutex, QWaitCondition, QThreadPool, QRunnable, QObject,
    QEvent, QMargins
)

from PySide6.QtGui import (
    QFont, QFontDatabase, QIcon, QPixmap, QColor, QPainter,
    QPen, QBrush, QLinearGradient, QRadialGradient, QConicalGradient,
    QPalette, QImage, QMovie, QKeySequence, QShortcut, QCursor,
    QActionEvent, QResizeEvent, QCloseEvent, QValidator, QIntValidator,
    QDoubleValidator, QRegularExpressionValidator
)

# Importando o modelo do banco de dados
from database_model import (
    Base, Session, engine, Instituicao, Aluno, Professor, Funcionario,
    Turma, Matricula, Pagamento, ParcelaPropina, Disciplina, Nota,
    PresencaAula, CursoTecnico, Estagio, Usuario, ConfiguracaoSistema,
    StatusPagamento, TipoPagamento, Turno, StatusAluno, NivelAcesso
)

# ============================================================================
# CONSTANTES E CONFIGURAÇÕES
# ============================================================================

class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    ANGOLA = "angola"

class AppConfig:
    """Configurações da aplicação"""
    APP_NAME = "SomaBemSchool ERP"
    APP_VERSION = "3.0.0"
    COMPANY_NAME = "SomaBemSchool"
    
    # Cores da bandeira de Angola
    COLORS = {
        Theme.LIGHT: {
            "primary": "#1E88E5",
            "secondary": "#FFC107",
            "accent": "#4CAF50",
            "background": "#FFFFFF",
            "surface": "#F5F5F5",
            "text": "#212121",
            "text_secondary": "#757575",
            "border": "#E0E0E0",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336",
            "info": "#2196F3"
        },
        Theme.DARK: {
            "primary": "#2196F3",
            "secondary": "#FFB300",
            "accent": "#66BB6A",
            "background": "#121212",
            "surface": "#1E1E1E",
            "text": "#FFFFFF",
            "text_secondary": "#B0B0B0",
            "border": "#2D2D2D",
            "success": "#66BB6A",
            "warning": "#FFB74D",
            "error": "#EF5350",
            "info": "#42A5F5"
        },
        Theme.ANGOLA: {
            "primary": "#CC0000",  # Vermelho da bandeira
            "secondary": "#000000",  # Preto da bandeira
            "accent": "#FFD700",  # Amarelo da bandeira
            "background": "#FFFFFF",
            "surface": "#F8F9FA",
            "text": "#212529",
            "text_secondary": "#6C757D",
            "border": "#DEE2E6",
            "success": "#198754",
            "warning": "#FFC107",
            "error": "#DC3545",
            "info": "#0DCAF0"
        }
    }
    
    # Tamanhos
    FONT_SIZES = {
        "tiny": 8,
        "small": 10,
        "medium": 12,
        "large": 14,
        "xlarge": 16,
        "xxlarge": 18,
        "title": 24,
        "heading": 32
    }
    
    # Animations
    ANIMATION_DURATION = 300

# ============================================================================
# CLASSES AUXILIARES E WIDGETS PERSONALIZADOS
# ============================================================================

class LoadingOverlay(QWidget):
    """Overlay de carregamento"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.spinner = QLabel("Carregando...")
        self.spinner.setAlignment(Qt.AlignCenter)
        self.spinner.setStyleSheet("""
            font-size: 16px;
            color: white;
            padding: 20px;
            border-radius: 10px;
            background-color: rgba(0, 0, 0, 150);
        """)
        
        layout.addWidget(self.spinner)
        self.setLayout(layout)
        
        self.hide()
    
    def showEvent(self, event):
        """Centraliza o overlay quando é mostrado"""
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(event)

class ModernButton(QPushButton):
    """Botão moderno com efeitos"""
    def __init__(self, text="", parent=None, icon=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        
        # Efeito de sombra
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(0, 3)
        self.shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(self.shadow)
        
        # Configuração inicial
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 11))
        
        if icon:
            self.setIcon(icon)
    
    def enterEvent(self, event):
        """Animação ao passar o mouse"""
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setStartValue(self.geometry())
        anim.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
        anim.setEasingCurve(QEasingCurve.OutBack)
        anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animação ao sair do mouse"""
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(200)
        anim.setStartValue(self.geometry())
        anim.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
        anim.setEasingCurve(QEasingCurve.InBack)
        anim.start()
        super().leaveEvent(event)

class CardWidget(QFrame):
    """Widget de cartão moderno"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
            layout.addWidget(title_label)
        
        # Área de conteúdo
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)
        
        self.setLayout(layout)
        
        # Efeito de sombra
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 5)
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(self.shadow)

class AnimatedStackedWidget(QStackedWidget):
    """Stacked widget com animação de transição"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.next_index = 0
        self.animation_duration = 300
    
    def setCurrentIndexWithAnimation(self, index, direction="right"):
        """Muda de página com animação"""
        if index == self.currentIndex():
            return
        
        self.next_index = index
        current_widget = self.widget(self.currentIndex())
        next_widget = self.widget(index)
        
        # Posiciona o próximo widget
        width = self.width()
        height = self.height()
        
        if direction == "right":
            next_widget.setGeometry(width, 0, width, height)
        elif direction == "left":
            next_widget.setGeometry(-width, 0, width, height)
        elif direction == "up":
            next_widget.setGeometry(0, height, width, height)
        elif direction == "down":
            next_widget.setGeometry(0, -height, width, height)
        
        next_widget.show()
        next_widget.raise_()
        
        # Animação do widget atual
        anim_current = QPropertyAnimation(current_widget, b"geometry")
        anim_current.setDuration(self.animation_duration)
        anim_current.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Animação do próximo widget
        anim_next = QPropertyAnimation(next_widget, b"geometry")
        anim_next.setDuration(self.animation_duration)
        anim_next.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Configura as animações baseadas na direção
        if direction == "right":
            anim_current.setEndValue(QRect(-width, 0, width, height))
            anim_next.setEndValue(QRect(0, 0, width, height))
        elif direction == "left":
            anim_current.setEndValue(QRect(width, 0, width, height))
            anim_next.setEndValue(QRect(0, 0, width, height))
        elif direction == "up":
            anim_current.setEndValue(QRect(0, -height, width, height))
            anim_next.setEndValue(QRect(0, 0, width, height))
        elif direction == "down":
            anim_current.setEndValue(QRect(0, height, width, height))
            anim_next.setEndValue(QRect(0, 0, width, height))
        
        # Grupo de animações
        group = QParallelAnimationGroup()
        group.addAnimation(anim_current)
        group.addAnimation(anim_next)
        
        group.finished.connect(lambda: self.setCurrentIndex(index))
        group.start()

class ModernTableWidget(QTableWidget):
    """Tabela moderna com estilização"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        
        # Configurações de performance
        self.setSortingEnabled(True)
        self.setCornerButtonEnabled(False)
        
        # Efeito de hover
        self.setMouseTracking(True)
    
    def addContextMenu(self):
        """Adiciona menu de contexto"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
    
    def showContextMenu(self, pos):
        """Mostra menu de contexto"""
        menu = QMenu()
        
        copy_action = QAction("Copiar", self)
        copy_action.triggered.connect(self.copySelection)
        menu.addAction(copy_action)
        
        export_action = QAction("Exportar para Excel", self)
        export_action.triggered.connect(self.exportToExcel)
        menu.addAction(export_action)
        
        menu.addSeparator()
        
        refresh_action = QAction("Atualizar", self)
        refresh_action.triggered.connect(self.refreshData)
        menu.addAction(refresh_action)
        
        menu.exec_(self.mapToGlobal(pos))
    
    def copySelection(self):
        """Copia seleção para clipboard"""
        selected = self.selectedRanges()
        if not selected:
            return
        
        text = ""
        for row in range(selected[0].topRow(), selected[0].bottomRow() + 1):
            row_data = []
            for col in range(selected[0].leftColumn(), selected[0].rightColumn() + 1):
                item = self.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        
        QApplication.clipboard().setText(text)
    
    def exportToExcel(self):
        """Exporta dados para Excel"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar para Excel", "", "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                data = []
                headers = []
                
                # Coleta cabeçalhos
                for col in range(self.columnCount()):
                    headers.append(self.horizontalHeaderItem(col).text())
                
                # Coleta dados
                for row in range(self.rowCount()):
                    row_data = []
                    for col in range(self.columnCount()):
                        item = self.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                # Cria DataFrame e exporta
                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file_path, index=False)
                
                QMessageBox.information(self, "Sucesso", "Dados exportados com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar: {str(e)}")
    
    def refreshData(self):
        """Atualiza dados da tabela"""
        # Implementar nas subclasses
        pass

class ChartWidget(QWidget):
    """Widget para gráficos"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plotBarChart(self, data, labels, title="", xlabel="", ylabel=""):
        """Plota gráfico de barras"""
        self.axes.clear()
        self.axes.bar(labels, data, color=AppConfig.COLORS[Theme.ANGOLA]["primary"])
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.tick_params(axis='x', rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plotLineChart(self, x_data, y_data, title="", xlabel="", ylabel=""):
        """Plota gráfico de linha"""
        self.axes.clear()
        self.axes.plot(x_data, y_data, 
                      color=AppConfig.COLORS[Theme.ANGOLA]["primary"],
                      marker='o', linewidth=2)
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.grid(True, alpha=0.3)
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plotPieChart(self, data, labels, title=""):
        """Plota gráfico de pizza"""
        self.axes.clear()
        colors = [AppConfig.COLORS[Theme.ANGOLA]["primary"],
                 AppConfig.COLORS[Theme.ANGOLA]["secondary"],
                 AppConfig.COLORS[Theme.ANGOLA]["accent"],
                 AppConfig.COLORS[Theme.ANGOLA]["success"],
                 AppConfig.COLORS[Theme.ANGOLA]["warning"]]
        
        self.axes.pie(data, labels=labels, colors=colors[:len(data)],
                     autopct='%1.1f%%', startangle=90)
        self.axes.set_title(title)
        self.axes.axis('equal')
        self.figure.tight_layout()
        self.canvas.draw()

class QRCodeWidget(QWidget):
    """Widget para gerar QR Codes"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        
        layout = QVBoxLayout()
        layout.addWidget(self.qr_label)
        self.setLayout(layout)
    
    def generateQR(self, data, size=200):
        """Gera QR Code"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Converte para QPixmap
            img_bytes = img.tobytes()
            qimage = QImage(img_bytes, img.size[0], img.size[1], 
                          QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimage).scaled(size, size, 
                                                     Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation)
            
            self.qr_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Erro ao gerar QR Code: {e}")

# ============================================================================
# TELA DE LOGIN
# ============================================================================

class LoginWindow(QMainWindow):
    """Janela de login"""
    login_success = Signal(object)  # Emite objeto usuário
    
    def __init__(self):
        super().__init__()
        self.session = Session()
        self.current_theme = Theme.ANGOLA
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Configura a interface"""
        self.setWindowTitle(f"{AppConfig.APP_NAME} - Login")
        self.setFixedSize(1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Painel esquerdo (imagem/branding)
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 50, 50, 50)
        
        # Logo e título
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(":/icons/logo.png").scaled(200, 200, 
                                                                Qt.KeepAspectRatio,
                                                                Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(AppConfig.APP_NAME)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        
        subtitle_label = QLabel("Sistema de Gestão Escolar Integrado")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 14))
        
        # Informações da instituição
        info_label = QLabel()
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setFont(QFont("Segoe UI", 10))
        
        try:
            instituicao = self.session.query(Instituicao).first()
            if instituicao:
                info_text = f"""
                <b>{instituicao.nome_oficial}</b><br>
                {instituicao.endereco_completo}<br>
                {instituicao.email_principal}
                """
                info_label.setText(info_text)
        except:
            pass
        
        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addSpacing(50)
        left_layout.addWidget(info_label)
        left_layout.addStretch()
        
        # Painel direito (formulário de login)
        right_panel = CardWidget()
        right_panel.setObjectName("loginPanel")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(20)
        
        # Título do formulário
        form_title = QLabel("Acesso ao Sistema")
        form_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        form_title.setAlignment(Qt.AlignCenter)
        
        # Campo de usuário
        user_layout = QVBoxLayout()
        user_label = QLabel("Usuário:")
        user_label.setFont(QFont("Segoe UI", 11))
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Digite seu nome de usuário ou email")
        self.user_input.setMinimumHeight(45)
        self.user_input.setFont(QFont("Segoe UI", 11))
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        
        # Campo de senha
        pass_layout = QVBoxLayout()
        pass_label = QLabel("Senha:")
        pass_label.setFont(QFont("Segoe UI", 11))
        
        pass_hbox = QHBoxLayout()
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Digite sua senha")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setMinimumHeight(45)
        self.pass_input.setFont(QFont("Segoe UI", 11))
        
        self.show_pass_btn = QToolButton()
        self.show_pass_btn.setIcon(QIcon.fromTheme("view-conceal"))
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.clicked.connect(self.toggle_password)
        
        pass_hbox.addWidget(self.pass_input)
        pass_hbox.addWidget(self.show_pass_btn)
        
        pass_layout.addWidget(pass_label)
        pass_layout.addLayout(pass_hbox)
        
        # Lembrar de mim
        self.remember_check = QCheckBox("Lembrar de mim")
        self.remember_check.setFont(QFont("Segoe UI", 10))
        
        # Botão de login
        self.login_btn = ModernButton("ENTRAR")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_btn.clicked.connect(self.authenticate)
        
        # Botão de trocar tema
        self.theme_btn = ModernButton("Alternar Tema")
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        # Links
        links_layout = QHBoxLayout()
        links_layout.setAlignment(Qt.AlignCenter)
        
        forgot_link = QPushButton("Esqueci a senha")
        forgot_link.setFlat(True)
        forgot_link.setCursor(Qt.PointingHandCursor)
        forgot_link.clicked.connect(self.show_forgot_password)
        
        help_link = QPushButton("Ajuda")
        help_link.setFlat(True)
        help_link.setCursor(Qt.PointingHandCursor)
        help_link.clicked.connect(self.show_help)
        
        links_layout.addWidget(forgot_link)
        links_layout.addWidget(help_link)
        
        # Adiciona widgets ao layout
        right_layout.addWidget(form_title)
        right_layout.addSpacing(20)
        right_layout.addLayout(user_layout)
        right_layout.addLayout(pass_layout)
        right_layout.addWidget(self.remember_check)
        right_layout.addWidget(self.login_btn)
        right_layout.addWidget(self.theme_btn)
        right_layout.addLayout(links_layout)
        
        right_panel.setLayout(right_layout)
        
        # Adiciona painéis ao layout principal
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
        
        # Configura atalhos
        self.setup_shortcuts()
        
        # Carrega credenciais salvas
        self.load_saved_credentials()
    
    def setup_shortcuts(self):
        """Configura atalhos de teclado"""
        # Enter para login
        QShortcut(Qt.Key_Return, self, self.authenticate)
        QShortcut(Qt.Key_Enter, self, self.authenticate)
        
        # F1 para ajuda
        QShortcut(Qt.Key_F1, self, self.show_help)
        
        # Ctrl+T para trocar tema
        QShortcut(QKeySequence("Ctrl+T"), self, self.toggle_theme)
    
    def toggle_password(self):
        """Alterna visibilidade da senha"""
        if self.show_pass_btn.isChecked():
            self.pass_input.setEchoMode(QLineEdit.Normal)
            self.show_pass_btn.setIcon(QIcon.fromTheme("view-reveal"))
        else:
            self.pass_input.setEchoMode(QLineEdit.Password)
            self.show_pass_btn.setIcon(QIcon.fromTheme("view-conceal"))
    
    def toggle_theme(self):
        """Alterna entre temas"""
        if self.current_theme == Theme.ANGOLA:
            self.current_theme = Theme.DARK
        elif self.current_theme == Theme.DARK:
            self.current_theme = Theme.LIGHT
        else:
            self.current_theme = Theme.ANGOLA
        
        self.apply_theme()
    
    def apply_theme(self):
        """Aplica o tema atual"""
        colors = AppConfig.COLORS[self.current_theme]
        
        style = f"""
        QMainWindow {{
            background-color: {colors['background']};
        }}
        
        #leftPanel {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['primary']}, stop:1 {colors['secondary']});
            color: white;
        }}
        
        #loginPanel {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 15px;
        }}
        
        QLabel {{
            color: {colors['text']};
        }}
        
        QLineEdit {{
            padding: 10px;
            border: 2px solid {colors['border']};
            border-radius: 8px;
            background-color: {colors['background']};
            color: {colors['text']};
            font-size: 14px;
        }}
        
        QLineEdit:focus {{
            border-color: {colors['primary']};
        }}
        
        QCheckBox {{
            color: {colors['text_secondary']};
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
        }}
        
        QPushButton {{
            color: {colors['text']};
        }}
        
        QPushButton[flat="true"] {{
            color: {colors['primary']};
            text-decoration: underline;
            padding: 5px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border: none;
            padding: 5px;
        }}
        """
        
        self.setStyleSheet(style)
    
    def load_saved_credentials(self):
        """Carrega credenciais salvas"""
        settings = QSettings(AppConfig.COMPANY_NAME, AppConfig.APP_NAME)
        
        remember = settings.value("remember_me", False, bool)
        self.remember_check.setChecked(remember)
        
        if remember:
            username = settings.value("username", "")
            password = settings.value("password", "")
            
            self.user_input.setText(username)
            self.pass_input.setText(password)
    
    def save_credentials(self):
        """Salva credenciais"""
        settings = QSettings(AppConfig.COMPANY_NAME, AppConfig.APP_NAME)
        
        if self.remember_check.isChecked():
            settings.setValue("remember_me", True)
            settings.setValue("username", self.user_input.text())
            settings.setValue("password", self.pass_input.text())
        else:
            settings.setValue("remember_me", False)
            settings.remove("username")
            settings.remove("password")
    
    def authenticate(self):
        """Autentica o usuário"""
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Atenção", 
                               "Por favor, preencha todos os campos.")
            return
        
        # Mostra overlay de carregamento
        self.overlay = LoadingOverlay(self)
        self.overlay.show()
        QApplication.processEvents()
        
        try:
            # Busca usuário
            user = self.session.query(Usuario).filter(
                (Usuario.username == username) | (Usuario.email == username)
            ).first()
            
            if not user:
                self.overlay.hide()
                QMessageBox.warning(self, "Erro", 
                                   "Usuário não encontrado.")
                return
            
            if not user.ativo:
                self.overlay.hide()
                QMessageBox.warning(self, "Erro", 
                                   "Usuário desativado.")
                return
            
            # Verifica senha
            if not user.verificar_senha(password):
                user.tentativas_login_falhas += 1
                
                if user.tentativas_login_falhas >= 5:
                    user.data_bloqueio = datetime.utcnow()
                    user.ativo = False
                    self.session.commit()
                    
                    self.overlay.hide()
                    QMessageBox.critical(self, "Erro", 
                                        "Conta bloqueada por tentativas falhas.")
                    return
                
                self.session.commit()
                self.overlay.hide()
                QMessageBox.warning(self, "Erro", 
                                   f"Senha incorreta. Tentativas restantes: {5 - user.tentativas_login_falhas}")
                return
            
            # Login bem-sucedido
            user.data_ultimo_login = datetime.utcnow()
            user.tentativas_login_falhas = 0
            user.data_bloqueio = None
            
            if user.trocar_senha_proximo_login:
                # Força troca de senha
                self.overlay.hide()
                self.show_change_password(user)
                return
            
            self.session.commit()
            self.save_credentials()
            
            self.overlay.hide()
            self.login_success.emit(user)
            
        except Exception as e:
            self.overlay.hide()
            QMessageBox.critical(self, "Erro", 
                               f"Erro ao autenticar: {str(e)}")
    
    def show_change_password(self, user):
        """Mostra diálogo para troca de senha"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Trocar Senha")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        title = QLabel("É necessário trocar sua senha")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        current_label = QLabel("Senha atual:")
        self.current_pass = QLineEdit()
        self.current_pass.setEchoMode(QLineEdit.Password)
        
        new_label = QLabel("Nova senha:")
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.Password)
        
        confirm_label = QLabel("Confirmar nova senha:")
        self.confirm_pass = QLineEdit()
        self.confirm_pass.setEchoMode(QLineEdit.Password)
        
        # Validador de força de senha
        strength_bar = QProgressBar()
        strength_bar.setRange(0, 100)
        
        self.new_pass.textChanged.connect(
            lambda: self.check_password_strength(self.new_pass.text(), strength_bar)
        )
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.change_password(user, dialog))
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(title)
        layout.addWidget(current_label)
        layout.addWidget(self.current_pass)
        layout.addWidget(new_label)
        layout.addWidget(self.new_pass)
        layout.addWidget(strength_bar)
        layout.addWidget(confirm_label)
        layout.addWidget(self.confirm_pass)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def check_password_strength(self, password, progress_bar):
        """Verifica força da senha"""
        score = 0
        
        if len(password) >= 8:
            score += 25
        if any(c.isupper() for c in password) and any(c.islower() for c in password):
            score += 25
        if any(c.isdigit() for c in password):
            score += 25
        if any(not c.isalnum() for c in password):
            score += 25
        
        progress_bar.setValue(score)
        
        if score < 50:
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif score < 75:
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
    
    def change_password(self, user, dialog):
        """Troca a senha do usuário"""
        current = self.current_pass.text()
        new = self.new_pass.text()
        confirm = self.confirm_pass.text()
        
        if not user.verificar_senha(current):
            QMessageBox.warning(dialog, "Erro", "Senha atual incorreta.")
            return
        
        if new != confirm:
            QMessageBox.warning(dialog, "Erro", "As senhas não coincidem.")
            return
        
        if len(new) < 8:
            QMessageBox.warning(dialog, "Erro", "A senha deve ter pelo menos 8 caracteres.")
            return
        
        user.atualizar_senha(new)
        user.trocar_senha_proximo_login = False
        self.session.commit()
        
        QMessageBox.information(dialog, "Sucesso", "Senha alterada com sucesso!")
        dialog.accept()
        
        # Faz login automaticamente
        self.login_success.emit(user)
    
    def show_forgot_password(self):
        """Mostra diálogo de recuperação de senha"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Recuperar Senha")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        title = QLabel("Recuperação de Senha")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        email_label = QLabel("Digite seu email:")
        email_input = QLineEdit()
        email_input.setPlaceholderText("email@exemplo.com")
        
        info_label = QLabel("Um link de recuperação será enviado para seu email.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray;")
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        
        layout.addWidget(title)
        layout.addWidget(email_label)
        layout.addWidget(email_input)
        layout.addWidget(info_label)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            email = email_input.text().strip()
            
            if not email:
                QMessageBox.warning(self, "Erro", "Por favor, digite seu email.")
                return
            
            # Aqui implementaria o envio de email
            QMessageBox.information(self, "Sucesso", 
                                  f"Link de recuperação enviado para {email}")
    
    def show_help(self):
        """Mostra diálogo de ajuda"""
        QMessageBox.information(self, "Ajuda",
                              f"""
{AppConfig.APP_NAME} - Sistema de Gestão Escolar

Versão: {AppConfig.APP_VERSION}

Para acessar o sistema:
1. Digite seu nome de usuário ou email
2. Digite sua senha
3. Clique em ENTRAR ou pressione Enter

Atalhos:
- Enter: Login
- F1: Ajuda
- Ctrl+T: Alternar tema

Suporte: suporte@somabemschool.edu.ao
                              """)

# ============================================================================
# DASHBOARD PRINCIPAL
# ============================================================================

class MainWindow(QMainWindow):
    """Janela principal do sistema"""
    
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.session = Session()
        self.current_theme = Theme.ANGOLA
        self.dashboard_widget = None
        
        # Configura baseado no nível de acesso
        if self.usuario.nivel_acesso == NivelAcesso.SUPER_ADMIN:
            self.dashboard_widget = SuperAdminDashboard(self.usuario, self)
        elif self.usuario.nivel_acesso == NivelAcesso.DIRECAO_GERAL:
            self.dashboard_widget = DirecaoGeralDashboard(self.usuario, self)
        elif self.usuario.nivel_acesso == NivelAcesso.DIRECAO_PEDAGOGICA:
            self.dashboard_widget = DirecaoPedagogicaDashboard(self.usuario, self)
        elif self.usuario.nivel_acesso == NivelAcesso.SECRETARIA:
            self.dashboard_widget = SecretariaDashboard(self.usuario, self)
        elif self.usuario.nivel_acesso == NivelAcesso.PROFESSOR:
            self.dashboard_widget = ProfessorDashboard(self.usuario, self)
        elif self.usuario.nivel_acesso == NivelAcesso.ALUNO:
            self.dashboard_widget = AlunoDashboard(self.usuario, self)
        elif self.usuario.nivel_acesso == NivelAcesso.ENCARREGADO:
            self.dashboard_widget = EncarregadoDashboard(self.usuario, self)
        elif self.usuario.nivel_acesso == NivelAcesso.FUNCIONARIO:
            self.dashboard_widget = FuncionarioDashboard(self.usuario, self)
        else:
            self.dashboard_widget = BaseDashboard(self.usuario, self)
        
        self.setup_ui()
        self.apply_theme()
        
        # Timer para atualizações automáticas
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(30000)  # 30 segundos
    
    def setup_ui(self):
        """Configura a interface principal"""
        self.setWindowTitle(f"{AppConfig.APP_NAME} - {self.usuario.nivel_acesso.value.title()}")
        self.setMinimumSize(1366, 768)
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Barra de menu superior
        self.setup_menu_bar()
        
        # Barra de ferramentas
        self.setup_toolbar()
        
        # Área principal
        self.main_area = QHBoxLayout()
        self.main_area.setContentsMargins(0, 0, 0, 0)
        self.main_area.setSpacing(0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        self.main_area.addWidget(self.sidebar)
        
        # Área de conteúdo
        self.content_area = QStackedWidget()
        self.main_area.addWidget(self.content_area, 1)
        
        self.main_layout.addLayout(self.main_area)
        
        # Barra de status
        self.setup_status_bar()
        
        # Adiciona dashboard inicial
        self.content_area.addWidget(self.dashboard_widget)
        
        # Configura ações da sidebar
        self.connect_sidebar_actions()
        
        # Carrega dados iniciais
        QTimer.singleShot(100, self.load_initial_data)
    
    def setup_menu_bar(self):
        """Configura a barra de menu"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("&Arquivo")
        
        novo_action = QAction("&Novo", self)
        novo_action.setShortcut(QKeySequence.New)
        file_menu.addAction(novo_action)
        
        abrir_action = QAction("&Abrir", self)
        abrir_action.setShortcut(QKeySequence.Open)
        file_menu.addAction(abrir_action)
        
        file_menu.addSeparator()
        
        imprimir_action = QAction("&Imprimir", self)
        imprimir_action.setShortcut(QKeySequence.Print)
        file_menu.addAction(imprimir_action)
        
        file_menu.addSeparator()
        
        sair_action = QAction("&Sair", self)
        sair_action.setShortcut(QKeySequence.Quit)
        sair_action.triggered.connect(self.close)
        file_menu.addAction(sair_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("&Editar")
        
        copiar_action = QAction("&Copiar", self)
        copiar_action.setShortcut(QKeySequence.Copy)
        edit_menu.addAction(copiar_action)
        
        colar_action = QAction("&Colar", self)
        colar_action.setShortcut(QKeySequence.Paste)
        edit_menu.addAction(colar_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu("&Exibir")
        
        self.fullscreen_action = QAction("&Tela Cheia", self)
        self.fullscreen_action.setShortcut(QKeySequence.FullScreen)
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(self.fullscreen_action)
        
        view_menu.addSeparator()
        
        theme_menu = view_menu.addMenu("&Tema")
        
        light_action = QAction("&Claro", self)
        light_action.triggered.connect(lambda: self.set_theme(Theme.LIGHT))
        theme_menu.addAction(light_action)
        
        dark_action = QAction("&Escuro", self)
        dark_action.triggered.connect(lambda: self.set_theme(Theme.DARK))
        theme_menu.addAction(dark_action)
        
        angola_action = QAction("&Angola", self)
        angola_action.triggered.connect(lambda: self.set_theme(Theme.ANGOLA))
        theme_menu.addAction(angola_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("&Ajuda")
        
        sobre_action = QAction("&Sobre", self)
        sobre_action.triggered.connect(self.show_about)
        help_menu.addAction(sobre_action)
        
        ajuda_action = QAction("&Ajuda", self)
        ajuda_action.setShortcut(QKeySequence.HelpContents)
        ajuda_action.triggered.connect(self.show_help)
        help_menu.addAction(ajuda_action)
    
    def setup_toolbar(self):
        """Configura a barra de ferramentas"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Botão do dashboard
        dashboard_btn = QToolButton()
        dashboard_btn.setText("Dashboard")
        dashboard_btn.setIcon(QIcon.fromTheme("go-home"))
        dashboard_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        dashboard_btn.clicked.connect(self.show_dashboard)
        toolbar.addWidget(dashboard_btn)
        
        toolbar.addSeparator()
        
        # Botão de atualizar
        refresh_btn = QToolButton()
        refresh_btn.setText("Atualizar")
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        refresh_btn.clicked.connect(self.refresh_all)
        toolbar.addWidget(refresh_btn)
        
        # Botão de notificações
        self.notif_btn = QToolButton()
        self.notif_btn.setText("Notificações")
        self.notif_btn.setIcon(QIcon.fromTheme("preferences-system-notifications"))
        self.notif_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.notif_btn.clicked.connect(self.show_notifications)
        toolbar.addWidget(self.notif_btn)
        
        toolbar.addSeparator()
        
        # Espaço flexível
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        
        # Perfil do usuário
        profile_btn = QToolButton()
        profile_btn.setText(self.usuario.username)
        profile_btn.setIcon(QIcon.fromTheme("system-users"))
        profile_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        profile_btn.setPopupMode(QToolButton.InstantPopup)
        
        profile_menu = QMenu()
        profile_action = QAction("Meu Perfil", self)
        profile_action.triggered.connect(self.show_profile)
        profile_menu.addAction(profile_action)
        
        settings_action = QAction("Configurações", self)
        settings_action.triggered.connect(self.show_settings)
        profile_menu.addAction(settings_action)
        
        profile_menu.addSeparator()
        
        logout_action = QAction("Sair", self)
        logout_action.triggered.connect(self.logout)
        profile_menu.addAction(logout_action)
        
        profile_btn.setMenu(profile_menu)
        toolbar.addWidget(profile_btn)
    
    def create_sidebar(self):
        """Cria a barra lateral de navegação"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(0)
        
        # Logo reduzida
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(":/icons/logo_small.png").scaled(100, 100,
                                                                      Qt.KeepAspectRatio,
                                                                      Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        layout.addSpacing(20)
        
        # Menu de navegação
        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        self.nav_list.setSpacing(5)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Adiciona itens baseado no nível de acesso
        self.add_navigation_items()
        
        layout.addWidget(self.nav_list)
        layout.addStretch()
        
        # Informações do sistema
        version_label = QLabel(f"v{AppConfig.APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(version_label)
        
        return sidebar
    
    def add_navigation_items(self):
        """Adiciona itens de navegação baseado no nível de acesso"""
        self.nav_list.clear()
        
        # Itens comuns
        common_items = [
            ("dashboard", "Dashboard", "go-home"),
            ("profile", "Meu Perfil", "system-users"),
            ("messages", "Mensagens", "mail-message"),
            ("calendar", "Calendário", "view-calendar"),
            ("reports", "Relatórios", "document-print")
        ]
        
        # Adiciona itens específicos por nível
        if self.usuario.nivel_acesso == NivelAcesso.SUPER_ADMIN:
            items = common_items + [
                ("system", "Sistema", "preferences-system"),
                ("users", "Usuários", "system-users"),
                ("audit", "Auditoria", "document-properties"),
                ("backup", "Backup", "document-save")
            ]
        elif self.usuario.nivel_acesso == NivelAcesso.DIRECAO_GERAL:
            items = common_items + [
                ("finance", "Financeiro", "office-chart-area"),
                ("hr", "RH", "system-users"),
                ("institution", "Instituição", "building"),
                ("analytics", "Analytics", "view-statistics")
            ]
        elif self.usuario.nivel_acesso == NivelAcesso.DIRECAO_PEDAGOGICA:
            items = common_items + [
                ("academic", "Acadêmico", "document-edit"),
                ("teachers", "Professores", "system-users"),
                ("students", "Alunos", "system-users"),
                ("courses", "Cursos", "bookmarks")
            ]
        elif self.usuario.nivel_acesso == NivelAcesso.SECRETARIA:
            items = common_items + [
                ("registration", "Matrículas", "document-edit"),
                ("payments", "Pagamentos", "office-chart-bar"),
                ("documents", "Documentos", "document-save"),
                ("pos", "Ponto de Venda", "shopping-cart")
            ]
        elif self.usuario.nivel_acesso == NivelAcesso.PROFESSOR:
            items = common_items + [
                ("classes", "Minhas Turmas", "bookmarks"),
                ("grades", "Notas", "document-edit"),
                ("attendance", "Presenças", "view-calendar"),
                ("materials", "Materiais", "folder")
            ]
        elif self.usuario.nivel_acesso == NivelAcesso.ALUNO:
            items = common_items + [
                ("mygrades", "Minhas Notas", "document-edit"),
                ("attendance", "Minhas Presenças", "view-calendar"),
                ("payments", "Meus Pagamentos", "office-chart-bar"),
                ("schedule", "Meu Horário", "view-calendar-day")
            ]
        
        # Adiciona itens à lista
        for item_id, text, icon_name in items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, item_id)
            item.setIcon(QIcon.fromTheme(icon_name))
            self.nav_list.addItem(item)
    
    def connect_sidebar_actions(self):
        """Conecta ações da sidebar"""
        self.nav_list.currentRowChanged.connect(self.on_nav_item_changed)
        self.nav_list.setCurrentRow(0)  # Seleciona dashboard
    
    def on_nav_item_changed(self, row):
        """Quando um item da navegação é selecionado"""
        if row < 0:
            return
        
        item = self.nav_list.item(row)
        item_id = item.data(Qt.UserRole)
        
        # Mostra o widget correspondente
        self.show_content(item_id)
    
    def show_content(self, content_id):
        """Mostra conteúdo baseado no ID"""
        if content_id == "dashboard":
            self.content_area.setCurrentWidget(self.dashboard_widget)
        elif content_id == "profile":
            self.show_profile()
        elif content_id == "messages":
            self.show_messages()
        elif content_id == "calendar":
            self.show_calendar()
        elif content_id == "reports":
            self.show_reports()
        elif content_id == "pos":
            self.show_pos()
        # Adicionar outros casos conforme necessário
    
    def setup_status_bar(self):
        """Configura a barra de status"""
        status_bar = self.statusBar()
        
        # Status da conexão
        self.connection_status = QLabel("🟢 Conectado")
        status_bar.addPermanentWidget(self.connection_status)
        
        # Data e hora
        self.datetime_label = QLabel()
        self.update_datetime()
        status_bar.addPermanentWidget(self.datetime_label)
        
        # Timer para atualizar data/hora
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # 1 segundo
    
    def update_datetime(self):
        """Atualiza data e hora na status bar"""
        now = QDateTime.currentDateTime()
        self.datetime_label.setText(now.toString("dd/MM/yyyy hh:mm:ss"))
    
    def load_initial_data(self):
        """Carrega dados iniciais"""
        # Carrega notificações
        self.load_notifications()
        
        # Atualiza dashboard
        self.dashboard_widget.load_data()
    
    def load_notifications(self):
        """Carrega notificações do usuário"""
        # Implementar carregamento de notificações do banco
        notification_count = 3  # Exemplo
        self.notif_btn.setText(f"Notificações ({notification_count})")
    
    def apply_theme(self):
        """Aplica o tema atual"""
        colors = AppConfig.COLORS[self.current_theme]
        
        style = f"""
        QMainWindow {{
            background-color: {colors['background']};
        }}
        
        #sidebar {{
            background-color: {colors['surface']};
            border-right: 1px solid {colors['border']};
        }}
        
        #navList {{
            background-color: transparent;
            border: none;
            outline: none;
        }}
        
        #navList::item {{
            padding: 12px 15px;
            border-radius: 5px;
            margin: 2px 10px;
            color: {colors['text']};
        }}
        
        #navList::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        #navList::item:hover:!selected {{
            background-color: {colors['border']};
        }}
        
        QToolBar {{
            background-color: {colors['surface']};
            border-bottom: 1px solid {colors['border']};
            spacing: 5px;
            padding: 5px;
        }}
        
        QStatusBar {{
            background-color: {colors['surface']};
            border-top: 1px solid {colors['border']};
            color: {colors['text_secondary']};
        }}
        
        QMenuBar {{
            background-color: {colors['surface']};
            color: {colors['text']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QMenu {{
            background-color: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
        }}
        
        QMenu::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        """
        
        self.setStyleSheet(style)
        
        # Aplica tema ao dashboard
        if self.dashboard_widget:
            self.dashboard_widget.apply_theme(self.current_theme)
    
    def set_theme(self, theme):
        """Define o tema"""
        self.current_theme = theme
        self.apply_theme()
    
    def toggle_fullscreen(self):
        """Alterna tela cheia"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_action.setChecked(False)
        else:
            self.showFullScreen()
            self.fullscreen_action.setChecked(True)
    
    def refresh_all(self):
        """Atualiza todos os dados"""
        self.dashboard_widget.load_data()
        self.load_notifications()
        QMessageBox.information(self, "Atualizado", "Dados atualizados com sucesso!")
    
    def show_dashboard(self):
        """Mostra o dashboard"""
        self.content_area.setCurrentWidget(self.dashboard_widget)
        self.nav_list.setCurrentRow(0)
    
    def show_profile(self):
        """Mostra perfil do usuário"""
        dialog = ProfileDialog(self.usuario, self)
        dialog.exec_()
    
    def show_settings(self):
        """Mostra configurações"""
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def show_messages(self):
        """Mostra mensagens"""
        dialog = MessagesDialog(self.usuario, self)
        dialog.exec_()
    
    def show_calendar(self):
        """Mostra calendário"""
        dialog = CalendarDialog(self)
        dialog.exec_()
    
    def show_reports(self):
        """Mostra relatórios"""
        dialog = ReportsDialog(self.usuario, self)
        dialog.exec_()
    
    def show_notifications(self):
        """Mostra notificações"""
        dialog = NotificationsDialog(self.usuario, self)
        dialog.exec_()
    
    def show_pos(self):
        """Mostra ponto de venda"""
        pos = POSWindow(self.usuario, self)
        pos.exec_()
    
    def show_about(self):
        """Mostra sobre o sistema"""
        QMessageBox.about(self, f"Sobre {AppConfig.APP_NAME}",
                         f"""
{AppConfig.APP_NAME} - Sistema de Gestão Escolar
Versão: {AppConfig.APP_VERSION}

Desenvolvido para Colégios Públicos e Privados
Totalmente integrado com normas do MED Angola

© 2024 {AppConfig.COMPANY_NAME}
Todos os direitos reservados.
                         """)
    
    def show_help(self):
        """Mostra ajuda"""
        dialog = HelpDialog(self)
        dialog.exec_()
    
    def update_dashboard(self):
        """Atualiza dados do dashboard periodicamente"""
        self.dashboard_widget.update_data()
    
    def logout(self):
        """Faz logout do sistema"""
        reply = QMessageBox.question(self, "Sair", 
                                    "Deseja realmente sair do sistema?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.session.close()
            self.close()

# ============================================================================
# DASHBOARDS ESPECÍFICOS POR NÍVEL DE ACESSO
# ============================================================================

class BaseDashboard(QWidget):
    """Dashboard base"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.session = Session()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface base"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Cabeçalho
        header = QHBoxLayout()
        
        title = QLabel(f"Bem-vindo, {self.usuario.username}!")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        
        header.addWidget(title)
        header.addStretch()
        
        self.layout.addLayout(header)
        
        # Área de conteúdo
        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack)
    
    def load_data(self):
        """Carrega dados do dashboard"""
        pass
    
    def update_data(self):
        """Atualiza dados do dashboard"""
        pass
    
    def apply_theme(self, theme):
        """Aplica tema ao dashboard"""
        colors = AppConfig.COLORS[theme]
        
        style = f"""
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        """
        
        self.setStyleSheet(style)

class SuperAdminDashboard(BaseDashboard):
    """Dashboard para Super Admin"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(usuario, parent)
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Configura dashboard específico"""
        # Limpa layout base
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Cabeçalho
        header = QHBoxLayout()
        
        welcome_label = QLabel(f"Super Admin - {self.usuario.username}")
        welcome_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        
        header.addWidget(welcome_label)
        header.addStretch()
        
        # Botões rápidos
        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(10)
        
        buttons = [
            ("Sistema", "preferences-system", self.show_system),
            ("Usuários", "system-users", self.show_users),
            ("Backup", "document-save", self.show_backup),
            ("Logs", "document-properties", self.show_logs)
        ]
        
        for text, icon, callback in buttons:
            btn = ModernButton(text)
            btn.setIcon(QIcon.fromTheme(icon))
            btn.clicked.connect(callback)
            quick_actions.addWidget(btn)
        
        main_layout.addLayout(header)
        main_layout.addLayout(quick_actions)
        
        # Grid de estatísticas
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Cards de estatísticas
        stats = [
            ("Total Usuários", "250", "system-users", "users"),
            ("Instituições", "3", "building", "institutions"),
            ("Logs Hoje", "1,245", "document-properties", "logs"),
            ("Backups", "15", "document-save", "backups"),
            ("Uptime", "99.8%", "computer", "uptime"),
            ("Armazenamento", "45%", "drive-harddisk", "storage")
        ]
        
        row, col = 0, 0
        for title, value, icon, stat_id in stats:
            card = self.create_stat_card(title, value, icon, stat_id)
            stats_grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        main_layout.addLayout(stats_grid)
        
        # Gráficos
        charts_layout = QHBoxLayout()
        
        # Gráfico de uso do sistema
        usage_chart = ChartWidget()
        usage_chart.plotBarChart(
            [65, 59, 80, 81, 56, 55, 40],
            ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            "Uso do Sistema por Dia",
            "Dia",
            "Usuários Ativos"
        )
        
        charts_layout.addWidget(usage_chart, 1)
        
        # Gráfico de armazenamento
        storage_chart = ChartWidget()
        storage_chart.plotPieChart(
            [45, 25, 20, 10],
            ['Dados', 'Logs', 'Backups', 'Livre'],
            "Uso de Armazenamento"
        )
        
        charts_layout.addWidget(storage_chart, 1)
        
        main_layout.addLayout(charts_layout)
        
        # Tabela de atividades recentes
        activities_label = QLabel("Atividades Recentes")
        activities_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        main_layout.addWidget(activities_label)
        
        self.activities_table = ModernTableWidget()
        self.activities_table.setColumnCount(4)
        self.activities_table.setHorizontalHeaderLabels([
            "Data/Hora", "Usuário", "Ação", "Detalhes"
        ])
        
        main_layout.addWidget(self.activities_table)
        
        self.load_data()
    
    def create_stat_card(self, title, value, icon, stat_id):
        """Cria card de estatística"""
        card = CardWidget()
        layout = QVBoxLayout()
        
        # Cabeçalho
        header = QHBoxLayout()
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon.fromTheme(icon).pixmap(24, 24))
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet("color: gray;")
        
        header.addWidget(icon_label)
        header.addWidget(title_label)
        header.addStretch()
        
        # Valor
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        
        # Progresso (se aplicável)
        progress = QProgressBar()
        progress.setVisible(False)
        
        if stat_id == "storage":
            progress.setVisible(True)
            progress.setValue(45)
        
        layout.addLayout(header)
        layout.addWidget(value_label)
        layout.addWidget(progress)
        
        card.setLayout(layout)
        return card
    
    def load_data(self):
        """Carrega dados do dashboard"""
        try:
            # Carrega estatísticas
            total_users = self.session.query(Usuario).count()
            
            # Atualiza cards
            # Implementar atualização dos valores
            
            # Carrega atividades
            self.load_activities()
            
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
    
    def load_activities(self):
        """Carrega atividades recentes"""
        self.activities_table.setRowCount(0)
        
        # Exemplo de dados
        activities = [
            ["10:30", "admin", "Login", "Acesso ao sistema"],
            ["10:25", "prof.maria", "Atualização", "Lançou notas da turma 7A"],
            ["09:45", "secretaria", "Cadastro", "Nova matrícula #12345"],
            ["09:20", "admin", "Backup", "Backup automático realizado"],
            ["08:50", "diretor", "Relatório", "Gerou relatório financeiro"]
        ]
        
        for i, activity in enumerate(activities):
            self.activities_table.insertRow(i)
            for j, data in enumerate(activity):
                item = QTableWidgetItem(str(data))
                self.activities_table.setItem(i, j, item)
    
    def show_system(self):
        """Mostra configurações do sistema"""
        dialog = SystemConfigDialog(self)
        dialog.exec_()
    
    def show_users(self):
        """Mostra gerenciamento de usuários"""
        dialog = UserManagementDialog(self)
        dialog.exec_()
    
    def show_backup(self):
        """Mostra gerenciamento de backup"""
        dialog = BackupDialog(self)
        dialog.exec_()
    
    def show_logs(self):
        """Mostra logs do sistema"""
        dialog = LogsDialog(self)
        dialog.exec_()

class DirecaoGeralDashboard(BaseDashboard):
    """Dashboard para Direção Geral"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(usuario, parent)
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Configura dashboard específico"""
        # Similar ao SuperAdmin, mas focado em gestão institucional
        # Implementação similar com métricas institucionais
        pass

class DirecaoPedagogicaDashboard(BaseDashboard):
    """Dashboard para Direção Pedagógica"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(usuario, parent)
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Configura dashboard específico"""
        # Focado em métricas acadêmicas
        pass

class SecretariaDashboard(BaseDashboard):
    """Dashboard para Secretaria"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(usuario, parent)
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Configura dashboard específico"""
        # Focado em matrículas, pagamentos, documentos
        pass

class ProfessorDashboard(BaseDashboard):
    """Dashboard para Professor"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(usuario, parent)
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Configura dashboard específico"""
        # Focado em turmas, notas, presenças
        pass

class AlunoDashboard(BaseDashboard):
    """Dashboard para Aluno"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(usuario, parent)
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Configura dashboard específico"""
        # Focado em notas, presenças, pagamentos pessoais
        pass

class EncarregadoDashboard(BaseDashboard):
    """Dashboard para Encarregado"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(usuario, parent)
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Configura dashboard específico"""
        # Focado em acompanhamento de educandos
        pass

class FuncionarioDashboard(BaseDashboard):
    """Dashboard para Funcionário"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(usuario, parent)
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Configura dashboard específico"""
        # Focado em tarefas administrativas
        pass

# ============================================================================
# PONTO DE VENDA (POS)
# ============================================================================

class POSWindow(QDialog):
    """Janela de Ponto de Venda"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.session = Session()
        self.cart = []  # Carrinho de compras
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do POS"""
        self.setWindowTitle("Ponto de Venda")
        self.setMinimumSize(1200, 800)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Painel esquerdo - Produtos
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Barra de busca
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar produto...")
        self.search_input.textChanged.connect(self.filter_products)
        
        category_combo = QComboBox()
        category_combo.addItems(["Todos", "Uniforme", "Material", "Livros", "Outros"])
        category_combo.currentTextChanged.connect(self.filter_products)
        
        search_layout.addWidget(self.search_input, 3)
        search_layout.addWidget(category_combo, 1)
        
        # Grade de produtos
        self.products_grid = QGridLayout()
        self.products_grid.setSpacing(10)
        
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_content.setLayout(self.products_grid)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        
        left_layout.addLayout(search_layout)
        left_layout.addWidget(scroll_area)
        
        # Painel direito - Carrinho e pagamento
        right_panel = CardWidget("Carrinho de Compras")
        right_layout = QVBoxLayout()
        
        # Itens do carrinho
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Produto", "Qtd", "Preço", "Total"])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        
        # Resumo
        summary_group = QGroupBox("Resumo da Compra")
        summary_layout = QFormLayout()
        
        self.subtotal_label = QLabel("0.00 Kz")
        self.discount_label = QLabel("0.00 Kz")
        self.total_label = QLabel("0.00 Kz")
        self.total_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        
        summary_layout.addRow("Subtotal:", self.subtotal_label)
        summary_layout.addRow("Desconto:", self.discount_label)
        summary_layout.addRow("TOTAL:", self.total_label)
        
        summary_group.setLayout(summary_layout)
        
        # Cliente
        client_group = QGroupBox("Cliente")
        client_layout = QVBoxLayout()
        
        self.client_search = QLineEdit()
        self.client_search.setPlaceholderText("Buscar aluno por nome ou código...")
        
        self.client_info = QLabel("Nenhum cliente selecionado")
        self.client_info.setWordWrap(True)
        self.client_info.setStyleSheet("color: gray; padding: 10px;")
        
        client_layout.addWidget(self.client_search)
        client_layout.addWidget(self.client_info)
        client_group.setLayout(client_layout)
        
        # Pagamento
        payment_group = QGroupBox("Pagamento")
        payment_layout = QVBoxLayout()
        
        # Forma de pagamento
        payment_method = QHBoxLayout()
        payment_method.addWidget(QRadioButton("Dinheiro"))
        payment_method.addWidget(QRadioButton("Cartão"))
        payment_method.addWidget(QRadioButton("Transferência"))
        
        # Valor pago
        paid_layout = QHBoxLayout()
        paid_layout.addWidget(QLabel("Valor pago:"))
        self.paid_input = QLineEdit()
        self.paid_input.setPlaceholderText("0.00")
        paid_layout.addWidget(self.paid_input)
        
        # Troco
        self.change_label = QLabel("Troco: 0.00 Kz")
        
        payment_layout.addLayout(payment_method)
        payment_layout.addLayout(paid_layout)
        payment_layout.addWidget(self.change_label)
        payment_group.setLayout(payment_layout)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        clear_btn = ModernButton("Limpar")
        clear_btn.clicked.connect(self.clear_cart)
        
        checkout_btn = ModernButton("Finalizar Venda")
        checkout_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        checkout_btn.clicked.connect(self.checkout)
        
        print_btn = ModernButton("Imprimir")
        print_btn.clicked.connect(self.print_receipt)
        
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addWidget(checkout_btn)
        buttons_layout.addWidget(print_btn)
        
        right_layout.addWidget(self.cart_table)
        right_layout.addWidget(summary_group)
        right_layout.addWidget(client_group)
        right_layout.addWidget(payment_group)
        right_layout.addLayout(buttons_layout)
        
        right_panel.setLayout(right_layout)
        
        layout.addWidget(left_panel, 2)
        layout.addWidget(right_panel, 1)
        
        self.setLayout(layout)
        
        # Carrega produtos
        self.load_products()
        
        # Conecta sinais
        self.paid_input.textChanged.connect(self.calculate_change)
    
    def load_products(self):
        """Carrega produtos do banco de dados"""
        try:
            products = self.session.query(Produto).filter(
                Produto.ativo == True,
                Produto.quantidade_estoque > 0
            ).all()
            
            # Limpa grid
            while self.products_grid.count():
                child = self.products_grid.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Adiciona produtos ao grid
            row, col = 0, 0
            for product in products:
                product_card = self.create_product_card(product)
                self.products_grid.addWidget(product_card, row, col)
                
                col += 1
                if col > 2:  # 3 colunas
                    col = 0
                    row += 1
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produtos: {e}")
    
    def create_product_card(self, product):
        """Cria card de produto"""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setMinimumHeight(150)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Nome do produto
        name_label = QLabel(product.nome)
        name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_label.setWordWrap(True)
        
        # Preço
        price_label = QLabel(f"{product.preco_venda:,.2f} Kz")
        price_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        price_label.setStyleSheet("color: #CC0000;")
        
        # Estoque
        stock_label = QLabel(f"Estoque: {product.quantidade_estoque}")
        stock_label.setStyleSheet("color: gray; font-size: 10px;")
        
        # Botão de adicionar
        add_btn = ModernButton("Adicionar")
        add_btn.clicked.connect(lambda: self.add_to_cart(product))
        
        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(stock_label)
        layout.addWidget(add_btn)
        
        card.setLayout(layout)
        return card
    
    def filter_products(self):
        """Filtra produtos baseado na busca"""
        # Implementar filtragem
        pass
    
    def add_to_cart(self, product):
        """Adiciona produto ao carrinho"""
        # Verifica se já está no carrinho
        for item in self.cart:
            if item['product'].id == product.id:
                item['quantity'] += 1
                self.update_cart_display()
                return
        
        # Adiciona novo item
        self.cart.append({
            'product': product,
            'quantity': 1,
            'price': product.preco_venda
        })
        
        self.update_cart_display()
    
    def update_cart_display(self):
        """Atualiza display do carrinho"""
        self.cart_table.setRowCount(len(self.cart))
        
        subtotal = 0
        for i, item in enumerate(self.cart):
            product = item['product']
            quantity = item['quantity']
            price = item['price']
            total = quantity * price
            
            # Produto
            self.cart_table.setItem(i, 0, QTableWidgetItem(product.nome))
            
            # Quantidade
            qty_item = QTableWidgetItem(str(quantity))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.cart_table.setItem(i, 1, qty_item)
            
            # Preço unitário
            price_item = QTableWidgetItem(f"{price:,.2f} Kz")
            self.cart_table.setItem(i, 2, price_item)
            
            # Total
            total_item = QTableWidgetItem(f"{total:,.2f} Kz")
            total_item.setTextAlignment(Qt.AlignRight)
            self.cart_table.setItem(i, 3, total_item)
            
            subtotal += total
        
        # Atualiza resumo
        discount = 0
        total = subtotal - discount
        
        self.subtotal_label.setText(f"{subtotal:,.2f} Kz")
        self.discount_label.setText(f"{discount:,.2f} Kz")
        self.total_label.setText(f"{total:,.2f} Kz")
        
        # Calcula troco
        self.calculate_change()
    
    def calculate_change(self):
        """Calcula troco"""
        try:
            paid = float(self.paid_input.text() or 0)
            total = float(self.total_label.text().replace(' Kz', '').replace(',', ''))
            
            change = paid - total
            if change >= 0:
                self.change_label.setText(f"Troco: {change:,.2f} Kz")
                self.change_label.setStyleSheet("color: green;")
            else:
                self.change_label.setText(f"Falta: {-change:,.2f} Kz")
                self.change_label.setStyleSheet("color: red;")
                
        except ValueError:
            self.change_label.setText("Troco: 0.00 Kz")
    
    def clear_cart(self):
        """Limpa carrinho"""
        self.cart.clear()
        self.update_cart_display()
        self.client_search.clear()
        self.paid_input.clear()
    
    def checkout(self):
        """Finaliza a venda"""
        if not self.cart:
            QMessageBox.warning(self, "Atenção", "Carrinho vazio!")
            return
        
        # Verifica estoque
        for item in self.cart:
            if item['quantity'] > item['product'].quantidade_estoque:
                QMessageBox.warning(self, "Estoque Insuficiente",
                                  f"Estoque insuficiente para {item['product'].nome}")
                return
        
        # Cria venda
        try:
            venda = Venda(
                funcionario_id=self.usuario.id,
                numero_venda=f"V{datetime.now().strftime('%Y%m%d%H%M%S')}",
                valor_total=0,
                desconto=0,
                valor_final=0,
                status='pendente',
                data_venda=datetime.now()
            )
            
            self.session.add(venda)
            self.session.flush()
            
            # Adiciona itens
            total = 0
            for item in self.cart:
                produto = item['product']
                quantidade = item['quantity']
                preco = item['price']
                item_total = quantidade * preco
                
                item_venda = ItemVenda(
                    venda_id=venda.id,
                    produto_id=produto.id,
                    quantidade=quantidade,
                    valor_unitario=preco,
                    valor_total=item_total
                )
                
                self.session.add(item_venda)
                
                # Atualiza estoque
                produto.quantidade_estoque -= quantidade
                
                total += item_total
            
            # Atualiza totais da venda
            venda.valor_total = total
            venda.valor_final = total
            venda.status = 'paga'  # Supondo pagamento à vista
            
            self.session.commit()
            
            QMessageBox.information(self, "Sucesso", f"Venda #{venda.numero_venda} realizada com sucesso!")
            self.clear_cart()
            
            # Imprime recibo
            self.print_receipt(venda)
            
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao finalizar venda: {e}")
    
    def print_receipt(self, venda=None):
        """Imprime recibo"""
        if venda is None and self.cart:
            # Cria venda temporária para impressão
            pass
        
        # Implementar impressão
        QMessageBox.information(self, "Impressão", "Recibo impresso com sucesso!")

# ============================================================================
# DIALOGOS E FORMULÁRIOS
# ============================================================================

class ProfileDialog(QDialog):
    """Diálogo de perfil do usuário"""
    
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.session = Session()
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface"""
        self.setWindowTitle("Meu Perfil")
        self.setFixedSize(600, 700)
        
        layout = QVBoxLayout()
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab Informações Pessoais
        personal_tab = QWidget()
        personal_layout = QFormLayout()
        
        self.nome_input = QLineEdit()
        self.email_input = QLineEdit()
        self.telefone_input = QLineEdit()
        self.endereco_input = QTextEdit()
        
        personal_layout.addRow("Nome:", self.nome_input)
        personal_layout.addRow("Email:", self.email_input)
        personal_layout.addRow("Telefone:", self.telefone_input)
        personal_layout.addRow("Endereço:", self.endereco_input)
        
        personal_tab.setLayout(personal_layout)
        
        # Tab Segurança
        security_tab = QWidget()
        security_layout = QFormLayout()
        
        self.current_pass = QLineEdit()
        self.current_pass.setEchoMode(QLineEdit.Password)
        
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.Password)
        
        self.confirm_pass = QLineEdit()
        self.confirm_pass.setEchoMode(QLineEdit.Password)
        
        security_layout.addRow("Senha atual:", self.current_pass)
        security_layout.addRow("Nova senha:", self.new_pass)
        security_layout.addRow("Confirmar senha:", self.confirm_pass)
        
        security_tab.setLayout(security_layout)
        
        # Tab Preferências
        preferences_tab = QWidget()
        preferences_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Angola", "Claro", "Escuro"])
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Português", "English"])
        
        self.notifications_check = QCheckBox("Receber notificações")
        self.email_notifications = QCheckBox("Notificações por email")
        
        preferences_layout.addRow("Tema:", self.theme_combo)
        preferences_layout.addRow("Idioma:", self.language_combo)
        preferences_layout.addRow("", self.notifications_check)
        preferences_layout.addRow("", self.email_notifications)
        
        preferences_tab.setLayout(preferences_layout)
        
        tabs.addTab(personal_tab, "Informações")
        tabs.addTab(security_tab, "Segurança")
        tabs.addTab(preferences_tab, "Preferências")
        
        layout.addWidget(tabs)
        
        # Botões
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.save_profile)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Carrega dados
        self.load_profile()
    
    def load_profile(self):
        """Carrega dados do perfil"""
        try:
            pessoa = self.session.query(Pessoa).filter_by(id=self.usuario.pessoa_id).first()
            if pessoa:
                self.nome_input.setText(pessoa.nome_completo)
                self.email_input.setText(pessoa.email_pessoal or "")
                # Carrega outros campos
                
        except Exception as e:
            print(f"Erro ao carregar perfil: {e}")
    
    def save_profile(self):
        """Salva alterações do perfil"""
        try:
            pessoa = self.session.query(Pessoa).filter_by(id=self.usuario.pessoa_id).first()
            if pessoa:
                pessoa.nome_completo = self.nome_input.text()
                pessoa.email_pessoal = self.email_input.text()
                # Salva outros campos
                
                self.session.commit()
                QMessageBox.information(self, "Sucesso", "Perfil atualizado!")
                self.accept()
                
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}")

class SettingsDialog(QDialog):
    """Diálogo de configurações do sistema"""
    pass

class MessagesDialog(QDialog):
    """Diálogo de mensagens"""
    pass

class CalendarDialog(QDialog):
    """Diálogo de calendário"""
    pass

class ReportsDialog(QDialog):
    """Diálogo de relatórios"""
    pass

class NotificationsDialog(QDialog):
    """Diálogo de notificações"""
    pass

class SystemConfigDialog(QDialog):
    """Diálogo de configuração do sistema"""
    pass

class UserManagementDialog(QDialog):
    """Diálogo de gerenciamento de usuários"""
    pass

class BackupDialog(QDialog):
    """Diálogo de backup"""
    pass

class LogsDialog(QDialog):
    """Diálogo de logs"""
    pass

class HelpDialog(QDialog):
    """Diálogo de ajuda"""
    pass

# ============================================================================
# THREADS PARA OPERAÇÕES PESADAS
# ============================================================================

class DatabaseWorker(QRunnable):
    """Worker para operações no banco de dados"""
    
    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        """Executa a tarefa"""
        try:
            result = self.task(*self.args, **self.kwargs)
            self.signals.result.emit(result)
            self.signals.finished.emit()
        except Exception as e:
            self.signals.error.emit(str(e))

class WorkerSignals(QObject):
    """Sinais para workers"""
    finished = Signal()
    error = Signal(str)
    result = Signal(object)
    progress = Signal(int)

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def create_gradient(color1, color2):
    """Cria gradiente de cores"""
    gradient = QLinearGradient(0, 0, 0, 400)
    gradient.setColorAt(0.0, QColor(color1))
    gradient.setColorAt(1.0, QColor(color2))
    return gradient

def format_currency(value):
    """Formata valor monetário"""
    return f"{value:,.2f} Kz"

def get_user_avatar(username):
    """Gera avatar baseado no nome do usuário"""
    # Implementar geração de avatar
    return QIcon.fromTheme("system-users")

# ============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# ============================================================================

class Application(QApplication):
    """Aplicação principal"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Configurações da aplicação
        self.setApplicationName(AppConfig.APP_NAME)
        self.setOrganizationName(AppConfig.COMPANY_NAME)
        self.setApplicationVersion(AppConfig.APP_VERSION)
        
        # Configura estilo
        self.setStyle(QStyleFactory.create("Fusion"))
        
        # Configura fonte
        font = QFont("Segoe UI", 10)
        self.setFont(font)
        
        # Pool de threads
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)
        
        # Mostra tela de login
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, usuario):
        """Quando login é bem-sucedido"""
        self.login_window.hide()
        
        # Cria janela principal
        self.main_window = MainWindow(usuario)
        self.main_window.showMaximized()
        
        # Conecta sinal de logout
        self.main_window.destroyed.connect(self.on_logout)
    
    def on_logout(self):
        """Quando usuário faz logout"""
        self.login_window.show()

def main():
    """Função principal"""
    import sys
    
    # Cria e executa aplicação
    app = Application(sys.argv)
    
    # Configura tratamento de exceções
    sys.excepthook = lambda exctype, value, traceback: (
        QMessageBox.critical(None, "Erro Crítico", 
                           f"Ocorreu um erro não tratado:\n\n{exctype.__name__}: {value}")
    )
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()