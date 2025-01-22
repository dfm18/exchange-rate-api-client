class UnsupportedCodeError(Exception):
    pass


class InvalidKeyError(Exception):
    pass


class InactiveAccountError(Exception):
    pass


class QuotaReachedError(Exception):
    pass


class PlanUpgradeRequiredError(Exception):
    pass


class NoDataAvailableError(Exception):
    pass
