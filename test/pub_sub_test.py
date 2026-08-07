# 创建事件总线
from typing import Callable, Any

container: dict[str, list] = {}


# 创建订阅者
def subscribe(event_type: str, callback: Callable):
    """
    订阅者
    :param event_type:
    :param callback:
    :return:
    """
    if not event_type in container:
        container[event_type] = []
    container[event_type].append(callback)

def tom_to_weather(data:dict[str,Any]):
    print(f"tom收到了{data}")

def jack_to_tech(data:dict[str,Any]):
    print(f"jack收到了{data}")

def publish(event_type: str, data: dict[str, Any]):
    """
    发布的本质 将对应的事件类型的数据发送给订阅者 给订阅者消费
    :param event_type:
    :param data:
    :return:
    """
    if event_type in container:
        for callback in container[event_type]:
            callback(data)


# 订阅者先行 核心逻辑在订阅者身上
subscribe("weather",tom_to_weather)
subscribe("tech",jack_to_tech)

# 把方法和需要的数据类型都发给发布者
publish("weather",{"city":"上海","weather":"晴天"})
publish("tech",{"ai":"deepseek v4 pro发布了"})

