from datetime import datetime
from .enum import *
from .maintenance_ticket import MaintenanceTicket

class Staff:
    def __init__(self, id: str, name: str, phone_number: str, status: str = "ACTIVE"):
        self.__id = id
        self.__name = name
        self.__phone_number = phone_number
        self.__status = status
        self.__hire_date = datetime.now()
        self.__current_task = None

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def phone_number(self):
        return self.__phone_number

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status: str):
        self.__status = new_status

    @property
    def hire_date(self):
        return self.__hire_date

    @property
    def current_task(self):
        return self.__current_task

    def update_status(self, task, status: str):
        """Update the given task's status (not the staff member's status)."""
        if hasattr(task, "update_maintenance_status"):
            task.update_maintenance_status(status)
        else:
            setattr(task, "status", status)
        return status

    def assign_task(self, task):
        self.__current_task = task
        self.__status = "WORKING"
        return self.__current_task

    def complete_task(self):
        self.__current_task = None
        self.__status = "AVAILABLE"
        return self.__status


class Cleaner(Staff):
    ID = 1

    def __init__(self, name: str, phone_number: str, cleaning_supplies_list=None, assigned_rooms=None, status: str = "ACTIVE"):
        cl_id = f"CL-{Cleaner.ID:04d}"
        super().__init__(id=cl_id,
                        name=name,
                        phone_number=phone_number,
                        status=status)
        self.__cleaning_supplies_list = cleaning_supplies_list or []
        self.__assigned_rooms = assigned_rooms or []

        Cleaner.ID += 1

    @property
    def cleaning_supplies_list(self):
        return self.__cleaning_supplies_list

    @property
    def assigned_rooms(self):
        return self.__assigned_rooms

    def clean_room(self, room_id):
        if room_id not in self.__assigned_rooms:
            self.__assigned_rooms.append(room_id)
        self.status = "WORKING"
        return {"room": room_id, "status": "cleaning"}


class Technician(Staff):
    ID = 1

    def __init__(
        self,
        name: str,
        phone_number: str,
        capabilities: list = None,
        schedule=None,
        current_task=None,
        status = AvailabilityStatus.AVAILABLE,
    ):
        tech_id = f"TC-{Technician.ID:04d}"
        super().__init__(tech_id, name, phone_number, status=status)
        self.__capabilities = capabilities or []
        self.__schedule = schedule
        self._current_task = current_task

        Technician.ID += 1

    @property
    def capabilities(self):
        return self.__capabilities

    @property
    def schedule(self):
        return self.__schedule

    def show_all_mt(self, building_id):
        # Placeholder: return maintenance tasks for a building
        return []

    def start_maintenance(self, notes: str = None):
        if self._current_task is None:
            raise ValueError(f"Technician {self.id} has no assigned ticket")

        ticket = self._current_task

        if ticket.issue_category not in self.__capabilities:
            raise PermissionError(
                f"Technician {self.id} is not capable of handling '{ticket.issue_category}' "
                f"(capabilities: {self.__capabilities})"
            )

        self.status = AvailabilityStatus.UNAVAILABLE
        ticket.begin_work(notes)

        return {
            "technician_id": self.id,
            "technician_name": self.name,
            "ticket_id": ticket.id,
            "room_id": ticket.room_id,
            "issue_category": ticket.issue_category,
            "status": ticket.status.value,
            "start_time": str(ticket.start_time),
            "notes": ticket.notes,
        }

    def finish_maintenance(self):
        if self._current_task is None:
            raise ValueError(f"Technician {self.id} has no assigned ticket")

        ticket = self._current_task

        if ticket.status != MaintenanceStatus.IN_PROGRESS:
            raise ValueError(f"Ticket {ticket.id} is not in progress, cannot finish")

        cost = MaintenanceCost[ticket.issue_category].value
        ticket.finish_work(cost)

        self.status = AvailabilityStatus.AVAILABLE
        completed_ticket = self._current_task
        self._current_task = None

        return completed_ticket

    def assign_ticket(self, ticket):
        self.status = AvailabilityStatus.UNAVAILABLE
        self._current_task = ticket

        ticket.update_maintenance_status("FINISH")
        self.status = AvailabilityStatus.AVAILABLE
        return "done"


class ElectricalTech(Technician):
    def __init__(self, name: str, phone_number: str, certification_no: str = None, **kwargs):
        kwargs["capabilities"] = ["ELECTRICAL"]
        super().__init__(name, phone_number, **kwargs)
        self.__certification_no = certification_no

    @property
    def certification_no(self):
        return self.__certification_no

    def start_maintenance(self, notes: str = None):
        if not self.__certification_no:
            raise PermissionError(
                f"Technician {self.id} cannot start electrical work without a certification"
            )
        return super().start_maintenance(notes)


class PlumbingTech(Technician):
    def __init__(self, name: str, phone_number: str, water_meter_tool: str = None, **kwargs):
        kwargs["capabilities"] = ["PLUMBING"]
        super().__init__(name, phone_number, **kwargs)
        self.__water_meter_tool = water_meter_tool

    @property
    def water_meter_tool(self):
        return self.__water_meter_tool

    def start_maintenance(self, notes: str = None):
        if not self.__water_meter_tool:
            raise ValueError(
                f"Technician {self.id} has no water meter tool available"
            )
        return super().start_maintenance(notes)


class ACTech(Technician):
    MIN_GAS_LEVEL = 20.0

    def __init__(self, name: str, phone_number: str, gas_level_refrigerant: float = 100.0, **kwargs):
        kwargs["capabilities"] = ["AC"]
        super().__init__(name, phone_number, **kwargs)
        self.__gas_level_refrigerant = gas_level_refrigerant

    @property
    def gas_level_refrigerant(self):
        return self.__gas_level_refrigerant

    def start_maintenance(self, notes: str = None):
        if self.__gas_level_refrigerant < ACTech.MIN_GAS_LEVEL:
            raise ValueError(
                f"Gas level too low ({self.__gas_level_refrigerant}%). "
                f"Minimum required: {ACTech.MIN_GAS_LEVEL}%"
            )
        return super().start_maintenance(notes)

    def finish_maintenance(self):
        self.__gas_level_refrigerant = max(0.0, self.__gas_level_refrigerant - 10.0)
        return super().finish_maintenance()