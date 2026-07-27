from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "metamodel"
OUT.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Node:
    id: str
    title: str
    x: int
    y: int
    w: int
    h: int
    stereo: str = ""
    attrs: tuple[str, ...] = field(default_factory=tuple)
    fill: str = "#ffffff"


@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    label: str
    kind: str = "assoc"
    points: tuple[tuple[int, int], ...] = field(default_factory=tuple)
    label_pos: tuple[int, int] | None = None
    color: str = "#41516b"
    dashed: bool = False


NODES: dict[str, Node] = {
    # EAST-ADL core
    "RequirementsModel": Node("RequirementsModel", "RequirementsModel", 80, 100, 300, 118, "<<Context>>", ("requirement: Requirement [0..*]", "useCase: UseCase [0..*]"), "#f7fbff"),
    "Requirement": Node("Requirement", "Requirement", 80, 300, 260, 98, "<<EAST-ADL>>", ("text: String",), "#fff8f0"),
    "Satisfy": Node("Satisfy", "Satisfy", 480, 100, 330, 142, "<<RequirementsRelationship>>", ("satisfiedRequirement [0..*]", "satisfiedUseCase [0..*]", "satisfiedBy: Identifiable [1..*]", "{xor: requirement/useCase}"), "#fff8f0"),
    "Actor": Node("Actor", "Actor", 480, 300, 280, 98, "<<EAST-ADL>>", ("external role", "not a physical entity"), "#fff8f0"),
    "UseCase": Node("UseCase", "UseCase", 950, 235, 360, 138, "<<EAST-ADL>>", ("text: String", "usage of a system", "captures required functionality"), "#fff8f0"),
    "ExtensionPoint": Node("ExtensionPoint", "ExtensionPoint", 1460, 245, 310, 104, "<<EAST-ADL>>", ("name: String", "belongs to extended UseCase"), "#fff8f0"),
    "Include": Node("Include", "Include", 2060, 150, 270, 98, "<<Relationship>>", ("addition: UseCase [1]", "mandatory insertion"), "#fff8f0"),
    "Extend": Node("Extend", "Extend", 2060, 310, 270, 118, "<<Relationship>>", ("extendedCase: UseCase [1]", "extensionLocation [1..*]", "condition [0..1]"), "#fff8f0"),

    # Scenario extension
    "Scenario": Node("Scenario", "Scenario", 80, 600, 330, 142, "<<Dynamic Functional MLDS>>", ("kind: main | alternative | exception", "goal: String", "pre/postcondition: Condition [0..*]"), "#f3fff8"),
    "ScenarioStep": Node("ScenarioStep", "ScenarioStep", 560, 580, 370, 190, "<<Dynamic Functional MLDS>>", ("stepNumber: int", "performedBy: Actor [0..1]", "kind: actorIntent | systemResponse | environmentObservation", "text: String", "occurrenceProbability: float [0..1]"), "#f3fff8"),
    "StepRelation": Node("StepRelation", "StepRelation", 1080, 600, 360, 140, "<<Dynamic Functional MLDS>>", ("kind: sequence | alternative | exception | fork | join | loop", "guard: Condition [0..1]", "probability: float [0..1]"), "#f3fff8"),
    "ParallelGroup": Node("ParallelGroup", "ParallelGroup", 1570, 600, 300, 104, "<<Dynamic Functional MLDS>>", ("label: String", "memberStep: ScenarioStep [2..*]"), "#f3fff8"),
    "Event": Node("Event", "Event", 80, 820, 280, 104, "<<Dynamic Functional MLDS>>", ("kind: temporal | spatial | signal | user | environment", "expression: String"), "#f3fff8"),
    "Condition": Node("Condition", "Condition", 520, 830, 300, 116, "<<Dynamic Functional MLDS>>", ("kind: guard | pre | post | spatial | timing", "expression: String", "randomVariable [0..*]"), "#f3fff8"),
    "StateAssertion": Node("StateAssertion", "StateAssertion", 930, 820, 320, 112, "<<Dynamic Functional MLDS>>", ("subject: Identifiable [1]", "expectedState: String"), "#f3fff8"),

    # Functional/runtime/validation bridge
    "Entity": Node("Entity", "Entity", 80, 1140, 280, 108, "<<Dynamic Functional MLDS>>", ("kind: user | system | environment | asset", "description: String"), "#f8f5ff"),
    "Agent": Node("Agent", "Agent", 80, 1360, 280, 92, "<<Dynamic Functional MLDS>>", ("playsActor: Actor [0..*]",), "#f8f5ff"),
    "CapabilityUse": Node("CapabilityUse", "CapabilityUse", 560, 1080, 330, 116, "<<Dynamic Functional MLDS>>", ("capability: Capability [1]", "parameters: KeyValue [0..*]"), "#f8f5ff"),
    "Capability": Node("Capability", "Capability", 560, 1320, 370, 148, "<<Dynamic Functional MLDS>>", ("intent: String", "precondition: Condition [0..*]", "promisedEffect: Effect [1..*]"), "#f8f5ff"),
    "Effect": Node("Effect", "Effect", 1110, 1320, 300, 104, "<<Dynamic Functional MLDS>>", ("expression: String", "observableBy: Actor [0..*]"), "#f8f5ff"),
    "FunctionBehavior": Node("FunctionBehavior", "EAST-ADL::FunctionBehavior", 1470, 1080, 340, 112, "<<optional bridge>>", ("behaviorKind [0..1]", "formal reference [0..1]"), "#f8f5ff"),
    "RuntimeBinding": Node("RuntimeBinding", "RuntimeBinding", 1470, 1320, 360, 126, "<<Dynamic Functional MLDS>>", ("capability: Capability [1]", "targetPlatform: String", "runtimeAction: RuntimeAction [1..*]"), "#f8f5ff"),
    "RuntimeAction": Node("RuntimeAction", "RuntimeAction", 2120, 1320, 350, 126, "<<technical>>", ("endpoint | tool | topic: String", "inputSchema: Schema [0..1]", "outputSchema: Schema [0..1]"), "#f8f5ff"),
    "ValidationCase": Node("ValidationCase", "ValidationCase", 2120, 1080, 350, 136, "<<validation specialization>>", ("level: abstract | concrete", "stimulus: Event | RuntimeAction [0..*]", "expectedOutcome: StateAssertion [1..*]"), "#f8f5ff"),
}


EDGES: tuple[Edge, ...] = (
    # Requirements/UseCase ownership and relationships
    Edge("RequirementsModel", "Requirement", "contains requirements\n[0..*]", "composition", ((230, 218), (230, 300)), (250, 255)),
    Edge("RequirementsModel", "UseCase", "contains use cases\n[0..*]", "composition", ((380, 150), (430, 150), (430, 88), (1130, 88), (1130, 235)), (1130, 170)),
    Edge("Actor", "UseCase", "interacts with\n[0..*]", "assoc", ((760, 349), (950, 349)), (855, 324)),
    Edge("UseCase", "ExtensionPoint", "defines\nextension points\n[0..*]", "composition", ((1310, 290), (1460, 290)), (1385, 252)),
    Edge("UseCase", "Include", "contains Include relationships\n[0..*]", "composition", ((1140, 235), (1140, 128), (2195, 128), (2195, 150)), (2195, 102)),
    Edge("UseCase", "Extend", "contains Extend relationships\n[0..*]", "composition", ((1310, 370), (1840, 370), (2060, 370)), (1830, 395)),
    Edge("Extend", "ExtensionPoint", "extension location\n[1..*]", "assoc", ((2060, 350), (1900, 350), (1900, 333), (1770, 333)), (1900, 305)),
    Edge("Satisfy", "Requirement", "satisfies\nrequirement\n[0..*]", "assoc", ((480, 220), (340, 220), (340, 325)), (410, 250)),
    Edge("Satisfy", "UseCase", "satisfies\nuse case\n[0..*]", "assoc", ((810, 178), (900, 178), (900, 275), (950, 275)), (890, 154)),

    # Scenario extension
    Edge("UseCase", "Scenario", "contains executable scenarios\n[1..*]", "composition", ((1130, 373), (1130, 455), (60, 455), (60, 670), (80, 670)), (270, 440)),
    Edge("Scenario", "ScenarioStep", "contains\nordered steps\n[1..*]", "composition", ((410, 672), (560, 672)), (485, 646)),
    Edge("Scenario", "StepRelation", "contains step relations\n[0..*]", "composition", ((380, 600), (380, 570), (1260, 570), (1260, 600)), (1260, 540)),
    Edge("Scenario", "ParallelGroup", "contains parallel groups\n[0..*]", "composition", ((320, 600), (320, 550), (1720, 550), (1720, 600)), (1720, 535)),
    Edge("ScenarioStep", "Event", "triggered by event\n[0..*]", "assoc", ((560, 700), (440, 700), (440, 872), (360, 872)), (438, 780)),
    Edge("ScenarioStep", "Condition", "guard condition\n[0..1]", "assoc", ((690, 770), (690, 830)), (600, 790)),
    Edge("ScenarioStep", "StateAssertion", "resulting state\n[0..*]", "assoc", ((880, 770), (880, 845), (930, 845)), (1130, 780)),
    Edge("StepRelation", "ScenarioStep", "source step\n[1]", "assoc", ((1080, 640), (930, 640)), (1005, 615)),
    Edge("StepRelation", "ScenarioStep", "target step\n[1]", "assoc", ((1080, 720), (930, 720)), (1005, 743)),
    Edge("ParallelGroup", "ScenarioStep", "member steps\n[2..*]", "assoc", ((1570, 650), (1500, 650), (1500, 790), (930, 790), (930, 770)), (1325, 775)),

    # Functional/runtime/validation bridge
    Edge("Agent", "Entity", "", "inherit", ((220, 1360), (220, 1248))),
    Edge("Entity", "Capability", "provides capability\n[0..*]", "assoc", ((360, 1195), (450, 1195), (450, 1394), (560, 1394)), (455, 1278)),
    Edge("ScenarioStep", "CapabilityUse", "requires capability use\n[0..*]", "composition", ((745, 770), (745, 1080)), (920, 1030)),
    Edge("CapabilityUse", "Capability", "uses capability\n[1]", "assoc", ((725, 1196), (725, 1320)), (825, 1260)),
    Edge("Capability", "Effect", "promised effect\n[1..*]", "composition", ((930, 1394), (1110, 1394)), (1020, 1360)),
    Edge("Capability", "FunctionBehavior", "refines function behavior\n[0..*]", "assoc", ((850, 1320), (850, 1225), (1640, 1225), (1640, 1192)), (1245, 1210), dashed=True),
    Edge("Capability", "RuntimeBinding", "runtime binding\n[0..*]", "assoc", ((930, 1360), (1200, 1360), (1200, 1280), (1650, 1280), (1650, 1320)), (1375, 1270)),
    Edge("RuntimeBinding", "RuntimeAction", "maps to runtime action\n[1..*]", "composition", ((1830, 1383), (2120, 1383)), (1975, 1350)),
    Edge("ValidationCase", "RuntimeBinding", "checks runtime binding\n[0..*]", "dependency", ((2295, 1216), (2295, 1250), (1760, 1250), (1760, 1320)), (2030, 1232), dashed=True),
)


def node_center(node: Node) -> tuple[int, int]:
    return node.x + node.w // 2, node.y + node.h // 2


def anchor(src: Node, dst: Node) -> tuple[int, int]:
    sx, sy = node_center(src)
    tx, ty = node_center(dst)
    dx = tx - sx
    dy = ty - sy
    if dx == 0 and dy == 0:
        return sx, sy
    if abs(dx) / max(src.w, 1) > abs(dy) / max(src.h, 1):
        x = src.x + (src.w if dx > 0 else 0)
        y = sy + int(dy * (abs(x - sx) / max(abs(dx), 1)))
    else:
        y = src.y + (src.h if dy > 0 else 0)
        x = sx + int(dx * (abs(y - sy) / max(abs(dy), 1)))
    return x, y


def edge_path(edge: Edge) -> str:
    if edge.points:
        points = edge.points
    else:
        sx, sy = anchor(NODES[edge.src], NODES[edge.dst])
        tx, ty = anchor(NODES[edge.dst], NODES[edge.src])
        points = ((sx, sy), (tx, ty))
    first, *rest = points
    return "M " + f"{first[0]} {first[1]} " + " ".join(f"L {x} {y}" for x, y in rest)


def label_position(edge: Edge) -> tuple[int, int]:
    if edge.label_pos:
        return edge.label_pos
    if edge.points:
        points = edge.points
        middle = len(points) // 2
        x1, y1 = points[middle - 1]
        x2, y2 = points[middle]
    else:
        x1, y1 = anchor(NODES[edge.src], NODES[edge.dst])
        x2, y2 = anchor(NODES[edge.dst], NODES[edge.src])
    return (x1 + x2) // 2, (y1 + y2) // 2 - 6


def wrap(text: str, width: int = 36) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        if sum(len(w) + 1 for w in current) + len(word) > width and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def render_node(node: Node) -> str:
    lines = [
        f'<g id="{escape(node.id)}">',
        f'<rect x="{node.x}" y="{node.y}" width="{node.w}" height="{node.h}" rx="4" class="node" fill="{node.fill}" />',
        f'<line x1="{node.x}" y1="{node.y + 44}" x2="{node.x + node.w}" y2="{node.y + 44}" class="separator" />',
    ]
    title_y = node.y + 19
    if node.stereo:
        lines.append(f'<text x="{node.x + node.w / 2}" y="{title_y}" class="stereo" text-anchor="middle">{escape(node.stereo)}</text>')
        title_y += 17
    lines.append(f'<text x="{node.x + node.w / 2}" y="{title_y}" class="title" text-anchor="middle">{escape(node.title)}</text>')
    attr_y = node.y + 64
    for attr in node.attrs:
        attr_lines = wrap(attr, max(20, (node.w - 24) // 7))
        for part in attr_lines:
            lines.append(f'<text x="{node.x + 14}" y="{attr_y}" class="attr">+ {escape(part)}</text>')
            attr_y += 17
    lines.append("</g>")
    return "\n".join(lines)


def render_edge(edge: Edge) -> str:
    marker = {
        "inherit": "url(#triangle)",
        "composition": "url(#arrow)",
        "assoc": "url(#arrow)",
        "dependency": "url(#arrow)",
    }[edge.kind]
    start_marker = ' marker-start="url(#diamond)"' if edge.kind == "composition" else ""
    dash = ' stroke-dasharray="6 5"' if edge.dashed or edge.kind == "dependency" else ""
    x, y = label_position(edge)
    classes = "edge inherit" if edge.kind == "inherit" else "edge"
    path = (
        f'<path d="{edge_path(edge)}" class="{classes}" stroke="{edge.color}"{dash}'
        f'{start_marker} marker-end="{marker}" />\n'
    )
    if not edge.label:
        return path
    label_lines = edge.label.split("\n")
    max_len = max(len(line) for line in label_lines)
    box_w = max(64, max_len * 7.6 + 26)
    box_h = 18 * len(label_lines) + 12
    label = [
        f'<rect x="{x - box_w / 2:.1f}" y="{y - 15:.1f}" width="{box_w:.1f}" height="{box_h:.1f}" class="edge-label-box" />',
        f'<text x="{x}" y="{y}" class="edge-label" text-anchor="middle">',
    ]
    for idx, line in enumerate(label_lines):
        dy = 0 if idx == 0 else 17
        label.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
    label.append("</text>")
    return path + "".join(label)


def render_svg() -> str:
    sections = (
        (40, 40, 2520, 430, "A. EAST-ADL Requirements / UseCases: unverfälschter Kern"),
        (40, 500, 2520, 500, "B. Scenario Layer: geordnete, bedingte und parallele Abläufe"),
        (40, 1030, 2520, 570, "C. Functional/Runtime Bridge: Domänenfähigkeit vor Technikbindung"),
    )
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="2600" height="1650" viewBox="0 0 2600 1650">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#41516b"/></marker>',
        '<marker id="triangle" markerWidth="12" markerHeight="12" refX="11" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" fill="#fff" stroke="#41516b" stroke-width="1.4"/></marker>',
        '<marker id="diamond" markerWidth="16" markerHeight="12" refX="1" refY="6" orient="auto" markerUnits="strokeWidth"><path d="M1,6 L7,1 L13,6 L7,11 z" fill="#41516b" stroke="#41516b" stroke-width="1"/></marker>',
        "<style>",
        dedent(
            """
            .canvas { fill: #fbfcfd; }
            .section { fill: #ffffff; stroke: #d8dee8; stroke-width: 1.2; }
            .section-title { font: 700 19px Arial, sans-serif; fill: #243044; }
            .node { stroke: #927f78; stroke-width: 1.35; filter: drop-shadow(2px 3px 1px rgba(0,0,0,.16)); }
            .separator { stroke: #927f78; stroke-width: 1; }
            .title { font: 700 15px Arial, sans-serif; fill: #222b35; }
            .stereo { font: 12px Arial, sans-serif; fill: #475569; font-style: italic; }
            .attr { font: 13px Arial, sans-serif; fill: #6b2b18; }
            .edge { fill: none; stroke-width: 1.45; }
            .inherit { stroke-width: 1.2; }
            .edge-label-box { fill: #ffffff; stroke: #dbe3ee; stroke-width: .8; rx: 3; }
            .edge-label { font: 13px Arial, sans-serif; fill: #243044; paint-order: stroke; stroke: #fbfcfd; stroke-width: 4px; stroke-linejoin: round; }
            .note { font: 700 13px Arial, sans-serif; fill: #8a1f1f; }
            .note-box { fill: #fff6f6; stroke: #df8b8b; stroke-width: 1.2; rx: 4; }
            """
        ),
        "</style>",
        "</defs>",
        '<rect width="2600" height="1650" class="canvas"/>',
        '<text x="40" y="27" class="section-title">Kompaktes Metamodell für Dynamic Functional MLDS (v0.4)</text>',
    ]
    for x, y, w, h, title in sections:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="section" rx="6"/>')
        parts.append(f'<text x="{x + 18}" y="{y + 28}" class="section-title">{escape(title)}</text>')
    parts.extend(render_edge(edge) for edge in EDGES)
    parts.extend(render_node(node) for node in NODES.values())
    parts.append('<rect x="1910" y="755" width="555" height="72" class="note-box"/>')
    parts.append('<text x="1928" y="782" class="note">Invariant: ScenarioStep hat keine direkte RuntimeAction-Kante.</text>')
    parts.append('<text x="1928" y="807" class="note">Ausführung läuft nur über CapabilityUse -> Capability -> RuntimeBinding.</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def render_mermaid() -> str:
    return dedent(
        """
        classDiagram
          class Identifiable {
            <<abstract>>
            uuid: Identifier
            shortName: String
          }
          class TraceableSpecification {
            <<abstract>>
            text: String
            formalism: String [0..1]
          }
          class RedefinableElement {
            <<abstract>>
          }
          class RequirementsModel {
            <<Context>>
          }
          class Requirement
          class Actor
          class UseCase
          class ExtensionPoint
          class Include {
            addition: UseCase [1]
          }
          class Extend {
            extendedCase: UseCase [1]
            extensionLocation: ExtensionPoint [1..*]
            condition: Condition [0..1]
          }
          class Satisfy {
            satisfiedRequirement: Requirement [0..*]
            satisfiedUseCase: UseCase [0..*]
            satisfiedBy: Identifiable [1..*]
            xor requirementOrUseCase
          }
          class Scenario {
            kind: main|alternative|exception
            goal: String
          }
          class ScenarioStep {
            stepNumber: int
            kind: actorIntent|systemResponse|environmentObservation
            text: String
          }
          class StepRelation {
            kind: sequence|alternative|exception|fork|join|loop
            probability: float [0..1]
          }
          class ParallelGroup {
            memberSteps: ScenarioStep [2..*]
          }
          class Event {
            kind: temporal|spatial|signal|user|environment
            expression: String
          }
          class Condition {
            kind: guard|pre|post|spatial|timing
            expression: String
          }
          class StateAssertion {
            subjectRef: Identifiable [1]
            expectedState: String
          }
          class RandomVariable {
            distribution: exponential|normal|uniform|custom
          }
          class Entity
          class Agent
          class Capability
          class CapabilityUse
          class Effect
          class RuntimeBinding
          class RuntimeAction
          class ValidationCase
          class FunctionBehavior

          TraceableSpecification --|> Identifiable
          RedefinableElement --|> Identifiable
          Requirement --|> TraceableSpecification
          Actor --|> TraceableSpecification
          UseCase --|> TraceableSpecification
          ExtensionPoint --|> RedefinableElement
          Scenario --|> TraceableSpecification
          ScenarioStep --|> TraceableSpecification
          Entity --|> TraceableSpecification
          Agent --|> Entity
          Capability --|> TraceableSpecification
          ValidationCase --|> TraceableSpecification

          RequirementsModel "1" *-- "0..*" Requirement
          RequirementsModel "1" *-- "0..*" UseCase
          Actor "0..*" -- "0..*" UseCase : interactsWith
          UseCase "1" *-- "0..*" ExtensionPoint
          UseCase "1" *-- "0..*" Include
          UseCase "1" *-- "0..*" Extend
          Include --> "1" UseCase : addition
          Extend --> "1" UseCase : extendedCase
          Extend --> "1..*" ExtensionPoint : extensionLocation
          Satisfy --> "0..*" Requirement : satisfiedRequirement
          Satisfy --> "0..*" UseCase : satisfiedUseCase
          Satisfy ..> "1..*" Identifiable : satisfiedBy

          UseCase "1" *-- "1..*" Scenario
          Scenario "1" *-- "1..*" ScenarioStep
          Scenario "1" *-- "0..*" StepRelation
          Scenario "1" *-- "0..*" ParallelGroup
          ScenarioStep --> "0..1" Actor : performedBy
          ScenarioStep --> "0..*" Event : triggeredBy
          ScenarioStep --> "0..1" Condition : guard
          ScenarioStep --> "0..*" StateAssertion : resultingState
          StepRelation --> "1" ScenarioStep : source
          StepRelation --> "1" ScenarioStep : target
          ParallelGroup --> "2..*" ScenarioStep : memberSteps
          Condition --> "0..*" RandomVariable : uses

          Entity --> "0..*" Capability : provides
          Agent ..> "0..*" Actor : playsRole
          ScenarioStep "1" *-- "0..*" CapabilityUse : requires
          CapabilityUse --> "1" Capability
          Capability "1" *-- "1..*" Effect : promisedEffect
          Capability ..> "0..*" FunctionBehavior : refines
          Capability --> "0..*" RuntimeBinding : binding
          RuntimeBinding "1" *-- "1..*" RuntimeAction : mapsTo
          ValidationCase ..> "0..*" Requirement : verifies
          ValidationCase ..> "0..*" UseCase : validates
          ValidationCase ..> "0..*" RuntimeBinding : executes/checks
        """
    ).strip() + "\n"


def render_spec() -> str:
    return dedent(
        """
        # Kompaktes Metamodell für Dynamic Functional MLDS

        Version: v0.4, EAST-ADL-abgeglichen und bewusst verdichtet.

        Quellenbasis: EAST-ADL Domain Model Specification V2.1.12, insbesondere Requirements, UseCases und VerificationValidation. Die EAST-ADL-Definitionen wurden nicht kopiert, sondern auf die für Dynamic Functional MLDS relevanten Beziehungen reduziert.

        ## Problem

        Bestehende Text-zu-VR- oder MLDS-Pipelines können Räume, Objekte und teilweise Interaktionen erzeugen. Für eine wissenschaftlich belastbare Modellierung reicht das aber nicht aus: Es muss nachvollziehbar sein, welche Anforderung oder welcher Use Case eine dynamische Funktion motiviert, in welchem Szenarioschritt sie ausgelöst wird, welche fachliche Fähigkeit dadurch benötigt wird, wie diese Fähigkeit technisch gebunden wird und wie das Verhalten validiert werden kann.

        Das Kernproblem ist also nicht: "Wie rufe ich in Unity oder WebXR eine Funktion auf?", sondern: "Wie bleibt eine dynamische Funktion von der Anforderung bis zur ausführbaren technischen Bindung traceable, prüfbar und austauschbar?"

        ## EAST-ADL-Abgleich

        Die Use-Case-Semantik folgt EAST-ADL:

        - `RequirementsModel` ist der Kontextcontainer für `Requirement` und `UseCase`.
        - `Requirement`, `Actor` und `UseCase` sind `TraceableSpecification`.
        - `Actor` beschreibt eine externe Rolle, nicht zwingend eine physische Instanz. Ein realer Benutzer, Sensor oder Agent kann mehrere Rollen spielen.
        - `UseCase` beschreibt eine Nutzung des Systems und erfasst, was das System leisten soll.
        - `Include` ist verpflichtend: Die Behavior des inkludierten Use Cases wird in den inkludierenden Use Case eingefügt; der inkludierende Use Case ist ohne diese Behavior nicht korrekt ausführbar.
        - `Extend` ist ergänzend: Ein erweiternder Use Case ergänzt einen eigenständig sinnvollen Basis-Use-Case an einem oder mehreren `ExtensionPoint`.
        - `ExtensionPoint` gehört zum erweiterten Use Case und bezeichnet die Stelle, an der Verhalten ergänzt werden darf.
        - `Satisfy` verbindet Anforderungen oder Use Cases mit erfüllenden Elementen. Gemäß EAST-ADL darf eine einzelne `Satisfy`-Beziehung entweder Requirements oder UseCases referenzieren, aber nicht beides gleichzeitig.

        ## Was gegenüber der größeren Fassung geändert wurde

        Das Modell wurde bewusst verkleinert:

        - `SpatialEvent`, `TemporalEvent`, `EnvironmentEvent` usw. wurden zu `Event.kind` zusammengefasst.
        - `SpatialConstraint`, Timing- und Guard-Ausdrücke wurden zu `Condition.kind` zusammengefasst.
        - `ScenarioStep` erbt nicht mehr von `RedefinableElement`. In EAST-ADL ist `RedefinableElement` hier für `ExtensionPoint` relevant, nicht für jeden Schritt.
        - `Actor` und `Agent` sind getrennt. `Actor` ist eine Rolle im Use Case; `Agent` ist eine ausführende oder beobachtete Entität, die diese Rolle spielen kann.
        - `ParallelGroup` besitzt keine Schritte. Schritte gehören genau zum `Scenario`; eine Parallelgruppe referenziert nur mindestens zwei dieser Schritte.
        - `ScenarioStep` zeigt nicht direkt auf technische APIs, Tools, Topics oder RuntimeActions. Der fachliche Pfad ist: `ScenarioStep -> CapabilityUse -> Capability -> RuntimeBinding -> RuntimeAction`.

        ## Modellidee

        Das Metamodell besteht aus drei kompakten Teilen:

        1. Der EAST-ADL-nahe Use-Case-Kern beschreibt Anforderungen, Use Cases, Actors, Include, Extend, ExtensionPoint und Satisfy.
        2. Die Scenario-Erweiterung beschreibt konkrete dynamische Abläufe innerhalb eines Use Cases: Schritte, Ereignisse, Bedingungen, Zustandsaussagen, Alternativen und Parallelität.
        3. Die Functional/Runtime Bridge trennt fachliche Fähigkeiten von technischer Ausführung: Ein Szenarioschritt benötigt eine `CapabilityUse`; diese referenziert eine fachliche `Capability`; erst `RuntimeBinding` ordnet diese Fähigkeit einer konkreten `RuntimeAction` zu.

        ## Zentrale Kardinalitäten

        | Beziehung | Kardinalität | Bedeutung |
        | --- | ---: | --- |
        | `RequirementsModel -> Requirement` | `0..*` | Ein Requirements-Kontext kann beliebig viele Anforderungen enthalten. |
        | `RequirementsModel -> UseCase` | `0..*` | Ein Requirements-Kontext kann beliebig viele Use Cases enthalten. |
        | `UseCase -> ExtensionPoint` | `0..*` composite | ExtensionPoints gehören zum Use Case, dessen Verhalten erweitert werden darf. |
        | `UseCase -> Include` | `0..*` composite | Ein Use Case kann verpflichtende Teilverhalten inkludieren. |
        | `Include -> UseCase` | `addition [1]` | Genau ein Use Case liefert das eingefügte Verhalten. |
        | `UseCase -> Extend` | `0..*` composite | Ein Use Case kann andere Use Cases erweitern. |
        | `Extend -> UseCase` | `extendedCase [1]` | Genau ein Basis-Use-Case wird erweitert. |
        | `Extend -> ExtensionPoint` | `1..*` | Die Erweiterung muss mindestens einen ExtensionPoint des Basis-Use-Cases adressieren. |
        | `UseCase -> Scenario` | `1..*` composite | Jeder dynamisch ausführbare Use Case hat mindestens ein Szenario. |
        | `Scenario -> ScenarioStep` | `1..*` ordered composite | Ein Szenario besteht aus geordneten Schritten. |
        | `Scenario -> StepRelation` | `0..*` composite | Nichtlineare Flüsse werden explizit modelliert. |
        | `ParallelGroup -> ScenarioStep` | `2..*` reference | Parallelität referenziert Schritte, besitzt sie aber nicht. |
        | `ScenarioStep -> CapabilityUse` | `0..*` composite | Ein Schritt kann fachliche Fähigkeiten benötigen. |
        | `CapabilityUse -> Capability` | `1` | Jede Nutzung referenziert genau eine fachliche Fähigkeit. |
        | `Capability -> RuntimeBinding` | `0..*` | Eine fachliche Fähigkeit kann auf keiner, einer oder mehreren Plattformen technisch gebunden werden. |
        | `RuntimeBinding.capability` | `1` | Jede technische Bindung referenziert genau eine fachliche Fähigkeit. |
        | `RuntimeBinding -> RuntimeAction` | `1..*` composite | Eine Fähigkeit kann durch eine oder mehrere technische Aktionen realisiert werden. |
        | `Capability -> Effect` | `1..*` composite | Eine Fähigkeit muss mindestens einen beobachtbaren versprochenen Effekt haben. |

        ## Invarianten

        1. Pro `UseCase` muss genau ein `Scenario.kind = main` existieren. Alternative und Exception-Szenarien dürfen zusätzlich existieren.
        2. `Include` beschreibt verpflichtende Wiederverwendung. Optionales oder bedingtes Zusatzverhalten ist kein Include, sondern ein `Extend` oder eine `StepRelation.kind = alternative|exception`.
        3. Ein `Extend.extensionLocation` muss auf `ExtensionPoint`-Elemente zeigen, die zum `extendedCase` gehören.
        4. Eine `Satisfy`-Instanz referenziert entweder `Requirement` oder `UseCase`, nicht beides gleichzeitig.
        5. `ScenarioStep` darf keine direkte Referenz auf `RuntimeAction`, API-Endpunkte, Tools oder Message Topics besitzen.
        6. `Capability` enthält keine technischen Endpoint- oder Tool-Daten. Technische Details liegen ausschließlich in `RuntimeBinding` und `RuntimeAction`.
        7. Alle `ScenarioStep`-Elemente einer `ParallelGroup` müssen zum selben `Scenario` gehören.
        8. Wenn `ScenarioStep.kind = actorIntent`, dann sollte `performedBy` auf einen `Actor` zeigen. Bei Systemantworten wird die ausführende Logik über `CapabilityUse` und `Capability` modelliert.

        ## Beispiel: Interaktive Kaffeemaschine im virtuellen Raum

        Angenommen, ein Besucher in einem VR-Schulungsraum soll eine Kaffeemaschine bedienen können.

        Requirement:
        `REQ-001`: "Der Benutzer muss den Brühvorgang durch Drücken der Starttaste auslösen können."

        Use Case:
        `UC_StartBrewing`: "Kaffee brühen starten"

        Actor:
        `Visitor`: externe Rolle, die mit dem System interagiert.

        Include:
        `UC_StartBrewing` inkludiert `UC_CheckMachineReady`. Das ist verpflichtend, weil der Brühvorgang ohne verfügbare Maschine, Wasser und Tasse nicht korrekt ausführbar ist.

        ExtensionPoint:
        `EP_AfterStartCommand`: Stelle nach dem Startkommando.

        Extend:
        `UC_ExplainBrewing` erweitert `UC_StartBrewing` an `EP_AfterStartCommand`, falls der Trainingsmodus aktiv ist. Das ist kein Include, weil die Erklärung optional ist und der Basis-Use-Case auch ohne Erklärung sinnvoll bleibt.

        Scenario:
        `SC_MainStartBrewing` ist das Main-Szenario von `UC_StartBrewing`.

        ScenarioSteps:
        - `S1`: Visitor drückt die Starttaste. `triggeredBy = Event(kind=user, expression="press(startButton)")`
        - `S2`: Das System prüft die Bereitschaft. `requires = CapabilityUse(CheckMachineReady)`
        - `S3`: Das System startet den Brühvorgang. `requires = CapabilityUse(StartBrewing)` und `resultingState = StateAssertion(coffeeMachine.state = brewing)`

        Capability:
        `StartBrewing` beschreibt fachlich: "Setzt die Kaffeemaschine in den Zustand brewing und macht den Brühfortschritt sichtbar." Die Capability kennt keine Unity-Methode, keinen MQTT-Topic und keinen API-Endpunkt.

        RuntimeBinding:
        `RB_StartBrewing_WebXR` bindet `StartBrewing` an technische Aktionen, z. B. `RuntimeAction(endpoint="CoffeeMachineController.startBrewing()", inputSchema="machineId")`.

        ValidationCase:
        `VC_StartBrewing`: Bei Stimulus `press(startButton)` und Vorbedingung `machine.ready = true` muss der erwartete Zustand `coffeeMachine.state = brewing` eintreten und eine Fortschrittsanzeige sichtbar sein.

        Damit ist die Funktion von der Anforderung bis zur ausführbaren VR-Interaktion nachvollziehbar:

        `REQ-001 -> UC_StartBrewing -> SC_MainStartBrewing -> S3 -> CapabilityUse(StartBrewing) -> Capability(StartBrewing) -> RuntimeBinding -> RuntimeAction -> ValidationCase`

        ## Interpretation

        Das Modell trennt bewusst drei Fragen:

        - Was soll das System aus Sicht von Anforderungen und Use Cases leisten?
        - Wann tritt dieses Verhalten in einem Szenario auf?
        - Wie wird die fachliche Fähigkeit auf einer konkreten Plattform ausgeführt und validiert?

        Diese Trennung ist entscheidend, weil ein MLDS- oder LLM-basierter Generator dadurch nicht sofort technische Aktionen halluzinieren muss. Er kann zuerst Use Case, Szenario, Bedingung und Capability erzeugen. Erst danach wird eine gültige RuntimeBinding ausgewählt oder erzeugt. Das macht die Pipeline erklärbarer, austauschbarer und prüfbarer.

        ## Quellen

        - EAST-ADL Association: EAST-ADL Domain Model Specification V2.1.12, Requirements, UseCases und VerificationValidation: https://east-adl.info/Specification/V2.1.12/EAST-ADL-Specification_V2.1.12.pdf
        - EAST-ADL Specification Portal: https://east-adl.info/Specification.html
        """
    ).strip() + "\n"


def main() -> None:
    (OUT / "dynamic_functional_mlds_metamodel.svg").write_text(render_svg(), encoding="utf-8")
    (OUT / "dynamic_functional_mlds_metamodel.mmd").write_text(render_mermaid(), encoding="utf-8")
    (OUT / "dynamic_functional_mlds_specification.md").write_text(render_spec(), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
