from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MissionTask:
    """
    One actionable task within a product mission.
    """

    title: str
    description: str
    category: str
    priority: int
    estimated_minutes: int
    completed: bool = False


@dataclass(slots=True)
class MissionPlan:
    """
    Action plan generated for one affiliate product.
    """

    product_name: str
    mission_title: str
    objective: str
    primary_channel: str
    estimated_total_minutes: int
    tasks: list[MissionTask] = field(
        default_factory=list
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "ProductName": self.product_name,
            "MissionTitle": self.mission_title,
            "Objective": self.objective,
            "PrimaryChannel": self.primary_channel,
            "EstimatedTotalMinutes": (
                self.estimated_total_minutes
            ),
            "Tasks": [
                {
                    "Title": task.title,
                    "Description": task.description,
                    "Category": task.category,
                    "Priority": task.priority,
                    "EstimatedMinutes": (
                        task.estimated_minutes
                    ),
                    "Completed": task.completed,
                }
                for task in self.tasks
            ],
        }