"""What each fault code means, its usual causes and what to check first.

This is the kind of knowledge that normally lives in a maintenance
engineer's head or a PDF manual. Keeping it in one small table means the
report can suggest first checks automatically. The codes are generic
examples for this demo cell, not any robot vendor's real codes.
"""

FAULTS = {
    "E-PWR-01": {
        "name": "Supply voltage dip",
        "causes": ["Large motor starting on the same supply", "Loose terminal in the cabinet", "Grid disturbance"],
        "checks": ["Compare the time with other machines starting up", "Check cabinet terminals and supply logs"],
    },
    "E-COMM-02": {
        "name": "Fieldbus timeout",
        "causes": ["Short power dip on the network switch", "Damaged or loose network cable", "Overloaded bus"],
        "checks": ["Check whether a power fault happened just before", "Inspect connectors and cable routing near moving parts"],
    },
    "E-GRIP-01": {
        "name": "Gripper vacuum below threshold",
        "causes": ["Worn suction cup", "Leak in the vacuum hose", "Dirty filter or ejector"],
        "checks": ["Inspect and replace the suction cup", "Leak-test the vacuum line", "Clean the ejector filter"],
    },
    "E-JNT-03": {
        "name": "Joint 3 over-temperature",
        "causes": ["Long run of heavy-payload cycles", "Blocked cooling fan", "Gearbox wear increasing friction"],
        "checks": ["Look at payload and cycle rate before the fault", "Check the fan and clean the motor housing", "Plan a gearbox check if it keeps repeating"],
    },
    "E-COLL-01": {
        "name": "Collision detected",
        "causes": ["Part placed out of position", "Changed fixture or tooling", "Path not updated after a change"],
        "checks": ["Check part position sensors on the conveyor", "Review recent program or fixture changes"],
    },
    "E-SAFE-01": {
        "name": "Light curtain tripped",
        "causes": ["Operator entered the cell", "Misaligned or dirty light curtain"],
        "checks": ["Check whether entries were planned (maintenance, material refill)", "Clean and realign the light curtain"],
    },
    "E-CONV-01": {
        "name": "Conveyor jam",
        "causes": ["Part stuck at a transfer point", "Worn belt or guide"],
        "checks": ["Inspect transfer points and guides", "Check belt tension"],
    },
}

UNKNOWN = {"name": "Unknown fault code", "causes": ["Code not in the knowledge base yet"], "checks": ["Look it up in the controller manual and add it to knowledge.py"]}


def describe(code: str) -> dict:
    return FAULTS.get(code, UNKNOWN)
