from typing import TypeVar, Generic, Tuple, Type, List, Any, Dict, Union

T = TypeVar('T')


class CommandParser(Generic[T]):
	class StrParser:
		types: Tuple[Type]
		input_type: T

		def __init__(self, input_type: T, types: Tuple[Type]):
			self.input_type = input_type
			self.types = types

		def parse(self, args: List[str]) -> Tuple[T, Tuple[Any]]:
			if len(args) != len(self.types):
				raise ValueError(f"{len(self.types)} arguments expected, {len(args)} actually received")
			parsed = tuple(_type(args[i]) for (i, _type) in enumerate(self.types))
			return self.input_type, parsed

	default_action: StrParser
	actions: Dict[str, StrParser]

	def __init__(self,
			default_action: Union[
				Tuple[T, Type],
				Tuple[T, ...],
			],
			actions: List[Union[
				Tuple[T, List[str]],
				Tuple[T, ...]
			]]
	):
		self.default_action = self.StrParser(default_action[0], default_action[1:])
		self.actions = dict()
		for action in actions:
			for matched in action[1]:
				self.actions[matched] = self.StrParser(action[0], action[2:])

	def parse(self, input_str: str) -> Tuple[T, Tuple[Any]]:
		parts = input_str.split(maxsplit=1)

		if parts[0] in self.actions:
			return self.actions[parts[0]].parse(parts[1:])

		return self.default_action.parse(parts)
