from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from typing import Union
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 从.env文件中读取DeepSeek模型的相关信息
DeepSeek_MODEL = os.getenv('DeepSeek_MODEL')
DeepSeek_API_KEY = os.getenv('DeepSeek_API_KEY')
DeepSeek_BASE_URL = os.getenv('DeepSeek_BASE_URL')


# 定义机票预订结果的数据模型
class FlightBookingResult(BaseModel):
    flight_number: str
    departure: str
    arrival: str


# 定义天气查询结果的数据模型
class WeatherResult(BaseModel):
    temperature: int
    weather_condition: str


# 定义最终决策结果的数据模型
class DecisionResult(BaseModel):
    need_umbrella: bool
    reason: str


# 创建DeepSeek模型实例
deepseek_model = OpenAIModel(
    model_name=DeepSeek_MODEL,
    api_key=DeepSeek_API_KEY,
    base_url=DeepSeek_BASE_URL,
)

# 创建机票预订agent
flight_booking_agent = Agent(
    model=deepseek_model,
    result_type=FlightBookingResult,
    system_prompt='Book a flight for the user based on their request.'
)

# 创建天气查询agent
weather_agent = Agent(
    model=deepseek_model,
    result_type=WeatherResult,
    system_prompt='Provide the weather forecast for the given location and date.'
)

# 创建决策agent
decision_agent = Agent(
    model=deepseek_model,
    result_type=DecisionResult,
    system_prompt='Decide if the user needs an umbrella based on the weather forecast.'
)

# 创建主对话agent
main_agent = Agent(
    model=deepseek_model,
    system_prompt='Help the user with their travel plans by booking a flight, checking the weather, and deciding if they need an umbrella.'
)


# 机票预订agent的工具函数
@flight_booking_agent.tool
async def book_flight(ctx: RunContext[str], destination: str, date: str) -> FlightBookingResult:
    # 这里可以调用实际的机票预订API
    return FlightBookingResult(flight_number='AK123', departure='2024-02-28', arrival=destination)


# 天气查询agent的工具函数
@weather_agent.tool
async def get_weather(ctx: RunContext[str], location: str, date: str) -> WeatherResult:
    # 这里可以调用实际的天气查询API
    return WeatherResult(temperature=22, weather_condition='sunny')


# 决策agent的工具函数
@decision_agent.tool
async def make_decision(ctx: RunContext[str], weather: WeatherResult) -> DecisionResult:
    # 根据天气情况做出决策
    if weather.weather_condition == 'rainy':
        return DecisionResult(need_umbrella=True, reason='It will rain.')
    else:
        return DecisionResult(need_umbrella=False, reason='It will not rain.')


# 主对话agent的工具函数
@main_agent.tool
async def handle_user_request(ctx: RunContext[str], user_request: str) -> str:
    print(f"Handling user request: {user_request}")

    # 简单的意图识别逻辑
    if 'book a flight' in user_request.lower():
        # 调用机票预订agent
        destination = 'New York'
        date = '2024-02-28'
        flight_result = await flight_booking_agent.run(f'Book a flight to {destination} on {date}.')
        print(f"Flight booking result: {flight_result.data}")
        return f'Flight booked: {flight_result.data.flight_number}'

    elif 'weather' in user_request.lower():
        # 调用天气查询agent
        location = 'New York'
        date = '2024-02-28'
        weather_result = await weather_agent.run(f'What will the weather be like in {location} on {date}?')
        print(f"Weather forecast result: {weather_result.data}")
        return f'Weather forecast: {weather_result.data.weather_condition}, {weather_result.data.temperature}°C'

    elif 'umbrella' in user_request.lower():
        # 调用决策agent
        weather_result = WeatherResult(temperature=22, weather_condition='sunny')
        decision_result = await decision_agent.run(f'Based on the weather forecast, do I need an umbrella?',
                                                   deps=weather_result)
        print(f"Decision result: {decision_result.data}")
        return f'Decision: {"Bring an umbrella" if decision_result.data.need_umbrella else "No umbrella needed"} because {decision_result.data.reason}'

    else:
        # 直接回复用户消息
        return "I'm sorry, I didn't understand your request. Please ask about flight booking, weather, or if you need an umbrella."


# 主函数，协调主对话agent的工作
async def main():
    while True:
        # 用户请求
        user_request = input("How can I assist you today? (type 'exit' to quit): ")

        # 检查用户是否想要退出
        if user_request.lower() == 'exit':
            print("Goodbye!")
            break

        # 调用主对话agent
        try:
            response = await main_agent.run(user_request)
            # 输出最终回复
            print(response.data)
            # print(response.all_messages_json())
        except Exception as e:
            print(f"An error occurred: {e}")


# 运行主函数
import asyncio

asyncio.run(main())
