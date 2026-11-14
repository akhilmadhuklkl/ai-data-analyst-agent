"""Application services shared by the UI and future API surfaces."""

from dataclasses import dataclass

import pandas as pd

from ai_data_analyst.ai import OllamaInterpreter
from ai_data_analyst.database import DatabaseQueryResult, SQLiteDatabase, run_database_question
from ai_data_analyst.pipeline import PipelineResult, run_analysis


@dataclass(frozen=True)
class ApplicationServices:
    """Reusable application-level entry points."""

    def analyze_dataframe(
        self,
        dataframe: pd.DataFrame,
        question: str,
        use_local_ai: bool = False,
    ) -> PipelineResult:
        """Analyze dataframe data using the selected interpreter."""

        interpreter = OllamaInterpreter().interpret if use_local_ai else None
        return run_analysis(dataframe, question, interpreter=interpreter)

    def analyze_database(
        self,
        database: SQLiteDatabase,
        question: str,
    ) -> DatabaseQueryResult:
        """Generate and execute a safe SQL question against a database."""

        return run_database_question(database, question)
