import re
import base64
import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st
import graphviz
from streamlit_agraph import agraph, Node, Edge, Config
from typing import Optional, Tuple, List, Literal
from utils import ask_chatgpt, Message, START_CONVERSATION

RANG = "cyan"
DIQQAT_RANG = "red"
MATN_RANGI = "green"

class MindMap:
    def __init__(self, edges: Optional[List[Tuple[str, str]]]=None, nodes: Optional[List[str]]=None) -> None:
        self.edges = [] if edges is None else edges
        self.nodes = [] if nodes is None else nodes
        self.definitions = {}
        self.save()

    @classmethod
    def load(cls):
        if "mindmap" in st.session_state:
            return st.session_state["mindmap"]
        return cls()

    def save(self) -> None:
        st.session_state["mindmap"] = self

    def is_empty(self) -> bool:
        return len(self.edges) == 0
    
    def ask_for_initial_graph(self, query: str) -> None:
        conversation = START_CONVERSATION + [
            Message(f"Ajoyib, endi barcha oldingi tugunlarga e'tibor bermang va noldan qayta boshlang. Endi sizdan quyidagilarni qilishni xohlayman: {query}", role="user")
        ]
        output, self.conversation = ask_chatgpt(conversation)
        self.parse_and_include_edges(output, replace=True)

    def ask_for_extended_graph(self, selected_node: Optional[str]=None, text: Optional[str]=None) -> None:
        if (selected_node is None and text is None):
            return

        if selected_node is not None:
            conversation = self.conversation + [Message(f'tugundan boshlab yangi tugunlarga yangi qirralar qo\'shing "{selected_node}"', role="user")]
            st.session_state.last_expanded = selected_node
        else:
            conversation = self.conversation + [Message(text, role="user")]

        output, self.conversation = ask_chatgpt(conversation)
        self.parse_and_include_edges(output, replace=False)

    def parse_and_include_edges(self, output: str, replace: bool=True) -> None:
        pattern1 = r'(add|delete)\("([^()"]+)",\s*"([^()"]+)"\)'
        pattern2 = r'(delete)\("([^()"]+)"\)'

        matches = re.findall(pattern1, output) + re.findall(pattern2, output)

        new_edges = []
        remove_edges = set()
        remove_nodes = set()
        for match in matches:
            op, *args = match
            add = op == "add"
            if add or (op == "delete" and len(args)==2):
                a, b = args
                if a == b:
                    continue
                if add:
                    new_edges.append((a, b))
                else:
                    remove_edges.add(frozenset([a, b]))
            else:
                remove_nodes.add(args[0])

        if replace:
            edges = new_edges
        else:
            edges = self.edges + new_edges

        added = set()
        for edge in edges:
            nodes = frozenset(edge)
            if nodes in added or nodes & remove_nodes or nodes in remove_edges:
                continue
            added.add(nodes)

        self.edges = list([tuple(a) for a in added])
        self.nodes = list(set([n for e in self.edges for n in e]))
        self.save()

    def fetch_definition(self, node: str) -> None:
        conversation = self.conversation + [
            Message(f"'{node}' haqida ma'lumot bering.", role="user")
        ]
        output, _ = ask_chatgpt(conversation)
        self.definitions[node] = output.strip()
        self.save()

    def get_definition(self, node: str) -> str:
        return self.definitions.get(node, "Ta'rif mavjud emas.")

    def _delete_node(self, node) -> None:
        self.edges = [e for e in self.edges if node not in frozenset(e)]
        self.nodes = list(set([n for e in self.edges for n in e]))
        self.definitions.pop(node, None)
        self.conversation.append(Message(f'delete("{node}")', role="user"))
        self.save()

    def _add_expand_delete_buttons(self, node) -> None:
        st.sidebar.subheader(node)
        cols = st.sidebar.columns(3)
        cols[0].button(
            label="Kengaytma", 
            on_click=self.ask_for_extended_graph,
            key=f"expand_{node}",
            kwargs={"selected_node": node}
        )
        cols[1].button(
            label="Ma'lumot", 
            on_click=self.fetch_definition,
            key=f"define_{node}",
            args=(node,)
        )
        cols[2].button(
            label="O'chirish", 
            on_click=self._delete_node,
            type="primary",
            key=f"delete_{node}",
            args=(node,)
        )

        # Show definition if it exists
        if node in self.definitions:
            st.sidebar.write(self.get_definition(node))

    def visualize(self, graph_type: Literal["graf", "tarmoqli"]) -> None:
        selected = st.session_state.get("last_expanded")
        if graph_type == "graf":
            vis_nodes = [
                Node(
                    id=n, 
                    label=n, 
                    text_color=MATN_RANGI,  
                    size=10+10*(n==selected), 
                    color=RANG if n != selected else DIQQAT_RANG
                ) 
                for n in self.nodes
            ]
            vis_edges = [Edge(source=a, target=b) for a, b in self.edges]
            config = Config(width="100%", height=600, directed=False, physics=True, hierarchical=False)
            clicked_node = agraph(nodes=vis_nodes, edges=vis_edges, config=config)
            if clicked_node is not None:
                self._add_expand_delete_buttons(clicked_node)
            return
        if graph_type == "tarmoqli":
            graph = nx.Graph()
            for a, b in self.edges:
                graph.add_edge(a, b)
            colors = [DIQQAT_RANG if node == selected else RANG for node in graph]
            fig, _ = plt.subplots(figsize=(16, 16))
            pos = nx.spring_layout(graph, seed=123)
            nx.draw(graph, pos=pos, node_color=colors, with_labels=True)
            st.pyplot(fig)
        else:
            graph = graphviz.Graph()
            graph.attr(rankdir='LR')
            for a, b in self.edges:
                graph.edge(a, b, dir="both")
            for n in self.nodes:
                graph.node(n, style="filled", fillcolor=DIQQAT_RANG if n == selected else RANG)
            b64 = base64.b64encode(graph.pipe(format='svg')).decode("utf-8")
            html = f"<img style='width: 100%' src='data:image/svg+xml;base64,{b64}'/>"
            st.write(html, unsafe_allow_html=True)
        for node in sorted(self.nodes):
            self._add_expand_delete_buttons(node)
