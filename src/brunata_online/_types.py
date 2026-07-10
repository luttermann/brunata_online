from typing import TypeAlias

JsonDict: TypeAlias = dict[str, object]
JsonData: TypeAlias = JsonDict | list[JsonDict]

