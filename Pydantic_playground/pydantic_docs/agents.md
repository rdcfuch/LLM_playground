# Source URL: https://ai.pydantic.dev/agents/

[ Skip to content ](https://ai.pydantic.dev/agents/<#introduction>)
[ ![logo](https://ai.pydantic.dev/img/logo-white.svg) ](https://ai.pydantic.dev/agents/<..> "PydanticAI")
PydanticAI 
Agents 
Initializing search 
[ pydantic/pydantic-ai  ](https://ai.pydantic.dev/agents/<https:/github.com/pydantic/pydantic-ai> "Go to repository")
[ ![logo](https://ai.pydantic.dev/img/logo-white.svg) ](https://ai.pydantic.dev/agents/<..> "PydanticAI") PydanticAI 
[ pydantic/pydantic-ai  ](https://ai.pydantic.dev/agents/<https:/github.com/pydantic/pydantic-ai> "Go to repository")
  * [ Introduction  ](https://ai.pydantic.dev/agents/<..>)
  * [ Installation  ](https://ai.pydantic.dev/agents/<../install/>)
  * [ Getting Help  ](https://ai.pydantic.dev/agents/<../help/>)
  * [ Contributing  ](https://ai.pydantic.dev/agents/<../contributing/>)
  * [ Troubleshooting  ](https://ai.pydantic.dev/agents/<../troubleshooting/>)
  * Documentation  Documentation 
    * Agents  [ Agents  ](https://ai.pydantic.dev/agents/<./>) Table of contents 
      * [ Introduction  ](https://ai.pydantic.dev/agents/<#introduction>)
      * [ Running Agents  ](https://ai.pydantic.dev/agents/<#running-agents>)
        * [ Additional Configuration  ](https://ai.pydantic.dev/agents/<#additional-configuration>)
          * [ Usage Limits  ](https://ai.pydantic.dev/agents/<#usage-limits>)
          * [ Model (Run) Settings  ](https://ai.pydantic.dev/agents/<#model-run-settings>)
        * [ Model specific settings  ](https://ai.pydantic.dev/agents/<#model-specific-settings>)
      * [ Runs vs. Conversations  ](https://ai.pydantic.dev/agents/<#runs-vs-conversations>)
      * [ Type safe by design  ](https://ai.pydantic.dev/agents/<#static-type-checking>)
      * [ System Prompts  ](https://ai.pydantic.dev/agents/<#system-prompts>)
      * [ Reflection and self-correction  ](https://ai.pydantic.dev/agents/<#reflection-and-self-correction>)
      * [ Model errors  ](https://ai.pydantic.dev/agents/<#model-errors>)
    * [ Models  ](https://ai.pydantic.dev/agents/<../models/>)
    * [ Dependencies  ](https://ai.pydantic.dev/agents/<../dependencies/>)
    * [ Function Tools  ](https://ai.pydantic.dev/agents/<../tools/>)
    * [ Results  ](https://ai.pydantic.dev/agents/<../results/>)
    * [ Messages and chat history  ](https://ai.pydantic.dev/agents/<../message-history/>)
    * [ Testing and Evals  ](https://ai.pydantic.dev/agents/<../testing-evals/>)
    * [ Debugging and Monitoring  ](https://ai.pydantic.dev/agents/<../logfire/>)
    * [ Multi-agent Applications  ](https://ai.pydantic.dev/agents/<../multi-agent-applications/>)
    * [ Graphs  ](https://ai.pydantic.dev/agents/<../graph/>)
  * [ Examples  ](https://ai.pydantic.dev/agents/<../examples/>)
Examples 
    * [ Pydantic Model  ](https://ai.pydantic.dev/agents/<../examples/pydantic-model/>)
    * [ Weather agent  ](https://ai.pydantic.dev/agents/<../examples/weather-agent/>)
    * [ Bank support  ](https://ai.pydantic.dev/agents/<../examples/bank-support/>)
    * [ SQL Generation  ](https://ai.pydantic.dev/agents/<../examples/sql-gen/>)
    * [ Flight booking  ](https://ai.pydantic.dev/agents/<../examples/flight-booking/>)
    * [ RAG  ](https://ai.pydantic.dev/agents/<../examples/rag/>)
    * [ Stream markdown  ](https://ai.pydantic.dev/agents/<../examples/stream-markdown/>)
    * [ Stream whales  ](https://ai.pydantic.dev/agents/<../examples/stream-whales/>)
    * [ Chat App with FastAPI  ](https://ai.pydantic.dev/agents/<../examples/chat-app/>)
    * [ Question Graph  ](https://ai.pydantic.dev/agents/<../examples/question-graph/>)
  * API Reference  API Reference 
    * [ pydantic_ai.agent  ](https://ai.pydantic.dev/agents/<../api/agent/>)
    * [ pydantic_ai.tools  ](https://ai.pydantic.dev/agents/<../api/tools/>)
    * [ pydantic_ai.result  ](https://ai.pydantic.dev/agents/<../api/result/>)
    * [ pydantic_ai.messages  ](https://ai.pydantic.dev/agents/<../api/messages/>)
    * [ pydantic_ai.exceptions  ](https://ai.pydantic.dev/agents/<../api/exceptions/>)
    * [ pydantic_ai.settings  ](https://ai.pydantic.dev/agents/<../api/settings/>)
    * [ pydantic_ai.usage  ](https://ai.pydantic.dev/agents/<../api/usage/>)
    * [ pydantic_ai.format_as_xml  ](https://ai.pydantic.dev/agents/<../api/format_as_xml/>)
    * [ pydantic_ai.models  ](https://ai.pydantic.dev/agents/<../api/models/base/>)
    * [ pydantic_ai.models.openai  ](https://ai.pydantic.dev/agents/<../api/models/openai/>)
    * [ pydantic_ai.models.anthropic  ](https://ai.pydantic.dev/agents/<../api/models/anthropic/>)
    * [ pydantic_ai.models.gemini  ](https://ai.pydantic.dev/agents/<../api/models/gemini/>)
    * [ pydantic_ai.models.vertexai  ](https://ai.pydantic.dev/agents/<../api/models/vertexai/>)
    * [ pydantic_ai.models.groq  ](https://ai.pydantic.dev/agents/<../api/models/groq/>)
    * [ pydantic_ai.models.mistral  ](https://ai.pydantic.dev/agents/<../api/models/mistral/>)
    * [ pydantic_ai.models.ollama  ](https://ai.pydantic.dev/agents/<../api/models/ollama/>)
    * [ pydantic_ai.models.test  ](https://ai.pydantic.dev/agents/<../api/models/test/>)
    * [ pydantic_ai.models.function  ](https://ai.pydantic.dev/agents/<../api/models/function/>)
    * [ pydantic_graph  ](https://ai.pydantic.dev/agents/<../api/pydantic_graph/graph/>)
    * [ pydantic_graph.nodes  ](https://ai.pydantic.dev/agents/<../api/pydantic_graph/nodes/>)
    * [ pydantic_graph.state  ](https://ai.pydantic.dev/agents/<../api/pydantic_graph/state/>)
    * [ pydantic_graph.mermaid  ](https://ai.pydantic.dev/agents/<../api/pydantic_graph/mermaid/>)
    * [ pydantic_graph.exceptions  ](https://ai.pydantic.dev/agents/<../api/pydantic_graph/exceptions/>)


Table of contents 
  * [ Introduction  ](https://ai.pydantic.dev/agents/<#introduction>)
  * [ Running Agents  ](https://ai.pydantic.dev/agents/<#running-agents>)
    * [ Additional Configuration  ](https://ai.pydantic.dev/agents/<#additional-configuration>)
      * [ Usage Limits  ](https://ai.pydantic.dev/agents/<#usage-limits>)
      * [ Model (Run) Settings  ](https://ai.pydantic.dev/agents/<#model-run-settings>)
    * [ Model specific settings  ](https://ai.pydantic.dev/agents/<#model-specific-settings>)
  * [ Runs vs. Conversations  ](https://ai.pydantic.dev/agents/<#runs-vs-conversations>)
  * [ Type safe by design  ](https://ai.pydantic.dev/agents/<#static-type-checking>)
  * [ System Prompts  ](https://ai.pydantic.dev/agents/<#system-prompts>)
  * [ Reflection and self-correction  ](https://ai.pydantic.dev/agents/<#reflection-and-self-correction>)
  * [ Model errors  ](https://ai.pydantic.dev/agents/<#model-errors>)


  1. [ Introduction  ](https://ai.pydantic.dev/agents/<..>)
  2. [ Documentation  ](https://ai.pydantic.dev/agents/<./>)


# Agents
## Introduction
Agents are PydanticAI's primary interface for interacting with LLMs.
In some use cases a single Agent will control an entire application or component, but multiple agents can also interact to embody more complex workflows.
The `Agent`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent>) class has full API documentation, but conceptually you can think of an agent as a container for:
**Component** | **Description**  
---|---  
[System prompt(s)](https://ai.pydantic.dev/agents/<#system-prompts>) | A set of instructions for the LLM written by the developer.  
[Function tool(s)](https://ai.pydantic.dev/agents/<../tools/>) | Functions that the LLM may call to get information while generating a response.  
[Structured result type](https://ai.pydantic.dev/agents/<../results/>) | The structured datatype the LLM must return at the end of a run, if specified.  
[Dependency type constraint](https://ai.pydantic.dev/agents/<../dependencies/>) | System prompt functions, tools, and result validators may all use dependencies when they're run.  
[LLM model](https://ai.pydantic.dev/agents/<../api/models/base/>) | Optional default LLM model associated with the agent. Can also be specified when running the agent.  
[Model Settings](https://ai.pydantic.dev/agents/<#additional-configuration>) | Optional default model settings to help fine tune requests. Can also be specified when running the agent.  
In typing terms, agents are generic in their dependency and result types, e.g., an agent which required dependencies of type `Foobar` and returned results of type `list[str]` would have type `Agent[Foobar, list[str]]`. In practice, you shouldn't need to care about this, it should just mean your IDE can tell you when you have the right type, and if you choose to use [static type checking](https://ai.pydantic.dev/agents/<#static-type-checking>) it should work well with PydanticAI.
Here's a toy example of an agent that simulates a roulette wheel:
roulette_wheel.py```
from pydantic_ai import Agent, RunContext
roulette_agent = Agent( 
Create an agent, which expects an integer dependency and returns a boolean result. This agent will have type Agent[int, bool].
[](https://ai.pydantic.dev/agents/<#__code_0_annotation_1>)
  'openai:gpt-4o',
  deps_type=int,
  result_type=bool,
  system_prompt=(
    'Use the `roulette_wheel` function to see if the '
    'customer has won based on the number they provide.'
  ),
)

@roulette_agent.tool
async def roulette_wheel(ctx: RunContext[int], square: int) -> str: 
Define a tool that checks if the square is a winner. Here RunContext[](https://ai.pydantic.dev/agents/<../api/tools/#pydantic_ai.tools.RunContext>) is parameterized with the dependency type int; if you got the dependency type wrong you'd get a typing error.
[](https://ai.pydantic.dev/agents/<#__code_0_annotation_2>)
"""check if the square is a winner"""
  return 'winner' if square == ctx.deps else 'loser'

# Run the agent
success_number = 18 
In reality, you might want to use a random number here e.g. random.randint(0, 36).
[](https://ai.pydantic.dev/agents/<#__code_0_annotation_3>)
result = roulette_agent.run_sync('Put my money on square eighteen', deps=success_number)
print(result.data) 
result.data will be a boolean indicating if the square is a winner. Pydantic performs the result validation, it'll be typed as a bool since its type is derived from the result_type generic parameter of the agent.
[](https://ai.pydantic.dev/agents/<#__code_0_annotation_4>)
#> True
result = roulette_agent.run_sync('I bet five is the winner', deps=success_number)
print(result.data)
#> False

```

Agents are designed for reuse, like FastAPI Apps
Agents are intended to be instantiated once (frequently as module globals) and reused throughout your application, similar to a small [FastAPI](https://ai.pydantic.dev/agents/<https:/fastapi.tiangolo.com/reference/fastapi/#fastapi.FastAPI>) app or an [APIRouter](https://ai.pydantic.dev/agents/<https:/fastapi.tiangolo.com/reference/apirouter/#fastapi.APIRouter>).
## Running Agents
There are three ways to run an agent:
  1. `agent.run()`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.run>) — a coroutine which returns a `RunResult`[](https://ai.pydantic.dev/agents/<../api/result/#pydantic_ai.result.RunResult>) containing a completed response
  2. `agent.run_sync()`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.run_sync>) — a plain, synchronous function which returns a `RunResult`[](https://ai.pydantic.dev/agents/<../api/result/#pydantic_ai.result.RunResult>) containing a completed response (internally, this just calls `loop.run_until_complete(self.run())`)
  3. `agent.run_stream()`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.run_stream>) — a coroutine which returns a `StreamedRunResult`[](https://ai.pydantic.dev/agents/<../api/result/#pydantic_ai.result.StreamedRunResult>), which contains methods to stream a response as an async iterable


Here's a simple example demonstrating all three:
run_agent.py```
from pydantic_ai import Agent
agent = Agent('openai:gpt-4o')
result_sync = agent.run_sync('What is the capital of Italy?')
print(result_sync.data)
#> Rome

async def main():
  result = await agent.run('What is the capital of France?')
  print(result.data)
  #> Paris
  async with agent.run_stream('What is the capital of the UK?') as response:
    print(await response.get_data())
    #> London

```

_(This example is complete, it can be run "as is" — you'll need to add`asyncio.run(main())` to run `main`)_
You can also pass messages from previous runs to continue a conversation or provide context, as described in [Messages and Chat History](https://ai.pydantic.dev/agents/<../message-history/>).
### Additional Configuration
#### Usage Limits
PydanticAI offers a `UsageLimits`[](https://ai.pydantic.dev/agents/<../api/usage/#pydantic_ai.usage.UsageLimits>) structure to help you limit your usage (tokens and/or requests) on model runs.
You can apply these settings by passing the `usage_limits` argument to the `run{_sync,_stream}` functions.
Consider the following example, where we limit the number of response tokens:
```
from pydantic_ai import Agent
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits
agent = Agent('claude-3-5-sonnet-latest')
result_sync = agent.run_sync(
  'What is the capital of Italy? Answer with just the city.',
  usage_limits=UsageLimits(response_tokens_limit=10),
)
print(result_sync.data)
#> Rome
print(result_sync.usage())
"""
Usage(requests=1, request_tokens=62, response_tokens=1, total_tokens=63, details=None)
"""
try:
  result_sync = agent.run_sync(
    'What is the capital of Italy? Answer with a paragraph.',
    usage_limits=UsageLimits(response_tokens_limit=10),
  )
except UsageLimitExceeded as e:
  print(e)
  #> Exceeded the response_tokens_limit of 10 (response_tokens=32)

```

Restricting the number of requests can be useful in preventing infinite loops or excessive tool calling:
```
from typing_extensions import TypedDict
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.exceptions import UsageLimitExceeded
from pydantic_ai.usage import UsageLimits

class NeverResultType(TypedDict):
"""
  Never ever coerce data to this type.
  """
  never_use_this: str

agent = Agent(
  'claude-3-5-sonnet-latest',
  retries=3,
  result_type=NeverResultType,
  system_prompt='Any time you get a response, call the `infinite_retry_tool` to produce another response.',
)

@agent.tool_plain(retries=5) 
This tool has the ability to retry 5 times before erroring, simulating a tool that might get stuck in a loop.
[](https://ai.pydantic.dev/agents/<#__code_3_annotation_1>)
def infinite_retry_tool() -> int:
  raise ModelRetry('Please try again.')

try:
  result_sync = agent.run_sync(
    'Begin infinite retry loop!', usage_limits=UsageLimits(request_limit=3) 
This run will error after 3 requests, preventing the infinite tool calling.
[](https://ai.pydantic.dev/agents/<#__code_3_annotation_2>)
  )
except UsageLimitExceeded as e:
  print(e)
  #> The next request would exceed the request_limit of 3

```

Note
This is especially relevant if you're registered a lot of tools, `request_limit` can be used to prevent the model from choosing to make too many of these calls.
#### Model (Run) Settings
PydanticAI offers a `settings.ModelSettings`[](https://ai.pydantic.dev/agents/<../api/settings/#pydantic_ai.settings.ModelSettings>) structure to help you fine tune your requests. This structure allows you to configure common parameters that influence the model's behavior, such as `temperature`, `max_tokens`, `timeout`, and more.
There are two ways to apply these settings: 1. Passing to `run{_sync,_stream}` functions via the `model_settings` argument. This allows for fine-tuning on a per-request basis. 2. Setting during `Agent`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent>) initialization via the `model_settings` argument. These settings will be applied by default to all subsequent run calls using said agent. However, `model_settings` provided during a specific run call will override the agent's default settings.
For example, if you'd like to set the `temperature` setting to `0.0` to ensure less random behavior, you can do the following:
```
from pydantic_ai import Agent
agent = Agent('openai:gpt-4o')
result_sync = agent.run_sync(
  'What is the capital of Italy?', model_settings={'temperature': 0.0}
)
print(result_sync.data)
#> Rome

```

### Model specific settings
If you wish to further customize model behavior, you can use a subclass of `ModelSettings`[](https://ai.pydantic.dev/agents/<../api/settings/#pydantic_ai.settings.ModelSettings>), like `AnthropicModelSettings`[](https://ai.pydantic.dev/agents/<../api/models/anthropic/#pydantic_ai.models.anthropic.AnthropicModelSettings>), associated with your model of choice.
For example:
```
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModelSettings
agent = Agent('anthropic:claude-3-5-sonnet-latest')
result_sync = agent.run_sync(
  'What is the capital of Italy?',
  model_settings=AnthropicModelSettings(anthropic_metadata={'user_id': 'my_user_id'}),
)
print(result_sync.data)
#> Rome

```

## Runs vs. Conversations
An agent **run** might represent an entire conversation — there's no limit to how many messages can be exchanged in a single run. However, a **conversation** might also be composed of multiple runs, especially if you need to maintain state between separate interactions or API calls.
Here's an example of a conversation comprised of multiple runs:
conversation_example.py```
from pydantic_ai import Agent
agent = Agent('openai:gpt-4o')
# First run
result1 = agent.run_sync('Who was Albert Einstein?')
print(result1.data)
#> Albert Einstein was a German-born theoretical physicist.
# Second run, passing previous messages
result2 = agent.run_sync(
  'What was his most famous equation?',
  message_history=result1.new_messages(), 
Continue the conversation; without message_history the model would not know who "his" was referring to.
[](https://ai.pydantic.dev/agents/<#__code_6_annotation_1>)
)
print(result2.data)
#> Albert Einstein's most famous equation is (E = mc^2).

```

_(This example is complete, it can be run "as is")_
## Type safe by design
PydanticAI is designed to work well with static type checkers, like mypy and pyright.
Typing is (somewhat) optional
PydanticAI is designed to make type checking as useful as possible for you if you choose to use it, but you don't have to use types everywhere all the time.
That said, because PydanticAI uses Pydantic, and Pydantic uses type hints as the definition for schema and validation, some types (specifically type hints on parameters to tools, and the `result_type` arguments to `Agent`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent>)) are used at runtime.
We (the library developers) have messed up if type hints are confusing you more than helping you, if you find this, please create an [issue](https://ai.pydantic.dev/agents/<https:/github.com/pydantic/pydantic-ai/issues>) explaining what's annoying you!
In particular, agents are generic in both the type of their dependencies and the type of results they return, so you can use the type hints to ensure you're using the right types.
Consider the following script with type mistakes:
type_mistakes.py```
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class User:
  name: str

agent = Agent(
  'test',
  deps_type=User, 
The agent is defined as expecting an instance of User as deps.
[](https://ai.pydantic.dev/agents/<#__code_7_annotation_1>)
  result_type=bool,
)

@agent.system_prompt
def add_user_name(ctx: RunContext[str]) -> str: 
But here add_user_name is defined as taking a str as the dependency, not a User.
[](https://ai.pydantic.dev/agents/<#__code_7_annotation_2>)
  return f"The user's name is {ctx.deps}."

def foobar(x: bytes) -> None:
  pass

result = agent.run_sync('Does their name start with "A"?', deps=User('Anne'))
foobar(result.data) 
Since the agent is defined as returning a bool, this will raise a type error since foobar expects bytes.
[](https://ai.pydantic.dev/agents/<#__code_7_annotation_3>)

```

Running `mypy` on this will give the following output:
```
➤uvrunmypytype_mistakes.py
type_mistakes.py:18:error:Argument1to"system_prompt"of"Agent"hasincompatibletype"Callable[[RunContext[str]], str]";expected"Callable[[RunContext[User]], str]"[arg-type]
type_mistakes.py:28:error:Argument1to"foobar"hasincompatibletype"bool";expected"bytes"[arg-type]
Found2errorsin1file(checked1sourcefile)

```

Running `pyright` would identify the same issues.
## System Prompts
System prompts might seem simple at first glance since they're just strings (or sequences of strings that are concatenated), but crafting the right system prompt is key to getting the model to behave as you want.
Generally, system prompts fall into two categories:
  1. **Static system prompts** : These are known when writing the code and can be defined via the `system_prompt` parameter of the `Agent`[ constructor](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.__init__>).
  2. **Dynamic system prompts** : These depend in some way on context that isn't known until runtime, and should be defined via functions decorated with `@agent.system_prompt`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.system_prompt>).


You can add both to a single agent; they're appended in the order they're defined at runtime.
Here's an example using both types of system prompts:
system_prompts.py```
from datetime import date
from pydantic_ai import Agent, RunContext
agent = Agent(
  'openai:gpt-4o',
  deps_type=str, 
The agent expects a string dependency.
[](https://ai.pydantic.dev/agents/<#__code_9_annotation_1>)
  system_prompt="Use the customer's name while replying to them.", 
Static system prompt defined at agent creation time.
[](https://ai.pydantic.dev/agents/<#__code_9_annotation_2>)
)

@agent.system_prompt 
Dynamic system prompt defined via a decorator with RunContext[](https://ai.pydantic.dev/agents/<../api/tools/#pydantic_ai.tools.RunContext>), this is called just after run_sync, not when the agent is created, so can benefit from runtime information like the dependencies used on that run.
[](https://ai.pydantic.dev/agents/<#__code_9_annotation_3>)
def add_the_users_name(ctx: RunContext[str]) -> str:
  return f"The user's name is {ctx.deps}."

@agent.system_prompt
def add_the_date() -> str: 
Another dynamic system prompt, system prompts don't have to have the RunContext parameter.
[](https://ai.pydantic.dev/agents/<#__code_9_annotation_4>)
  return f'The date is {date.today()}.'

result = agent.run_sync('What is the date?', deps='Frank')
print(result.data)
#> Hello Frank, the date today is 2032-01-02.

```

_(This example is complete, it can be run "as is")_
## Reflection and self-correction
Validation errors from both function tool parameter validation and [structured result validation](https://ai.pydantic.dev/agents/<../results/#structured-result-validation>) can be passed back to the model with a request to retry.
You can also raise `ModelRetry`[](https://ai.pydantic.dev/agents/<../api/exceptions/#pydantic_ai.exceptions.ModelRetry>) from within a [tool](https://ai.pydantic.dev/agents/<../tools/>) or [result validator function](https://ai.pydantic.dev/agents/<../results/#result-validators-functions>) to tell the model it should retry generating a response.
  * The default retry count is **1** but can be altered for the [entire agent](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.__init__>), a [specific tool](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.tool>), or a [result validator](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.__init__>).
  * You can access the current retry count from within a tool or result validator via `ctx.retry`[](https://ai.pydantic.dev/agents/<../api/tools/#pydantic_ai.tools.RunContext>).


Here's an example:
tool_retry.py```
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext, ModelRetry
from fake_database import DatabaseConn

class ChatResult(BaseModel):
  user_id: int
  message: str

agent = Agent(
  'openai:gpt-4o',
  deps_type=DatabaseConn,
  result_type=ChatResult,
)

@agent.tool(retries=2)
def get_user_by_name(ctx: RunContext[DatabaseConn], name: str) -> int:
"""Get a user's ID from their full name."""
  print(name)
  #> John
  #> John Doe
  user_id = ctx.deps.users.get(name=name)
  if user_id is None:
    raise ModelRetry(
      f'No user found with name {name!r}, remember to provide their full name'
    )
  return user_id

result = agent.run_sync(
  'Send a message to John Doe asking for coffee next week', deps=DatabaseConn()
)
print(result.data)
"""
user_id=123 message='Hello John, would you be free for coffee sometime next week? Let me know what works for you!'
"""

```

## Model errors
If models behave unexpectedly (e.g., the retry limit is exceeded, or their API returns `503`), agent runs will raise `UnexpectedModelBehavior`[](https://ai.pydantic.dev/agents/<../api/exceptions/#pydantic_ai.exceptions.UnexpectedModelBehavior>).
In these cases, `capture_run_messages`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.capture_run_messages>) can be used to access the messages exchanged during the run to help diagnose the issue.
```
from pydantic_ai import Agent, ModelRetry, UnexpectedModelBehavior, capture_run_messages
agent = Agent('openai:gpt-4o')

@agent.tool_plain
def calc_volume(size: int) -> int: 
Define a tool that will raise ModelRetry repeatedly in this case.
[](https://ai.pydantic.dev/agents/<#__code_11_annotation_1>)
  if size == 42:
    return size**3
  else:
    raise ModelRetry('Please try again.')

with capture_run_messages() as messages: 
capture_run_messages[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.capture_run_messages>) is used to capture the messages exchanged during the run.
[](https://ai.pydantic.dev/agents/<#__code_11_annotation_2>)
  try:
    result = agent.run_sync('Please get me the volume of a box with size 6.')
  except UnexpectedModelBehavior as e:
    print('An error occurred:', e)
    #> An error occurred: Tool exceeded max retries count of 1
    print('cause:', repr(e.__cause__))
    #> cause: ModelRetry('Please try again.')
    print('messages:', messages)
"""
    messages:
    [
      ModelRequest(
        parts=[
          UserPromptPart(
            content='Please get me the volume of a box with size 6.',
            timestamp=datetime.datetime(...),
            part_kind='user-prompt',
          )
        ],
        kind='request',
      ),
      ModelResponse(
        parts=[
          ToolCallPart(
            tool_name='calc_volume',
            args={'size': 6},
            tool_call_id=None,
            part_kind='tool-call',
          )
        ],
        model_name='function:model_logic',
        timestamp=datetime.datetime(...),
        kind='response',
      ),
      ModelRequest(
        parts=[
          RetryPromptPart(
            content='Please try again.',
            tool_name='calc_volume',
            tool_call_id=None,
            timestamp=datetime.datetime(...),
            part_kind='retry-prompt',
          )
        ],
        kind='request',
      ),
      ModelResponse(
        parts=[
          ToolCallPart(
            tool_name='calc_volume',
            args={'size': 6},
            tool_call_id=None,
            part_kind='tool-call',
          )
        ],
        model_name='function:model_logic',
        timestamp=datetime.datetime(...),
        kind='response',
      ),
    ]
    """
  else:
    print(result.data)

```

_(This example is complete, it can be run "as is")_
Note
If you call `run`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.run>), `run_sync`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.run_sync>), or `run_stream`[](https://ai.pydantic.dev/agents/<../api/agent/#pydantic_ai.agent.Agent.run_stream>) more than once within a single `capture_run_messages` context, `messages` will represent the messages exchanged during the first call only.
© Pydantic Services Inc. 2024 to present 
