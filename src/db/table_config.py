from dataclasses import dataclass

@dataclass
class TableFillData:
    columns: list[str]
    rows: list[list[str | int]]

@dataclass
class TableConfig:
    name: str
    columns_data: str
    fill_data: TableFillData
