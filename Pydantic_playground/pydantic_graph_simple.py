from __future__ import annotations
from dataclasses import dataclass
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

@dataclass
class UserState:
    age: int | None = None
    favorite_candy: str | None = None
    favorite_game: str | None = None

@dataclass
class NodeA(BaseNode[UserState]):
    async def run(self, ctx: GraphRunContext[UserState]) -> NodeB | NodeC:
        age = int(input("Please enter your age: "))
        ctx.state.age = age
        if age < 10:
            return NodeB()
        else:
            return NodeC()

@dataclass
class NodeB(BaseNode[UserState]):
    async def run(self, ctx: GraphRunContext[UserState]) -> NodeD:
        favorite_candy = input("What is your favorite candy? ")
        ctx.state.favorite_candy = favorite_candy
        return NodeD()

@dataclass
class NodeC(BaseNode[UserState]):
    async def run(self, ctx: GraphRunContext[UserState]) -> NodeD:
        favorite_game = input("What is your favorite game? ")
        ctx.state.favorite_game = favorite_game
        return NodeD()

@dataclass
class NodeD(BaseNode[UserState, None, UserState]):
    async def run(self, ctx: GraphRunContext[UserState]) -> End[UserState]:
        print("Thank you for your responses!")
        return End(ctx.state)

# Define the graph with the four nodes
user_interaction_graph = Graph(nodes=[NodeA, NodeB, NodeC, NodeD])

# Run the graph starting with NodeA
result, history = user_interaction_graph.run_sync(NodeA(), state=UserState())
print(f"Result: {result}")
