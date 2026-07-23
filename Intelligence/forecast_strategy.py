from abc import ABC
from abc import abstractmethod

from intelligence.state import EconomicState
from intelligence.forecast import EconomicForecast


class ForecastStrategy(ABC):

    """
    Strategy interface.

    Future implementations:

    RuleBasedStrategy

    BayesianStrategy

    MLForecastStrategy

    EnsembleStrategy
    """

    @abstractmethod
    def forecast(
        self,
        state: EconomicState,
    ) -> EconomicForecast:
        pass
