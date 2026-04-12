def grade(trajectory, *args, **kwargs):
    """
    REAL GRADER: Evaluates the agent's actual performance trajectory.
    It checks the final observations to see if the AI actually 
    neutralized the threat and restored the service.
    """
    if not trajectory:
        return 0.0
    
    # Get the final observation from the agent's run
    last_step = trajectory[-1]
    last_obs = str(last_step.get("observation", ""))
    
    # Grade based on actual environment logic outcomes
    if "SUCCESS: Full recovery achieved" in last_obs:
        return 1.0  # Perfect score for the hardest task
    elif "SUCCESS: Service restored" in last_obs:
        return 0.95 # Excellent score for standard tasks
    elif "SUCCESS" in last_obs:
        return 0.5  # Partial credit (fixed one issue but didn't finish)
    elif "CRITICAL ERROR" in last_obs:
        return 0.0  # Failed (killed the wrong process)
    
    return 0.1 # Base score for participating but failing to restore