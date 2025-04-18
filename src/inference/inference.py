#inference module

import pytholog as pl
from dataclasses import dataclass

@dataclass
class InferenceEngine:
    __knowledgeBase: pl.KnowledgeBase = pl.KnowledgeBase("kb")

    @property
    def knowledgeBase(self) -> pl.KnowledgeBase:
        return self.__knowledgeBase

    def print_kb(self):
        print(self.__knowledgeBase)

    def print_kb_db(self):
        print(self.__knowledgeBase.db)

    def query(self, query: str):
        query_result = self.__knowledgeBase.query(pl.Expr(query))
        return query_result