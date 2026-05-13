from __future__ import annotations

import copy
import json
import re
import sys
import uuid
from pathlib import Path

from PySide6.QtCore import QDir, Qt, QSize, Signal
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
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QPlainTextEdit,
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
EDITOR_SAVE_FILE = DATA_DIR / "editor_project.json"


def make_node(name: str, node_type: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "type": node_type,
        "position": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
        "obj_file": "",
        "script": "",
        "children": [],
    }


def make_document(name: str, kind: str) -> dict:
    root_name = "Scene Root" if kind == "scene" else "Class Root"
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "kind": kind,
        "nodes": [make_node(root_name, "Structure Node")],
    }


def safe_script_name(name: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_")
    return clean or "NodeScript"


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

        save_button = QPushButton("Save Code")
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
        current = self.current_file
        self.file_picker.clear()

        scripts = sorted(SCRIPTS_DIR.glob("*.py")) if SCRIPTS_DIR.exists() else []
        if not scripts:
            self.file_picker.addItem("Geen .py files gevonden", None)
        else:
            for script in scripts:
                self.file_picker.addItem(script.name, script)
                if current == script:
                    self.file_picker.setCurrentIndex(self.file_picker.count() - 1)

        self.file_picker.blockSignals(False)
        self.load_selected_script()

    def open_script(self, path: Path) -> None:
        self.refresh_scripts()
        for index in range(self.file_picker.count()):
            if self.file_picker.itemData(index) == path:
                self.file_picker.setCurrentIndex(index)
                return
        self.current_file = path
        self.editor.setPlainText(path.read_text(encoding="utf-8"))

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
        scene_label = QLabel("Actieve scene: opgeslagen in Game/data bij sluiten")
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
        sub_label = QLabel("Versie 2 bewaart scenes, classes, nodes en inspector-data.")
        sub_label.setObjectName("MutedText")
        viewport_layout.addWidget(label, alignment=Qt.AlignCenter)
        viewport_layout.addWidget(sub_label, alignment=Qt.AlignCenter)

        layout.addLayout(header)
        layout.addWidget(viewport, 1)


class SceneTabs(QWidget):
    selected_node_changed = Signal(object)
    script_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.documents: list[dict] = []
        self.copied_class_nodes: list[dict] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("Scenes / Classes")
        title.setObjectName("PanelTitle")

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)
        self.tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.customContextMenuRequested.connect(self.open_tab_menu)

        add_scene = QPushButton("+ Scene")
        add_scene.clicked.connect(lambda: self.add_document("scene"))
        add_class = QPushButton("+ Class")
        add_class.clicked.connect(lambda: self.add_document("class"))

        buttons = QHBoxLayout()
        buttons.addWidget(add_scene)
        buttons.addWidget(add_class)

        layout.addWidget(title)
        layout.addWidget(self.tabs, 1)
        layout.addLayout(buttons)

    def load_documents(self, documents: list[dict]) -> None:
        self.documents = documents or [
            make_document("game_play.scene", "scene"),
            make_document("Pickup.class", "class"),
        ]
        self.tabs.clear()
        for document in self.documents:
            self.tabs.addTab(self._make_tree(document), document["name"])

    def serialize(self) -> list[dict]:
        return self.documents

    def add_document(self, kind: str) -> None:
        number = len([doc for doc in self.documents if doc["kind"] == kind]) + 1
        suffix = "scene" if kind == "scene" else "class"
        name, ok = QInputDialog.getText(self, f"New {suffix}", "Name:", text=f"New{number}.{suffix}")
        if not ok or not name.strip():
            return

        document = make_document(name.strip(), kind)
        self.documents.append(document)
        self.tabs.addTab(self._make_tree(document), document["name"])
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def _make_tree(self, document: dict) -> QTreeWidget:
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setContextMenuPolicy(Qt.CustomContextMenu)
        tree.customContextMenuRequested.connect(lambda pos, widget=tree: self.open_node_menu(widget, pos))
        tree.itemSelectionChanged.connect(lambda widget=tree: self.emit_selected_node(widget))

        for node in document["nodes"]:
            tree.addTopLevelItem(self._node_to_item(node))
        tree.expandAll()
        return tree

    def _node_to_item(self, node: dict) -> QTreeWidgetItem:
        item = QTreeWidgetItem([node["name"]])
        item.setData(0, Qt.UserRole, node)
        for child in node.get("children", []):
            item.addChild(self._node_to_item(child))
        return item

    def current_document(self) -> dict | None:
        index = self.tabs.currentIndex()
        if 0 <= index < len(self.documents):
            return self.documents[index]
        return None

    def current_tree(self) -> QTreeWidget | None:
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, QTreeWidget) else None

    def emit_selected_node(self, tree: QTreeWidget) -> None:
        item = tree.currentItem()
        self.selected_node_changed.emit(item.data(0, Qt.UserRole) if item else None)

    def refresh_item_text(self, node: dict) -> None:
        tree = self.current_tree()
        if tree is None:
            return
        item = self.find_item_for_node(tree.invisibleRootItem(), node)
        if item is not None:
            item.setText(0, node["name"])

    def find_item_for_node(self, parent: QTreeWidgetItem, node: dict) -> QTreeWidgetItem | None:
        for index in range(parent.childCount()):
            child = parent.child(index)
            if child.data(0, Qt.UserRole) is node:
                return child
            found = self.find_item_for_node(child, node)
            if found is not None:
                return found
        return None

    def open_tab_menu(self, pos) -> None:
        index = self.tabs.tabBar().tabAt(pos)
        if index < 0:
            return

        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        action = menu.exec(self.tabs.mapToGlobal(pos))
        if action == rename_action:
            self.rename_document(index)

    def rename_document(self, index: int) -> None:
        document = self.documents[index]
        name, ok = QInputDialog.getText(self, "Rename", "Name:", text=document["name"])
        if not ok or not name.strip():
            return
        document["name"] = name.strip()
        self.tabs.setTabText(index, document["name"])

    def open_node_menu(self, tree: QTreeWidget, pos) -> None:
        document = self.current_document()
        if document is None:
            return

        item = tree.itemAt(pos) or tree.invisibleRootItem()
        item_node = item.data(0, Qt.UserRole) if item is not tree.invisibleRootItem() else None
        menu = QMenu(self)

        add_structure = menu.addAction("Add Structure Node")
        add_2d = menu.addAction("Add 2D Node")
        add_3d = menu.addAction("Add 3D Node")
        menu.addSeparator()
        rename_action = menu.addAction("Rename Node")
        rename_action.setEnabled(item_node is not None)
        script_action = menu.addAction("Create/Attach Script")
        script_action.setEnabled(item_node is not None)

        menu.addSeparator()
        copy_action = menu.addAction("Copy Class Nodes")
        copy_action.setEnabled(document["kind"] == "class" and item_node is not None)
        paste_action = menu.addAction("Paste Class Instance")
        paste_action.setEnabled(document["kind"] == "scene" and bool(self.copied_class_nodes))

        action = menu.exec(tree.viewport().mapToGlobal(pos))
        if action == add_structure:
            self.add_node(tree, item, "Structure Node")
        elif action == add_2d:
            self.add_node(tree, item, "2D Node")
        elif action == add_3d:
            self.add_node(tree, item, "3D Node")
        elif action == rename_action and item_node is not None:
            self.rename_node(item, item_node)
        elif action == copy_action and item_node is not None:
            self.copy_class_nodes(item_node)
        elif action == paste_action:
            self.paste_class_instance(tree, item)
        elif action == script_action and item_node is not None:
            self.create_script_for_node(item_node)

    def add_node(self, tree: QTreeWidget, parent_item: QTreeWidgetItem, node_type: str) -> None:
        node = make_node(node_type, node_type)
        node["name"] = self.unique_child_name(parent_item, node_type)

        if parent_item is tree.invisibleRootItem():
            document = self.current_document()
            if document is None:
                return
            document["nodes"].append(node)
            tree.addTopLevelItem(self._node_to_item(node))
        else:
            parent_node = parent_item.data(0, Qt.UserRole)
            parent_node.setdefault("children", []).append(node)
            parent_item.addChild(self._node_to_item(node))
            parent_item.setExpanded(True)

    def unique_child_name(self, parent_item: QTreeWidgetItem, base: str) -> str:
        names = {parent_item.child(index).text(0) for index in range(parent_item.childCount())}
        if base not in names:
            return base
        number = 2
        while f"{base} {number}" in names:
            number += 1
        return f"{base} {number}"

    def rename_node(self, item: QTreeWidgetItem, node: dict) -> None:
        name, ok = QInputDialog.getText(self, "Rename Node", "Name:", text=node["name"])
        if not ok or not name.strip():
            return
        node["name"] = name.strip()
        item.setText(0, node["name"])
        self.selected_node_changed.emit(node)

    def copy_class_nodes(self, node: dict) -> None:
        self.copied_class_nodes = [copy.deepcopy(node)]

    def paste_class_instance(self, tree: QTreeWidget, parent_item: QTreeWidgetItem) -> None:
        if not self.copied_class_nodes:
            return

        copies = copy.deepcopy(self.copied_class_nodes)
        for node in copies:
            self.refresh_ids(node)
            node["name"] = f"{node['name']} Instance"

            if parent_item is tree.invisibleRootItem():
                document = self.current_document()
                if document is not None:
                    document["nodes"].append(node)
                    tree.addTopLevelItem(self._node_to_item(node))
            else:
                parent_node = parent_item.data(0, Qt.UserRole)
                parent_node.setdefault("children", []).append(node)
                parent_item.addChild(self._node_to_item(node))
                parent_item.setExpanded(True)

    def refresh_ids(self, node: dict) -> None:
        node["id"] = str(uuid.uuid4())
        for child in node.get("children", []):
            self.refresh_ids(child)

    def create_script_for_node(self, node: dict) -> None:
        SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
        script_name = safe_script_name(node["name"])
        script_path = SCRIPTS_DIR / f"{script_name}.py"
        if not script_path.exists():
            script_path.write_text(
                f"class {script_name}:\n"
                "    def __init__(self):\n"
                "        self.node = None\n\n"
                "    def update(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
        node["script"] = str(script_path.relative_to(ROOT_DIR)).replace("\\", "/")
        self.selected_node_changed.emit(node)
        self.script_requested.emit(str(script_path))


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
    node_changed = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.current_node: dict | None = None
        self.loading = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("Inspector")
        title.setObjectName("PanelTitle")

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)

        self.name = QLineEdit()
        self.node_type = QComboBox()
        self.node_type.addItems(["Structure Node", "2D Node", "3D Node"])
        self.position = [QLineEdit(), QLineEdit(), QLineEdit()]
        self.rotation = [QLineEdit(), QLineEdit(), QLineEdit()]
        self.scale = [QLineEdit(), QLineEdit(), QLineEdit()]
        self.obj_file = QLineEdit()
        self.script = QLineEdit()

        form.addRow("Name", self.name)
        form.addRow("Type", self.node_type)
        form.addRow("Position X", self.position[0])
        form.addRow("Position Y", self.position[1])
        form.addRow("Position Z", self.position[2])
        form.addRow("Rotation X", self.rotation[0])
        form.addRow("Rotation Y", self.rotation[1])
        form.addRow("Rotation Z", self.rotation[2])
        form.addRow("Scale X", self.scale[0])
        form.addRow("Scale Y", self.scale[1])
        form.addRow("Scale Z", self.scale[2])
        form.addRow("OBJ file", self.obj_file)
        form.addRow("Script", self.script)

        for widget in [self.name, self.obj_file, self.script, *self.position, *self.rotation, *self.scale]:
            widget.editingFinished.connect(self.apply_to_node)
        self.node_type.currentTextChanged.connect(self.apply_to_node)

        note = QLabel("Selecteer een node. Waardes worden bewaard in Game/data/editor_project.json.")
        note.setWordWrap(True)
        note.setObjectName("MutedText")

        layout.addWidget(title)
        layout.addLayout(form)
        layout.addWidget(note)
        layout.addStretch(1)
        self.set_node(None)

    def set_node(self, node: dict | None) -> None:
        self.current_node = node
        self.loading = True
        enabled = node is not None

        for widget in [self.name, self.obj_file, self.script, *self.position, *self.rotation, *self.scale]:
            widget.setEnabled(enabled)
        self.node_type.setEnabled(enabled)

        if node is None:
            self.name.setText("Geen node geselecteerd")
            self.node_type.setCurrentIndex(0)
            for values, default in [(self.position, "0"), (self.rotation, "0"), (self.scale, "1")]:
                for widget in values:
                    widget.setText(default)
            self.obj_file.setText("")
            self.script.setText("")
        else:
            self.name.setText(node.get("name", "Node"))
            self.node_type.setCurrentText(node.get("type", "Structure Node"))
            self.set_vector(self.position, node.get("position", [0, 0, 0]))
            self.set_vector(self.rotation, node.get("rotation", [0, 0, 0]))
            self.set_vector(self.scale, node.get("scale", [1, 1, 1]))
            self.obj_file.setText(node.get("obj_file", ""))
            self.script.setText(node.get("script", ""))

        self.loading = False

    def set_vector(self, widgets: list[QLineEdit], values: list[float]) -> None:
        for widget, value in zip(widgets, values):
            widget.setText(str(value))

    def read_vector(self, widgets: list[QLineEdit], fallback: list[float]) -> list[float]:
        result = []
        for index, widget in enumerate(widgets):
            try:
                result.append(float(widget.text()))
            except ValueError:
                result.append(float(fallback[index]))
                widget.setText(str(fallback[index]))
        return result

    def apply_to_node(self) -> None:
        if self.loading or self.current_node is None:
            return

        node = self.current_node
        node["name"] = self.name.text().strip() or "Node"
        node["type"] = self.node_type.currentText()
        node["position"] = self.read_vector(self.position, node.get("position", [0, 0, 0]))
        node["rotation"] = self.read_vector(self.rotation, node.get("rotation", [0, 0, 0]))
        node["scale"] = self.read_vector(self.scale, node.get("scale", [1, 1, 1]))
        node["obj_file"] = self.obj_file.text().strip()
        node["script"] = self.script.text().strip()
        self.node_changed.emit(node)


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
        toolbar.addAction(QAction("Play", self))
        self.addToolBar(toolbar)

        self.scene_tabs = SceneTabs()
        self.inspector = Inspector()
        self.scene_tabs.selected_node_changed.connect(self.inspector.set_node)
        self.scene_tabs.script_requested.connect(self.open_script_from_path)
        self.inspector.node_changed.connect(self.scene_tabs.refresh_item_text)

        left_splitter = QSplitter(Qt.Vertical)
        left_splitter.addWidget(self.scene_tabs)
        left_splitter.addWidget(FileExplorer())
        left_splitter.setSizes([420, 260])

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.stack)
        main_splitter.addWidget(self.inspector)
        main_splitter.setSizes([310, 680, 290])

        self.setCentralWidget(main_splitter)
        self.apply_theme()
        self.load_editor_data()

    def load_editor_data(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if EDITOR_SAVE_FILE.exists():
            data = json.loads(EDITOR_SAVE_FILE.read_text(encoding="utf-8"))
            self.scene_tabs.load_documents(data.get("documents", []))
        else:
            self.scene_tabs.load_documents([])

    def save_editor_data(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "version": 2,
            "documents": self.scene_tabs.serialize(),
        }
        EDITOR_SAVE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.code_editor.save_current_script()

    def closeEvent(self, event) -> None:
        self.save_editor_data()
        super().closeEvent(event)

    def open_script_from_path(self, path_text: str) -> None:
        self.code_editor.open_script(Path(path_text))
        self.code_button.setChecked(True)
        self.stack.setCurrentIndex(1)

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
            QLineEdit:disabled, QComboBox:disabled {
                color: #6f7785;
                background: #151820;
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
