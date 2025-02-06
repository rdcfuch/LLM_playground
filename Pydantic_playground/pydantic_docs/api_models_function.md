# Source URL: https://ai.pydantic.dev/api/models/function/

[ Skip to content ](https://ai.pydantic.dev/api/models/function/<#pydantic_aimodelsfunction>)
[ ![logo](https://ai.pydantic.dev/img/logo-white.svg) ](https://ai.pydantic.dev/api/models/function/..> "PydanticAI")
PydanticAI 
pydantic_ai.models.function 
Type to start searching
[ pydantic/pydantic-ai  ](https://ai.pydantic.dev/api/models/function/<https:/github.com/pydantic/pydantic-ai> "Go to repository")
[ ![logo](https://ai.pydantic.dev/img/logo-white.svg) ](https://ai.pydantic.dev/api/models/function/..> "PydanticAI") PydanticAI 
[ pydantic/pydantic-ai  ](https://ai.pydantic.dev/api/models/function/<https:/github.com/pydantic/pydantic-ai> "Go to repository")
  * [ Introduction  ](https://ai.pydantic.dev/api/models/function/..>)
  * [ Installation  ](https://ai.pydantic.dev/api/models/install/>)
  * [ Getting Help  ](https://ai.pydantic.dev/api/models/help/>)
  * [ Contributing  ](https://ai.pydantic.dev/api/models/contributing/>)
  * [ Troubleshooting  ](https://ai.pydantic.dev/api/models/troubleshooting/>)
  * Documentation  Documentation 
    * [ Agents  ](https://ai.pydantic.dev/api/models/agents/>)
    * [ Models  ](https://ai.pydantic.dev/api/models/models/>)
    * [ Dependencies  ](https://ai.pydantic.dev/api/models/dependencies/>)
    * [ Function Tools  ](https://ai.pydantic.dev/api/models/tools/>)
    * [ Results  ](https://ai.pydantic.dev/api/models/results/>)
    * [ Messages and chat history  ](https://ai.pydantic.dev/api/models/message-history/>)
    * [ Testing and Evals  ](https://ai.pydantic.dev/api/models/testing-evals/>)
    * [ Debugging and Monitoring  ](https://ai.pydantic.dev/api/models/logfire/>)
    * [ Multi-agent Applications  ](https://ai.pydantic.dev/api/models/multi-agent-applications/>)
    * [ Graphs  ](https://ai.pydantic.dev/api/models/graph/>)
  * [ Examples  ](https://ai.pydantic.dev/api/models/examples/>)
Examples 
    * [ Pydantic Model  ](https://ai.pydantic.dev/api/models/examples/pydantic-model/>)
    * [ Weather agent  ](https://ai.pydantic.dev/api/models/examples/weather-agent/>)
    * [ Bank support  ](https://ai.pydantic.dev/api/models/examples/bank-support/>)
    * [ SQL Generation  ](https://ai.pydantic.dev/api/models/examples/sql-gen/>)
    * [ Flight booking  ](https://ai.pydantic.dev/api/models/examples/flight-booking/>)
    * [ RAG  ](https://ai.pydantic.dev/api/models/examples/rag/>)
    * [ Stream markdown  ](https://ai.pydantic.dev/api/models/examples/stream-markdown/>)
    * [ Stream whales  ](https://ai.pydantic.dev/api/models/examples/stream-whales/>)
    * [ Chat App with FastAPI  ](https://ai.pydantic.dev/api/models/examples/chat-app/>)
    * [ Question Graph  ](https://ai.pydantic.dev/api/models/examples/question-graph/>)
  * API Reference  API Reference 
    * [ pydantic_ai.agent  ](https://ai.pydantic.dev/api/models/function/agent/>)
    * [ pydantic_ai.tools  ](https://ai.pydantic.dev/api/models/function/tools/>)
    * [ pydantic_ai.result  ](https://ai.pydantic.dev/api/models/function/result/>)
    * [ pydantic_ai.messages  ](https://ai.pydantic.dev/api/models/function/messages/>)
    * [ pydantic_ai.exceptions  ](https://ai.pydantic.dev/api/models/function/exceptions/>)
    * [ pydantic_ai.settings  ](https://ai.pydantic.dev/api/models/function/settings/>)
    * [ pydantic_ai.usage  ](https://ai.pydantic.dev/api/models/function/usage/>)
    * [ pydantic_ai.format_as_xml  ](https://ai.pydantic.dev/api/models/function/format_as_xml/>)
    * [ pydantic_ai.models  ](https://ai.pydantic.dev/api/models/function/<../base/>)
    * [ pydantic_ai.models.openai  ](https://ai.pydantic.dev/api/models/function/<../openai/>)
    * [ pydantic_ai.models.anthropic  ](https://ai.pydantic.dev/api/models/function/<../anthropic/>)
    * [ pydantic_ai.models.gemini  ](https://ai.pydantic.dev/api/models/function/<../gemini/>)
    * [ pydantic_ai.models.vertexai  ](https://ai.pydantic.dev/api/models/function/<../vertexai/>)
    * [ pydantic_ai.models.groq  ](https://ai.pydantic.dev/api/models/function/<../groq/>)
    * [ pydantic_ai.models.mistral  ](https://ai.pydantic.dev/api/models/function/<../mistral/>)
    * [ pydantic_ai.models.ollama  ](https://ai.pydantic.dev/api/models/function/<../ollama/>)
    * [ pydantic_ai.models.test  ](https://ai.pydantic.dev/api/models/function/<../test/>)
    * pydantic_ai.models.function  [ pydantic_ai.models.function  ](https://ai.pydantic.dev/api/models/function/<./>) Table of contents 
      * [ function  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function>)
      * [ FunctionModel  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionModel>)
        * [ __init__  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionModel.__init__>)
      * [ AgentInfo  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo>)
        * [ function_tools  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo.function_tools>)
        * [ allow_text_result  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo.allow_text_result>)
        * [ result_tools  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo.result_tools>)
        * [ model_settings  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo.model_settings>)
      * [ DeltaToolCall  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCall>)
        * [ name  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCall.name>)
        * [ json_args  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCall.json_args>)
      * [ DeltaToolCalls  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCalls>)
      * [ FunctionDef  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionDef>)
      * [ StreamFunctionDef  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.StreamFunctionDef>)
      * [ FunctionAgentModel  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionAgentModel>)
      * [ FunctionStreamedResponse  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionStreamedResponse>)
    * [ pydantic_graph  ](https://ai.pydantic.dev/api/models/function/pydantic_graph/graph/>)
    * [ pydantic_graph.nodes  ](https://ai.pydantic.dev/api/models/function/pydantic_graph/nodes/>)
    * [ pydantic_graph.state  ](https://ai.pydantic.dev/api/models/function/pydantic_graph/state/>)
    * [ pydantic_graph.mermaid  ](https://ai.pydantic.dev/api/models/function/pydantic_graph/mermaid/>)
    * [ pydantic_graph.exceptions  ](https://ai.pydantic.dev/api/models/function/pydantic_graph/exceptions/>)


Table of contents 
  * [ function  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function>)
  * [ FunctionModel  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionModel>)
    * [ __init__  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionModel.__init__>)
  * [ AgentInfo  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo>)
    * [ function_tools  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo.function_tools>)
    * [ allow_text_result  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo.allow_text_result>)
    * [ result_tools  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo.result_tools>)
    * [ model_settings  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo.model_settings>)
  * [ DeltaToolCall  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCall>)
    * [ name  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCall.name>)
    * [ json_args  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCall.json_args>)
  * [ DeltaToolCalls  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCalls>)
  * [ FunctionDef  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionDef>)
  * [ StreamFunctionDef  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.StreamFunctionDef>)
  * [ FunctionAgentModel  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionAgentModel>)
  * [ FunctionStreamedResponse  ](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionStreamedResponse>)


  1. [ Introduction  ](https://ai.pydantic.dev/api/models/function/..>)
  2. [ API Reference  ](https://ai.pydantic.dev/api/models/function/agent/>)


Version Notice
This documentation is ahead of the last release by [9 commits](https://ai.pydantic.dev/api/models/function/<https:/github.com/pydantic/pydantic-ai/compare/v0.0.20...main>). You may see documentation for features not yet supported in the latest release [v0.0.20 2025-01-23](https://ai.pydantic.dev/api/models/function/<https:/github.com/pydantic/pydantic-ai/releases/tag/v0.0.20>). 
# `pydantic_ai.models.function`
A model controlled by a local function.
`FunctionModel`[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionModel>) is similar to `TestModel`[](https://ai.pydantic.dev/api/models/function/<../test/>), but allows greater control over the model's behavior.
Its primary use case is for more advanced unit testing than is possible with `TestModel`.
Here's a minimal example:
function_model_usage.py```
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart
from pydantic_ai.models.function import FunctionModel, AgentInfo
my_agent = Agent('openai:gpt-4o')

async def model_function(
  messages: list[ModelMessage], info: AgentInfo
) -> ModelResponse:
  print(messages)
"""
  [
    ModelRequest(
      parts=[
        UserPromptPart(
          content='Testing my agent...',
          timestamp=datetime.datetime(...),
          part_kind='user-prompt',
        )
      ],
      kind='request',
    )
  ]
  """
  print(info)
"""
  AgentInfo(
    function_tools=[], allow_text_result=True, result_tools=[], model_settings=None
  )
  """
  return ModelResponse(parts=[TextPart('hello world')])

async def test_my_agent():
"""Unit test for my_agent, to be run by pytest."""
  with my_agent.override(model=FunctionModel(model_function)):
    result = await my_agent.run('Testing my agent...')
    assert result.data == 'hello world'

```

See [Unit testing with `FunctionModel`](https://ai.pydantic.dev/api/models/testing-evals/#unit-testing-with-functionmodel>) for detailed documentation.
###  FunctionModel `dataclass`
Bases: `Model[](https://ai.pydantic.dev/api/models/function/<../base/#pydantic_ai.models.Model> "pydantic_ai.models.Model")`
A model controlled by a local function.
Apart from `__init__`, all methods are private or match those of the base class.
Source code in `pydantic_ai_slim/pydantic_ai/models/function.py`
```
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
```
| ```
@dataclass(init=False)
class FunctionModel(Model):
"""A model controlled by a local function.
  Apart from `__init__`, all methods are private or match those of the base class.
  """
  function: FunctionDef | None = None
  stream_function: StreamFunctionDef | None = None
  @overload
  def __init__(self, function: FunctionDef) -> None: ...
  @overload
  def __init__(self, *, stream_function: StreamFunctionDef) -> None: ...
  @overload
  def __init__(self, function: FunctionDef, *, stream_function: StreamFunctionDef) -> None: ...
  def __init__(self, function: FunctionDef | None = None, *, stream_function: StreamFunctionDef | None = None):
"""Initialize a `FunctionModel`.
    Either `function` or `stream_function` must be provided, providing both is allowed.
    Args:
      function: The function to call for non-streamed requests.
      stream_function: The function to call for streamed requests.
    """
    if function is None and stream_function is None:
      raise TypeError('Either `function` or `stream_function` must be provided')
    self.function = function
    self.stream_function = stream_function
  async def agent_model(
    self,
    *,
    function_tools: list[ToolDefinition],
    allow_text_result: bool,
    result_tools: list[ToolDefinition],
  ) -> AgentModel:
    return FunctionAgentModel(
      self.function,
      self.stream_function,
      AgentInfo(function_tools, allow_text_result, result_tools, None),
    )
  def name(self) -> str:
    function_name = self.function.__name__ if self.function is not None else ''
    stream_function_name = self.stream_function.__name__ if self.stream_function is not None else ''
    return f'function:{function_name}:{stream_function_name}'

```
  
---|---  
####  __init__
```
__init__(function: FunctionDef[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionDef> "pydantic_ai.models.function.FunctionDef")) -> None

```

```
__init__(*, stream_function: StreamFunctionDef[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.StreamFunctionDef> "pydantic_ai.models.function.StreamFunctionDef")) -> None

```

```
__init__(
  function: FunctionDef[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionDef> "pydantic_ai.models.function.FunctionDef"),
  *,
  stream_function: StreamFunctionDef[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.StreamFunctionDef> "pydantic_ai.models.function.StreamFunctionDef")
) -> None

```

```
__init__(
  function: FunctionDef[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionDef> "pydantic_ai.models.function.FunctionDef") | None = None,
  *,
  stream_function: StreamFunctionDef[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.StreamFunctionDef> "pydantic_ai.models.function.StreamFunctionDef") | None = None
)

```

Initialize a `FunctionModel`.
Either `function` or `stream_function` must be provided, providing both is allowed.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`function` |  `FunctionDef[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionDef> "pydantic_ai.models.function.FunctionDef") | None` |  The function to call for non-streamed requests. |  `None`  
`stream_function` |  `StreamFunctionDef[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.StreamFunctionDef> "pydantic_ai.models.function.StreamFunctionDef") | None` |  The function to call for streamed requests. |  `None`  
Source code in `pydantic_ai_slim/pydantic_ai/models/function.py`
```
52
53
54
55
56
57
58
59
60
61
62
63
64
```
| ```
def __init__(self, function: FunctionDef | None = None, *, stream_function: StreamFunctionDef | None = None):
"""Initialize a `FunctionModel`.
  Either `function` or `stream_function` must be provided, providing both is allowed.
  Args:
    function: The function to call for non-streamed requests.
    stream_function: The function to call for streamed requests.
  """
  if function is None and stream_function is None:
    raise TypeError('Either `function` or `stream_function` must be provided')
  self.function = function
  self.stream_function = stream_function

```
  
---|---  
###  AgentInfo `dataclass`
Information about an agent.
This is passed as the second to functions used within `FunctionModel`[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionModel>).
Source code in `pydantic_ai_slim/pydantic_ai/models/function.py`
```
 85
 86
 87
 88
 89
 90
 91
 92
 93
 94
 95
 96
 97
 98
 99
100
101
102
103
```
| ```
@dataclass(frozen=True)
class AgentInfo:
"""Information about an agent.
  This is passed as the second to functions used within [`FunctionModel`][pydantic_ai.models.function.FunctionModel].
  """
  function_tools: list[ToolDefinition]
"""The function tools available on this agent.
  These are the tools registered via the [`tool`][pydantic_ai.Agent.tool] and
  [`tool_plain`][pydantic_ai.Agent.tool_plain] decorators.
  """
  allow_text_result: bool
"""Whether a plain text result is allowed."""
  result_tools: list[ToolDefinition]
"""The tools that can called as the final result of the run."""
  model_settings: ModelSettings | None
"""The model settings passed to the run call."""

```
  
---|---  
####  function_tools `instance-attribute`
```
function_tools: list[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/stdtypes.html#list>)[ToolDefinition[](https://ai.pydantic.dev/api/models/function/tools/#pydantic_ai.tools.ToolDefinition> "pydantic_ai.tools.ToolDefinition")]

```

The function tools available on this agent.
These are the tools registered via the `tool`[](https://ai.pydantic.dev/api/models/function/agent/#pydantic_ai.agent.Agent.tool>) and `tool_plain`[](https://ai.pydantic.dev/api/models/function/agent/#pydantic_ai.agent.Agent.tool_plain>) decorators.
####  allow_text_result `instance-attribute`
```
allow_text_result: bool[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/functions.html#bool>)

```

Whether a plain text result is allowed.
####  result_tools `instance-attribute`
```
result_tools: list[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/stdtypes.html#list>)[ToolDefinition[](https://ai.pydantic.dev/api/models/function/tools/#pydantic_ai.tools.ToolDefinition> "pydantic_ai.tools.ToolDefinition")]

```

The tools that can called as the final result of the run.
####  model_settings `instance-attribute`
```
model_settings: ModelSettings[](https://ai.pydantic.dev/api/models/function/settings/#pydantic_ai.settings.ModelSettings> "pydantic_ai.settings.ModelSettings") | None

```

The model settings passed to the run call.
###  DeltaToolCall `dataclass`
Incremental change to a tool call.
Used to describe a chunk when streaming structured responses.
Source code in `pydantic_ai_slim/pydantic_ai/models/function.py`
```
106
107
108
109
110
111
112
113
114
115
116
```
| ```
@dataclass
class DeltaToolCall:
"""Incremental change to a tool call.
  Used to describe a chunk when streaming structured responses.
  """
  name: str | None = None
"""Incremental change to the name of the tool."""
  json_args: str | None = None
"""Incremental change to the arguments as JSON"""

```
  
---|---  
####  name `class-attribute` `instance-attribute`
```
name: str[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/stdtypes.html#str>) | None = None

```

Incremental change to the name of the tool.
####  json_args `class-attribute` `instance-attribute`
```
json_args: str[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/stdtypes.html#str>) | None = None

```

Incremental change to the arguments as JSON
###  DeltaToolCalls `module-attribute`
```
DeltaToolCalls: TypeAlias[](https://ai.pydantic.dev/api/models/function/<https:/typing-extensions.readthedocs.io/en/latest/index.html#typing_extensions.TypeAlias> "typing_extensions.TypeAlias") = dict[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/stdtypes.html#dict>)[int[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/functions.html#int>), DeltaToolCall[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCall> "pydantic_ai.models.function.DeltaToolCall")]

```

A mapping of tool call IDs to incremental changes.
###  FunctionDef `module-attribute`
```
FunctionDef: TypeAlias[](https://ai.pydantic.dev/api/models/function/<https:/typing-extensions.readthedocs.io/en/latest/index.html#typing_extensions.TypeAlias> "typing_extensions.TypeAlias") = Callable[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/typing.html#typing.Callable> "typing.Callable")[
  [list[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/stdtypes.html#list>)[ModelMessage[](https://ai.pydantic.dev/api/models/function/messages/#pydantic_ai.messages.ModelMessage> "pydantic_ai.messages.ModelMessage")], AgentInfo[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo> "pydantic_ai.models.function.AgentInfo")],
  Union[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/typing.html#typing.Union> "typing.Union")[ModelResponse[](https://ai.pydantic.dev/api/models/function/messages/#pydantic_ai.messages.ModelResponse> "pydantic_ai.messages.ModelResponse"), Awaitable[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/collections.abc.html#collections.abc.Awaitable> "collections.abc.Awaitable")[ModelResponse[](https://ai.pydantic.dev/api/models/function/messages/#pydantic_ai.messages.ModelResponse> "pydantic_ai.messages.ModelResponse")]],
]

```

A function used to generate a non-streamed response.
###  StreamFunctionDef `module-attribute`
```
StreamFunctionDef: TypeAlias[](https://ai.pydantic.dev/api/models/function/<https:/typing-extensions.readthedocs.io/en/latest/index.html#typing_extensions.TypeAlias> "typing_extensions.TypeAlias") = Callable[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/typing.html#typing.Callable> "typing.Callable")[
  [list[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/stdtypes.html#list>)[ModelMessage[](https://ai.pydantic.dev/api/models/function/messages/#pydantic_ai.messages.ModelMessage> "pydantic_ai.messages.ModelMessage")], AgentInfo[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.AgentInfo> "pydantic_ai.models.function.AgentInfo")],
  AsyncIterator[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/collections.abc.html#collections.abc.AsyncIterator> "collections.abc.AsyncIterator")[Union[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/typing.html#typing.Union> "typing.Union")[str[](https://ai.pydantic.dev/api/models/function/<https:/docs.python.org/3/library/stdtypes.html#str>), DeltaToolCalls[](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.DeltaToolCalls> "pydantic_ai.models.function.DeltaToolCalls")]],
]

```

A function used to generate a streamed response.
While this is defined as having return type of `AsyncIterator[Union[str, DeltaToolCalls]]`, it should really be considered as `Union[AsyncIterator[str], AsyncIterator[DeltaToolCalls]`,
E.g. you need to yield all text or all `DeltaToolCalls`, not mix them.
###  FunctionAgentModel `dataclass`
Bases: `AgentModel[](https://ai.pydantic.dev/api/models/function/<../base/#pydantic_ai.models.AgentModel> "pydantic_ai.models.AgentModel")`
Implementation of `AgentModel` for [FunctionModel](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionModel>).
Source code in `pydantic_ai_slim/pydantic_ai/models/function.py`
```
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
161
162
163
164
165
166
167
168
169
170
171
172
173
174
175
176
```
| ```
@dataclass
class FunctionAgentModel(AgentModel):
"""Implementation of `AgentModel` for [FunctionModel][pydantic_ai.models.function.FunctionModel]."""
  function: FunctionDef | None
  stream_function: StreamFunctionDef | None
  agent_info: AgentInfo
  async def request(
    self, messages: list[ModelMessage], model_settings: ModelSettings | None
  ) -> tuple[ModelResponse, usage.Usage]:
    agent_info = replace(self.agent_info, model_settings=model_settings)
    assert self.function is not None, 'FunctionModel must receive a `function` to support non-streamed requests'
    model_name = f'function:{self.function.__name__}'
    if inspect.iscoroutinefunction(self.function):
      response = await self.function(messages, agent_info)
    else:
      response_ = await _utils.run_in_executor(self.function, messages, agent_info)
      assert isinstance(response_, ModelResponse), response_
      response = response_
    response.model_name = model_name
    # TODO is `messages` right here? Should it just be new messages?
    return response, _estimate_usage(chain(messages, [response]))
  @asynccontextmanager
  async def request_stream(
    self, messages: list[ModelMessage], model_settings: ModelSettings | None
  ) -> AsyncIterator[StreamedResponse]:
    assert (
      self.stream_function is not None
    ), 'FunctionModel must receive a `stream_function` to support streamed requests'
    model_name = f'function:{self.stream_function.__name__}'
    response_stream = PeekableAsyncStream(self.stream_function(messages, self.agent_info))
    first = await response_stream.peek()
    if isinstance(first, _utils.Unset):
      raise ValueError('Stream function must return at least one item')
    yield FunctionStreamedResponse(_model_name=model_name, _iter=response_stream)

```
  
---|---  
###  FunctionStreamedResponse `dataclass`
Bases: `StreamedResponse[](https://ai.pydantic.dev/api/models/function/<../base/#pydantic_ai.models.StreamedResponse> "pydantic_ai.models.StreamedResponse")`
Implementation of `StreamedResponse` for [FunctionModel](https://ai.pydantic.dev/api/models/function/<#pydantic_ai.models.function.FunctionModel>).
Source code in `pydantic_ai_slim/pydantic_ai/models/function.py`
```
179
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
```
| ```
@dataclass
class FunctionStreamedResponse(StreamedResponse):
"""Implementation of `StreamedResponse` for [FunctionModel][pydantic_ai.models.function.FunctionModel]."""
  _iter: AsyncIterator[str | DeltaToolCalls]
  _timestamp: datetime = field(default_factory=_utils.now_utc)
  def __post_init__(self):
    self._usage += _estimate_usage([])
  async def _get_event_iterator(self) -> AsyncIterator[ModelResponseStreamEvent]:
    async for item in self._iter:
      if isinstance(item, str):
        response_tokens = _estimate_string_tokens(item)
        self._usage += usage.Usage(response_tokens=response_tokens, total_tokens=response_tokens)
        yield self._parts_manager.handle_text_delta(vendor_part_id='content', content=item)
      else:
        delta_tool_calls = item
        for dtc_index, delta_tool_call in delta_tool_calls.items():
          if delta_tool_call.json_args:
            response_tokens = _estimate_string_tokens(delta_tool_call.json_args)
            self._usage += usage.Usage(response_tokens=response_tokens, total_tokens=response_tokens)
          maybe_event = self._parts_manager.handle_tool_call_delta(
            vendor_part_id=dtc_index,
            tool_name=delta_tool_call.name,
            args=delta_tool_call.json_args,
            tool_call_id=None,
          )
          if maybe_event is not None:
            yield maybe_event
  def timestamp(self) -> datetime:
    return self._timestamp

```
  
---|---  
© Pydantic Services Inc. 2024 to present 
