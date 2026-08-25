from pydantic import BaseModel
from typing import List

class SREMetricsStatus(BaseModel):
    slo_target: float
    current_availability: float
    error_budget_consumed_percent: float
    status: str
    mttd_avg: float
    mtta_avg: float
    mttr_avg: float
    mtbf_avg: float

    def format_report(self) -> str:
        return (
            f"SLO: {self.slo_target}%\n"
            f"Current availability: {self.current_availability}%\n"
            f"Error budget consumed: {self.error_budget_consumed_percent}%\n"
            f"Status: {self.status}\n"
        )

class SREMetricsTracker:
    """
    Tracks and computes top-level SRE indicators across the environment.
    """
    def __init__(self, slo_target: float = 99.95):
        self.slo_target = slo_target
        # Default baseline for a running system (approx 30 days)
        self.total_uptime_minutes = 43200.0 
        self.total_downtime_minutes = 12.0
        
        # Historical metric lists (in seconds)
        self.mttd_list: List[float] = [120, 300]
        self.mtta_list: List[float] = [30, 45]
        self.mttr_list: List[float] = [600, 1200]
        self.mtbf_list: List[float] = [864000, 1200000]

    def record_incident_metrics(self, mttd: float, mtta: float, mttr: float, downtime_minutes: float):
        self.mttd_list.append(mttd)
        self.mtta_list.append(mtta)
        self.mttr_list.append(mttr)
        self.total_downtime_minutes += downtime_minutes

    def calculate_status(self) -> SREMetricsStatus:
        total_time = self.total_uptime_minutes + self.total_downtime_minutes
        availability = (self.total_uptime_minutes / total_time) * 100 if total_time > 0 else 100.0
        
        # Error budget allowed downtime
        allowed_downtime = (total_time * (100 - self.slo_target)) / 100
        
        budget_consumed = 0.0
        if allowed_downtime > 0:
            budget_consumed = (self.total_downtime_minutes / allowed_downtime) * 100
            
        status = "HEALTHY"
        if budget_consumed >= 100:
            status = "VIOLATED"
        elif budget_consumed >= 75:
            status = "AT RISK"
            
        return SREMetricsStatus(
            slo_target=self.slo_target,
            current_availability=round(availability, 3),
            error_budget_consumed_percent=round(budget_consumed, 1),
            status=status,
            mttd_avg=round(sum(self.mttd_list) / len(self.mttd_list), 1) if self.mttd_list else 0.0,
            mtta_avg=round(sum(self.mtta_list) / len(self.mtta_list), 1) if self.mtta_list else 0.0,
            mttr_avg=round(sum(self.mttr_list) / len(self.mttr_list), 1) if self.mttr_list else 0.0,
            mtbf_avg=round(sum(self.mtbf_list) / len(self.mtbf_list), 1) if self.mtbf_list else 0.0,
        )
