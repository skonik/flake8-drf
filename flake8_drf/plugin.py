import ast
from _ast import Call
from typing import Any, Generator, List, Tuple, Type, NamedTuple, Union

from flake8_drf.constants import STATUS_CODES, DRF_RESPONSE_CLASS_NAME, DRF_RESPONSE_STATUS_KEYWORD


class Flake8Error(NamedTuple):
    lineno: int
    col_offset: int
    msg: str


class Visitor(ast.NodeVisitor):
    parent = None

    def __init__(self) -> None:
        self.errors: List[Flake8Error] = []


    def _check_error(
            self,
            status_code: int,
            arg: Union[ast.arg, ast.keyword],
    ) -> None:
        if status_code in STATUS_CODES.keys():
            change_to = STATUS_CODES[status_code]
            error = Flake8Error(
                arg.lineno,
                arg.col_offset,
                f'DRF0 Status code can be changed to constant: {change_to}',
            )
            self.errors.append(error)

    def _check_positional_args(self, node: ast.Call) -> None:
        if node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant):
                status_code = arg.value
                self._check_error(status_code, arg)

    def _check_status_keyword_args(self, node: ast.Call):
        for keyword in node.keywords:
            if keyword.arg == DRF_RESPONSE_STATUS_KEYWORD:
                if isinstance(keyword.value, (ast.Constant, ast.Num)):
                    status_code = keyword.value.value
                    self._check_error(status_code, keyword)

    def visit_Call(self, node: Call) -> Any:
        if isinstance(node.func, ast.Name):
            callable_name = node.func.id
            if callable_name == DRF_RESPONSE_CLASS_NAME:
                self._check_positional_args(node)
                self._check_status_keyword_args(node)


class Plugin:
    name = 'flake8-drf'
    version = '0.1.0'

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self) -> Generator[Tuple[int, int, str, Type[Any]], None, None]:
        visitor = Visitor()
        visitor.visit(self._tree)
        for error in visitor.errors:
            yield error.lineno, error.col_offset, error.msg, type(self)
