from pydantic import BaseModel


class BusinessImpact(BaseModel):
    impact_per_minute: float
    incident_duration_seconds: float
    total_impact: float
    formatted_estimate: str

class BusinessImpactCalculator:
    """
    Estimates the financial and user impact of an incident based on traffic data.
    """
    def __init__(self, request_rate_per_sec: int = 100, revenue_per_request: float = 0.05):
        self.request_rate_per_sec = request_rate_per_sec
        self.revenue_per_request = revenue_per_request

    def calculate_impact(self, duration_seconds: float, failure_rate_percent: float = 100.0) -> BusinessImpact:
        # Number of failed requests per second
        failed_requests_per_sec = self.request_rate_per_sec * (failure_rate_percent / 100.0)
        
        impact_per_sec = failed_requests_per_sec * self.revenue_per_request
        impact_per_minute = impact_per_sec * 60.0
        
        total_impact = impact_per_sec * duration_seconds
        
        mins = int(duration_seconds // 60)
        secs = int(duration_seconds % 60)
        
        formatted = (
            f"Estimated impact: ${impact_per_minute:,.0f}/min\n"
            f"Incident duration: {mins}m {secs}s\n"
            f"Estimated total impact: ${total_impact:,.0f}"
        )
        
        return BusinessImpact(
            impact_per_minute=impact_per_minute,
            incident_duration_seconds=duration_seconds,
            total_impact=total_impact,
            formatted_estimate=formatted
        )
