# Plan voor de Python 3D Game Editor

## Doel

We bouwen een aparte editor-app voor je bestaande Python 3D engine. De editor moet projecten kunnen beheren, code kunnen openen en bewerken, scenes kunnen maken, nodes in scenes tonen, properties aanpassen via een inspector, assets beheren via een filesysteem-paneel, en een render viewport tonen waarin je de scene ziet.

Belangrijk: dit plan is nog geen implementatie. Eerst bepalen we de structuur, daarna bouwen we stap voor stap.

## Voorstel bibliotheken

### UI framework

Aanbevolen: PySide6

Waarom:
- Goede desktop-app basis.
- Tabs, panels, dock widgets, tree views en text editors zijn standaard mogelijk.
- Past goed bij een editor zoals Godot, Unity of Blender.
- Werkt beter voor grote tools dan simpele GUI libraries.

Alternatief:
- PyQt6: bijna hetzelfde als PySide6.
- Dear PyGui: sneller voor tool-achtige UI, maar minder klassiek desktopgevoel.
- Tkinter: standaard in Python, maar te beperkt voor een moderne game editor.

### Code editor

Start simpel met `QPlainTextEdit`.

Later uitbreiden met:
- line numbers
- syntax highlighting
- meerdere geopende code files
- save status per tab
- zoek/vervang

### 3D viewport

Keuze hangt af van je bestaande engine.

Mogelijke opties:
- De editor embedt de render output van je eigen engine.
- De editor gebruikt een apart OpenGL widget voor preview.
- De editor start de engine-preview als apart proces en toont/communiceert ermee.

Voor de eerste versie kiezen we de simpelste koppeling die bij je engine past.

## Hoofdonderdelen

## 1. Projectstructuur

Voorgestelde mappen:

```text
Pymath 3d/
  Editor/
    Editor.py
    plan.markdown
    ui/
    core/
    scene/
    assets/
    code_editor/
    viewport/
  projects/
```

Editor modules:

```text
Editor/
  Editor.py
  core/
    project.py
    event_bus.py
  scene/
    scene_model.py
    node_model.py
    scene_tabs.py
    hierarchy.py
    inspector.py
  assets/
    file_browser.py
    asset_registry.py
  code_editor/
    code_tabs.py
    python_highlighter.py
  viewport/
    render_viewport.py
```

## 2. Scene systeem

Een scene is een bestand waarin nodes staan.

Voorbeeld:

```json
{
  "name": "StartScreen",
  "nodes": [
    {
      "id": "node_001",
      "name": "Player",
      "class": "Player",
      "position": [0, 0, 0],
      "rotation": [0, 0, 0],
      "scale": [1, 1, 1],
      "mesh": "assets/models/player.obj"
    }
  ]
}
```

Scenes worden tabs bovenaan, zoals browser-tabs:
- StartScreen
- Game
- GameOver
- Level1

Je moet later vanuit code of engine kunnen springen naar een scene.

## 3. Nodes

Een node is een object in een scene.

Basis-properties:
- naam
- unieke id
- class/type
- x, y, z
- rotation x, y, z
- scale x, y, z
- `.obj` model path
- eventueel parent/child relatie

Editor functies:
- node aanmaken
- node selecteren
- node dupliceren
- node verwijderen
- node hernoemen
- node zichtbaar maken in hierarchy
- node properties aanpassen in inspector

## 4. Inspector

De inspector toont de geselecteerde node.

Velden:
- Name
- Class
- Position X/Y/Z
- Rotation X/Y/Z
- Scale X/Y/Z
- OBJ file

Gedrag:
- Als je een node selecteert, vult de inspector automatisch.
- Als je een waarde verandert, past de scene-data direct aan.
- Later kan de viewport live updaten.

## 5. Render viewport

De render viewport toont de actieve scene.

Eerste versie:
- viewport-paneel met placeholder of simpele engine-preview
- actieve scene naam zichtbaar
- geselecteerde node kan later highlighted worden

Latere versie:
- camera controls
- selecteren met muis
- drag/move gizmo
- object preview uit `.obj`
- play knop om scene in engine te starten

## 6. Filesysteem

Een file browser toont projectbestanden.

Moet tonen:
- scenes
- scripts
- classes
- models
- textures
- andere assets

Acties:
- file openen
- nieuwe file maken
- map maken
- bestand hernoemen
- bestand verwijderen, later met bevestiging
- `.obj` naar inspector kunnen slepen
- class naar scene kunnen slepen om instance te maken

## 7. Code files editen

Code editor tabs:
- meerdere bestanden tegelijk open
- Python code bewerken
- opslaan
- nieuw script maken
- eventueel auto-save later

Eerste versie:
- openen vanuit file browser
- editten
- opslaan met Ctrl+S

Latere versie:
- syntax highlighting
- line numbers
- error markers
- zoeken
- jump to class

## 8. Classes en instances

Naast scenes moet je classes kunnen maken.

Concept:
- Een class is een script/template.
- Je kan er instances van maken in een scene.
- Dat kan door te slepen vanuit het filesysteem/class-paneel.
- In code moet je ook instances kunnen aanmaken.

Voorbeeld class bestand:

```python
class Enemy:
    def __init__(self):
        self.position = [0, 0, 0]
        self.mesh = "assets/models/enemy.obj"
```

Voorbeeld instance in scene:

```json
{
  "name": "Enemy01",
  "class": "Enemy",
  "position": [4, 0, 2],
  "mesh": "assets/models/enemy.obj"
}
```

## 9. Editor layout

Voorgestelde layout:

```text
+-------------------------------------------------------------+
| Menu / Toolbar: New Scene | Save | Play | Stop              |
+-------------------+-----------------------------+-----------+
| File System       | Scene Tabs                  | Inspector |
|                   | +-------------------------+ |           |
|                   | | Render Viewport         | | Node data |
|                   | |                         | | x y z     |
|                   | +-------------------------+ | .obj      |
|                   | Code Tabs / Output Console  |           |
+-------------------+-----------------------------+-----------+
```

## 10. Data bestanden

Voorstel:

```text
project.json
scenes/
  StartScreen.scene.json
  Game.scene.json
  GameOver.scene.json
scripts/
  Player.py
  Enemy.py
assets/
  models/
    player.obj
  textures/
```

## 11. Bouwvolgorde

### Fase 1: Editor skelet

- PySide6 app starten.
- Main window maken.
- Dock panels maken:
  - File System
  - Scene Hierarchy
  - Inspector
  - Viewport
  - Code Editor
- Nog geen echte engine-koppeling.

### Fase 2: Project en files

- Projectmap herkennen.
- File browser vullen.
- Code files openen.
- Code files opslaan.

### Fase 3: Scene tabs

- Nieuwe scene maken.
- Scene opslaan als JSON.
- Scene openen.
- Meerdere scenes als tabs tonen.

### Fase 4: Nodes

- Node model maken.
- Node toevoegen aan scene.
- Scene hierarchy tonen.
- Node selecteren.

### Fase 5: Inspector

- Node properties tonen.
- X/Y/Z aanpassen.
- OBJ file koppelen.
- Data direct opslaan of dirty-state markeren.

### Fase 6: Classes

- Nieuwe class/script maken.
- Class lijst tonen.
- Class instance maken in actieve scene.
- Drag & drop voorbereiden.

### Fase 7: Viewport koppeling

- Render viewport verbinden met je engine.
- Actieve scene naar engine-preview sturen.
- Node transforms zichtbaar maken.

### Fase 8: Play mode

- Play knop.
- Stop knop.
- Start actieve scene in je engine.
- Scene switching testen.

## 12. Grill Me vragen

Dit is de stap waarin Codex jou eerst veel vragen stelt voordat er gebouwd wordt. De antwoorden komen daarna terug in dit plan, zodat de editor precies past bij jouw engine en jouw manier van werken.

### A. Engine koppeling

1. Hoe heet je bestaande engine main file?
2. Hoe start je engine nu een scene?
3. Gebruikt je engine OpenGL, pygame, panda3d, moderngl, ursina, of iets anders?
4. Hoe laad je nu `.obj` bestanden?
5. Heeft je engine al een eigen Scene class?
6. Heeft je engine al een eigen Object/Node/GameObject class?
7. Kan je engine live data krijgen terwijl hij draait, of moet hij opnieuw starten om wijzigingen te zien?
8. Moet de editor de engine in hetzelfde Python proces starten, of als apart programma?
9. Waar staat de render-code nu precies?
10. Moet de editor uiteindelijk ook games kunnen exporteren/builden?

### B. Editor uiterlijk

1. Wil je dat de editor meer lijkt op Godot, Unity, Blender, of iets eigen?
2. Moet de editor donker thema, licht thema, of allebei hebben?
3. Moeten knoppen en labels Nederlands, Engels, of gemengd zijn?
4. Wil je bovenaan browser-achtige tabs voor scenes?
5. Wil je code-tabs apart onderaan, of code als hoofdtab naast de viewport?
6. Moet de file browser links staan?
7. Moet de inspector rechts staan?
8. Wil je een console/output panel onderaan?

### C. Projecten en bestanden

1. Moet de editor altijd het huidige project `Pymath 3d` openen?
2. Wil je later meerdere projecten kunnen openen?
3. Hoe moeten scenes opgeslagen worden: JSON, Python, of eigen `.scene` formaat?
4. Waar moeten scenes komen te staan?
5. Waar moeten scripts/classes komen te staan?
6. Waar moeten models/textures/audio komen te staan?
7. Moet de editor automatisch mappen maken zoals `Scenes`, `Scripts`, `Assets`, `Classes`?
8. Moet de editor bestanden kunnen hernoemen en verwijderen?

### D. Scenes

1. Is een scene bij jou een volledig level/scherm?
2. Wil je scenes gebruiken voor dingen zoals StartScreen, Game, PauseMenu en GameOver?
3. Moet een scene ook instellingen hebben zoals background color, camera en gravity?
4. Mag een scene child-scenes of sub-scenes hebben?
5. Moet de editor een standaard scene maken als er nog geen scene bestaat?
6. Moet je scenes kunnen dupliceren?
7. Moet een scene automatisch opslaan, of alleen als je op Save klikt?

### E. Nodes

1. Noem jij objecten liever nodes, objects, entities, actors, of iets anders?
2. Moet elke node een naam hebben?
3. Moet elke node een unieke id hebben?
4. Moeten nodes parent/child kunnen zijn?
5. Moet elke node standaard position, rotation en scale hebben?
6. Moet een node meerdere components kunnen hebben?
7. Moet een node altijd een `.obj` model kunnen hebben, of soms ook geen model?
8. Moet je nodes kunnen slepen in de hierarchy om parent/child te veranderen?
9. Moet je nodes in de viewport met de muis kunnen verplaatsen?

### F. Inspector

1. Welke properties wil je in versie 1 kunnen aanpassen?
2. Wil je alleen position x/y/z, of ook rotation en scale meteen?
3. Moet de inspector een knop hebben om een `.obj` bestand te kiezen?
4. Moet je een `.obj` vanuit de file browser naar de inspector kunnen slepen?
5. Moeten class-properties automatisch in de inspector verschijnen?
6. Moeten waardes direct veranderen terwijl je typt, of pas na Enter?
7. Moet de inspector undo/redo ondersteunen?

### G. Classes en instances

1. Wat is precies een class in jouw engine?
2. Is een class een Python bestand met een Python class erin?
3. Moet een class erven van een engine-basisclass?
4. Moet de editor automatisch een template maken voor nieuwe classes?
5. Moet je classes kunnen slepen naar de scene om een instance te maken?
6. Moet je instances ook via code kunnen maken?
7. Moet een instance eigen aangepaste waardes kunnen hebben naast de class-defaults?
8. Moeten classes zichtbaar zijn in een apart Class panel, of gewoon in de file browser?

### H. Code editor

1. Moet de code editor alleen Python files openen?
2. Moet Ctrl+S opslaan?
3. Wil je syntax highlighting in versie 1?
4. Wil je line numbers in versie 1?
5. Wil je meerdere code files als tabs?
6. Moet de editor waarschuwingen tonen als een file niet opgeslagen is?
7. Moet de code editor later autocomplete krijgen?

### I. Viewport

1. Moet de eerste versie al echt 3D renderen?
2. Is een placeholder viewport eerst oké?
3. Moet de viewport je bestaande engine gebruiken?
4. Wil je camera controls zoals rechtsklikken + WASD?
5. Moet je objecten kunnen selecteren door erop te klikken?
6. Moet geselecteerde node highlighted worden?
7. Moet de viewport gridlijnen hebben?
8. Moet de viewport gizmos krijgen voor move/rotate/scale?

### J. Play mode

1. Moet er een Play knop komen?
2. Moet Play de actieve scene starten?
3. Moet Stop teruggaan naar edit mode?
4. Moet de game in de editor viewport spelen, of in een apart venster?
5. Moet de editor scene-wijzigingen blokkeren tijdens Play mode?
6. Moet de engine logs naar een output console sturen?

### K. Eerste versie

1. Wat is belangrijker voor versie 1: code editor, scene tabs, inspector, of viewport?
2. Welke functies moeten absoluut in de eerste werkende versie?
3. Welke functies mogen later?
4. Mag versie 1 simpel zijn als de structuur goed is?
5. Wil je dat ik na jouw antwoorden het plan herschrijf naar een concrete todo-lijst?

## 13. Antwoorden van Elias

Deze sectie vullen we in nadat jij de Grill Me vragen hebt beantwoord.

```Main phyton name engine:  Engine/engine.py
   Hoe werkt de Engine: Zelf gemaakte 3d projectie maar met pygame screen pixel array in plaats van Pygame.polygons omdat pixelarray sneller gaat.
   Hoe start ik een test van de game.: Je runt de Engine/engine.py file. Dit doet alles voor jou.
   Hoe laat je een obj file: Run de functie uit engine.py load_obj(file_name) jij moet dan zelf niets met dat object doen

   Uiterlijk: donker en simpel van boven een switcher tussen coding en viewer en heel veel het zelfde als godot
   wat zijn scenes: scenes zijn momenten zoals game_play, start_menu, Game_over_menu

   BELANGERIJK classes: classes kan je maken op de zelfde manier als scenes aleen maak je ze door niet op scenes te drukken als je op plus tabblad drukt maar op class. classes zijn objecten verdeelt uit nodes net als scenes maar dit zijn dinges die je kunt dragen in een scene zoals een pick up die je veel wil plaatsen je kunt ze ook plaatsen in code alle code is phyton

   Moet er play knop komen: JA

   Voor de vieuw poort: Bedenk zelf hoe je dit zou kunnen doen met de pygame engine die ik heb maar wel met mijn engine.

   Projecten en bestanden: Er staat en Game folder met daarin Scripts, assets, en data zo kan jij dinges importeren van de assets of aan de code kunnen.

   DE LAYOUT: bovenaan moet een switcher komen tuseen code of vieuwpoort als je in code zit staat er in het midden de code met daar in dat code vakje ergens een file kiezer. zorg er voor dat dit alleen de .py folders zijn van Game/Scripts.
   Als je dus een file hebt gekozen met de file kiezer die ergens staat een beetje zoals godot dan is de middenste "coder" van die file.  Als je bij de switcher zit dan staat daar in het midden de vieuwpoort.  Rechts staat de inspector van de geselecteerde node.Als je selecteerde tabblat scene is kan je node makelijk aanmaken ALS JE rechtermuisknop drukt op de scene of node. dan wordt het zoals een tree  daaronder gedaan. Maar als je cuurent tabblad geen scene is maar een classe is, dit is eigenlijk het zelfde systeem met de node links maar je kan rechter muisknop klikken en dan staat er copy en dat kan je dat dan pasten in
   je scene. links onderaan staat de file exploreer dit zijn gewoon de zelfde functies als bij godot.

   Versie 1: Begin maar  met het bouwen van de layout en labels zetten in de stukjes van waar wat komt.

   Node: Ja elke node het heen staandaart x y z nodig rotatie en scale behalve bij 2d beperkt voor de menus.   Je hebt voor te beginnen 3 soorten nodes een 2d node, een 3d node,   en een structuur node dit is eigenlijk gewoon eeen beetje zoals een folder. 

   Saving: Je moet net zoals bij godot alles saven de scenes de classes de nodes en hun inspector data. De code maar dat moet gewoon in de .py files zijn.
```

## 14. Eerste concrete stap na goedkeuring

Als dit plan goed is, wordt de eerste echte bouwstap:

```text
Maak een PySide6 editor skelet in Editor/Editor.py met:
- main window
- toolbar
- scene tabs
- file browser
- hierarchy
- inspector
- viewport placeholder
- code editor paneel
```

Daarna pas voegen we echte scene-data, nodes en engine-koppeling toe.

