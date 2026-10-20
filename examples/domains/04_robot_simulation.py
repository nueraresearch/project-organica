"""
Multi-Domain Reproduction Pack — Domain 4: Autonomous Robotic Kinematics
Expected emergence:
  - Sensorimotor loops: 'sonar' -> 'obstacle' -> 'turn' -> 'clear'
  - Experiment probing to resolve obstacle navigation ambiguity
"""

from pathlib import Path
from organica import MemoryService, SleepService

def run():
    print("=" * 60)
    print("Reproduction Domain 4: Autonomous Robotic Kinematics")
    print("=" * 60)
    
    db_path = Path("robot_domain.db")
    if db_path.exists():
        db_path.unlink()
        
    mem = MemoryService(db_path)
    
    events = [
        "robot drive forward velocity high",
        "sonar detect obstacle distance near",
        "actuator steer pivot turn left",
        "sonar sense clear corridor open",
        "robot drive forward velocity high",
        "sonar detect obstacle distance near",
        "actuator steer pivot turn right",
        "sonar sense clear corridor open",
        "robot drive forward velocity high",
        "sonar detect obstacle distance near",
        "actuator steer pivot turn left",
        "sonar sense clear corridor open",
    ] * 5
    
    for e in events:
        mem.store(e, event_type="observe", source="ros_kinematics")
        
    sleep = SleepService(mem)
    print(f"Loaded {mem.count()} robotic sensorimotor events. Running sleep cycles...")
    for cycle in range(1, 4):
        report = sleep.run()
        print(f"Cycle {cycle}: {len(report.processes)} processes, {len(report.questions)} questions, "
              f"{len(report.investigations)} investigations, {len(report.experiments)} experiments")
              
    assert len(report.processes) > 0 or len(report.questions) > 0, "Failed to emerge robotic sensorimotor structures!"
    if report.questions:
        q = report.questions[0]
        print(f"\n[ROBOTIC UNCERTAINTY] When '{q.subject}' occurs, will robot see: {q.competing_expectations}?")
    if report.experiments:
        exp = report.experiments[0]
        print(f"[ACTIONABLE EXPERIMENT] Action: {exp.action_type} | Payload: {exp.probe_payload['test_vector']}")
        
    mem.close()
    if db_path.exists():
        db_path.unlink()
    print("Domain 4 verified.\n")

if __name__ == "__main__":
    run()
