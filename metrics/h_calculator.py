class HCalculator:
    @staticmethod
    def calculate(U: float, D: float, A: float, lambdas: dict) -> float:
        H = lambdas["U"] * U + lambdas["D"] * D - lambdas["A"] * A
        return max(0.0, min(1.0, H))