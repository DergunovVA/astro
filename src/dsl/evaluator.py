"""
DSL Evaluator - выполнение AST на данных натальной карты

Evaluator принимает AST от Parser и выполняет его на данных карты,
возвращая результат (обычно bool для формул-условий).

Поддерживает:
- Логические операторы: AND, OR, NOT
- Сравнения: ==, !=, <, >, <=, >=, IN
- Доступ к свойствам: Sun.Sign, Mars.House
- Агрегаторы: planets.Dignity, aspects.Type

Примеры:
    >>> from src.dsl.parser import parse
    >>> from src.dsl.evaluator import Evaluator
    >>>
    >>> # Простая карта (для примера)
    >>> chart_data = {
    ...     'planets': {
    ...         'Sun': {'Sign': 'Capricorn', 'House': 9, 'Dignity': 'Neutral'},
    ...         'Moon': {'Sign': 'Aquarius', 'House': 2, 'Dignity': 'Neutral'},
    ...         'Mars': {'Sign': 'Libra', 'House': 6, 'Retrograde': False}
    ...     }
    ... }
    >>>
    >>> evaluator = Evaluator(chart_data)
    >>> ast = parse("Sun.Sign == Capricorn")
    >>> result = evaluator.evaluate(ast)
    >>> print(result)  # True
"""

from typing import Any, List, Dict, Union
from src.dsl.parser import ASTNode, NodeType


class EvaluatorError(Exception):
    """Ошибка при выполнении формулы"""

    pass


class Evaluator:
    """
    Выполняет AST на данных натальной карты

    Attributes:
        chart_data: Данные карты (словарь с планетами, домами, аспектами)

    Ожидаемая структура chart_data:
        {
            'planets': {
                'Sun': {'Sign': 'Aries', 'House': 1, 'Dignity': 'Exaltation', ...},
                'Moon': {...},
                ...
            },
            'houses': {
                1: {'Sign': 'Aries', 'Ruler': 'Mars', ...},
                2: {...},
                ...
            },
            'aspects': [
                {'Planet1': 'Sun', 'Planet2': 'Moon', 'Type': 'Conjunction', ...},
                ...
            ]
        }
    """

    def __init__(self, chart_data: Dict[str, Any]):
        """
        Инициализация Evaluator

        Args:
            chart_data: Данные натальной карты
        """
        self.chart_data = chart_data

    def evaluate(self, ast: ASTNode) -> Any:
        """
        Выполнить AST и вернуть результат

        Args:
            ast: Корневой узел AST

        Returns:
            Результат вычисления (обычно bool, но может быть любой тип)

        Raises:
            EvaluatorError: Если выполнение невозможно
        """
        return self._eval_node(ast)

    def _eval_node(self, node: ASTNode) -> Any:
        """
        Диспетчер - выбирает метод выполнения по типу узла

        Args:
            node: Узел AST для выполнения

        Returns:
            Результат выполнения узла
        """
        if node.type == NodeType.BINARY_OP:
            return self._eval_binary_op(node)
        elif node.type == NodeType.UNARY_OP:
            return self._eval_unary_op(node)
        elif node.type == NodeType.COMPARISON:
            return self._eval_comparison(node)
        elif node.type == NodeType.PROPERTY:
            return self._eval_property(node)
        elif node.type == NodeType.AGGREGATOR:
            return self._eval_aggregator(node)
        elif node.type == NodeType.IDENTIFIER:
            return self._eval_identifier(node)
        elif node.type == NodeType.NUMBER:
            return self._eval_number(node)
        elif node.type == NodeType.STRING:
            return self._eval_string(node)
        elif node.type == NodeType.BOOLEAN:
            return self._eval_boolean(node)
        elif node.type == NodeType.LIST:
            return self._eval_list(node)
        else:
            raise EvaluatorError(f"Неизвестный тип узла: {node.type}")

    def _eval_binary_op(self, node: ASTNode) -> bool:
        """
        Выполнить бинарный оператор (AND, OR)

        Args:
            node: Узел BINARY_OP

        Returns:
            Результат логической операции
        """
        left = self._eval_node(node.left)
        right = self._eval_node(node.right)

        if node.value == "AND" or node.value == "&&":
            return bool(left) and bool(right)
        elif node.value == "OR" or node.value == "||":
            return bool(left) or bool(right)
        else:
            raise EvaluatorError(f"Неизвестный бинарный оператор: {node.value}")

    def _eval_unary_op(self, node: ASTNode) -> bool:
        """
        Выполнить унарный оператор (NOT)

        Args:
            node: Узел UNARY_OP

        Returns:
            Результат логического отрицания
        """
        operand = self._eval_node(node.operand)

        if node.value == "NOT" or node.value == "!":
            return not bool(operand)
        else:
            raise EvaluatorError(f"Неизвестный унарный оператор: {node.value}")

    def _eval_comparison(self, node: ASTNode) -> bool:
        """
        Выполнить сравнение (==, !=, <, >, <=, >=, IN)

        Args:
            node: Узел COMPARISON

        Returns:
            Результат сравнения
        """
        left = self._eval_node(node.left)
        right = self._eval_node(node.right)

        if node.value == "==":
            return left == right
        elif node.value == "!=":
            return left != right
        elif node.value == "<":
            return left < right
        elif node.value == ">":
            return left > right
        elif node.value == "<=":
            return left <= right
        elif node.value == ">=":
            return left >= right
        elif node.value == "IN":
            # Правая часть должна быть списком
            if not isinstance(right, list):
                raise EvaluatorError(
                    f"Оператор IN требует список справа, получен: {type(right)}"
                )
            return left in right
        else:
            raise EvaluatorError(f"Неизвестный оператор сравнения: {node.value}")

    def _eval_property(self, node: ASTNode) -> Any:
        """
        Получить значение свойства объекта (Sun.Sign → "Aries")

        Args:
            node: Узел PROPERTY

        Returns:
            Значение свойства

        Raises:
            EvaluatorError: Если объект или свойство не найдены
        """
        # Получаем имя объекта (Sun, Moon, Mars, ...)
        obj_name = self._eval_node(node.object)

        if not isinstance(obj_name, str):
            raise EvaluatorError(
                f"Имя объекта должно быть строкой, получен: {type(obj_name)}"
            )

        property_name = node.property

        # Ищем объект в данных карты
        # Сначала пробуем в planets
        if "planets" in self.chart_data and obj_name in self.chart_data["planets"]:
            planet_data = self.chart_data["planets"][obj_name]
            if property_name in planet_data:
                return planet_data[property_name]
            else:
                raise EvaluatorError(
                    f"Свойство '{property_name}' не найдено у планеты '{obj_name}'. "
                    f"Доступные свойства: {list(planet_data.keys())}"
                )

        # Потом в houses (если это числовой идентификатор)
        if "houses" in self.chart_data:
            try:
                house_num = int(obj_name)
                if house_num in self.chart_data["houses"]:
                    house_data = self.chart_data["houses"][house_num]
                    if property_name in house_data:
                        return house_data[property_name]
                    else:
                        raise EvaluatorError(
                            f"Свойство '{property_name}' не найдено у дома {house_num}"
                        )
            except ValueError:
                pass  # obj_name не число

        raise EvaluatorError(
            f"Объект '{obj_name}' не найден в данных карты. "
            f"Доступные планеты: {list(self.chart_data.get('planets', {}).keys())}"
        )

    def _eval_aggregator(self, node: ASTNode) -> List[Any]:
        """
        Раскрыть агрегатор в список значений

        planets.Dignity → [Sun.Dignity, Moon.Dignity, Mercury.Dignity, ...]

        Args:
            node: Узел AGGREGATOR

        Returns:
            Список значений свойства для всех объектов в агрегаторе
        """
        aggregator = node.aggregator
        property_name = node.property

        if aggregator == "planets":
            if "planets" not in self.chart_data:
                raise EvaluatorError("Данные планет отсутствуют в карте")

            # Собираем значения свойства для каждой планеты
            result = []
            for planet_name, planet_data in self.chart_data["planets"].items():
                if property_name in planet_data:
                    result.append(planet_data[property_name])
                else:
                    raise EvaluatorError(
                        f"Свойство '{property_name}' не найдено у планеты '{planet_name}'"
                    )
            return result

        elif aggregator == "houses":
            if "houses" not in self.chart_data:
                raise EvaluatorError("Данные домов отсутствуют в карте")

            result = []
            for house_num, house_data in self.chart_data["houses"].items():
                if property_name in house_data:
                    result.append(house_data[property_name])
                else:
                    raise EvaluatorError(
                        f"Свойство '{property_name}' не найдено у дома {house_num}"
                    )
            return result

        elif aggregator == "aspects":
            if "aspects" not in self.chart_data:
                raise EvaluatorError("Данные аспектов отсутствуют в карте")

            result = []
            for aspect in self.chart_data["aspects"]:
                if property_name in aspect:
                    result.append(aspect[property_name])
                else:
                    raise EvaluatorError(
                        f"Свойство '{property_name}' не найдено у аспекта"
                    )
            return result

        else:
            raise EvaluatorError(f"Неизвестный агрегатор: {aggregator}")

    def _eval_identifier(self, node: ASTNode) -> str:
        """
        Вернуть значение идентификатора

        Args:
            node: Узел IDENTIFIER

        Returns:
            Строковое значение идентификатора
        """
        return node.value

    def _eval_number(self, node: ASTNode) -> Union[int, float]:
        """
        Вернуть числовое значение

        Args:
            node: Узел NUMBER

        Returns:
            Числовое значение
        """
        return node.value

    def _eval_string(self, node: ASTNode) -> str:
        """
        Вернуть строковое значение

        Args:
            node: Узел STRING

        Returns:
            Строковое значение
        """
        return node.value

    def _eval_boolean(self, node: ASTNode) -> bool:
        """
        Вернуть булево значение

        Args:
            node: Узел BOOLEAN

        Returns:
            Булево значение
        """
        return node.value

    def _eval_list(self, node: ASTNode) -> List[Any]:
        """
        Вычислить список (выполнить каждый элемент)

        Args:
            node: Узел LIST

        Returns:
            Список вычисленных значений
        """
        return [self._eval_node(child) for child in node.children]


def evaluate(formula: str, chart_data: Dict[str, Any]) -> Any:
    """
    Convenience function - выполнить формулу на карте

    Args:
        formula: Текстовая формула DSL
        chart_data: Данные натальной карты

    Returns:
        Результат вычисления

    Example:
        >>> chart = {'planets': {'Sun': {'Sign': 'Aries'}}}
        >>> result = evaluate("Sun.Sign == Aries", chart)
        >>> print(result)  # True
    """
    from src.dsl.parser import parse

    ast = parse(formula)
    evaluator = Evaluator(chart_data)
    return evaluator.evaluate(ast)
