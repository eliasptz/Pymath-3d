from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QDir, Qt, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QFileSystemModel,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
GAME_DIR = ROOT_DIR / "Game"
SCRIPTS_DIR = GAME_DIR / "Scripts"
ASSETS_DIR = GAME_DIR / "Assets"
DATA_DIR = GAME_DIR / "data"


class ScriptEditor(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_file: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        top_bar = QHBoxLayout()
        title = QLabel("Code")
        title.setObjectName("PanelTitle")
        self.file_picker = QComboBox()
        self.file_picker.setMinimumWidth(260)
        self.file_picker.currentIndexChanged.connect(self.load_selected_script)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_current_script)

        top_bar.addWidget(title)
        top_bar.addStretch(1)
        top_bar.addWidget(QLabel("Game/Scripts"))
        top_bar.addWidget(self.file_picker)
        top_bar.addWidget(save_button)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Kies een .py bestand uit Game/Scripts.")
        self.editor.setObjectName("CodeEditor")

        layout.addLayout(top_bar)
        layout.addWidget(self.editor)
        self.refresh_scripts()

    def refresh_scripts(self) -> None:
        self.file_picker.blockSignals(True)
        self.file_picker.clear()

        scripts = sorted(SCRIPTS_DIR.glob("*.py")) if SCRIPTS_DIR.exists() else []
        if not scripts:
            self.file_picker.addItem("Geen .py files gevonden", None)
        else:
            for script in scripts:
                self.file_picker.addItem(script.name, script)

        self.file_picker.blockSignals(False)
        self.load_selected_script()

    def load_selected_script(self) -> None:
        path = self.file_picker.currentData()
        if not path:
            self.current_file = None
            self.editor.setPlainText("")
            return

        self.current_file = Path(path)
        self.editor.setPlainText(self.current_file.read_text(encoding="utf-8"))

    def save_current_script(self) -> None:
        if self.current_file is None:
            return
        self.current_file.write_text(self.editor.toPlainText(), encoding="utf-8")


class ViewportPlaceholder(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("Viewport")
        title.setObjectName("PanelTitle")
        scene_label = QLabel("Actieve scene: nog geen scene gekozen")
        scene_label.setObjectName("MutedText")
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(scene_label)

        viewport = QFrame()
        viewport.setObjectName("ViewportFrame")
        viewport_layout = QVBoxLayout(viewport)
        viewport_layout.setAlignment(Qt.AlignCenter)

        label = QLabel("Pygame engine preview komt hier")
        label.setObjectName("ViewportTitle")
        sub_label = QLabel("Versie 1 bouwt eerst de editor-layout en panelen.")
        sub_label.setObjectName("MutedText")
        viewport_layout.addWidget(label, alignment=Qt.AlignCenter)
        viewport_layout.addWidget(sub_label, alignment=Qt.AlignCenter)

        layout.addLayout(header)
        layout.addWidget(viewport, 1)


class SceneTabs(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Scenes / Classes")
        title.setObjectName("PanelTitle")

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.addTab(self._make_tree("scene"), "game_play.scene")
        self.tabs.addTab(self._make_tree("class"), "Pickup.class")

        add_scene = QPushButton("+ Scene")
        add_scene.clicked.connect(lambda: self.add_tab("scene"))
        add_class = QPushButton("+ Class")
        add_class.clicked.connect(lambda: self.add_tab("class"))

        buttons = QHBoxLayout()
        buttons.addWidget(add_scene)
        buttons.addWidget(add_class)

        layout.addWidget(title)
        layout.addWidget(self.tabs, 1)
        layout.addLayout(buttons)

    def _make_tree(self, kind: str) -> QTreeWidget:
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setContextMenuPolicy(Qt.CustomContextMenu)
        tree.customContextMenuRequested.connect(
            lambda pos, widget=tree, tab_kind=kind: self.open_node_menu(widget, tab_kind, pos)
        )

        root_name = "Scene Root" if kind == "scene" else "Class Root"
        root = QTreeWidgetItem([root_name])
        root.setData(0, Qt.UserRole, kind)
        tree.addTopLevelItem(root)
        root.setExpanded(True)
        return tree

    def add_tab(self, kind: str) -> None:
        number = self.tabs.count() + 1
        suffix = "scene" if kind == "scene" else "class"
        self.tabs.addTab(self._make_tree(kind), f"New{number}.{suffix}")
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def open_node_menu(self, tree: QTreeWidget, kind: str, pos) -> None:
        item = tree.itemAt(pos) or tree.invisibleRootItem()
        menu = QMenu(self)

        add_structure = menu.addAction("Add Structure Node")
        add_2d = menu.addAction("Add 2D Node")
        add_3d = menu.addAction("Add 3D Node")
        menu.addSeparator()
        copy_action = menu.addAction("Copy Class Nodes")
        copy_action.setEnabled(kind == "class")

        action = menu.exec(tree.viewport().mapToGlobal(pos))
        if action == add_structure:
            self.add_node(item, "Structure Node")
        elif action == add_2d:
            self.add_node(item, "2D Node")
        elif action == add_3d:
            self.add_node(item, "3D Node")

    def add_node(self, parent: QTreeWidgetItem, node_type: str) -> None:
        if parent is parent.treeWidget().invisibleRootItem():
            parent = parent.treeWidget().topLevelItem(0)

        node = QTreeWidgetItem([node_type])
        node.setData(0, Qt.UserRole, node_type)
        parent.addChild(node)
        parent.setExpanded(True)


class FileExplorer(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("File Explorer")
        title.setObjectName("PanelTitle")

        self.model = QFileSystemModel(self)
        self.model.setRootPath(str(GAME_DIR))
        self.model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Game"])
        self.tree.header().setSectionResizeMode(QHeaderView.Stretch)
        self.populate_tree()

        layout.addWidget(title)
        layout.addWidget(self.tree, 1)

    def populate_tree(self) -> None:
        self.tree.clear()
        root = QTreeWidgetItem(["Game"])
        self.tree.addTopLevelItem(root)
        self._add_path(root, GAME_DIR)
        root.setExpanded(True)

    def _add_path(self, parent: QTreeWidgetItem, path: Path) -> None:
        if not path.exists():
            return

        for child in sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower())):
            item = QTreeWidgetItem([child.name])
            parent.addChild(item)
            if child.is_dir():
                self._add_path(item, child)


class Inspector(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Inspector")
        title.setObjectName("PanelTitle")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        self.name = QLineEdit("Geen node geselecteerd")
        self.node_type = QComboBox()
        self.node_type.addItems(["Structure Node", "2D Node", "3D Node"])

        form.addRow("Name", self.name)
        form.addRow("Type", self.node_type)
        form.addRow("Position X", QLineEdit("0"))
        form.addRow("Position Y", QLineEdit("0"))
        form.addRow("Position Z", QLineEdit("0"))
        form.addRow("Rotation X", QLineEdit("0"))
        form.addRow("Rotation Y", QLineEdit("0"))
        form.addRow("Rotation Z", QLineEdit("0"))
        form.addRow("Scale X", QLineEdit("1"))
        form.addRow("Scale Y", QLineEdit("1"))
        form.addRow("Scale Z", QLineEdit("1"))
        form.addRow("OBJ file", QLineEdit("Game/Assets/..."))

        note = QLabel("Hier komt later live node data, save state en engine sync.")
        note.setWordWrap(True)
        note.setObjectName("MutedText")

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(note)
        layout.addStretch(1)


class EditorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Pymath 3D Editor")
        self.resize(1280, 760)
        self.setMinimumSize(QSize(980, 620))

        self.stack = QStackedWidget()
        self.viewport = ViewportPlaceholder()
        self.code_editor = ScriptEditor()
        self.stack.addWidget(self.viewport)
        self.stack.addWidget(self.code_editor)

        self.viewer_button = QPushButton("Viewer")
        self.code_button = QPushButton("Code")
        self.viewer_button.setCheckable(True)
        self.code_button.setCheckable(True)
        self.viewer_button.setChecked(True)

        group = QButtonGroup(self)
        group.addButton(self.viewer_button, 0)
        group.addButton(self.code_button, 1)
        group.idClicked.connect(self.switch_mode)

        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        toolbar.addWidget(QLabel("  Pymath 3D  "))
        toolbar.addSeparator()
        toolbar.addWidget(self.viewer_button)
        toolbar.addWidget(self.code_button)
        toolbar.addSeparator()
        toolbar.addAction(QAction("New Scene", self))
        toolbar.addAction(QAction("New Class", self))
        toolbar.addAction(QAction("Save", self))
        toolbar.addAction(QAction("Play", self))
        self.addToolBar(toolbar)

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(SceneTabs())
        left_splitter.addWidget(FileExplorer())
        left_splitter.setSizes([420, 260])

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.stack)
        main_splitter.addWidget(Inspector())
        main_splitter.setSizes([310, 680, 290])

        self.setCentralWidget(main_splitter)
        self.apply_theme()

    def switch_mode(self, mode_id: int) -> None:
        self.stack.setCurrentIndex(1 if mode_id == 1 else 0)

    def apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #191b20;
                color: #d9dee7;
                font-family: Segoe UI, Arial;
                font-size: 10pt;
            }
            QToolBar {
                background: #20242b;
                border-bottom: 1px solid #303640;
                spacing: 6px;
                padding: 6px;
            }
            QPushButton {
                background: #2a3039;
                border: 1px solid #3a4350;
                border-radius: 4px;
                padding: 6px 10px;
            }
            QPushButton:hover {
                background: #343c47;
            }
            QPushButton:checked {
                background: #3f6fb5;
                border-color: #6f9ee5;
            }
            QTabWidget::pane {
                border: 1px solid #303640;
                background: #1f232a;
            }
            QTabBar::tab {
                background: #252a32;
                border: 1px solid #303640;
                padding: 6px 10px;
            }
            QTabBar::tab:selected {
                background: #303744;
                border-bottom-color: #303744;
            }
            QTreeWidget, QPlainTextEdit, QLineEdit, QComboBox {
                background: #111318;
                border: 1px solid #303640;
                color: #e7ebf2;
                selection-background-color: #3f6fb5;
                selection-color: white;
            }
            QPlainTextEdit#CodeEditor {
                font-family: Consolas, Cascadia Mono, monospace;
                font-size: 11pt;
                padding: 8px;
            }
            QFrame#ViewportFrame {
                background: #0d1015;
                border: 1px solid #303640;
            }
            QLabel#PanelTitle {
                font-size: 11pt;
                font-weight: 600;
                color: #ffffff;
            }
            QLabel#ViewportTitle {
                font-size: 18pt;
                font-weight: 600;
                color: #ffffff;
            }
            QLabel#MutedText {
                color: #9aa6b8;
            }
            QSplitter::handle {
                background: #252a32;
            }
            """
        )


def main() -> None:
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
